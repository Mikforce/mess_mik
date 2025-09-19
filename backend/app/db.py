# db.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    pass


def create_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)


engine: AsyncEngine = create_engine()
async_session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session







