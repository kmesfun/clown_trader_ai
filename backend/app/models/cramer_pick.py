import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, Boolean, Enum as SAEnum, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utcnow
import enum


class PickDirection(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    hold = "hold"


class CramerPick(Base, TimestampMixin):
    __tablename__ = "cramer_picks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(500), default="")
    parsed_ticker: Mapped[str] = mapped_column(String(20))
    direction: Mapped[PickDirection] = mapped_column(SAEnum(PickDirection))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    aired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    executed: Mapped[bool] = mapped_column(Boolean, default=False)
    trade_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("trades.id"), nullable=True)
    player_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)

    player: Mapped["Player | None"] = relationship("Player", back_populates="cramer_picks")
