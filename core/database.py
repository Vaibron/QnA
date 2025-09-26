from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import config
import logging

logger = logging.getLogger(__name__)

# Определение декларативной базы
logger.debug("Создание декларативной базы SQLAlchemy")
Base = declarative_base()

# Создание асинхронного движка
logger.info(f"Инициализация асинхронного движка базы данных с URL: {config.DATABASE_URL}")
engine = create_async_engine(config.DATABASE_URL, echo=False)
logger.debug("Асинхронный движок базы данных успешно создан")

# Настройка фабрики сессий
logger.debug("Настройка фабрики сессий SQLAlchemy")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
logger.info("Фабрика асинхронных сессий успешно настроена")
