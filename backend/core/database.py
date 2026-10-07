from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.core.settings import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session


engine = create_async_engine(settings.db.DB_URL)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session


async def ping_database() -> bool:
    try:
        async with session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.error("Database ping failed", exc_info=True)
        return False
