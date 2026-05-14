import uuid
from datetime import date, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trade, Portfolio, TradeDirection
from app.engine.market_hours import next_business_day, is_business_day
from app.config import settings


async def get_day_trades_in_window(player_id: uuid.UUID, db: AsyncSession, window_days: int = 5) -> int:
    """Count day trades in the rolling 5-business-day window."""
    today = date.today()
    window_start = today
    bdays_counted = 0
    while bdays_counted < window_days:
        window_start -= timedelta(days=1)
        if is_business_day(window_start):
            bdays_counted += 1

    result = await db.execute(
        select(func.count(Trade.id)).where(
            and_(
                Trade.player_id == player_id,
                Trade.source.contains("day_trade"),
                func.date(Trade.executed_at) >= window_start,
            )
        )
    )
    return result.scalar_one() or 0


async def record_day_trade(player_id: uuid.UUID, db: AsyncSession) -> None:
    result = await db.execute(select(Portfolio).where(Portfolio.player_id == player_id))
    portfolio = result.scalar_one_or_none()
    if portfolio:
        portfolio.day_trade_count += 1


async def check_and_enforce_pdt(player_id: uuid.UUID, db: AsyncSession) -> bool:
    """Returns True if PDT is currently locked."""
    result = await db.execute(select(Portfolio).where(Portfolio.player_id == player_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        return False

    if portfolio.pdt_locked_until and portfolio.pdt_locked_until > date.today():
        return True

    if portfolio.total_equity >= settings.pdt_min_equity:
        return False

    day_trades = await get_day_trades_in_window(player_id, db)
    if day_trades >= settings.pdt_day_trade_limit:
        lock_until = next_business_day(date.today())
        for _ in range(settings.pdt_lockout_days - 1):
            lock_until = next_business_day(lock_until)
        portfolio.pdt_locked_until = lock_until
        portfolio.pdt_triggered = True
        await db.commit()
        return True

    return False


async def is_pdt_locked(player_id: uuid.UUID, db: AsyncSession) -> bool:
    result = await db.execute(select(Portfolio).where(Portfolio.player_id == player_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        return False
    if portfolio.pdt_locked_until and portfolio.pdt_locked_until > date.today():
        return True
    return False
