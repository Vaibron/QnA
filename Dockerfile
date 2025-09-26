# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Скрипт для проверки и создания миграций
CMD ["sh", "-c", "if [ ! -d 'alembic/versions' ] || [ -z \"$(ls -A alembic/versions)\" ]; then alembic revision --autogenerate -m 'initial migration'; fi && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
