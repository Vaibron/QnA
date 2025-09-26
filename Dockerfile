# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости и Postgres-клиент
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Скрипт для проверки и создания миграций + запуск приложения
CMD ["sh", "-c", "\
  # Ждем готовности базы данных \
  until pg_isready -h $DB_HOST -U $DB_USER -d $DB_NAME; do sleep 2; done; \
  # Создаем миграцию, если папка пустая \
  if [ ! -d 'alembic/versions' ] || [ -z \"$(ls -A alembic/versions)\" ]; then \
    alembic revision --autogenerate -m 'initial migration'; \
  fi; \
  # Применяем миграции и запускаем сервер \
  alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 \
"]
