import uuid
import html
import re
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

CNBC_STOCK_PICKS_URL = "https://www.cnbc.com/stock-picks/"
YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
BUY_LANGUAGE = (
    " buy ",
    " buying ",
    " is a buy",
    " says buy",
    " says to buy",
    " like ",
    " likes ",
    " bullish",
    " recommends",
    " top pick",
)
NON_TICKERS = {
    "CNBC",
    "CEO",
    "ETF",
    "ETFS",
    "IPO",
    "IRS",
    "NYSE",
    "NASDAQ",
    "SEC",
    "USA",
}


class CramerPickCreate(BaseModel):
    parsed_ticker: str
    direction: PickDirection = PickDirection.buy
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
    if body.direction != PickDirection.buy:
        raise HTTPException(status_code=400, detail="Cramer picks track buy calls only")

    pick = CramerPick(
        parsed_ticker=body.parsed_ticker.upper(),
        direction=PickDirection.buy,
        raw_text=body.raw_text,
        source_url=body.source_url,
        confidence=body.confidence,
        aired_at=body.aired_at or datetime.now(timezone.utc),
    )
    db.add(pick)
    await db.commit()
    await db.refresh(pick)
    return {"id": str(pick.id), "ticker": pick.parsed_ticker, "direction": pick.direction}


@router.post("/refresh-buy-calls")
async def refresh_cramer_buy_calls(db: AsyncSession = Depends(get_db)):
    try:
        candidates = await fetch_cnbc_buy_call_candidates()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch Cramer buy calls: {e}")

    created = []
    skipped = []

    for candidate in candidates:
        existing = await db.execute(
            select(CramerPick).where(
                CramerPick.parsed_ticker == candidate["ticker"],
                CramerPick.direction == PickDirection.buy,
            )
        )
        if existing.scalar_one_or_none():
            skipped.append(candidate)
            continue

        pick = CramerPick(
            parsed_ticker=candidate["ticker"],
            direction=PickDirection.buy,
            raw_text=candidate["headline"],
            source_url=candidate["url"],
            confidence=candidate["confidence"],
            aired_at=datetime.now(timezone.utc),
        )
        db.add(pick)
        created.append(candidate)

    await db.commit()
    return {
        "created": len(created),
        "skipped": len(skipped),
        "candidates": len(candidates),
        "picks": created,
        "source": CNBC_STOCK_PICKS_URL,
    }


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


async def fetch_cnbc_buy_call_candidates() -> list[dict]:
    import aiohttp

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ClownArena/0.1; paper-trading research)",
        "Accept": "text/html,application/xhtml+xml",
    }
    yahoo_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "application/json",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(CNBC_STOCK_PICKS_URL, timeout=15) as response:
            response.raise_for_status()
            page = await response.text()

    links = extract_article_links(page)
    candidates = []
    seen = set()
    ticker_cache = {}
    async with aiohttp.ClientSession(headers=yahoo_headers) as session:
        for headline, url in links:
            if not is_cramer_buy_call(headline):
                continue

            ticker = extract_ticker(headline)
            confidence = 0.72
            company = None
            if not ticker:
                company = extract_buy_company(headline)
                if not company:
                    continue
                ticker = await resolve_company_ticker(company, session, ticker_cache)
                confidence = 0.62
            if not ticker:
                continue

            key = (ticker, company or headline)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                {
                    "ticker": ticker,
                    "headline": headline,
                    "url": url,
                    "confidence": confidence,
                }
            )

    return candidates[:20]


def extract_article_links(page: str) -> list[tuple[str, str]]:
    links = []
    pattern = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
    for url, label in pattern.findall(page):
        text = re.sub(r"<[^>]+>", " ", label)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        if not text:
            continue
        if url.startswith("/"):
            url = f"https://www.cnbc.com{url}"
        if "cnbc.com" not in url:
            continue
        links.append((text, url))
    return links


def is_cramer_buy_call(headline: str) -> bool:
    normalized = f" {headline.lower()} "
    if "cramer" not in normalized and "lightning round:" not in normalized:
        return False
    return any(term in normalized for term in BUY_LANGUAGE)


def extract_ticker(headline: str) -> str | None:
    ticker_patterns = [
        r"\(([A-Z]{1,5})\)",
        r"\$([A-Z]{1,5})\b",
        r"\bNYSE:\s*([A-Z]{1,5})\b",
        r"\bNASDAQ:\s*([A-Z]{1,5})\b",
    ]
    for pattern in ticker_patterns:
        match = re.search(pattern, headline)
        if match and match.group(1) not in NON_TICKERS:
            return match.group(1)

    return None


def extract_buy_company(headline: str) -> str | None:
    patterns = [
        r"(?:lightning round:\s*)?buy\s+(.+?)(?:,|\s+says|\s+-|$)",
        r"(?:lightning round:\s*)?(.+?)\s+is a buy(?:,|\s+says|$)",
        r"cramer(?:'s)?\s+(?:likes|recommends)\s+(.+?)(?:,|\s+-|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, headline, re.IGNORECASE)
        if not match:
            continue
        company = re.sub(r"\s+", " ", match.group(1)).strip(" .:")
        if company and len(company) <= 80:
            return company
    return None


async def resolve_company_ticker(company: str, session, cache: dict[str, str | None]) -> str | None:
    key = company.lower()
    if key in cache:
        return cache[key]

    try:
        async with session.get(YAHOO_SEARCH_URL, params={"q": company, "quotesCount": 5, "newsCount": 0}, timeout=10) as response:
            response.raise_for_status()
            payload = await response.json()
    except Exception:
        cache[key] = None
        return None

    for quote in payload.get("quotes", []):
        symbol = quote.get("symbol", "")
        quote_type = quote.get("quoteType", "")
        if quote_type == "EQUITY" and re.fullmatch(r"[A-Z.]{1,6}", symbol):
            cache[key] = symbol
            return symbol

    cache[key] = None
    return None
