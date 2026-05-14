from datetime import datetime, time, timedelta, date
from zoneinfo import ZoneInfo
import holidays

ET = ZoneInfo("America/New_York")
US_HOLIDAYS = holidays.UnitedStates()

MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)


def now_et() -> datetime:
    return datetime.now(ET)


def is_business_day(d: date) -> bool:
    return d.weekday() < 5 and d not in US_HOLIDAYS


def is_market_open(dt: datetime | None = None) -> bool:
    dt = dt or now_et()
    dt_et = dt.astimezone(ET)
    if not is_business_day(dt_et.date()):
        return False
    return MARKET_OPEN <= dt_et.time() < MARKET_CLOSE


def next_market_open(dt: datetime | None = None) -> datetime:
    dt = dt or now_et()
    dt_et = dt.astimezone(ET)
    candidate = dt_et.date()
    if dt_et.time() >= MARKET_CLOSE or not is_business_day(candidate):
        candidate += timedelta(days=1)
    while not is_business_day(candidate):
        candidate += timedelta(days=1)
    return datetime.combine(candidate, MARKET_OPEN, tzinfo=ET)


def next_business_day(d: date) -> date:
    candidate = d + timedelta(days=1)
    while not is_business_day(candidate):
        candidate += timedelta(days=1)
    return candidate


def business_days_between(start: date, end: date) -> int:
    count = 0
    current = start
    while current < end:
        if is_business_day(current):
            count += 1
        current += timedelta(days=1)
    return count
