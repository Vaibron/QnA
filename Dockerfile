FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# создаём папку для миграций
RUN mkdir -p /app/alembic/versions

# Убедитесь, что скрипты исполняемые
RUN chmod +x /app/*.sh 2>/dev/null || true

# Простая команда по умолчанию (будет переопределена в docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]