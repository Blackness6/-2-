# Task Manager API

REST API для управления задачами на базе **FastAPI + PostgreSQL**.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **Alembic** — миграции БД
- **PostgreSQL** — база данных (продакшн)
- **Docker / docker-compose** — запуск окружения
- **pytest + SQLite in-memory** — тесты

## Быстрый старт

### Docker (рекомендуется)

```bash
docker-compose up --build
```

API будет доступен на `http://localhost:8000`.  
Документация Swagger: `http://localhost:8000/docs`.

### Локально

1. Создать и активировать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Создать файл `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=task_manager
DB_USER=beibarys
DB_PASSWORD=postgres
```

4. Применить миграции:

```bash
alembic upgrade head
```

5. Запустить сервер:

```bash
uvicorn app.main:app --reload
```

## Эндпоинты

| Метод    | URL                  | Описание                        |
|----------|----------------------|---------------------------------|
| `GET`    | `/`                  | Health check                    |
| `POST`   | `/api/tasks`         | Создать задачу                  |
| `GET`    | `/api/tasks`         | Список задач (фильтрация)       |
| `GET`    | `/api/tasks/stats`   | Статистика по статусам          |
| `GET`    | `/api/tasks/{id}`    | Получить задачу по ID           |
| `PATCH`  | `/api/tasks/{id}`    | Обновить задачу                 |
| `DELETE` | `/api/tasks/{id}`    | Удалить задачу                  |

### Фильтрация списка

```
GET /api/tasks?status=TODO&priority=1
```

Параметры необязательны, можно использовать по отдельности или вместе.

### Статусы задачи

`TODO` · `IN_PROGRESS` · `DONE` · `CANCELLED`

### Приоритеты

`1` — низкий · `2` — средний (по умолчанию) · `3` — высокий

### Пример создания задачи

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Новая задача", "priority": 3}'
```

Ответ:

```json
{
  "id": 1,
  "title": "Новая задача",
  "description": null,
  "status": "TODO",
  "priority": 3,
  "created_at": "2026-06-25T10:00:00",
  "updated_at": "2026-06-25T10:00:00"
}
```

## Тесты

```bash
pytest tests/ -v
```

Тесты используют SQLite in-memory — PostgreSQL для их запуска не нужен.

## Структура проекта

```
task-api/
├── app/
│   ├── core/config.py          # Настройки через pydantic-settings
│   ├── database.py             # Подключение к БД, get_db
│   ├── models.py               # SQLAlchemy-модель Task
│   ├── schemas.py              # Pydantic-схемы (запрос/ответ)
│   ├── repositories/           # Слой работы с БД
│   ├── services/               # Бизнес-логика
│   ├── routers/                # FastAPI-роутеры
│   └── main.py                 # Точка входа
├── migrations/                 # Alembic-миграции
├── tests/
│   ├── conftest.py             # Фикстуры pytest (SQLite)
│   └── test_takes.py           # 13 тестов
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh               # alembic upgrade head + uvicorn
├── requirements.txt
└── .env
```

## Миграции

Создать новую миграцию:

```bash
alembic revision --autogenerate -m "описание"
```

Применить:

```bash
alembic upgrade head
```

Откатить:

```bash
alembic downgrade -1
```
