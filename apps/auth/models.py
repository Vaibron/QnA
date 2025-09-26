from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'comment': 'Users'}

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    birth_date = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    answers = relationship("Answer", back_populates="user", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="author", cascade="all, delete-orphan")
