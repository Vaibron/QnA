import logging
from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from apps.auth.schemas import UserCreate, Token, UserUpdate, PasswordChange, RefreshToken
from apps.auth.crud import get_user_by_email, create_user, update_user, change_password, create_verification_token, \
    verify_user_email
from apps.auth.utils import verify_password, create_access_token, create_refresh_token  # Импорт утилит
from apps.auth.models import User
from core.dependencies import get_db
from core.config import config
from core.email import send_email
from jose import jwt, JWTError
from datetime import timedelta, UTC
import traceback
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Авторизация"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login",
                                     auto_error=False)  # auto_error=False делает заголовок необязательным


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Получает пользователя по JWT-токену."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        logger.warning("Токен не предоставлен")
        raise credentials_exception
    logger.debug("Проверка текущего пользователя по токену")
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("type") != "access":
            logger.warning("Недействительный тип токена")
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Токен не содержит email")
            raise credentials_exception
        logger.debug(f"Извлечён email из токена: {email}")
    except JWTError as e:
        logger.error(f"Ошибка декодирования токена: {str(e)}")
        raise credentials_exception

    user = await get_user_by_email(db, email)
    if user is None:
        logger.warning(f"Пользователь с email {email} не найден")
        raise credentials_exception
    if not user.is_verified:
        logger.warning(f"Пользователь {email} не верифицирован")
        raise HTTPException(status_code=401, detail="Email не подтверждён")
    logger.debug(f"Пользователь успешно аутентифицирован: {email}")
    return user


@router.post("/register", response_model=Token, summary="Регистрация")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрирует пользователя и отправляет письмо для подтверждения.

    Args:
        user: Данные пользователя (username, email, password).
        db: Сессия базы данных.

    Returns:
        Token: Access- и refresh-токены, тип токена, ID пользователя.

    Raises:
        HTTPException: Если email занят или ошибка сервера.
    """
    logger.debug(f"Регистрация нового пользователя: {user.email}")
    try:
        if await get_user_by_email(db, user.email):
            logger.warning(f"Попытка регистрации с занятым email: {user.email}")
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
        db_user, verification_token = await create_user(db, user)
        logger.info(f"Пользователь успешно создан: {db_user.email}")

        verification_link = f"{config.BASE_URL}/auth/verify?token={verification_token}"
        email_body = f"""
        Здравствуйте, {db_user.username}!

        Спасибо за регистрацию в QnA. Пожалуйста, подтвердите ваш email, перейдя по ссылке:
        {verification_link}

        Если вы не регистрировались, просто проигнорируйте это письмо.
        """
        logger.debug(f"Отправка письма для подтверждения email: {db_user.email}")
        await send_email(db_user.email, "Подтверждение регистрации в QnA", email_body)
        logger.info(f"Письмо с подтверждением отправлено: {db_user.email}")

        access_token = create_access_token(data={"sub": db_user.email})
        refresh_token = create_refresh_token(data={"sub": db_user.email})
        logger.debug(f"Токены созданы для пользователя: {db_user.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": db_user.id
        }
    except Exception as e:
        logger.error(f"Ошибка в register: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.get("/verify", summary="Подтверждение email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Подтверждает email по токену."""
    logger.debug("Проверка токена подтверждения email")
    user = await verify_user_email(db, token)
    if not user:
        logger.warning("Недействительный или истёкший токен подтверждения")
        raise HTTPException(status_code=400, detail="Недействительный или истёкший токен подтверждения")
    logger.info(f"Email успешно подтверждён: {user.email}")
    return {"message": "Email успешно подтверждён"}


