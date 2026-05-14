import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base_bot import BaseBot
from app.models import Position, Portfolio
from app.engine.market_hours import now_et

UNIVERSE = ["SPY", "QQQ", "VTI"]
DCA_AMOUNT = Decimal("1000")


class IndexerBot(BaseBot):
    name = "The Indexer"

    def should_run_now(self) -> bool:
        now = now_et()
        return now.weekday() == 0 and 9 <= now.hour < 16

    async def evaluate(self, db: AsyncSession) -> list[dict]:
        signals = []
        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        now = now_et()
        is_quarterly = now.month in (1, 4, 7, 10) and now.day <= 7

        if is_quarterly:
            signals.extend(await self._rebalance(db))
        else:
            signals.extend(await self._dca(portfolio))

        return signals

    async def _dca(self, portfolio: Portfolio) -> list[dict]:
        signals = []
        for ticker in UNIVERSE:
            if portfolio.settled_cash >= DCA_AMOUNT:
                price = await self.market.get_price(ticker)
                if price:
                    qty = DCA_AMOUNT / Decimal(str(price))
                    signals.append({
                        "ticker": ticker,
                        "direction": "buy",
                        "quantity": float(round(qty, 4)),
                        "reason": f"Weekly DCA ${DCA_AMOUNT} into {ticker}",
                    })
        return signals

    async def _rebalance(self, db: AsyncSession) -> list[dict]:
        signals = []
        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        target_per = portfolio.total_equity / Decimal("3")

        positions_result = await db.execute(select(Position).where(Position.player_id == self.player_id))
        positions = {p.ticker: p for p in positions_result.scalars().all()}

        for ticker in UNIVERSE:
            price = await self.market.get_price(ticker)
            if not price:
                continue
            price_dec = Decimal(str(price))
            current_value = positions[ticker].market_value if ticker in positions else Decimal("0")
            diff = target_per - current_value

            if diff > Decimal("100"):
                qty = diff / price_dec
                signals.append({
                    "ticker": ticker,
                    "direction": "buy",
                    "quantity": float(round(qty, 4)),
                    "reason": f"Quarterly rebalance: buy {ticker} to reach equal weight",
                })
            elif diff < Decimal("-100") and ticker in positions:
                qty = abs(diff) / price_dec
                qty = min(qty, positions[ticker].quantity)
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(round(qty, 4)),
                    "reason": f"Quarterly rebalance: trim {ticker} to equal weight",
                })

        return signals
