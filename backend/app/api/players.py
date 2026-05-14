import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Player, Portfolio, Position, Trade
from app.engine.portfolio_manager import get_portfolio_summary

router = APIRouter(prefix="/players", tags=["players"])


@router.get("")
async def list_players(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Player))
    players = result.scalars().all()
    out = []
    for p in players:
        try:
            summary = await get_portfolio_summary(p.id, db)
        except Exception:
            summary = {}
        out.append({
            "id": str(p.id),
            "name": p.name,
            "slug": p.slug,
            "type": p.type,
            "strategy_description": p.strategy_description,
            "avatar_emoji": p.avatar_emoji,
            **summary,
        })
    return out


@router.get("/{player_id}")
async def get_player(player_id: str, db: AsyncSession = Depends(get_db)):
    pid = uuid.UUID(player_id)
    result = await db.execute(select(Player).where(Player.id == pid))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    summary = await get_portfolio_summary(pid, db)

    port_result = await db.execute(select(Portfolio).where(Portfolio.player_id == pid))
    portfolio = port_result.scalar_one_or_none()

    return {
        "id": str(player.id),
        "name": player.name,
        "slug": player.slug,
        "type": player.type,
        "strategy_description": player.strategy_description,
        "avatar_emoji": player.avatar_emoji,
        **summary,
        "pdt_locked_until": portfolio.pdt_locked_until.isoformat() if portfolio and portfolio.pdt_locked_until else None,
        "realized_pnl": str(portfolio.realized_pnl) if portfolio else "0",
        "after_tax_equity": str(portfolio.after_tax_equity) if portfolio else "0",
    }


@router.get("/{player_id}/positions")
async def get_positions(player_id: str, db: AsyncSession = Depends(get_db)):
    pid = uuid.UUID(player_id)
    result = await db.execute(select(Position).where(Position.player_id == pid))
    positions = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "ticker": p.ticker,
            "quantity": str(p.quantity),
            "avg_cost_basis": str(p.avg_cost_basis),
            "current_price": str(p.current_price),
            "market_value": str(p.market_value),
            "unrealized_pnl": str(p.unrealized_pnl),
            "unrealized_pnl_pct": str(p.unrealized_pnl_pct),
            "is_short": p.is_short,
            "opened_at": p.opened_at.isoformat(),
        }
        for p in positions
    ]


@router.get("/{player_id}/trades")
async def get_player_trades(player_id: str, limit: int = 100, db: AsyncSession = Depends(get_db)):
    pid = uuid.UUID(player_id)
    result = await db.execute(
        select(Trade).where(Trade.player_id == pid).order_by(Trade.executed_at.desc()).limit(limit)
    )
    trades = result.scalars().all()
    return [_trade_to_dict(t) for t in trades]


@router.get("/{player_id}/tax")
async def get_player_tax(player_id: str, db: AsyncSession = Depends(get_db)):
    from app.models import TaxLot, TaxTerm
    from sqlalchemy import func
    pid = uuid.UUID(player_id)

    short_result = await db.execute(
        select(func.sum(TaxLot.gain_loss)).where(
            TaxLot.player_id == pid, TaxLot.term == TaxTerm.short
        )
    )
    long_result = await db.execute(
        select(func.sum(TaxLot.gain_loss)).where(
            TaxLot.player_id == pid, TaxLot.term == TaxTerm.long
        )
    )
    wash_result = await db.execute(
        select(func.sum(TaxLot.disallowed_loss)).where(TaxLot.player_id == pid)
    )

    short_gains = short_result.scalar_one() or 0
    long_gains = long_result.scalar_one() or 0
    wash_adj = wash_result.scalar_one() or 0

    short_tax = max(0, float(short_gains)) * 0.37
    long_tax = max(0, float(long_gains)) * 0.20
    niit = max(0, float(short_gains) + float(long_gains)) * 0.038
    total_tax = short_tax + long_tax + niit

    port_result = await db.execute(select(Portfolio).where(Portfolio.player_id == pid))
    portfolio = port_result.scalar_one_or_none()
    equity = float(portfolio.total_equity) if portfolio else 0
    after_tax = equity - total_tax

    return {
        "player_id": player_id,
        "total_short_term_gains": round(float(short_gains), 2),
        "total_long_term_gains": round(float(long_gains), 2),
        "wash_sale_adjustments": round(float(wash_adj), 2),
        "short_term_tax": round(short_tax, 2),
        "long_term_tax": round(long_tax, 2),
        "niit": round(niit, 2),
        "total_tax_owed": round(total_tax, 2),
        "pre_tax_equity": round(equity, 2),
        "after_tax_equity": round(after_tax, 2),
    }


def _trade_to_dict(t: Trade) -> dict:
    return {
        "id": str(t.id),
        "player_id": str(t.player_id),
        "ticker": t.ticker,
        "direction": t.direction,
        "quantity": str(t.quantity),
        "price": str(t.price),
        "total_value": str(t.total_value),
        "realized_pnl": str(t.realized_pnl) if t.realized_pnl is not None else None,
        "wash_sale_flag": t.wash_sale_flag,
        "source": t.source,
        "notes": t.notes,
        "executed_at": t.executed_at.isoformat(),
    }
