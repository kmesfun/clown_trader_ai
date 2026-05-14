import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base_bot import BaseBot
from app.models import Position, Portfolio
from app.engine.market_hours import now_et

THETA_UNIVERSE = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "AMZN", "META", "GOOGL"]
MAX_POSITION_PCT = Decimal("0.20")
PREMIUM_PCT = Decimal("0.02")
TAKE_PROFIT_PCT = Decimal("0.02")
STOP_LOSS_PCT = Decimal("0.08")
CYCLE_DAYS = 21


class ThetaGangBot(BaseBot):
    name = "Theta Gang"

    def should_run_now(self) -> bool:
        now = now_et()
        return now.weekday() in (0, 2, 4) and now.hour == 10 and now.minute < 30

    async def evaluate(self, db: AsyncSession) -> list[dict]:
        signals = []

        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        positions_result = await db.execute(select(Position).where(Position.player_id == self.player_id))
        positions = {p.ticker: p for p in positions_result.scalars().all()}
        now = datetime.now(timezone.utc)

        for ticker, pos in list(positions.items()):
            current_price = Decimal(str(await self.market.get_price(ticker) or pos.current_price))
            pnl_pct = (current_price - pos.avg_cost_basis) / pos.avg_cost_basis

            age_days = (now - pos.opened_at).days

            if pnl_pct >= TAKE_PROFIT_PCT:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(pos.quantity),
                    "reason": f"Theta: +{float(pnl_pct)*100:.1f}% — simulated premium collected",
                })
            elif pnl_pct <= -STOP_LOSS_PCT:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(pos.quantity),
                    "reason": f"Theta: -{abs(float(pnl_pct))*100:.1f}% — stop loss hit",
                })
            elif age_days >= CYCLE_DAYS:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(pos.quantity),
                    "reason": f"Theta: 21-day cycle complete, rolling position",
                })

        open_tickers = set(positions.keys()) - {s["ticker"] for s in signals if s["direction"] == "sell"}
        max_allocation = portfolio.total_equity * MAX_POSITION_PCT

        for ticker in THETA_UNIVERSE:
            if ticker in open_tickers:
                continue

            current_value = sum(
                p.market_value for t, p in positions.items() if t == ticker
            )
            if current_value >= max_allocation:
                continue

            price = await self.market.get_price(ticker)
            if not price:
                continue

            price_dec = Decimal(str(price))
            alloc = min(max_allocation, portfolio.settled_cash * Decimal("0.20"))
            if alloc < price_dec:
                continue

            quantity = alloc / price_dec
            signals.append({
                "ticker": ticker,
                "direction": "buy",
                "quantity": float(round(quantity, 4)),
                "reason": f"Theta: open cash-secured position, target +{float(PREMIUM_PCT)*100:.1f}% premium simulation",
            })
            break

        return signals
