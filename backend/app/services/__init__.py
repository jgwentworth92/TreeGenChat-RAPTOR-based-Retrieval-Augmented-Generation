from app.config import get_config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging



Base = declarative_base()


class Database:
    """
    Async Database class to manage database connections and sessions.
    """

    def __init__(self):
        """
        Initialize the database class.
        """
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        """
        Get the attribute from the session.
        """
        return getattr(self._session, name)

    def connect(self):
        """
        Connect to the database.
        """
        logging.info("Connecting to the database...")
        self._engine = create_async_engine(
            get_config().DATABASE_URL,
            future=True,
            echo=get_config().DEBUG
        )

        self._session = async_sessionmaker(
            bind=self._engine, autocommit=False, class_=AsyncSession
        )

    async def disconnect(self):
        """
        Dispose the database connection.
        """
        await self._engine.dispose()

    async def get_db(self):
        """
        Get the database session.
        """
        async with self._session() as session:
            yield session


db = Database()