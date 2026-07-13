# Task Manager — Полное объяснение проекта

## Что это такое

Fullstack-приложение для управления задачами — как упрощённый Trello с командной работой.
Проект состоит из четырёх частей:

- **Backend** — REST API на Python (FastAPI) + PostgreSQL
- **Frontend** — SPA на React + TypeScript (Vite)
- **Мониторинг** — Prometheus + Grafana
- **CI** — GitHub Actions (тесты и сборка при каждом push/PR)

Есть регистрация и вход (JWT), задачи привязаны к пользователям: у задачи есть **создатель**, **исполнитель** и тот, кто исполнителя **назначил**.

## Как устроена архитектура

```
Браузер (React SPA, порт 3000)
        │  HTTP + JWT-токен в заголовке Authorization
        ▼
[routers/]                 ← принимает запросы, проверяет токен
        ▼
[services/]                ← бизнес-логика, права доступа, транзакции
        ▼
[repositories/]            ← SQL-запросы через SQLAlchemy
        ▼
   PostgreSQL

Сборка зависимостей: dishka (DI-контейнер)
Сквозные слои: middleware (логирование, метрики) → Prometheus → Grafana
```

Слои разделены специально: можно поменять БД или фреймворк независимо друг от друга.
Сервисы зависят не от конкретных репозиториев, а от **интерфейсов** (`ITaskRepository`, `IUserRepository`) — это упрощает тестирование и подмену реализации.

## Структура файлов

```
task-api/
├── docker-compose.yml           ← запуск всего: db + api + frontend + prometheus + grafana
├── .github/workflows/ci.yml     ← CI: тесты backend и frontend
│
├── backend/
│   ├── Dockerfile               ← образ Python 3.13
│   ├── entrypoint.sh            ← старт: миграции → сервер
│   ├── requirements.txt         ← прод-зависимости
│   ├── requirements-dev.txt     ← pytest, httpx (в прод-образ не попадают)
│   ├── alembic.ini              ← настройки Alembic
│   ├── .env / .env.example      ← секреты (не в git) / шаблон
│   │
│   ├── app/
│   │   ├── main.py              ← точка входа FastAPI, middleware, /metrics
│   │   ├── database.py          ← engine, SessionLocal, Base
│   │   ├── models.py            ← таблицы users и tasks
│   │   ├── schemas.py           ← Pydantic-схемы запросов/ответов
│   │   ├── providers.py         ← DI-контейнер dishka
│   │   ├── core/
│   │   │   ├── config.py        ← настройки из .env
│   │   │   ├── security.py      ← bcrypt, JWT, get_current_user_id
│   │   │   └── logging.py       ← настройка логов
│   │   ├── middleware/
│   │   │   ├── logging_middleware.py  ← лог каждого запроса
│   │   │   └── metrics_middleware.py  ← метрики Prometheus
│   │   ├── observability/
│   │   │   └── metrics.py       ← определения метрик (Counter, Histogram, Gauge)
│   │   ├── interfaces/
│   │   │   ├── task_repository.py     ← ITaskRepository (абстрактный класс)
│   │   │   └── user_repository.py     ← IUserRepository
│   │   ├── routers/
│   │   │   ├── auth.py          ← /auth/register, /auth/login, /auth/me
│   │   │   ├── tasks.py         ← CRUD задач + /assign + /stats
│   │   │   └── users.py         ← список пользователей (для выбора исполнителя)
│   │   ├── services/
│   │   │   ├── auth_service.py  ← регистрация, вход, выдача токена
│   │   │   └── task_service.py  ← бизнес-логика задач
│   │   └── repositories/
│   │       ├── task_repository.py
│   │       └── user_repository.py
│   │
│   ├── migrations/versions/     ← 4 миграции Alembic:
│   │   ├── d97b81ffd2be_initial.py                ← таблица tasks
│   │   ├── 4d13fc3f415d_add_users_table.py        ← таблица users
│   │   ├── a1b2c3d4e5f6_add_user_id_to_tasks.py   ← связь задач с пользователями
│   │   └── b7e2f8a9c1d3_task_assignment_fields.py ← поля назначения
│   │
│   └── tests/
│       ├── conftest.py          ← тестовая БД (SQLite in-memory)
│       └── test_takes.py        ← 20 тестов
│
├── frontend/
│   ├── Dockerfile               ← сборка Vite → раздача через nginx
│   ├── package.json             ← react 19, axios, react-router, vitest
│   └── src/
│       ├── main.tsx / App.tsx   ← точка входа, роутинг
│       ├── api/                 ← axios-клиент, запросы к API, типы
│       ├── auth/AuthContext.tsx ← хранение токена, состояние «вошёл/не вошёл»
│       └── pages/               ← Login, Register, Tasks (+ тесты рядом)
│
└── monitoring/
    ├── prometheus/prometheus.yml ← кого опрашивать (scrape-таргеты)
    └── grafana/                  ← дашборд + авто-подключение источника данных
```

