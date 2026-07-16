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

3. Создать файл `.env` (см. `.env.example`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=task_manager
DB_USER=postgres
DB_PASSWORD=postgres

SECRET_KEY=<случайная-строка>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
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

Все эндпоинты, кроме `/`, `/metrics` и `/auth/*`, требуют заголовок
`Authorization: Bearer <token>`.

### Служебные

| Метод | URL        | Описание                       |
|-------|------------|--------------------------------|
| `GET` | `/`        | Health check                   |
| `GET` | `/metrics` | Метрики Prometheus             |

### Аутентификация

| Метод  | URL              | Описание                        |
|--------|------------------|---------------------------------|
| `POST` | `/auth/register` | Регистрация пользователя        |
| `POST` | `/auth/login`    | Логин, возвращает JWT-токен     |
| `GET`  | `/auth/me`       | Текущий пользователь            |

### Задачи

| Метод    | URL                       | Описание                        |
|----------|---------------------------|---------------------------------|
| `POST`   | `/api/tasks`              | Создать задачу                  |
| `GET`    | `/api/tasks`              | Список задач (фильтрация)       |
| `GET`    | `/api/tasks/stats`        | Статистика по статусам          |
| `GET`    | `/api/tasks/{id}`         | Получить задачу по ID           |
| `PATCH`  | `/api/tasks/{id}`         | Обновить задачу                 |
| `PATCH`  | `/api/tasks/{id}/assign`  | Назначить/снять исполнителя      |
| `DELETE` | `/api/tasks/{id}`         | Удалить задачу                  |

### Проекты

| Метод    | URL                                       | Описание                     |
|----------|-------------------------------------------|------------------------------|
| `POST`   | `/api/projects`                           | Создать проект               |
| `GET`    | `/api/projects`                           | Список проектов              |
| `GET`    | `/api/projects/{id}`                      | Получить проект              |
| `PATCH`  | `/api/projects/{id}`                      | Обновить проект (владелец)   |
| `DELETE` | `/api/projects/{id}`                      | Удалить проект (владелец)    |
| `POST`   | `/api/projects/{id}/tasks`                | Создать задачу в проекте     |
| `GET`    | `/api/projects/{id}/tasks`                | Задачи проекта               |
| `GET`    | `/api/projects/{id}/members`              | Участники проекта            |
| `POST`   | `/api/projects/{id}/members`              | Добавить участника (владелец)|
| `DELETE` | `/api/projects/{id}/members/{user_id}`    | Удалить участника (владелец) |

### Пользователи

| Метод | URL          | Описание                                  |
|-------|--------------|-------------------------------------------|
| `GET` | `/api/users` | Список пользователей (для выбора исполнителя) |

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
backend/
├── app/
│   ├── core/                   # config, security (JWT/bcrypt), logging, time
│   ├── database.py             # Подключение к БД (engine, SessionLocal)
│   ├── models.py               # SQLAlchemy-модели: User, Project, Task, ProjectMember
│   ├── schemas.py              # Pydantic-схемы (запрос/ответ)
│   ├── interfaces/             # Абстрактные интерфейсы репозиториев
│   ├── repositories/           # Слой работы с БД
│   ├── services/               # Бизнес-логика
│   ├── routers/                # FastAPI-роутеры
│   ├── middleware/             # Логирование и метрики запросов
│   ├── observability/          # Определения метрик Prometheus
│   ├── providers.py            # DI-контейнер (dishka)
│   └── main.py                 # Точка входа
├── migrations/                 # Alembic-миграции
├── tests/                      # pytest + SQLite in-memory
├── docker-compose.yml          # Postgres + backend
├── Dockerfile
├── entrypoint.sh               # alembic upgrade head + uvicorn
├── requirements.txt            # Прод-зависимости
├── requirements-dev.txt        # pytest, httpx
└── .env                        # Локальные настройки (не в git)
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


