# Task Manager API — Полное объяснение проекта

## Что это такое

REST API для управления задачами — как упрощённый Trello. Написан на Python с FastAPI, хранит данные в PostgreSQL. Запускается в Docker.

## Как устроена архитектура

```
Клиент (браузер/Postman)
        ↓  HTTP-запрос
   [routers/tasks.py]          ← принимает запросы
        ↓
  [services/task_service.py]   ← бизнес-логика
        ↓
  [repositories/task_repository.py]  ← работа с БД
        ↓
   [PostgreSQL / SQLite]
```

Три слоя разделены специально — можно поменять БД или фреймворк независимо друг от друга.

## Структура файлов

```
task-api/
├── .env                    ← секреты (не в git)
├── requirements.txt        ← зависимости Python
├── Dockerfile              ← сборка Docker-образа
├── docker-compose.yml      ← запуск api + db вместе
├── entrypoint.sh           ← старт: миграции → сервер
├── alembic.ini             ← настройки Alembic
│
├── app/
│   ├── main.py             ← точка входа FastAPI
│   ├── database.py         ← подключение к БД, сессии
│   ├── models.py           ← таблица tasks в виде Python-класса
│   ├── schemas.py          ← формат запросов и ответов
│   ├── core/
│   │   └── config.py       ← читает .env, собирает DATABASE_URL
│   ├── routers/
│   │   └── tasks.py        ← HTTP-маршруты (GET/POST/PATCH/DELETE)
│   ├── services/
│   │   └── task_service.py ← бизнес-логика
│   └── repositories/
│       └── task_repository.py ← SQL-запросы
│
├── migrations/
│   ├── env.py              ← конфиг Alembic (как запускать миграции)
│   └── versions/
│       └── d97b81ffd2be_initial.py ← первая миграция (создание таблицы)
│
└── tests/
    ├── conftest.py         ← настройка тестовой БД (SQLite in-memory)
    └── test_takes.py       ← 13 тестов
```

---

## requirements.txt — зависимости проекта

```
fastapi           — веб-фреймворк для создания API
uvicorn[standard] — сервер, который запускает FastAPI
sqlalchemy        — ORM (работа с БД через Python-объекты, без SQL)
alembic           — миграции БД (создание/изменение таблиц)
psycopg2-binary   — драйвер для подключения к PostgreSQL
pydantic          — валидация данных (проверяет что title не пустой и т.д.)
pydantic-settings — загрузка настроек из файла .env
python-dotenv     — читает файл .env
```

---

## .env — переменные окружения (секреты)

```
DB_HOST=localhost      # адрес сервера базы данных
DB_PORT=5432           # порт PostgreSQL (стандартный)
DB_NAME=task_manager   # название базы данных
DB_USER=beibarys       # пользователь БД
DB_PASSWORD=postgres   # пароль БД
```

Этот файл не заливается в git (там секреты). Приложение читает его при запуске.

---

## app/core/config.py — настройки приложения

```python
from pydantic_settings import BaseSettings
# Импортируем базовый класс для настроек.

class Settings(BaseSettings):
    DB_HOST: str = "localhost"   # значения по умолчанию — если .env не найден
    DB_PORT: int = 5432
    DB_NAME: str = "task_manager"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    # Класс автоматически читает переменные из .env файла и подставляет их сюда.

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    # Собирает строку подключения к БД из отдельных переменных.
    # Пример: postgresql+psycopg2://beibarys:postgres@localhost:5432/task_manager

    @property
    def TEST_DATABASE_URL(self) -> str:
        return "sqlite:///./test.db"
    # URL для тестовой базы — SQLite (файл на диске, не нужен сервер PostgreSQL).

    model_config = {"env_file": ".env", "extra": "ignore"}
    # Говорим pydantic: читать из файла .env, лишние переменные игнорировать.

settings = Settings()
# Создаём один глобальный объект настроек. Все файлы импортируют именно его.
```

---

## app/database.py — подключение к базе данных

