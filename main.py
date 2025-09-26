import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps.auth.routes import router as auth_router
from apps.qna.routes import router as qna_router, answers_router
from apps.admin import init_admin
from core.config import config
from core.database import Base, engine
from starlette.middleware.sessions import SessionMiddleware

# Настройка глобального логирования
logging.basicConfig(level=logging.DEBUG)

# Управление жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# Инициализация FastAPI приложения
app = FastAPI(title="My Awesome Project", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

# Подключение маршрутов существующих приложений
app.include_router(auth_router)
app.include_router(qna_router)  # /questions
app.include_router(answers_router)  # /answers

# Инициализация админки
init_admin(app)

# Корневой эндпоинт
@app.get("/")
async def read_root():
    return {"message": "Welcome to the API QnA"}
