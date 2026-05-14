from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Trade, Player

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("")
async def list_trades(limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trade, Player)
        .join(Player, Trade.player_id == Player.id)
        .order_by(Trade.executed_at.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": str(trade.id),
            "player_id": str(trade.player_id),
            "player_name": player.name,
            "player_avatar_emoji": player.avatar_emoji,
            "ticker": trade.ticker,
            "direction": trade.direction,
            "quantity": str(trade.quantity),
            "price": str(trade.price),
            "total_value": str(trade.total_value),
            "realized_pnl": str(trade.realized_pnl) if trade.realized_pnl is not None else None,
            "wash_sale_flag": trade.wash_sale_flag,
            "source": trade.source,
            "notes": trade.notes,
            "executed_at": trade.executed_at.isoformat(),
        }
        for trade, player in rows
    ]
