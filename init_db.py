import asyncio
from nex.db.conn import engine
from nex.db.mod.base import Base

from nex.db.mod.task import Task
from nex.db.mod.secret import Secret

try:
    from nex.db.mod.note import Note
except ImportError:
    pass

async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_tables())
