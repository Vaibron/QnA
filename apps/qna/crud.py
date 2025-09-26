from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from apps.qna.models import Question, Answer

async def get_all_questions(db: AsyncSession) -> List[Question]:
    result = await db.execute(select(Question))
    return result.scalars().all()

async def get_question_by_id(db: AsyncSession, question_id: int) -> Optional[Question]:
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.id == question_id)
    )
    return result.scalar_one_or_none()

async def create_question(db: AsyncSession, text: str, author_id: str) -> Question:  # Изменено на str
    question = Question(text=text, author_id=author_id)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question

async def delete_question(db: AsyncSession, question: Question):
    await db.delete(question)
    await db.commit()

async def create_answer(db: AsyncSession, question_id: int, user_id: str, text: str) -> Answer:
    answer = Answer(question_id=question_id, user_id=user_id, text=text)
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer

async def get_answer_by_id(db: AsyncSession, answer_id: int) -> Optional[Answer]:
    result = await db.execute(
        select(Answer)
        .where(Answer.id == answer_id)
    )
    return result.scalar_one_or_none()

async def delete_answer(db: AsyncSession, answer: Answer):
    await db.delete(answer)
    await db.commit()
