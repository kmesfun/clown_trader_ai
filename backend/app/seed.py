import asyncio
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import Player, Portfolio, PlayerType

PLAYERS = [
    {
        "name": "The Clown",
        "slug": "the-clown",
        "type": PlayerType.clown,
        "strategy_description": "Mirrors Jim Cramer's public stock picks. Buys at next market open after recommendation. No options, no leverage — pure Cramer chaos.",
        "avatar_emoji": "🤡",
    },
    {
        "name": "The Indexer",
        "slug": "the-indexer",
        "type": PlayerType.bot,
        "strategy_description": "Buy & hold SPY/QQQ/VTI. DCA $1,000/week into each ETF until fully deployed. Rebalances quarterly to equal weight. The boring baseline.",
        "avatar_emoji": "📊",
    },
    {
        "name": "The Quant",
        "slug": "the-quant",
        "type": PlayerType.bot,
        "strategy_description": "RSI(14) mean reversion + 200 SMA trend filter on S&P 500 stocks. Buys oversold, sells overbought. Risks 2% per trade with 5% stop-loss.",
        "avatar_emoji": "🤖",
    },
    {
        "name": "YOLO Bot",
        "slug": "yolo-bot",
        "type": PlayerType.bot,
        "strategy_description": "Simulated 3x leveraged momentum plays on the highest-volatility tickers. Buys 5% of portfolio on breakouts. Holds until +100% or -50%. Risk is the feature.",
        "avatar_emoji": "🎰",
    },
    {
        "name": "Theta Gang",
        "slug": "theta-gang",
        "type": PlayerType.bot,
        "strategy_description": "Simulates premium selling (covered calls, cash-secured puts) on high-IV blue chips. Targets +2% per 21-day cycle. Cuts at -8% loss.",
        "avatar_emoji": "🧛",
    },
    {
        "name": "Inverse Clown",
        "slug": "inverse-clown",
        "type": PlayerType.bot,
        "strategy_description": "Takes the exact opposite position of every Cramer pick. Cramer says buy? We short. Cramer says sell? We buy. $5,000 per trade, 15% stop-loss.",
        "avatar_emoji": "🔄",
    },
    {
        "name": "Degen GPT",
        "slug": "degen-gpt",
        "type": PlayerType.bot,
        "strategy_description": "LLM-powered trading via Claude API. Analyzes momentum data and portfolio state. Makes 0-3 trades per day with AI-generated reasoning. Pure chaos intelligence.",
        "avatar_emoji": "🦍",
    },
]


async def seed(db: AsyncSession):
    from sqlalchemy import select
    for player_data in PLAYERS:
        result = await db.execute(select(Player).where(Player.slug == player_data["slug"]))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"[Seed] {player_data['name']} already exists, skipping")
            continue

        player = Player(**player_data)
        db.add(player)
        await db.flush()

        portfolio = Portfolio(
            player_id=player.id,
            cash_balance=Decimal("100000"),
            settled_cash=Decimal("100000"),
            total_equity=Decimal("100000"),
        )
        db.add(portfolio)
        print(f"[Seed] Created player: {player_data['name']}")

    await db.commit()
    print("[Seed] Done!")


async def run():
    async with AsyncSessionLocal() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(run())
