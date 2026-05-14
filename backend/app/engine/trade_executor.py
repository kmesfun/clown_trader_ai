import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine import portfolio_manager as pm
from app.data.market_data import MarketDataClient
from app.models import TradeDirection, Trade


market_client = MarketDataClient()


async def fill_order(
    player_id: uuid.UUID,
    ticker: str,
    direction: TradeDirection,
    quantity: Decimal,
    source: str,
    db: AsyncSession,
    notes: str = "",
) -> Trade:
    price = await market_client.get_price(ticker)
    if price is None:
        raise ValueError(f"Could not fetch price for {ticker}")

    price = Decimal(str(price))

    if direction == TradeDirection.buy:
        return await pm.execute_buy(player_id, ticker, quantity, price, source, db, notes=notes)
    elif direction == TradeDirection.sell:
        return await pm.execute_sell(player_id, ticker, quantity, price, source, db, notes=notes)
    elif direction == TradeDirection.short:
        return await pm.execute_short(player_id, ticker, quantity, price, source, db, notes=notes)
    elif direction == TradeDirection.cover:
        return await pm.execute_cover(player_id, ticker, quantity, price, source, db, notes=notes)
    else:
        raise ValueError(f"Unsupported direction: {direction}")


async def fill_order_at_price(
    player_id: uuid.UUID,
    ticker: str,
    direction: TradeDirection,
    quantity: Decimal,
    price: Decimal,
    source: str,
    db: AsyncSession,
    notes: str = "",
) -> Trade:
    if direction == TradeDirection.buy:
        return await pm.execute_buy(player_id, ticker, quantity, price, source, db, notes=notes)
    elif direction == TradeDirection.sell:
        return await pm.execute_sell(player_id, ticker, quantity, price, source, db, notes=notes)
    elif direction == TradeDirection.short:
        return await pm.execute_short(player_id, ticker, quantity, price, source, db, notes=notes)
    elif direction == TradeDirection.cover:
        return await pm.execute_cover(player_id, ticker, quantity, price, source, db, notes=notes)
    else:
        raise ValueError(f"Unsupported direction: {direction}")
