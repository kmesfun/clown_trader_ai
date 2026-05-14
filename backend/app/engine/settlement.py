import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trade, Portfolio, TradeDirection


async def process_settlements(db: AsyncSession) -> int:
    """Move settled cash from pending to available. Returns count of settled trades."""
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(Trade).where(
            and_(
                Trade.settled_at <= now,
                Trade.settled_at != None,
                Trade.direction.in_([TradeDirection.sell, TradeDirection.sell_to_close, TradeDirection.cover]),
            )
        )
    )
    pending_trades = result.scalars().all()

    settled_count = 0
    for trade in pending_trades:
        portfolio_result = await db.execute(
            select(Portfolio).where(Portfolio.player_id == trade.player_id)
        )
        portfolio = portfolio_result.scalar_one_or_none()
        if portfolio and trade.total_value > 0:
            amount = trade.total_value - trade.fees
            portfolio.settled_cash += amount
            portfolio.pending_settlement = max(Decimal("0"), portfolio.pending_settlement - amount)
            trade.settled_at = None  # Mark as processed
            settled_count += 1

    await db.commit()
    return settled_count


async def queue_settlement(trade: Trade, portfolio: Portfolio) -> None:
    """Called at trade time to move cash to pending and set settled_at = T+1."""
    from app.engine.market_hours import next_business_day
    from datetime import date, timedelta, timezone
    import datetime as dt

    settled_date = next_business_day(date.today())
    settled_dt = dt.datetime.combine(settled_date, dt.time(16, 30), tzinfo=timezone.utc)
    trade.settled_at = settled_dt

    proceeds = trade.total_value - trade.fees
    portfolio.pending_settlement += proceeds
    portfolio.cash_balance += proceeds
