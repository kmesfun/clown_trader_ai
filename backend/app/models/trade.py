import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Boolean, Enum as SAEnum, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utcnow
import enum


class TradeDirection(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    short = "short"
    cover = "cover"
    buy_to_open = "buy_to_open"
    sell_to_open = "sell_to_open"
    buy_to_close = "buy_to_close"
    sell_to_close = "sell_to_close"


class Trade(Base, TimestampMixin):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("players.id"))
    ticker: Mapped[str] = mapped_column(String(20))
    direction: Mapped[TradeDirection] = mapped_column(SAEnum(TradeDirection))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    total_value: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    fees: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    slippage: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    realized_pnl: Mapped[Decimal | None] = mapped_column(Numeric(20, 6), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    wash_sale_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    disallowed_loss_amount: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    source: Mapped[str] = mapped_column(String(100), default="manual")
    notes: Mapped[str] = mapped_column(Text, default="")

    player: Mapped["Player"] = relationship("Player", back_populates="trades")
    tax_lot: Mapped["TaxLot | None"] = relationship("TaxLot", back_populates="trade", uselist=False)
