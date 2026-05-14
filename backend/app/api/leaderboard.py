from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Player, Portfolio

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Player, Portfolio)
        .join(Portfolio, Player.id == Portfolio.player_id)
        .order_by(Portfolio.total_return_pct.desc())
    )
    rows = result.all()

    entries = []
    for rank, (player, portfolio) in enumerate(rows, 1):
        equity = float(portfolio.total_equity)
        total_return_pct = float(portfolio.total_return_pct)

        short_gains = 0.0
        long_gains = 0.0
        short_tax = max(0, short_gains) * 0.37
        long_tax = max(0, long_gains) * 0.20
        niit = max(0, short_gains + long_gains) * 0.038
        total_tax = short_tax + long_tax + niit
        after_tax_equity = equity - total_tax

        entries.append({
            "rank": rank,
            "player_id": str(player.id),
            "name": player.name,
            "slug": player.slug,
            "type": player.type,
            "strategy_description": player.strategy_description,
            "avatar_emoji": player.avatar_emoji,
            "cash_balance": str(portfolio.cash_balance),
            "total_equity": str(portfolio.total_equity),
            "total_return_pct": str(portfolio.total_return_pct),
            "unrealized_pnl": str(portfolio.unrealized_pnl),
            "realized_pnl": str(portfolio.realized_pnl),
            "after_tax_equity": round(after_tax_equity, 2),
            "after_tax_return_pct": round((after_tax_equity - 100_000) / 100_000 * 100, 4),
            "pdt_triggered": portfolio.pdt_triggered,
        })

    return entries
