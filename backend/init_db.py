from alembic import command
from alembic.config import Config
from app.database import Base
from app.models import *
import asyncio
from app.database import async_engine


def init_db():
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(create_tables())
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
