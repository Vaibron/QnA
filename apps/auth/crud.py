import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from apps.auth.models import User
from apps.auth.schemas import UserCreate, UserUpdate, PasswordChange
import bcrypt
from jose import jwt, JWTError
from core.config import config
from datetime import timedelta

logger = logging.getLogger(__name__)

async def get_user_by_email(db: AsyncSession, email: str):
    email = email.lower()
    logger.debug(f"Поиск пользователя по email: {email}")
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    logger.debug(f"Пользователь найден: {user.email if user else 'не найден'}")
    return user

async def create_verification_token(email: str) -> str:
    """Генерирует токен подтверждения email."""
    logger.debug(f"Создание токена подтверждения для email: {email}")
    to_encode = {"sub": email, "type": "verify"}
    expire = timedelta(hours=24)
    token = jwt.encode(to_encode, config.SECRET_KEY, config.ALGORITHM)
    logger.debug("Токен подтверждения успешно создан")
    return token

async def create_user(db: AsyncSession, user: UserCreate):
    logger.debug(f"Создание пользователя: {user.email}")
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db_user = User(
        username=user.username,
        email=user.email.lower(),
        hashed_password=hashed_password,
        birth_date=user.birth_date,
        gender=user.gender.value if user.gender else None,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"Пользователь успешно создан: {db_user.email}")

    verification_token = await create_verification_token(db_user.email)
    logger.debug(f"Токен подтверждения создан для пользователя: {db_user.email}")
    return db_user, verification_token

async def verify_user_email(db: AsyncSession, token: str):
    """Подтверждает email по токену."""
    logger.debug("Проверка токена подтверждения email")
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "verify":
            logger.warning("Недействительный токен или неверный тип токена")
            return None
        user = await get_user_by_email(db, email)
        if user and not user.is_verified:
            user.is_verified = True
            await db.commit()
            await db.refresh(user)
            logger.info(f"Email успешно подтверждён для пользователя: {user.email}")
            return user
        logger.warning(f"Пользователь не найден или email уже подтверждён: {email}")
        return None
    except JWTError as e:
        logger.error(f"Ошибка при проверке токена: {str(e)}")
        return None

async def update_user(db: AsyncSession, user: User, user_update: UserUpdate):
    logger.debug(f"Обновление профиля пользователя: {user.email}")
    if user_update.email is not None and user_update.email != user.email:
        if await get_user_by_email(db, user_update.email):
            logger.warning(f"Попытка обновления на занятый email: {user_update.email}")
            raise ValueError("Этот email уже занят")
        user.email = user_update.email.lower()
        user.is_verified = False
        logger.debug(f"Email изменён на: {user.email}, статус верификации сброшен")
    if user_update.gender is not None:
        user.gender = user_update.gender.value
        logger.debug(f"Пол изменён на: {user.gender}")
    await db.commit()
    await db.refresh(user)
    logger.info(f"Профиль пользователя успешно обновлён: {user.email}")
    return user

async def change_password(db: AsyncSession, user: User, password_change: PasswordChange):
    logger.debug(f"Смена пароля для пользователя: {user.email}")
    if not bcrypt.checkpw(password_change.current_password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        logger.warning("Неверный текущий пароль")
        raise ValueError("Текущий пароль неверный")
    user.hashed_password = bcrypt.hashpw(password_change.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    await db.commit()
    await db.refresh(user)
    logger.info(f"Пароль успешно изменён для пользователя: {user.email}")
    return user