```python
class Base(DeclarativeBase):
    pass
# Базовый класс для всех моделей (таблиц).
# Все модели наследуются от него — SQLAlchemy так знает о всех таблицах.

def get_engine(url: str | None = None):
    db_url = url or settings.DATABASE_URL
    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
    return create_engine(db_url, connect_args=connect_args)
# Создаёт "движок" — объект соединения с БД.
# check_same_thread: False нужен только для SQLite (PostgreSQL не требует).

engine = get_engine()
# Создаём движок один раз при запуске приложения.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Фабрика сессий. Сессия — это как "транзакция": набор операций с БД,
# которые либо все выполняются, либо ни одна.
# autocommit=False — мы сами решаем когда сохранять.

def get_db():
    db = SessionLocal()   # открываем сессию
    try:
        yield db          # передаём её в роутер (здесь выполняется логика запроса)
    finally:
        db.close()        # гарантированно закрываем после запроса
# Генератор-зависимость для FastAPI.
# Каждый HTTP-запрос получает свою сессию БД, которая закрывается после ответа.
```

---

## app/models.py — структура таблицы в БД

```python
class Task(Base):
    __tablename__ = "tasks"   # название таблицы в БД

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), "postgresql"),
        primary_key=True,
        autoincrement=True,
    )
    # Колонка id. with_variant — хитрость:
    # для PostgreSQL используем BigInteger (большие числа),
    # для SQLite — обычный Integer (SQLite не умеет BIGINT с autoincrement).

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # Заголовок задачи. Строка до 255 символов, обязательное поле.

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Описание. Text — длинный текст без ограничения. Может быть пустым.

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="TODO")
    # Статус задачи. Максимум 30 символов.

    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    # Приоритет (1, 2, или 3). По умолчанию 2 — средний.

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Временные метки создания и обновления.
```

---

## app/schemas.py — формат данных от клиента

Схемы — это "контракт": что клиент должен прислать и что получит в ответ.

```python
TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]
TaskPriority = Literal[1, 2, 3]
# Типы-ограничения. Если клиент пришлёт status: "FLYING" — Pydantic вернёт ошибку 422.

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)  # обязательное, 1-255 символов
    description: str | None = None                          # необязательное
    priority: TaskPriority = 2                              # необязательное, по умолчанию 2
# Данные при создании задачи. ... означает "обязательное поле".

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
# Данные при обновлении. Все поля необязательные — можно менять только один атрибут.

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
# Что API возвращает клиенту.
# from_attributes=True позволяет создать схему из объекта SQLAlchemy (не из словаря).

class TaskStats(BaseModel):
    TODO: int = 0
    IN_PROGRESS: int = 0
    DONE: int = 0
    CANCELLED: int = 0
# Структура ответа для статистики.
```

---

## app/repositories/task_repository.py — работа с БД

```python
class TaskRepository:
    def __init__(self, db: Session):
        self.db = db          # сохраняем сессию БД

    def create(self, task: Task) -> Task:
        self.db.add(task)     # добавляем объект в сессию (ещё не в БД)
        self.db.commit()      # выполняем INSERT в БД
        self.db.refresh(task) # обновляем объект из БД (получаем id)
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)
        # SELECT * FROM tasks WHERE id = task_id

    def get_all(self, status=None, priority=None) -> list[Task]:
        stmt = select(Task)                           # SELECT * FROM tasks
        if status is not None:
            stmt = stmt.where(Task.status == status)  # добавляем WHERE status = ?
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        return list(self.db.scalars(stmt).all())      # выполняем и возвращаем список

    def update(self, task: Task) -> Task:
        self.db.commit()       # SQLAlchemy уже знает об изменениях — просто сохраняем
        self.db.refresh(task)  # обновляем объект из БД
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)  # помечаем на удаление
        self.db.commit()      # выполняем DELETE

    def get_stats(self) -> dict[str, int]:
        rows = self.db.execute(
            select(Task.status, func.count(Task.id).label("cnt"))
            .group_by(Task.status)
            # SQL: SELECT status, COUNT(id) FROM tasks GROUP BY status
        ).all()
        return {row.status: row.cnt for row in rows}  # {"TODO": 5, "DONE": 3}
```

---

## app/services/task_service.py — бизнес-логика