---

## Backend

### app/core/config.py — настройки

```python
class Settings(BaseSettings):
    DB_HOST: str        # без значений по умолчанию — приложение
    DB_PORT: int        # не стартует, если переменная не задана
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    SECRET_KEY: str     # ключ подписи JWT-токенов

    ALGORITHM: str = "HS256"              # алгоритм подписи JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # токен живёт 30 минут

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
```

Переменные читаются из `.env` (локально) или из environment в docker-compose / Render.

### app/models.py — две таблицы

**User** — пользователь:

| Поле | Тип | Описание |
|------|-----|----------|
| id | int (BigInteger в PG) | первичный ключ |
| username | str(100), unique | имя пользователя |
| email | str(255), unique | почта (логин) |
| hashed_password | str(255) | bcrypt-хэш, пароль в открытом виде не хранится |
| role | str(20), default "user" | роль (задел на будущее) |
| created_at | datetime | когда зарегистрировался |

**Task** — задача:

| Поле | Тип | Описание |
|------|-----|----------|
| id, title, description, status, priority | — | как раньше (status: TODO/IN_PROGRESS/DONE/CANCELLED, priority: 1–3) |
| creator_id | FK → users.id, CASCADE | кто создал; при удалении пользователя его задачи удаляются |
| assignee_id | FK → users.id, SET NULL | кто выполняет; при удалении пользователя поле обнуляется |
| assigned_by_id | FK → users.id, SET NULL | кто назначил текущего исполнителя |
| created_at, updated_at | datetime | временные метки |

Плюс `relationship` в обе стороны (`creator`, `assignee`, `assigned_by`) — чтобы API отдавал не только id, но и имя пользователя.

### app/schemas.py — формат данных

Новое по сравнению со старой версией:

```python
class TaskStatus(str, Enum): ...        # статусы теперь Enum, а не Literal
class TaskPriorityEnum(int, Enum): ...  # LOW=1, MEDIUM=2, HIGH=3

class UserCreate(BaseModel):            # регистрация
    username: str   # 3–100 символов
    email: EmailStr # pydantic сам проверяет формат почты
    password: str   # минимум 8 символов

class TaskCreate(BaseModel):
    ...
    assignee_id: int | None = None      # можно сразу назначить исполнителя

class TaskAssign(BaseModel):            # отдельная схема для /assign
    assignee_id: int

class TaskResponse(BaseModel):
    ...
    creator: UserShortResponse          # вложенные объекты пользователей —
    assigned_by: UserShortResponse | None  # frontend показывает имена,
    assignee: UserShortResponse | None     # а не голые id

class Token(BaseModel):                 # ответ /auth/login
    access_token: str
    token_type: str                     # "bearer"
```

### app/core/security.py — пароли и JWT

```python
hash_password(password)        # bcrypt-хэш при регистрации
verify_password(plain, hashed) # проверка при входе

create_access_token({"sub": str(user.id)})
# JWT с id пользователя внутри и сроком жизни 30 минут,
# подписан SECRET_KEY — подделать без ключа нельзя.

get_current_user_id(credentials)
# FastAPI-зависимость: достаёт токен из заголовка Authorization: Bearer <token>,
# проверяет подпись и срок, возвращает user_id. Невалидный токен → 401.
```

Каждый защищённый эндпоинт просто добавляет `user_id: int = Depends(get_current_user_id)` — и автоматически требует авторизацию.

### app/providers.py — dishka (внедрение зависимостей)

Раньше зависимости собирались вручную через фабрику `get_service()`. Теперь это делает DI-контейнер **dishka**:

```python
class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)      # на каждый HTTP-запрос — своя сессия БД
    def get_session(self) -> Iterable[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()                 # сессия гарантированно закрывается

class AppProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_task_repository(self, db: Session) -> ITaskRepository:
        return TaskRepository(db)      # запросили интерфейс — получили реализацию
    # ... то же для UserRepository, TaskService, AuthService
```

В роутере пишем `service: FromDishka[TaskService]` (и `route_class=DishkaRoute` у роутера) — контейнер сам строит цепочку: сессия → репозитории → сервис.

### app/repositories/ — работа с БД

