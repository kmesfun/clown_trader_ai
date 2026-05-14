from fastapi import APIRouter
from app.data.market_data import MarketDataClient
from app.engine.market_hours import is_market_open, next_market_open, now_et

router = APIRouter(prefix="/market", tags=["market"])
client = MarketDataClient()


@router.get("/status")
async def market_status():
    now = now_et()
    open_ = is_market_open(now)
    return {
        "is_open": open_,
        "next_open": next_market_open(now).isoformat() if not open_ else None,
        "current_time_et": now.strftime("%Y-%m-%d %H:%M:%S ET"),
    }


@router.get("/price/{ticker}")
async def get_price(ticker: str):
    quote = await client.get_quote(ticker.upper())
    if not quote:
        return {"error": f"Could not fetch price for {ticker}"}
    return quote


@router.get("/history/{ticker}")
async def get_history(ticker: str, days: int = 30):
    ohlcv = await client.get_ohlcv(ticker.upper(), days=days)
    return {"ticker": ticker.upper(), "data": ohlcv}
