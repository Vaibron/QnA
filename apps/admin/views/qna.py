from sqladmin import ModelView
from apps.qna.models import Question, Answer


class QuestionAdmin(ModelView, model=Question):
    column_list = [Question.id, Question.text, Question.created_at]
    column_searchable_list = [Question.text]
    column_sortable_list = [Question.id, Question.created_at]
    page_size = 20
    name = "Вопрос"
    name_plural = "Вопросы"
    icon = "fa fa-question-circle"


class AnswerAdmin(ModelView, model=Answer):
    column_list = [Answer.id, Answer.text, Answer.user_id, Answer.question_id, Answer.created_at]
    column_searchable_list = [Answer.text]
    column_sortable_list = [Answer.id, Answer.created_at]
    page_size = 20
    name = "Ответ"
    name_plural = "Ответы"
    icon = "fa fa-reply"