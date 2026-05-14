import uuid
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
import enum


class PlayerType(str, enum.Enum):
    clown = "clown"
    bot = "bot"


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    type: Mapped[PlayerType] = mapped_column(SAEnum(PlayerType), default=PlayerType.bot)
    strategy_description: Mapped[str] = mapped_column(String(500), default="")
    avatar_emoji: Mapped[str] = mapped_column(String(10), default="🤖")
    avatar_url: Mapped[str] = mapped_column(String(500), default="")

    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="player", uselist=False)
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="player")
    positions: Mapped[list["Position"]] = relationship("Position", back_populates="player")
    cramer_picks: Mapped[list["CramerPick"]] = relationship("CramerPick", back_populates="player")
