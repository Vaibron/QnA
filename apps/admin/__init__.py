from fastapi import FastAPI
from sqladmin import Admin
from apps.admin.auth import AdminAuth
from apps.admin.views.users import UserAdmin
from apps.admin.views.qna import QuestionAdmin, AnswerAdmin
from core.database import engine
import logging
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


def init_admin(app: FastAPI):
    logger.info("Начало инициализации панели администратора")

    logger.debug("Создание фабрики асинхронных сессий")
    AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    app.state.db_session_maker = AsyncSessionLocal
    logger.debug("Фабрика асинхронных сессий успешно создана")
    admin = Admin(
        app,
        engine,
        title="Админ-панель QnA",
        authentication_backend=AdminAuth()
    )
    logger.info("SQLAdmin успешно инициализирован")

    logger.debug("Регистрация представлений админ-панели")
    admin.add_view(UserAdmin)
    admin.add_view(QuestionAdmin)
    admin.add_view(AnswerAdmin)
    logger.info("Панель администратора полностью инициализирована")
