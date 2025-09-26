import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db
from . import schemas, crud, models
from apps.auth.routes import get_current_user
from apps.auth.models import User

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["Вопросы"])

@router.get("/", response_model=list[schemas.QuestionResponse], summary="Получить список всех вопросов")
async def get_questions(db: AsyncSession = Depends(get_db)):
    """Получить список всех вопросов (публичный доступ)."""
    logger.info("Запрос на получение списка всех вопросов")
    questions = await crud.get_all_questions(db)
    logger.info(f"Успешно возвращено {len(questions)} вопросов")
    return questions

@router.post("/", response_model=schemas.QuestionResponse, summary="Создать новый вопрос")
async def create_question(
    question: schemas.QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый вопрос (только для авторизованных пользователей)."""
    logger.info(f"Пользователь {current_user.id} создает новый вопрос: {question.text}")
    result = await crud.create_question(db, text=question.text, author_id=current_user.id)
    logger.info(f"Вопрос успешно создан с ID: {result.id}")
    return result

@router.get("/{id}", response_model=schemas.QuestionDetailResponse, summary="Получить информацию о вопросе")
async def get_question(id: int, db: AsyncSession = Depends(get_db)):
    """Получить информацию о вопросе и его ответах (публичный доступ)."""
    logger.info(f"Запрос на получение вопроса с ID: {id}")
    question = await crud.get_question_by_id(db, id)
    if not question:
        logger.warning(f"Вопрос с ID {id} не найден")
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    logger.info(f"Успешно возвращен вопрос с ID: {id}")
    return question

@router.delete("/{id}", summary="Удалить вопрос")
async def delete_question(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить вопрос и связанные с ним ответы (только для владельца вопроса)."""
    logger.info(f"Пользователь {current_user.id} пытается удалить вопрос с ID: {id}")
    question = await crud.get_question_by_id(db, id)
    if not question:
        logger.warning(f"Вопрос с ID {id} не найден")
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    if question.author_id != current_user.id:
        logger.error(f"Пользователь {current_user.id} не авторизован для удаления вопроса с ID: {id}")
        raise HTTPException(status_code=403, detail="Нет прав для удаления этого вопроса")
    await crud.delete_question(db, question)
    logger.info(f"Вопрос с ID {id} успешно удален")
    return {"detail": "Вопрос успешно удален"}

@router.post("/{id}/answers/", response_model=schemas.AnswerResponse, summary="Добавить ответ к вопросу")
async def create_answer(
    id: int,
    answer: schemas.AnswerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Добавить ответ к вопросу (только для авторизованных пользователей)."""
    logger.info(f"Пользователь {current_user.id} добавляет ответ к вопросу с ID: {id}")
    question = await crud.get_question_by_id(db, id)
    if not question:
        logger.warning(f"Вопрос с ID {id} не найден")
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    result = await crud.create_answer(db, question_id=id, user_id=current_user.id, text=answer.text)
    logger.info(f"Ответ успешно добавлен к вопросу с ID: {id}, ответ ID: {result.id}")
    return result

answers_router = APIRouter(prefix="/answers", tags=["Ответы"])

@answers_router.get("/{id}", response_model=schemas.AnswerResponse, summary="Получить информацию об ответе")
async def get_answer(id: int, db: AsyncSession = Depends(get_db)):
    """Получить информацию об ответе (публичный доступ)."""
    logger.info(f"Запрос на получение ответа с ID: {id}")
    answer = await crud.get_answer_by_id(db, id)
    if not answer:
        logger.warning(f"Ответ с ID {id} не найден")
        raise HTTPException(status_code=404, detail="Ответ не найден")
    logger.info(f"Успешно возвращен ответ с ID: {id}")
    return answer

@answers_router.delete("/{id}", summary="Удалить ответ")
async def delete_answer(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить ответ (только для владельца ответа)."""
    logger.info(f"Пользователь {current_user.id} пытается удалить ответ с ID: {id}")
    answer = await crud.get_answer_by_id(db, id)
    if not answer:
        logger.warning(f"Ответ с ID {id} не найден")
        raise HTTPException(status_code=404, detail="Ответ не найден")
    if answer.user_id != current_user.id:
        logger.error(f"Пользователь {current_user.id} не авторизован для удаления ответа с ID: {id}")
        raise HTTPException(status_code=403, detail="Нет прав для удаления этого ответа")
    await crud.delete_answer(db, answer)
    logger.info(f"Ответ с ID {id} успешно удален")
    return {"detail": "Ответ успешно удален"}
