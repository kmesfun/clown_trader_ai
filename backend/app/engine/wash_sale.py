import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trade, TradeDirection


async def check_wash_sale(
    player_id: uuid.UUID,
    ticker: str,
    loss_amount: Decimal,
    sold_at: datetime,
    db: AsyncSession,
) -> Decimal:
    """
    Check if a loss sale triggers the wash sale rule.
    Returns the disallowed loss amount (0 if no wash sale).

    Wash sale applies if a substantially identical security is purchased
    within 30 days before or after the loss sale.
    """
    if loss_amount >= 0:
        return Decimal("0")

    window_start = sold_at - timedelta(days=30)
    window_end = sold_at + timedelta(days=30)

    result = await db.execute(
        select(Trade).where(
            and_(
                Trade.player_id == player_id,
                Trade.ticker == ticker,
                Trade.direction.in_([TradeDirection.buy, TradeDirection.buy_to_open]),
                Trade.executed_at >= window_start,
                Trade.executed_at <= window_end,
                Trade.id != None,
            )
        )
    )
    repurchases = result.scalars().all()

    if repurchases:
        disallowed = abs(loss_amount)
        return disallowed

    return Decimal("0")


async def apply_wash_sale_to_trade(trade_id: uuid.UUID, disallowed_amount: Decimal, db: AsyncSession) -> None:
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if trade:
        trade.wash_sale_flag = True
        trade.disallowed_loss_amount = disallowed_amount
        await db.commit()