Ключевые изменения:

```python
def _visible_to(user_id):
    # Пользователь видит задачу, только если он её создатель ИЛИ исполнитель.
    return or_(Task.creator_id == user_id, Task.assignee_id == user_id)

def _with_users(stmt):
    # selectinload — жадная подгрузка creator/assigned_by/assignee одним
    # дополнительным запросом (иначе N+1 запросов при сериализации ответа).
    return stmt.options(selectinload(Task.creator), ...)
```

Все методы чтения (`get_by_id`, `get_all`, `get_stats`) фильтруют по `_visible_to(user_id)` — чужие задачи не видны вообще.

Важно: репозиторий теперь делает **`flush()` вместо `commit()`**. Flush отправляет SQL в БД (и получает id), но не завершает транзакцию — коммитит сервис. Так несколько операций объединяются в одну атомарную транзакцию.

### app/services/task_service.py — бизнес-логика и права

```python
def create_task(self, data, user_id):
    # Если при создании указан исполнитель — проверяем, что он существует,
    # и записываем, кто назначил (текущий пользователь из JWT).
    ...
    try:
        task = self.repo.create(task)   # flush
        self.db.commit()                # транзакция завершается здесь
    except Exception:
        self.db.rollback()              # при ошибке — откат, БД не портится
        raise
```

Правила доступа:

- **видеть/редактировать** задачу может создатель и исполнитель;
- **назначать исполнителя** (`PATCH /{id}/assign`) может только создатель → иначе 403;
- **удалять** может только создатель → иначе 403;
- чужая задача выглядит как несуществующая → 404 (не раскрываем, что она есть).

### app/services/auth_service.py

- `register` — проверка «email уже занят» (400), хэширование пароля, создание пользователя;
- `login` — поиск по email + проверка пароля; при любой ошибке один и тот же ответ 401 «Invalid email or password» (не подсказываем, что именно неверно);
- `get_account` — данные текущего пользователя для `/auth/me`.

### app/main.py — точка входа

```python
app.add_middleware(LoggingMiddleware)   # лог: "GET /api/tasks -> 200 (12.34 ms)"
app.add_middleware(MetricsMiddleware)   # счётчики для Prometheus

app.add_middleware(CORSMiddleware, allow_origins=[
    "http://localhost:3000",              # локальный frontend
    "https://frontend-928y.onrender.com", # frontend на Render
])
# CORS обязателен: frontend и API живут на разных доменах/портах,
# без него браузер заблокирует запросы.

container = make_async_container(DatabaseProvider(), AppProvider())
setup_dishka(container, app=app)        # подключаем DI-контейнер

@app.get("/metrics", include_in_schema=False)  # не показываем в /docs
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
# Отсюда Prometheus каждые 5 секунд забирает метрики.
```

### Мониторинг

**observability/metrics.py** — четыре метрики:

| Метрика | Тип | Что измеряет |
|---------|-----|--------------|
| task_api_http_requests_total | Counter | количество запросов (метод, путь, статус) |
| task_api_http_request_duration_seconds | Histogram | время ответа |
| task_api_http_requests_in_progress | Gauge | сколько запросов выполняется прямо сейчас |
| task_api_http_errors_total | Counter | ответы со статусом ≥ 400 |

**metrics_middleware.py** оборачивает каждый запрос: инкрементирует счётчики, замеряет время через `time.perf_counter()`. В качестве пути берёт **шаблон роута** (`/api/tasks/{task_id}`), а не реальный URL — иначе каждый id создавал бы отдельную метрику. Запросы к самому `/metrics` не считаются.

**Prometheus** (порт 9090) опрашивает `/metrics` каждые 5 секунд — и локальный api, и задеплоенный на Render.
**Grafana** (порт 3001, admin/admin) — готовый дашборд из `monitoring/grafana/dashboards/`, источник данных подключается автоматически через provisioning.

---

## Frontend

React 19 + TypeScript + Vite. Запросы через axios, роутинг через react-router-dom.

