from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session
import logging

logger = logging.getLogger(__name__)

async def get_db():
    logger.debug("Открытие новой сессии базы данных")
    async with async_session() as session:
        logger.debug("Сессия базы данных успешно предоставлена")
        yield session
        logger.debug("Закрытие сессии базы данных")

async def get_db_session() -> AsyncSession:
    logger.debug("Создание новой сессии базы данных")
    async with async_session() as session:
        logger.debug("Сессия базы данных успешно создана")
        return session
