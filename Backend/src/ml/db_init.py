# Backend/src/ml/db_init.py
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

async def initialize_database(engine: AsyncEngine):
    """Create tables if they don’t exist."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)