- **api/** — axios-клиент (`api.ts` подставляет `VITE_API_URL` и токен в заголовок), функции запросов (`auth.ts`, `tasks.ts`, `users.ts`), типы (`types.ts`);
- **auth/AuthContext.tsx** — React-контекст: хранит JWT-токен, знает, вошёл ли пользователь, отдаёт login/logout всему приложению;
- **pages/** — `Login`, `Register`, `Tasks` (основной экран: список задач, фильтры, назначение исполнителя).

Тесты — **vitest** + Testing Library (файлы `*.test.tsx` лежат рядом с кодом). Линтер — **oxlint**.

Docker-образ двухэтапный: сначала `node:22` собирает статику (`npm run build`), потом `nginx:alpine` её раздаёт. `VITE_API_URL` передаётся на этапе сборки — Vite вшивает адрес API прямо в JS-бандл.

---

## Docker Compose — пять сервисов

| Сервис | Порт (снаружи) | Что это |
|--------|----------------|---------|
| db | 5433 → 5432 | PostgreSQL 16 (5433 — чтобы не конфликтовать с локальным Postgres) |
| api | 8001 → 8000 | backend (ждёт готовности db через healthcheck) |
| frontend | 3000 → 80 | nginx со статикой React |
| prometheus | 9090 | сбор метрик |
| grafana | 3001 → 3000 | дашборды |

Данные Postgres, Prometheus и Grafana живут в именованных volumes — переживают перезапуск контейнеров.

`entrypoint.sh` у api: `alembic upgrade head` (применить миграции) → `exec uvicorn ...` (запустить сервер).

---

## CI — .github/workflows/ci.yml

Запускается при push в `main` и на каждый Pull Request. Две независимые джобы:

- **backend**: Python 3.13 → `pip install` → `python -m pytest` (именно `python -m`, чтобы пакет `app` попал в `sys.path`). Тесты идут на SQLite, поэтому переменные БД — заглушки, но задать их нужно: `Settings()` требует их при импорте.
- **frontend**: Node 22 → `npm ci` → `npm run lint` → `npm test` → `npm run build` (сборка заодно проверяет типы TypeScript).

---

## Тесты backend

`tests/conftest.py` — SQLite in-memory (`sqlite://` + `StaticPool` — один коннект на все тесты), таблицы создаются перед каждым тестом и удаляются после — каждый тест начинает с чистой БД.

`tests/test_takes.py` — **20 тестов**: CRUD задач, фильтры, валидация (422), статистика, плюс новое — регистрация/вход, доступ без токена (401), изоляция чужих задач (404), запрет удаления/назначения не-создателем (403), назначение исполнителя.

---

## Как запустить

### Через Docker (рекомендуется)

```bash
docker-compose up --build
```

| Что | Где |
|-----|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8001 |
| Swagger-документация | http://localhost:8001/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin/admin) |

### Локально (без Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (в другом терминале)
cd frontend
npm install
npm run dev
```

### Тесты

```bash
cd backend && python -m pytest     # backend
cd frontend && npm test            # frontend
```

---

## Все API-эндпоинты

| Метод | URL | Авторизация | Описание |
|-------|-----|-------------|----------|
| GET | / | нет | health check |
| GET | /metrics | нет | метрики для Prometheus |
| POST | /auth/register | нет | регистрация (201) |
| POST | /auth/login | нет | вход → JWT-токен |
| GET | /auth/me | JWT | текущий пользователь |
| GET | /api/users | JWT | список пользователей (для выбора исполнителя) |
| POST | /api/tasks | JWT | создать задачу (можно сразу с исполнителем) |
| GET | /api/tasks | JWT | список моих задач (?status=&priority=) |
| GET | /api/tasks/stats | JWT | статистика по статусам |
| GET | /api/tasks/{id} | JWT | одна задача |
| PATCH | /api/tasks/{id} | JWT | частичное обновление |
| PATCH | /api/tasks/{id}/assign | JWT, только создатель | назначить исполнителя |
| DELETE | /api/tasks/{id} | JWT, только создатель | удалить (204) |

Все запросы с пометкой JWT требуют заголовок `Authorization: Bearer <token>`.

---

## Что изменилось со старой версии

1. **Монорепозиторий**: код разъехался по `backend/` и `frontend/`.
2. **Авторизация**: JWT-токены, bcrypt-хэши паролей, таблица users.
3. **Командная работа**: у задачи есть создатель, исполнитель и назначивший; права проверяются в сервисе (403/404), видимость — в репозитории.
4. **DI через dishka** вместо ручных `Depends`-фабрик; сервисы зависят от интерфейсов, а не реализаций.
5. **Транзакции**: репозиторий делает `flush`, коммитит сервис (с rollback при ошибке).
6. **Frontend**: React 19 + TypeScript + Vite, свои тесты (vitest) и линтер (oxlint).
7. **Наблюдаемость**: логирование запросов, метрики Prometheus, дашборд Grafana.
8. **CI**: GitHub Actions гоняет тесты и сборку обеих частей.
9. **Деплой**: api и frontend задеплоены на Render (адреса видны в CORS и конфиге Prometheus).
