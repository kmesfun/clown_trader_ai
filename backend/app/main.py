from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.api import players, trades, leaderboard, cramer, market
from app.scheduler import start_scheduler
from app.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        from app.seed import seed
        await seed(db)

    start_scheduler()
    yield


app = FastAPI(
    title="Clown Arena API",
    description="🤡 The Clown vs. The Machines — Paper Trading Battle Arena",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/api")
app.include_router(trades.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")
app.include_router(cramer.router, prefix="/api")
app.include_router(market.router, prefix="/api")


@app.get("/api")
async def root():
    return {"message": "🤡 Welcome to the Clown Arena", "status": "honking"}


@app.post("/api/engine/mark-to-market")
async def trigger_mark_to_market():
    from app.scheduler import intraday_job
    await intraday_job()
    return {"status": "mark-to-market complete"}


@app.post("/api/engine/run-bots")
async def trigger_bots():
    async with AsyncSessionLocal() as db:
        from app.bots.bot_runner import run_all_bots
        summary = await run_all_bots(db)
    return {"status": "bots run", "summary": summary}


@app.post("/api/engine/process-settlements")
async def trigger_settlements():
    async with AsyncSessionLocal() as db:
        from app.engine.settlement import process_settlements
        count = await process_settlements(db)
    return {"status": "settlements processed", "count": count}
