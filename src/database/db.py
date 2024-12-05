import contextlib
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.services.logger import setup_logger


logger = setup_logger(__name__)


class DatabaseSessionManager:
    """
    Manages database sessions using SQLAlchemy's async engine and sessionmaker.
    """

    def __init__(self, url: str):
        # Initializes the session manager with the database URL
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autocommit=False, autoflush=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides an async context manager for database sessions. Rolls back on errors.
        """
        if self._session_maker is None:
            raise RuntimeError("Session maker is not initialized")
        async with self._session_maker() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                logger.error(f"Session error: {err}")
                raise


sessionmanager = DatabaseSessionManager(settings.DATABASE_URL)


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous session generator.
    """

    async with sessionmanager.session() as session:
        yield session
