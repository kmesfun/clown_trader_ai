import uuid
from abc import ABC, abstractmethod
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.market_data import MarketDataClient
from app.models import Trade


class BaseBot(ABC):
    def __init__(self, player_id: uuid.UUID):
        self.player_id = player_id
        self.market = MarketDataClient()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def evaluate(self, db: AsyncSession) -> list[dict]:
        """Return list of trade signals: {ticker, direction, quantity, reason}"""
        pass

    @abstractmethod
    def should_run_now(self) -> bool:
        pass

    async def run(self, db: AsyncSession) -> list[Trade]:
        if not self.should_run_now():
            return []
        signals = await self.evaluate(db)
        executed = []
        for signal in signals:
            try:
                from app.engine.trade_executor import fill_order
                from app.models import TradeDirection
                trade = await fill_order(
                    player_id=self.player_id,
                    ticker=signal["ticker"],
                    direction=TradeDirection(signal["direction"]),
                    quantity=Decimal(str(signal["quantity"])),
                    source=f"bot_{self.name.lower().replace(' ', '_')}",
                    db=db,
                    notes=signal.get("reason", ""),
                )
                executed.append(trade)
                print(f"[{self.name}] {signal['direction'].upper()} {signal['quantity']} {signal['ticker']}: {signal.get('reason', '')}")
            except Exception as e:
                print(f"[{self.name}] Trade failed {signal}: {e}")
        return executed
