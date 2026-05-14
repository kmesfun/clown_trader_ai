import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Numeric, Integer, ForeignKey, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("players.id"), unique=True)

    cash_balance: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("100000"))
    settled_cash: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("100000"))
    pending_settlement: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))

    margin_used: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    margin_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    total_equity: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("100000"))
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("0"))
    total_return_pct: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("0"))

    day_trade_count: Mapped[int] = mapped_column(Integer, default=0)
    pdt_locked_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    pdt_triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    after_tax_equity: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=Decimal("100000"))

    player: Mapped["Player"] = relationship("Player", back_populates="portfolio")
