import uuid
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CramerPick, Player, PickDirection, TradeDirection
from app.engine.trade_executor import fill_order

router = APIRouter(prefix="/cramer-picks", tags=["cramer"])


class CramerPickCreate(BaseModel):
    parsed_ticker: str
    direction: PickDirection
    raw_text: str = ""
    source_url: str = ""
    confidence: float = 1.0
    aired_at: datetime | None = None


@router.get("")
async def list_cramer_picks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CramerPick).order_by(CramerPick.aired_at.desc()).limit(200))
    picks = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "parsed_ticker": p.parsed_ticker,
            "direction": p.direction,
            "raw_text": p.raw_text,
            "source_url": p.source_url,
            "confidence": p.confidence,
            "aired_at": p.aired_at.isoformat(),
            "ingested_at": p.ingested_at.isoformat(),
            "executed": p.executed,
            "trade_id": str(p.trade_id) if p.trade_id else None,
        }
        for p in picks
    ]


@router.post("")
async def create_cramer_pick(body: CramerPickCreate, db: AsyncSession = Depends(get_db)):
    pick = CramerPick(
        parsed_ticker=body.parsed_ticker.upper(),
        direction=body.direction,
        raw_text=body.raw_text,
        source_url=body.source_url,
        confidence=body.confidence,
        aired_at=body.aired_at or datetime.now(timezone.utc),
    )
    db.add(pick)
    await db.commit()
    await db.refresh(pick)
    return {"id": str(pick.id), "ticker": pick.parsed_ticker, "direction": pick.direction}


@router.post("/{pick_id}/execute")
async def execute_cramer_pick(pick_id: str, db: AsyncSession = Depends(get_db)):
    pid = uuid.UUID(pick_id)
    result = await db.execute(select(CramerPick).where(CramerPick.id == pid))
    pick = result.scalar_one_or_none()
    if not pick:
        raise HTTPException(status_code=404, detail="Pick not found")
    if pick.executed:
        raise HTTPException(status_code=400, detail="Pick already executed")

    clown_result = await db.execute(select(Player).where(Player.slug == "the-clown"))
    clown = clown_result.scalar_one_or_none()
    if not clown:
        raise HTTPException(status_code=404, detail="The Clown player not found")

    direction = TradeDirection.buy if pick.direction == PickDirection.buy else TradeDirection.sell
    quantity = Decimal("50")

    try:
        trade = await fill_order(
            player_id=clown.id,
            ticker=pick.parsed_ticker,
            direction=direction,
            quantity=quantity,
            source="cramer_pick",
            db=db,
            notes=f"Cramer pick: {pick.raw_text[:200]}",
        )
        pick.executed = True
        pick.trade_id = trade.id
        pick.player_id = clown.id
        await db.commit()
        return {"trade_id": str(trade.id), "ticker": pick.parsed_ticker, "direction": direction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
