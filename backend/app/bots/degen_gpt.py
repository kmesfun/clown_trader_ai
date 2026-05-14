import uuid
import json
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base_bot import BaseBot
from app.models import Position, Portfolio
from app.engine.market_hours import now_et
from app.config import settings

UNIVERSE = [
    "GME", "AMC", "NVDA", "TSLA", "PLTR", "COIN", "MSTR", "AAPL",
    "MSFT", "META", "AMZN", "AMD", "SOFI", "RIVN", "HOOD", "RBLX",
]

MAX_POSITIONS = 5
MAX_POSITION_PCT = Decimal("0.10")
MIN_CONFIDENCE = 0.60

SYSTEM_PROMPT = """You are Degen GPT, an aggressive AI trading bot in a paper-trading arena.
Your goal is to maximize returns using momentum and sentiment signals.
Respond ONLY with a valid JSON array of trade decisions. No other text.
Each decision: {"ticker": str, "direction": "buy"|"sell"|"short"|"cover", "quantity_pct": float 0.01-0.10, "confidence": float 0-1, "reason": str}
Rules:
- Max 10% of portfolio per trade
- Only recommend trades you are >= 60% confident in
- If no good opportunities exist, return []
- Be aggressive. This is a competition."""


class DegenGPTBot(BaseBot):
    name = "Degen GPT"

    def should_run_now(self) -> bool:
        now = now_et()
        return now.hour == 10 and now.minute < 30

    async def evaluate(self, db: AsyncSession) -> list[dict]:
        if not settings.anthropic_api_key:
            print("[Degen GPT] No ANTHROPIC_API_KEY set, skipping")
            return []

        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        positions_result = await db.execute(select(Position).where(Position.player_id == self.player_id))
        positions = {p.ticker: p for p in positions_result.scalars().all()}

        momentum_data = {}
        for ticker in UNIVERSE[:10]:
            prices = await self.market.get_history(ticker, days=7)
            if len(prices) >= 2:
                momentum_7d = (prices[-1] - prices[0]) / prices[0] * 100
                momentum_data[ticker] = {
                    "price": round(prices[-1], 2),
                    "7d_momentum_pct": round(momentum_7d, 2),
                }

        portfolio_state = {
            "total_equity": float(portfolio.total_equity),
            "cash_balance": float(portfolio.settled_cash),
            "total_return_pct": float(portfolio.total_return_pct),
            "open_positions": [
                {
                    "ticker": t,
                    "quantity": float(p.quantity),
                    "avg_cost": float(p.avg_cost_basis),
                    "unrealized_pnl_pct": float(p.unrealized_pnl_pct),
                }
                for t, p in positions.items()
            ],
        }

        user_message = f"""Current portfolio state:
{json.dumps(portfolio_state, indent=2)}

7-day price momentum data:
{json.dumps(momentum_data, indent=2)}

What trades should Degen GPT make right now? Return JSON array only."""

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            raw = response.content[0].text.strip()
            decisions = json.loads(raw)
        except Exception as e:
            print(f"[Degen GPT] API call failed: {e}")
            return []

        signals = []
        open_count = len(positions)

        for decision in decisions:
            if decision.get("confidence", 0) < MIN_CONFIDENCE:
                continue
            if open_count >= MAX_POSITIONS and decision["direction"] == "buy":
                continue

            ticker = decision["ticker"].upper()
            qty_pct = min(float(decision.get("quantity_pct", 0.05)), 0.10)
            price = await self.market.get_price(ticker)
            if not price:
                continue

            price_dec = Decimal(str(price))
            position_value = portfolio.total_equity * Decimal(str(qty_pct))
            quantity = position_value / price_dec

            signals.append({
                "ticker": ticker,
                "direction": decision["direction"],
                "quantity": float(round(quantity, 4)),
                "reason": f"Degen GPT ({decision.get('confidence', 0)*100:.0f}% confidence): {decision.get('reason', '')}",
            })

            if decision["direction"] == "buy":
                open_count += 1

        return signals
