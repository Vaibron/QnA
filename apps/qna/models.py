from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from core.database import Base

class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False, unique=True)
    author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Изменено на String
    created_at = Column(DateTime, server_default=func.now())

    author = relationship("User", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answer"
    __table_args__ = {'comment': 'Answers'}

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")
