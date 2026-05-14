import uuid
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base_bot import BaseBot
from app.models import CramerPick, PickDirection, Position, Portfolio
from app.engine.market_hours import now_et

POSITION_SIZE = Decimal("5000")
STOP_LOSS_PCT = Decimal("0.15")


class InverseClownBot(BaseBot):
    name = "Inverse Clown"

    def should_run_now(self) -> bool:
        return True  # Always ready to react to Cramer picks

    async def evaluate(self, db: AsyncSession) -> list[dict]:
        signals = []

        result = await db.execute(
            select(CramerPick).where(
                and_(
                    CramerPick.executed == True,
                    CramerPick.direction.in_([PickDirection.buy, PickDirection.sell]),
                )
            ).order_by(CramerPick.aired_at.desc()).limit(10)
        )
        recent_picks = result.scalars().all()

        positions_result = await db.execute(select(Position).where(Position.player_id == self.player_id))
        existing_positions = {p.ticker: p for p in positions_result.scalars().all()}

        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        for pos in existing_positions.values():
            if not pos.is_short:
                continue
            price = await self.market.get_price(pos.ticker)
            if not price:
                continue
            current_price = Decimal(str(price))
            loss_pct = (current_price - pos.avg_cost_basis) / pos.avg_cost_basis
            if loss_pct >= STOP_LOSS_PCT:
                signals.append({
                    "ticker": pos.ticker,
                    "direction": "cover",
                    "quantity": float(pos.quantity),
                    "reason": f"Inverse Clown: stop loss on short at {float(loss_pct)*100:.1f}%",
                })

        reacted_tickers = set(existing_positions.keys())
        for pick in recent_picks:
            ticker = pick.parsed_ticker
            if ticker in reacted_tickers:
                continue

            price = await self.market.get_price(ticker)
            if not price:
                continue

            price_dec = Decimal(str(price))
            quantity = POSITION_SIZE / price_dec

            if pick.direction == PickDirection.buy:
                signals.append({
                    "ticker": ticker,
                    "direction": "short",
                    "quantity": float(round(quantity, 4)),
                    "reason": f"Inverse Clown: Cramer said BUY → we SHORT. Pick: {pick.raw_text[:100]}",
                })
            elif pick.direction == PickDirection.sell:
                if portfolio.settled_cash >= POSITION_SIZE:
                    signals.append({
                        "ticker": ticker,
                        "direction": "buy",
                        "quantity": float(round(quantity, 4)),
                        "reason": f"Inverse Clown: Cramer said SELL → we BUY. Pick: {pick.raw_text[:100]}",
                    })

            reacted_tickers.add(ticker)

        return signals