```python
class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo
    # Конструктор. Принимает репозиторий и сохраняет в self.repo.
    # Это инъекция зависимостей — сервис не создаёт репозиторий сам, а получает снаружи.

    def create_task(self, data: TaskCreate) -> Task:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        # Текущее время в UTC. replace(tzinfo=None) убирает timezone,
        # потому что SQLite не умеет хранить timezone-aware даты.
        task = Task(
            title=data.title,
            description=data.description,
            status="TODO",        # новая задача всегда начинается со статуса TODO
            priority=data.priority,
            created_at=now,
            updated_at=now,
        )
        return self.repo.create(task)

    def get_tasks(self, status=None, priority=None) -> list[Task]:
        return self.repo.get_all(status=status, priority=priority)
        # Просто передаёт фильтры в репозиторий и возвращает результат.

    def get_task(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        # Если задача не найдена — выбрасываем ошибку 404.
        # FastAPI поймает её и вернёт клиенту JSON: {"detail": "Task 5 not found"}
        return task

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        # Сначала проверяем существование (если нет — get_task сам выбросит 404).
        update_data = data.model_dump(exclude_none=True)
        # Преобразуем схему в словарь {"title": "...", "priority": 2}.
        # exclude_none=True — не включаем поля, которые клиент не передал.
        for field, value in update_data.items():
            setattr(task, field, value)
        # Перебираем все переданные поля и устанавливаем их на объект task.
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.repo.update(task)

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)   # проверяем существование (иначе 404)
        self.repo.delete(task)

    def get_stats(self) -> TaskStats:
        raw = self.repo.get_stats()
        # Получаем из репозитория сырой словарь {"TODO": 5, "DONE": 3, ...}
        return TaskStats(
            TODO=raw.get("TODO", 0),
            IN_PROGRESS=raw.get("IN_PROGRESS", 0),
            DONE=raw.get("DONE", 0),
            CANCELLED=raw.get("CANCELLED", 0),
        )
        # .get("TODO", 0) — если ключа нет (задач с этим статусом не было), вернём 0.
```

---

## app/routers/tasks.py — HTTP-эндпоинты

```python
router = APIRouter(prefix="/api/tasks", tags=["tasks"])
# Все маршруты будут начинаться с /api/tasks.

def get_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))
# Фабрика: FastAPI вызывает get_db() → получает сессию →
# создаёт репозиторий → создаёт сервис. Всё автоматически при каждом запросе.

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, service: Annotated[TaskService, Depends(get_service)]):
    return service.create_task(data)
# POST /api/tasks — создать задачу. Возвращает 201 Created.

@router.get("/stats", response_model=TaskStats)
def get_stats(service: Annotated[TaskService, Depends(get_service)]):
    return service.get_stats()
# GET /api/tasks/stats — статистика.
# Важно: /stats объявлен РАНЬШЕ /{task_id},
# иначе FastAPI интерпретировал бы "stats" как id.

@router.get("", response_model=list[TaskResponse])
def get_tasks(service, status=Query(default=None), priority=Query(default=None)):
    return service.get_tasks(status=status, priority=priority)
# GET /api/tasks?status=DONE&priority=1 — список с фильтрами.
# Query означает параметры в URL (после знака ?).

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, service: Annotated[TaskService, Depends(get_service)]):
    return service.get_task(task_id)
# GET /api/tasks/5 — одна задача по id.
# {task_id} — переменная часть URL.

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, service: Annotated[TaskService, Depends(get_service)]):
    return service.update_task(task_id, data)
# PATCH /api/tasks/5 — частичное обновление (не PUT, который требует все поля).

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, service: Annotated[TaskService, Depends(get_service)]):
    service.delete_task(task_id)
# DELETE /api/tasks/5 — удалить. 204 No Content — тело ответа пустое.
```

---

## app/main.py — точка входа

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
# Хук жизненного цикла. Сейчас пустой — таблицы создаются через миграции.
# До yield — код при старте сервера. После yield — код при остановке.

app = FastAPI(
    title="Task Manager API",
    description="REST API для управления задачами — FastAPI + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)
# Создаём приложение. Эти данные автоматически отображаются на странице /docs.

app.include_router(tasks_router)   # подключаем роутер с задачами

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "docs": "/docs"}
# GET / — проверка что сервер жив (health check).
```

---

## Миграции Alembic

### alembic.ini
Конфиг Alembic. Главное: `script_location = migrations` — где искать файлы миграций.

### migrations/env.py

```python
import app.models  # noqa: F401
# Импортируем модели чтобы Alembic видел все таблицы.
# noqa: F401 — подавляем предупреждение "импорт не используется".

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
# Передаём URL из настроек, чтобы не дублировать в alembic.ini.

def run_migrations_online():   # обычный режим — подключается к живой БД
def run_migrations_offline():  # генерирует SQL-скрипт без подключения к БД
```

### migrations/versions/d97b81ffd2be_initial.py

```python
def upgrade() -> None:
    op.create_table("tasks", ...)  # создаёт таблицу tasks

