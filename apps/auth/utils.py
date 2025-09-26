import logging
from jose import jwt
from datetime import datetime, timedelta, UTC
import bcrypt
from core.config import config

logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    logger.debug("Проверка пароля для входа")
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)):
    """Создает access-токен."""
    logger.debug("Создание access-токена")
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    token = jwt.encode(to_encode, config.SECRET_KEY, config.ALGORITHM)
    logger.debug("Access-токен успешно создан")
    return token

def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=30)):
    """Создает refresh-токен."""
    logger.debug("Создание refresh-токена")
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    token = jwt.encode(to_encode, config.SECRET_KEY, config.ALGORITHM)
    logger.debug("Refresh-токен успешно создан")
    return token