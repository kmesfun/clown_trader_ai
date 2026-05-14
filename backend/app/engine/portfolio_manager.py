import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Player, Portfolio, Position, Trade, TaxLot, TradeDirection, PositionType, TaxTerm
)
from app.engine.wash_sale import check_wash_sale, apply_wash_sale_to_trade
from app.engine.settlement import queue_settlement
from app.config import settings


class InsufficientFundsError(Exception):
    pass


class PositionNotFoundError(Exception):
    pass


class PDTViolationError(Exception):
    pass


def quantize(value: Decimal, places: int = 6) -> Decimal:
    fmt = Decimal(10) ** -places
    return value.quantize(fmt, rounding=ROUND_HALF_UP)


async def get_portfolio(player_id: uuid.UUID, db: AsyncSession) -> Portfolio:
    result = await db.execute(select(Portfolio).where(Portfolio.player_id == player_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise ValueError(f"Portfolio not found for player {player_id}")
    return portfolio


async def get_position(player_id: uuid.UUID, ticker: str, db: AsyncSession) -> Optional[Position]:
    result = await db.execute(
        select(Position).where(and_(Position.player_id == player_id, Position.ticker == ticker))
    )
    return result.scalar_one_or_none()


async def execute_buy(
    player_id: uuid.UUID,
    ticker: str,
    quantity: Decimal,
    price: Decimal,
    source: str,
    db: AsyncSession,
    slippage_pct: float = settings.slippage_pct,
    notes: str = "",
) -> Trade:
    slippage = quantize(price * Decimal(str(slippage_pct)))
    fill_price = quantize(price + slippage)
    total_value = quantize(fill_price * quantity)

    portfolio = await get_portfolio(player_id, db)

    if portfolio.settled_cash < total_value:
        raise InsufficientFundsError(
            f"Insufficient settled cash: need ${total_value}, have ${portfolio.settled_cash}"
        )

    portfolio.settled_cash -= total_value
    portfolio.cash_balance -= total_value

    position = await get_position(player_id, ticker, db)
    if position:
        new_qty = position.quantity + quantity
        new_cost = quantize((position.avg_cost_basis * position.quantity + fill_price * quantity) / new_qty)
        position.quantity = new_qty
        position.avg_cost_basis = new_cost
        position.current_price = fill_price
        position.market_value = quantize(new_qty * fill_price)
    else:
        position = Position(
            player_id=player_id,
            ticker=ticker,
            quantity=quantity,
            avg_cost_basis=fill_price,
            current_price=fill_price,
            market_value=total_value,
            type=PositionType.equity,
            is_short=False,
        )
        db.add(position)

    trade = Trade(
        player_id=player_id,
        ticker=ticker,
        direction=TradeDirection.buy,
        quantity=quantity,
        price=fill_price,
        total_value=total_value,
        slippage=quantize(slippage * quantity),
        source=source,
        notes=notes,
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return trade


async def execute_sell(
    player_id: uuid.UUID,
    ticker: str,
    quantity: Decimal,
    price: Decimal,
    source: str,
    db: AsyncSession,
    slippage_pct: float = settings.slippage_pct,
    notes: str = "",
) -> Trade:
    position = await get_position(player_id, ticker, db)
    if not position or position.quantity < quantity:
        raise PositionNotFoundError(f"Cannot sell {quantity} of {ticker}: position insufficient")

    slippage = quantize(price * Decimal(str(slippage_pct)))
    fill_price = quantize(price - slippage)
    total_value = quantize(fill_price * quantity)
    cost = quantize(position.avg_cost_basis * quantity)
    realized_pnl = quantize(total_value - cost)

    acquired_at = position.opened_at
    disposed_at = datetime.now(timezone.utc)
    holding_days = (disposed_at - acquired_at).days
    term = TaxTerm.long if holding_days >= 365 else TaxTerm.short

    portfolio = await get_portfolio(player_id, db)

    position.quantity -= quantity
    if position.quantity <= Decimal("0.000001"):
        await db.delete(position)
    else:
        position.market_value = quantize(position.quantity * fill_price)

    trade = Trade(
        player_id=player_id,
        ticker=ticker,
        direction=TradeDirection.sell,
        quantity=quantity,
        price=fill_price,
        total_value=total_value,
        slippage=quantize(slippage * quantity),
        realized_pnl=realized_pnl,
        source=source,
        notes=notes,
    )
    db.add(trade)
    await db.flush()

    disallowed = await check_wash_sale(player_id, ticker, realized_pnl, disposed_at, db)
    if disallowed > 0:
        await apply_wash_sale_to_trade(trade.id, disallowed, db)
        realized_pnl_adjusted = realized_pnl + disallowed
    else:
        realized_pnl_adjusted = realized_pnl

    tax_lot = TaxLot(
        trade_id=trade.id,
        player_id=player_id,
        ticker=ticker,
        cost_basis=cost,
        adjusted_basis=cost + disallowed,
        proceeds=total_value,
        gain_loss=realized_pnl_adjusted,
        acquired_at=acquired_at,
        disposed_at=disposed_at,
        holding_period_days=holding_days,
        term=term,
        wash_sale_adjusted=disallowed > 0,
        disallowed_loss=disallowed,
    )
    db.add(tax_lot)

    portfolio.realized_pnl += realized_pnl_adjusted
    await queue_settlement(trade, portfolio)

    await db.commit()
    await db.refresh(trade)
    return trade


async def execute_short(
    player_id: uuid.UUID,
    ticker: str,
    quantity: Decimal,
    price: Decimal,
    source: str,
    db: AsyncSession,
    notes: str = "",
) -> Trade:
    slippage = quantize(price * Decimal(str(settings.slippage_pct)))
    fill_price = quantize(price - slippage)
    total_value = quantize(fill_price * quantity)

    portfolio = await get_portfolio(player_id, db)

    position = await get_position(player_id, ticker, db)
    if position and not position.is_short:
        raise ValueError(f"Already hold long position in {ticker}, cannot short")

    if not position:
        position = Position(
            player_id=player_id,
            ticker=ticker,
            quantity=quantity,
            avg_cost_basis=fill_price,
            current_price=fill_price,
            market_value=total_value,
            type=PositionType.equity,
            is_short=True,
        )
        db.add(position)
    else:
        new_qty = position.quantity + quantity
        position.quantity = new_qty
        position.market_value = quantize(new_qty * fill_price)

    portfolio.cash_balance += total_value

    trade = Trade(
        player_id=player_id,
        ticker=ticker,
        direction=TradeDirection.short,
        quantity=quantity,
        price=fill_price,
        total_value=total_value,
        slippage=quantize(slippage * quantity),
        source=source,
        notes=notes,
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return trade


async def execute_cover(
    player_id: uuid.UUID,
    ticker: str,
    quantity: Decimal,
    price: Decimal,
    source: str,
    db: AsyncSession,
    notes: str = "",
) -> Trade:
    position = await get_position(player_id, ticker, db)
    if not position or not position.is_short:
        raise PositionNotFoundError(f"No short position in {ticker} to cover")

    slippage = quantize(price * Decimal(str(settings.slippage_pct)))
    fill_price = quantize(price + slippage)
    total_value = quantize(fill_price * quantity)
    short_proceeds = quantize(position.avg_cost_basis * quantity)
    realized_pnl = quantize(short_proceeds - total_value)

    portfolio = await get_portfolio(player_id, db)
    portfolio.cash_balance -= total_value
    portfolio.realized_pnl += realized_pnl

    position.quantity -= quantity
    if position.quantity <= Decimal("0.000001"):
        await db.delete(position)
    else:
        position.market_value = quantize(position.quantity * fill_price)

    trade = Trade(
        player_id=player_id,
        ticker=ticker,
        direction=TradeDirection.cover,
        quantity=quantity,
        price=fill_price,
        total_value=total_value,
        slippage=quantize(slippage * quantity),
        realized_pnl=realized_pnl,
        source=source,
        notes=notes,
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return trade


async def mark_to_market(player_id: uuid.UUID, prices: dict[str, Decimal], db: AsyncSession) -> Portfolio:
    result = await db.execute(select(Position).where(Position.player_id == player_id))
    positions = result.scalars().all()

    total_market_value = Decimal("0")
    total_unrealized = Decimal("0")

    for pos in positions:
        current_price = prices.get(pos.ticker)
        if not current_price:
            continue

        pos.current_price = current_price
        if pos.is_short:
            pnl = quantize((pos.avg_cost_basis - current_price) * pos.quantity)
        else:
            pnl = quantize((current_price - pos.avg_cost_basis) * pos.quantity)

        pos.unrealized_pnl = pnl
        if pos.avg_cost_basis > 0:
            if pos.is_short:
                pos.unrealized_pnl_pct = quantize(
                    (pos.avg_cost_basis - current_price) / pos.avg_cost_basis * 100
                )
            else:
                pos.unrealized_pnl_pct = quantize(
                    (current_price - pos.avg_cost_basis) / pos.avg_cost_basis * 100
                )

        mv = quantize(current_price * pos.quantity * (pos.leverage_factor or Decimal("1")))
        pos.market_value = mv
        total_market_value += mv
        total_unrealized += pnl

    portfolio = await get_portfolio(player_id, db)
    portfolio.unrealized_pnl = quantize(total_unrealized)
    portfolio.total_equity = quantize(portfolio.cash_balance + total_market_value)
    if settings.starting_cash > 0:
        portfolio.total_return_pct = quantize(
            (portfolio.total_equity - Decimal(str(settings.starting_cash))) / Decimal(str(settings.starting_cash)) * 100
        )

    await db.commit()
    return portfolio


async def get_portfolio_summary(player_id: uuid.UUID, db: AsyncSession) -> dict:
    portfolio = await get_portfolio(player_id, db)
    result = await db.execute(select(Position).where(Position.player_id == player_id))
    positions = result.scalars().all()
    return {
        "cash_balance": str(portfolio.cash_balance),
        "settled_cash": str(portfolio.settled_cash),
        "total_equity": str(portfolio.total_equity),
        "unrealized_pnl": str(portfolio.unrealized_pnl),
        "realized_pnl": str(portfolio.realized_pnl),
        "total_return_pct": str(portfolio.total_return_pct),
        "position_count": len(positions),
        "pdt_locked": portfolio.pdt_locked_until is not None and portfolio.pdt_locked_until > __import__("datetime").date.today(),
    }
