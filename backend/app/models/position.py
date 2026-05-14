import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Boolean, Enum as SAEnum, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utcnow
import enum


class PositionType(str, enum.Enum):
    equity = "equity"
    option = "option"


class Position(Base, TimestampMixin):
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("players.id"))
    ticker: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    avg_cost_basis: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    current_price: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    unrealized_pnl_pct: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("0"))
    market_value: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    type: Mapped[PositionType] = mapped_column(SAEnum(PositionType), default=PositionType.equity)
    is_short: Mapped[bool] = mapped_column(Boolean, default=False)
    option_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    stop_loss_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 6), nullable=True)
    leverage_factor: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1"))

    player: Mapped["Player"] = relationship("Player", back_populates="positions")
