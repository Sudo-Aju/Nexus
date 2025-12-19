from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "nexus.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DB_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session