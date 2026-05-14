import asyncio
from typing import Optional
from functools import lru_cache
from datetime import datetime, timedelta, timezone
import yfinance as yf


class MarketDataClient:
    """Wraps yfinance for async-compatible market data fetching."""

    _price_cache: dict[str, tuple[float, datetime]] = {}
    CACHE_TTL_SECONDS = 60

    async def get_price(self, ticker: str) -> Optional[float]:
        cached = self._price_cache.get(ticker)
        if cached:
            price, ts = cached
            if (datetime.now(timezone.utc) - ts).total_seconds() < self.CACHE_TTL_SECONDS:
                return price

        try:
            price = await asyncio.to_thread(self._fetch_price, ticker)
            if price:
                self._price_cache[ticker] = (price, datetime.now(timezone.utc))
            return price
        except Exception as e:
            print(f"[MarketData] Failed to fetch price for {ticker}: {e}")
            return None

    def _fetch_price(self, ticker: str) -> Optional[float]:
        t = yf.Ticker(ticker)
        data = t.fast_info
        price = getattr(data, "last_price", None)
        if price is None:
            hist = t.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        return price

    async def get_history(self, ticker: str, days: int = 60) -> list[float]:
        try:
            return await asyncio.to_thread(self._fetch_history, ticker, days)
        except Exception as e:
            print(f"[MarketData] Failed to fetch history for {ticker}: {e}")
            return []

    def _fetch_history(self, ticker: str, days: int) -> list[float]:
        t = yf.Ticker(ticker)
        hist = t.history(period=f"{days}d")
        if hist.empty:
            return []
        return [float(c) for c in hist["Close"].tolist()]

    async def get_ohlcv(self, ticker: str, days: int = 30) -> list[dict]:
        try:
            return await asyncio.to_thread(self._fetch_ohlcv, ticker, days)
        except Exception as e:
            print(f"[MarketData] Failed to fetch OHLCV for {ticker}: {e}")
            return []

    def _fetch_ohlcv(self, ticker: str, days: int) -> list[dict]:
        t = yf.Ticker(ticker)
        hist = t.history(period=f"{days}d")
        if hist.empty:
            return []
        records = []
        for ts, row in hist.iterrows():
            records.append({
                "date": ts.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]),
            })
        return records

    async def get_prices_batch(self, tickers: list[str]) -> dict[str, float]:
        results = await asyncio.gather(*[self.get_price(t) for t in tickers])
        return {t: p for t, p in zip(tickers, results) if p is not None}

    async def get_quote(self, ticker: str) -> dict:
        try:
            return await asyncio.to_thread(self._fetch_quote, ticker)
        except Exception as e:
            print(f"[MarketData] Failed to fetch quote for {ticker}: {e}")
            return {}

    def _fetch_quote(self, ticker: str) -> dict:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="2d")
        if len(hist) >= 2:
            prev_close = float(hist["Close"].iloc[-2])
            current = float(hist["Close"].iloc[-1])
            change_pct = (current - prev_close) / prev_close * 100
        elif len(hist) == 1:
            current = float(hist["Close"].iloc[-1])
            prev_close = current
            change_pct = 0.0
        else:
            return {}

        return {
            "ticker": ticker,
            "price": round(current, 4),
            "prev_close": round(prev_close, 4),
            "change_pct": round(change_pct, 4),
            "volume": int(hist["Volume"].iloc[-1]) if not hist.empty else 0,
        }
