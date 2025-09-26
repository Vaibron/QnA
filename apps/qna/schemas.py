from datetime import datetime
from pydantic import BaseModel
from typing import List

class QuestionBase(BaseModel):
    text: str

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    author_id: str  # Изменено на str
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionDetailResponse(QuestionBase):
    id: int
    author_id: str  # Изменено на str
    created_at: datetime
    answers: List["AnswerResponse"] = []

    class Config:
        from_attributes = True

class AnswerBase(BaseModel):
    text: str

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: int
    user_id: str
    question_id: int
    created_at: datetime

    class Config:
        from_attributes = True

QuestionDetailResponse.update_forward_refs()
