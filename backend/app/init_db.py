import asyncio
from app.database import engine
from app.models import Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[InitDB] Tables created")


async def run():
    await create_tables()
    from app.seed import run as seed
    await seed()


if __name__ == "__main__":
    asyncio.run(run())
