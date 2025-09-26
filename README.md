# QnA

### 1. Запуск проекта после клонирования

```bash
git clone <репозиторий>
cd QnA
sudo docker compose up -d --build
```

---

### 2. Зайти в контейнер приложения

```bash
sudo docker exec -it qna-app /bin/bash
```

---

### 3. Запуск скрипта для создания суперпользователя

```bash
python init_superuser.py
```

---

### 4. Остановка контейнеров проекта

```bash
sudo docker compose down
```

---

### 5. Удаление образов и контейнеров проекта

```bash
sudo docker rm -f $(sudo docker ps -a -q --filter "name=qna-app" --filter "name=qna-db")
sudo docker rmi -f $(sudo docker images -q qna-app postgres:15)
```

* Первая команда удаляет только контейнеры `qna-app` и `qna-db`.
* Вторая — удаляет только образы `qna-app` и `postgres:15`.
