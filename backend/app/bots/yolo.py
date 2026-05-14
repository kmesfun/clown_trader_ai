import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base_bot import BaseBot
from app.models import Position, Portfolio
from app.engine.market_hours import now_et

HIGH_VOL_UNIVERSE = [
    "TSLA", "NVDA", "AMD", "MSTR", "COIN", "RIVN", "PLTR", "SOFI",
    "GME", "AMC", "SPCE", "BB", "NOK", "CLOV", "HOOD", "RBLX",
]

MAX_POSITIONS = 3
POSITION_PCT = Decimal("0.05")
MOMENTUM_THRESHOLD = 0.10
STOP_LOSS_PCT = Decimal("0.50")
TAKE_PROFIT_PCT = Decimal("1.00")
LEVERAGE = Decimal("3")


class YoloBot(BaseBot):
    name = "YOLO Bot"

    def should_run_now(self) -> bool:
        now = now_et()
        return now.hour == 10 and now.minute < 30

    async def evaluate(self, db: AsyncSession) -> list[dict]:
        signals = []

        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        positions_result = await db.execute(select(Position).where(Position.player_id == self.player_id))
        positions = {p.ticker: p for p in positions_result.scalars().all()}

        for ticker, pos in list(positions.items()):
            current_price = Decimal(str(await self.market.get_price(ticker) or pos.current_price))
            simulated_return = (current_price - pos.avg_cost_basis) / pos.avg_cost_basis * LEVERAGE

            if simulated_return <= -STOP_LOSS_PCT:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(pos.quantity),
                    "reason": f"YOLO stop loss: simulated loss {float(simulated_return)*100:.1f}%",
                })
            elif simulated_return >= TAKE_PROFIT_PCT:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(pos.quantity),
                    "reason": f"YOLO take profit: simulated gain {float(simulated_return)*100:.1f}%",
                })

        open_count = len(positions) - len([s for s in signals if s["direction"] == "sell"])
        if open_count >= MAX_POSITIONS:
            return signals

        for ticker in HIGH_VOL_UNIVERSE:
            if ticker in positions:
                continue
            if open_count >= MAX_POSITIONS:
                break

            prices = await self.market.get_history(ticker, days=10)
            if len(prices) < 6:
                continue

            momentum_5d = (prices[-1] - prices[-6]) / prices[-6] if prices[-6] else 0

            if momentum_5d >= MOMENTUM_THRESHOLD:
                price = Decimal(str(prices[-1]))
                position_value = portfolio.total_equity * POSITION_PCT
                quantity = position_value / price
                signals.append({
                    "ticker": ticker,
                    "direction": "buy",
                    "quantity": float(round(quantity, 4)),
                    "reason": f"YOLO momentum breakout: +{momentum_5d*100:.1f}% over 5 days (3x simulated leverage)",
                })
                open_count += 1

        return signals