def downgrade() -> None:
    op.drop_table("tasks")         # откатывает — удаляет таблицу
```

Каждая миграция имеет `upgrade` (применить) и `downgrade` (откатить).
Запускается командой: `alembic upgrade head`

---

## Docker

### Dockerfile

```dockerfile
FROM python:3.13-slim          # берём минимальный образ Python 3.13
WORKDIR /app                   # все команды выполняются в /app
COPY requirements.txt .        # копируем только список зависимостей (кэш Docker)
RUN pip install -r requirements.txt  # устанавливаем пакеты
COPY . .                       # копируем весь код
RUN chmod +x entrypoint.sh     # делаем скрипт запуска исполняемым
EXPOSE 8000                    # документируем что контейнер слушает порт 8000
CMD ["./entrypoint.sh"]        # команда по умолчанию при запуске контейнера
```

### entrypoint.sh

```bash
set -e                          # при любой ошибке — остановиться
alembic upgrade head            # применяем все миграции (создаём таблицы)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000  # запускаем сервер
```

`exec` заменяет текущий процесс uvicorn'ом — правильная передача сигналов в Docker.

### docker-compose.yml

```yaml
services:
  db:                           # контейнер PostgreSQL
    image: postgres:16-alpine   # лёгкая версия PostgreSQL 16
    healthcheck:                # проверяем готовность БД перед запуском api
      test: pg_isready ...
      interval: 5s              # каждые 5 секунд
      retries: 5                # 5 попыток
    volumes:
      - postgres_data:/...      # данные БД сохраняются между перезапусками

  api:
    build: .                    # собираем из Dockerfile в текущей папке
    depends_on:
      db:
        condition: service_healthy  # ждём пока БД не скажет "готова"
```

---

## Тесты

### tests/conftest.py

```python
TEST_DATABASE_URL = "sqlite://"    # "" в конце = in-memory (только в памяти, не файл)

test_engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,          # один коннект на все тесты (нужно для SQLite in-memory)
)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)  # создаём таблицы перед тестом
    yield
    Base.metadata.drop_all(bind=test_engine)    # удаляем после теста (чистое состояние)
# autouse=True — фикстура запускается автоматически для каждого теста.

@pytest.fixture
def client(setup_db):
    def override_get_db():
        ...                              # возвращаем тестовую сессию вместо боевой
    app.dependency_overrides[get_db] = override_get_db  # подменяем зависимость
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()    # убираем подмену после теста
# dependency_overrides — мощная фича FastAPI:
# подменяет любую зависимость для тестов без изменения основного кода.
```

### tests/test_takes.py

7 обязательных тестов:

| # | Тест | Что проверяет |
|---|------|---------------|
| 1 | test_create_task | POST создаёт задачу, возвращает 201 и правильные поля |
| 2 | test_get_tasks_list | GET возвращает список всех задач |
| 3 | test_get_task_by_id | GET по id возвращает нужную задачу |
| 4 | test_update_status | PATCH меняет статус |
| 5 | test_update_priority | PATCH меняет приоритет |
| 6 | test_delete_task | DELETE удаляет, после — 404 |
| 7 | test_get_nonexistent_task | GET несуществующего id возвращает 404 |

Дополнительные тесты:

| Тест | Что проверяет |
|------|---------------|
| test_filter_by_status | Фильтрация ?status=DONE |
| test_filter_by_priority | Фильтрация ?priority=1 |
| test_invalid_status | Неверный статус → 422 |
| test_empty_title | Пустой title → 422 |
| test_missing_required_fields | Нет title → 422 |
| test_stats_endpoint | /stats возвращает правильные счётчики |

---

## Как запустить проект

### Через Docker (рекомендуется)

```bash
docker-compose up --build
```

После запуска:
- API: http://localhost:8000
- Документация: http://localhost:8000/docs

### Локально (без Docker)

```bash
# Установить зависимости
pip install -r requirements.txt

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Запустить тесты

```bash
pytest tests/
```

---

## Список всех API-эндпоинтов

| Метод | URL | Описание |
|-------|-----|----------|
| GET | / | Health check |
| POST | /api/tasks | Создать задачу |
| GET | /api/tasks | Список задач (с фильтрами) |
| GET | /api/tasks/stats | Статистика по статусам |
| GET | /api/tasks/{id} | Получить задачу по id |
| PATCH | /api/tasks/{id} | Обновить задачу |
| DELETE | /api/tasks/{id} | Удалить задачу |