@router.post("/login", response_model=Token, summary="Вход")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Аутентифицирует пользователя. Используйте email в поле username.

    Args:
        form_data: Данные формы (username=email, password).
        db: Сессия базы данных.

    Returns:
        Token: Access- и refresh-токены, тип токена, ID пользователя.

    Raises:
        HTTPException: Если email/пароль неверны.
    """
    logger.debug(f"Попытка входа пользователя: {form_data.username}")
    try:
        db_user = await get_user_by_email(db, form_data.username)  # username интерпретируется как email
        if not db_user or not verify_password(form_data.password, db_user.hashed_password):
            logger.warning(f"Неверный email или пароль: {form_data.username}")
            raise HTTPException(status_code=400, detail="Неверный email или пароль")
        access_token = create_access_token(data={"sub": db_user.email})
        refresh_token = create_refresh_token(data={"sub": db_user.email})
        logger.info(f"Успешный вход пользователя: {db_user.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": db_user.id
        }
    except Exception as e:
        logger.error(f"Ошибка в login: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.post("/refresh", response_model=Token, summary="Обновление токенов")
async def refresh_token(
        refresh_body: RefreshToken = Body(None),  # Токен из тела (опционально)
        token_from_header: Optional[str] = Depends(oauth2_scheme),  # Токен из заголовка (опционально)
        db: AsyncSession = Depends(get_db)
):
    """Обновляет токены по refresh-токену.

    Поддерживает передачу refresh_token в заголовке Authorization: Bearer <refresh_token> (рекомендуется для продакшена)
    или в теле запроса JSON {"refresh_token": "<refresh_token>"} (для удобства тестирования в Swagger).

    Args:
        refresh_body: Refresh-токен в теле запроса (опционально).
        token_from_header: Refresh-токен в заголовке Authorization (опционально).
        db: Сессия базы данных.

    Returns:
        Token: Новые access- и refresh-токены, тип токена, ID пользователя.

    Raises:
        HTTPException: Если refresh-токен недействителен или не передан.
    """
    token = refresh_body.refresh_token if refresh_body else token_from_header
    if not token:
        logger.warning("Refresh-токен не передан")
        raise HTTPException(status_code=400, detail="Refresh token required")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logger.debug("Попытка обновления токена")
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "refresh":
            logger.warning("Недействительный refresh-токен или неверный тип токена")
            raise credentials_exception
        logger.debug(f"Извлечён email из refresh-токена: {email}")
    except JWTError as e:
        logger.error(f"Ошибка декодирования refresh-токена: {str(e)}")
        raise credentials_exception

    user = await get_user_by_email(db, email)
    if user is None:
        logger.warning(f"Пользователь с email {email} не найден")
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    logger.info(f"Токены успешно обновлены для пользователя: {user.email}")
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user_id": user.id
    }


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление пользователя")
async def delete_user(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Удаляет учетную запись пользователя."""
    logger.debug(f"Удаление пользователя: {current_user.email}")
    try:
        await db.delete(current_user)
        await db.commit()
        logger.info(f"Пользователь успешно удалён: {current_user.email}")
        return None
    except Exception as e:
        logger.error(f"Ошибка в delete_user: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.put("/update", summary="Обновление профиля")
async def update_profile(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Обновляет профиль пользователя."""
    logger.debug(f"Обновление профиля пользователя: {current_user.email}")
    try:
        updated_user = await update_user(db, current_user, user_update)
        logger.info(f"Профиль успешно обновлён: {updated_user.email}")
        return {
            "message": "Профиль успешно обновлен",
            "username": updated_user.username,
            "email": updated_user.email,
            "gender": updated_user.gender
        }
    except ValueError as e:
        logger.warning(f"Ошибка валидации при обновлении профиля: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка в update_profile: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.put("/change-password", summary="Смена пароля")
async def change_user_password(
        password_change: PasswordChange,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Изменяет пароль пользователя."""
    logger.debug(f"Смена пароля для пользователя: {current_user.email}")
    try:
        await change_password(db, current_user, password_change)
        logger.info(f"Пароль успешно изменён: {current_user.email}")
        return {"message": "Пароль успешно изменен"}
    except ValueError as e:
        logger.warning(f"Ошибка валидации при смене пароля: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка в change_password: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
