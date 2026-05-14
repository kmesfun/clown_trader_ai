import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Boolean, Enum as SAEnum, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utcnow
import enum


class TaxTerm(str, enum.Enum):
    short = "short"
    long = "long"


class TaxLot(Base, TimestampMixin):
    __tablename__ = "tax_lots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trades.id"), unique=True)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("players.id"))
    ticker: Mapped[str] = mapped_column(String(20))
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    adjusted_basis: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    proceeds: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    gain_loss: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    disposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    holding_period_days: Mapped[int] = mapped_column(Integer)
    term: Mapped[TaxTerm] = mapped_column(SAEnum(TaxTerm))
    wash_sale_adjusted: Mapped[bool] = mapped_column(Boolean, default=False)
    disallowed_loss: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))

    trade: Mapped["Trade"] = relationship("Trade", back_populates="tax_lot")


class TaxReport(Base, TimestampMixin):
    __tablename__ = "tax_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("players.id"))
    year: Mapped[int] = mapped_column(Integer)
    total_short_term_gains: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    total_long_term_gains: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    wash_sale_adjustments: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    total_tax_owed: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    after_tax_portfolio_value: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
