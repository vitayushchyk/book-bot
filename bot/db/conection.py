import contextlib
import logging
from typing import AsyncGenerator

from redis import Redis
from redis.asyncio import ConnectionPool as RedisConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from bot.core.config import settings

engine = create_async_engine(
    settings.db_connection_uri.unicode_string(),  # type: ignore[union-attr]
    echo=settings.echo_query,
    future=True,
)


@contextlib.asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logging.error(f"Transaction rolled back due to: {e}")
            raise e


async def init_db():

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logging.info("Database tables created successfully.")


logging.info(f"REDIS CONNECTION URI: {settings.redis_connection_uri}")
pool = RedisConnectionPool.from_url(settings.redis_connection_uri)
redis = Redis(connection_pool=pool)


async def get_redis_client() -> Redis:

    return redis


logging.info(
    f"Redis client created successfully with URL {settings.redis_connection_uri}"
)
