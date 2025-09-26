from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from apps.auth.crud import get_user_by_email
from apps.auth.routes import verify_password
from core.config import config
from core.dependencies import get_db_session
import logging

logger = logging.getLogger(__name__)

class AdminAuth(AuthenticationBackend):
    def __init__(self):
        super().__init__(secret_key=config.SECRET_KEY)
        logger.debug("Инициализация аутентификации администратора")

    async def login(self, request: Request) -> bool:
        logger.info("Начало процесса входа в админ-панель")
        form_data = await request.form()
        email = form_data.get("username")
        password = form_data.get("password")
        logger.debug(f"Попытка входа с email: {email}")
        session = await get_db_session()
        async with session as db_session:
            user = await get_user_by_email(db_session, email)
            if user:
                logger.debug(f"Пользователь найден: id={user.id}, is_superuser={user.is_superuser}")
                if verify_password(password, user.hashed_password) and user.is_superuser:
                    request.session["authenticated"] = True
                    request.session["user_id"] = user.id
                    logger.info(f"Успешный вход: user_id={user.id}, email={email}")
                    return True
                else:
                    logger.warning(f"Неверный пароль или недостаточно прав для user_id={user.id}")
            else:
                logger.warning(f"Пользователь с email={email} не найден")
        return False

    async def logout(self, request: Request) -> bool:
        logger.info(f"Выход из админ-панели: user_id={request.session.get('user_id')}")
        request.session.clear()
        logger.debug("Сессия очищена")
        return True

    async def authenticate(self, request: Request) -> bool:
        authenticated = request.session.get("authenticated", False)
        logger.debug(f"Проверка аутентификации: authenticated={authenticated}, user_id={request.session.get('user_id')}")
        return authenticated
