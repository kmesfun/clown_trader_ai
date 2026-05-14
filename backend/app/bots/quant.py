import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base_bot import BaseBot
from app.models import Position, Portfolio
from app.engine.market_hours import now_et

UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "JNJ", "V",
    "PG", "MA", "HD", "CVX", "LLY", "ABBV", "PFE", "MRK", "BAC", "KO",
    "PEP", "AVGO", "COST", "TMO", "WMT", "MCD", "ACN", "CSCO", "ABT", "DHR",
    "NKE", "NEE", "PM", "TXN", "RTX", "HON", "LOW", "BMY", "AMGN", "UNP",
    "SBUX", "IBM", "INTU", "ELV", "MDT", "AXP", "GILD", "CVS", "ISRG", "REGN",
]

RSI_BUY = 35
RSI_SELL = 65
MAX_POSITIONS = 10
RISK_PCT = Decimal("0.02")
STOP_LOSS_PCT = Decimal("0.05")


def calculate_rsi(prices: list[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0.0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0.0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_sma(prices: list[float], period: int) -> float:
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    return sum(prices[-period:]) / period


class QuantBot(BaseBot):
    name = "The Quant"

    def should_run_now(self) -> bool:
        now = now_et()
        return now.hour == 15 and now.minute < 30

    async def evaluate(self, db: AsyncSession) -> list[dict]:
        signals = []

        portfolio_result = await db.execute(select(Portfolio).where(Portfolio.player_id == self.player_id))
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            return []

        positions_result = await db.execute(select(Position).where(Position.player_id == self.player_id))
        positions = {p.ticker: p for p in positions_result.scalars().all()}

        for ticker in positions:
            position = positions[ticker]
            prices = await self.market.get_history(ticker, days=60)
            if not prices:
                continue

            rsi = calculate_rsi(prices)
            current_price = Decimal(str(prices[-1]))

            if position.stop_loss_price and current_price <= position.stop_loss_price:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(position.quantity),
                    "reason": f"Stop loss triggered at ${current_price:.2f} (RSI: {rsi:.1f})",
                })
                continue

            if rsi > RSI_SELL:
                signals.append({
                    "ticker": ticker,
                    "direction": "sell",
                    "quantity": float(position.quantity),
                    "reason": f"RSI overbought: {rsi:.1f} > {RSI_SELL}",
                })

        if len(positions) < MAX_POSITIONS:
            import random
            candidates = [t for t in UNIVERSE if t not in positions]
            random.shuffle(candidates)
            for ticker in candidates[:15]:
                if len(positions) + len([s for s in signals if s["direction"] == "buy"]) >= MAX_POSITIONS:
                    break

                prices = await self.market.get_history(ticker, days=60)
                if len(prices) < 30:
                    continue

                rsi = calculate_rsi(prices)
                sma50 = calculate_sma(prices, 50) if len(prices) >= 50 else prices[-1]
                sma200 = calculate_sma(prices, min(200, len(prices)))
                current_price = Decimal(str(prices[-1]))

                if rsi < RSI_BUY and current_price > Decimal(str(sma200)):
                    risk_amount = portfolio.total_equity * RISK_PCT
                    quantity = risk_amount / current_price
                    stop = current_price * (Decimal("1") - STOP_LOSS_PCT)
                    signals.append({
                        "ticker": ticker,
                        "direction": "buy",
                        "quantity": float(round(quantity, 4)),
                        "reason": f"RSI oversold: {rsi:.1f} < {RSI_BUY}, price above 200SMA ${sma200:.2f}",
                        "stop_loss": float(stop),
                    })

        return signals
