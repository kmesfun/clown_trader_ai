import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerType
from app.bots.base_bot import BaseBot
from app.bots.indexer import IndexerBot
from app.bots.quant import QuantBot
from app.bots.yolo import YoloBot
from app.bots.theta_gang import ThetaGangBot
from app.bots.inverse_clown import InverseClownBot
from app.bots.degen_gpt import DegenGPTBot

BOT_REGISTRY: dict[str, type[BaseBot]] = {
    "the-indexer": IndexerBot,
    "the-quant": QuantBot,
    "yolo-bot": YoloBot,
    "theta-gang": ThetaGangBot,
    "inverse-clown": InverseClownBot,
    "degen-gpt": DegenGPTBot,
}


async def run_all_bots(db: AsyncSession) -> dict:
    result = await db.execute(select(Player).where(Player.type == PlayerType.bot))
    bot_players = result.scalars().all()

    summary = {}
    for player in bot_players:
        bot_class = BOT_REGISTRY.get(player.slug)
        if not bot_class:
            print(f"[BotRunner] No bot class for slug: {player.slug}")
            continue

        bot = bot_class(player_id=player.id)
        try:
            trades = await bot.run(db)
            summary[player.name] = {
                "trades_executed": len(trades),
                "tickers": [t.ticker for t in trades],
            }
            print(f"[BotRunner] {player.name}: {len(trades)} trades executed")
        except Exception as e:
            print(f"[BotRunner] {player.name} crashed: {e}")
            summary[player.name] = {"error": str(e)}

    return summary


async def run_bot(slug: str, db: AsyncSession) -> dict:
    result = await db.execute(select(Player).where(Player.slug == slug))
    player = result.scalar_one_or_none()
    if not player:
        return {"error": f"Player with slug '{slug}' not found"}

    bot_class = BOT_REGISTRY.get(slug)
    if not bot_class:
        return {"error": f"No bot class for slug '{slug}'"}

    bot = bot_class(player_id=player.id)
    try:
        trades = await bot.run(db)
        return {
            "bot": player.name,
            "trades_executed": len(trades),
            "trades": [{"ticker": t.ticker, "direction": str(t.direction)} for t in trades],
        }
    except Exception as e:
        return {"bot": player.name, "error": str(e)}
