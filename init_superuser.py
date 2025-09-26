import asyncio
from pydantic import BaseModel, EmailStr, ValidationError, field_validator
import apps.auth.models
import apps.qna.models

class SuperUserInput(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_confirm: str

    @field_validator("username")
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        return v

    @field_validator("password")
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен быть минимум 8 символов")
        return v

    @field_validator("password_confirm")
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return v

async def init_superuser():
    from core.database import async_session
    from apps.auth.crud import get_user_by_email, create_user
    from apps.auth.schemas import UserCreate
    from apps.auth.models import User

    async with async_session() as db:
        while True:
            email = input("Введите email суперпользователя: ").strip()
            try:
                SuperUserInput(email=email, username="x", password="12345678", password_confirm="12345678")
            except ValidationError as e:
                print(f"Ошибка email: {e.errors()[0]['msg']}")
                continue

            if await get_user_by_email(db, email):
                print(f"Пользователь с email {email} уже существует. Введите другой email.")
                continue
            break

        while True:
            username = input("Введите имя пользователя: ").strip()
            try:
                SuperUserInput(email="a@a.com", username=username, password="12345678", password_confirm="12345678")
                break
            except ValidationError as e:
                print(f"Ошибка имени пользователя: {e.errors()[0]['msg']}")

        while True:
            password = input("Введите пароль (мин. 8 символов): ").strip()
            password_confirm = input("Подтвердите пароль: ").strip()
            try:
                SuperUserInput(email="a@a.com", username="x", password=password, password_confirm=password_confirm)
                break
            except ValidationError as e:
                for err in e.errors():
                    print(f"Ошибка {err['loc'][0]}: {err['msg']}")

        user = UserCreate(
            email=email,
            username=username,
            password=password,
            password_confirm=password_confirm
        )
        db_user, _ = await create_user(db, user)
        db_user.is_superuser = True
        db_user.is_verified = True
        await db.commit()
        await db.refresh(db_user)
        print(f"Суперпользователь {email} успешно создан!")

if __name__ == "__main__":
    asyncio.run(init_superuser())
