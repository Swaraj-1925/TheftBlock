from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from Backend.src.config.constant import DATABASE_URL
print(DATABASE_URL)
#Create database 1st
# psql -U postgres -h localhost
# CREATE DATABASE "TheftBlock";
async_engine = create_async_engine(url=DATABASE_URL)

async def get_session() -> AsyncSession:
    """Dependency to provide the session object"""
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

