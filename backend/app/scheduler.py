from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import AsyncSessionLocal
from app.engine.market_hours import is_market_open


scheduler = AsyncIOScheduler(timezone="America/New_York")


async def pre_market_job():
    print("[Scheduler] Pre-market: fetching latest Cramer picks...")
    # In production: fetch from Quiver Quant API
    # For now, the manual entry UI handles this


async def market_open_job():
    print("[Scheduler] Market open: executing queued bot orders...")
    async with AsyncSessionLocal() as db:
        from app.bots.bot_runner import run_all_bots
        summary = await run_all_bots(db)
        print(f"[Scheduler] Bot run summary: {summary}")


async def intraday_job():
    if not is_market_open():
        return
    print("[Scheduler] Intraday: mark-to-market update...")
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from app.models import Player
        from app.engine.portfolio_manager import mark_to_market
        from app.data.market_data import MarketDataClient
        from decimal import Decimal

        client = MarketDataClient()
        result = await db.execute(select(Player))
        players = result.scalars().all()

        from app.models import Position
        all_tickers: set[str] = set()
        for player in players:
            pos_result = await db.execute(select(Position).where(Position.player_id == player.id))
            all_tickers.update(p.ticker for p in pos_result.scalars().all())

        if all_tickers:
            prices = await client.get_prices_batch(list(all_tickers))
            price_decimals = {t: Decimal(str(p)) for t, p in prices.items()}
            for player in players:
                try:
                    await mark_to_market(player.id, price_decimals, db)
                except Exception as e:
                    print(f"[Scheduler] mark-to-market failed for {player.name}: {e}")


async def market_close_job():
    print("[Scheduler] Market close: final mark-to-market...")
    await intraday_job()


async def post_close_job():
    print("[Scheduler] Post-close: processing T+1 settlements...")
    async with AsyncSessionLocal() as db:
        from app.engine.settlement import process_settlements
        count = await process_settlements(db)
        print(f"[Scheduler] Settled {count} trades")


def start_scheduler():
    scheduler.add_job(pre_market_job, CronTrigger(hour=9, minute=0, day_of_week="mon-fri"))
    scheduler.add_job(market_open_job, CronTrigger(hour=9, minute=30, day_of_week="mon-fri"))
    scheduler.add_job(intraday_job, CronTrigger(minute="*/15", hour="9-15", day_of_week="mon-fri"))
    scheduler.add_job(market_close_job, CronTrigger(hour=16, minute=0, day_of_week="mon-fri"))
    scheduler.add_job(post_close_job, CronTrigger(hour=16, minute=30, day_of_week="mon-fri"))
    scheduler.start()
    print("[Scheduler] Started — daily market cycle active")
