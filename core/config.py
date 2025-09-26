from dotenv import load_dotenv
import os

load_dotenv(".env")


class Config:
    def __init__(self):
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 10

        # SMTP settings
        self.SMTP_ENABLED = os.getenv("SMTP", "No").lower() == "yes"
        self.SMTP_HOST = os.getenv("SMTP_HOST") if self.SMTP_ENABLED else None
        self.SMTP_PORT = int(os.getenv("SMTP_PORT")) if self.SMTP_ENABLED and os.getenv("SMTP_PORT") else None
        self.SMTP_USER = os.getenv("SMTP_USER") if self.SMTP_ENABLED else None
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") if self.SMTP_ENABLED else None
        self.SMTP_FROM = os.getenv("SMTP_FROM") if self.SMTP_ENABLED else None

        self.BASE_URL = os.getenv("BASE_URL")


config = Config()

