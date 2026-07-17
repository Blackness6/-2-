# Task Manager — Полное объяснение проекта

## Что это такое

Fullstack-приложение для управления задачами — как упрощённый Trello с командной работой.
Проект состоит из четырёх частей:

- **Backend** — REST API на Python (FastAPI) + PostgreSQL
- **Frontend** — SPA на React + TypeScript (Vite)
- **Мониторинг** — Prometheus + Grafana
- **CI** — GitHub Actions (тесты и сборка при каждом push/PR)

Есть регистрация и вход (JWT). Задачи привязаны к пользователям: у задачи есть **создатель**, **исполнитель** и тот, кто исполнителя **назначил**.

Главное в текущей версии — **проекты**: задачи можно группировать по проектам, у проекта есть **владелец** и **участники** с ролями (`owner` / `manager` / `member`). Роль определяет, что участнику разрешено делать внутри проекта.

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
Сервисы зависят не от конкретных репозиториев, а от **интерфейсов** (`ITaskRepository`, `IUserRepository`, `IProjectRepository`) — это упрощает тестирование и подмену реализации.

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
│   │   ├── models.py            ← таблицы users, projects, tasks, project_members
│   │   ├── schemas.py           ← Pydantic-схемы запросов/ответов
│   │   ├── providers.py         ← DI-контейнер dishka
│   │   ├── core/
│   │   │   ├── config.py        ← настройки из .env
│   │   │   ├── security.py      ← bcrypt, JWT, get_current_user_id
│   │   │   ├── time.py          ← utcnow() — единое UTC-время для всего приложения
│   │   │   └── logging.py       ← настройка логов
│   │   ├── middleware/
│   │   │   ├── logging_middleware.py  ← лог каждого запроса
│   │   │   └── metrics_middleware.py  ← метрики Prometheus
│   │   ├── observability/
│   │   │   └── metrics.py       ← определения метрик (Counter, Histogram, Gauge)
│   │   ├── interfaces/
│   │   │   ├── task_repository.py     ← ITaskRepository (абстрактный класс)
│   │   │   ├── user_repository.py     ← IUserRepository
│   │   │   └── project_repository.py  ← IProjectRepository
│   │   ├── routers/
│   │   │   ├── auth.py          ← /auth/register, /auth/login, /auth/me
│   │   │   ├── tasks.py         ← CRUD задач + /assign + /stats
│   │   │   ├── projects.py      ← CRUD проектов + задачи проекта + участники
│   │   │   └── users.py         ← список пользователей (для выбора исполнителя)
│   │   ├── services/
│   │   │   ├── auth_service.py  ← регистрация, вход, выдача токена
│   │   │   ├── task_service.py  ← бизнес-логика задач
│   │   │   └── project_service.py ← бизнес-логика проектов, роли и права
│   │   └── repositories/
│   │       ├── task_repository.py
│   │       ├── user_repository.py
│   │       └── project_repository.py
│   │
│   ├── migrations/versions/     ← 6 миграций Alembic:
│   │   ├── d97b81ffd2be_initial.py                ← таблица tasks
│   │   ├── 4d13fc3f415d_add_users_table.py        ← таблица users
│   │   ├── a1b2c3d4e5f6_add_user_id_to_tasks.py   ← связь задач с пользователями
│   │   ├── b7e2f8a9c1d3_task_assignment_fields.py ← поля назначения
│   │   ├── c8f3a1b6d4e2_add_projects.py           ← таблица projects + tasks.project_id
│   │   └── d1e2f3a4b5c6_add_project_members.py    ← таблица project_members
│   │
│   └── tests/
│       ├── conftest.py          ← тестовая БД (SQLite in-memory)
│       ├── test_takes.py        ← 22 теста: задачи
│       ├── test_auth.py         ← 11 тестов: регистрация, вход, токены
│       └── test_projects.py     ← 27 тестов: проекты, участники, роли
│
├── frontend/
│   ├── Dockerfile               ← сборка Vite → раздача через nginx
│   ├── package.json             ← react 19, axios, react-router, vitest
│   └── src/
│       ├── main.tsx / App.tsx   ← точка входа
│       ├── api/                 ← client.ts (axios + токен), authApi, taskApi, projectApi, userApi
│       ├── types/               ← auth.ts, project.ts, task.ts, user.ts
│       ├── context/AuthContext.tsx ← хранение токена, состояние «вошёл/не вошёл»
│       ├── hooks/               ← useAuth, useProjects, useProjectTasks, useTasks
│       ├── components/
│       │   ├── common/          ← Button, Input, Loader, ErrorMessage
│       │   ├── projects/        ← ProjectCard, ProjectForm
│       │   └── tasks/           ← TaskCard, TaskForm, TaskFilters, TaskList
│       ├── pages/               ← Login/, Register/, Projects/ (список + ProjectDetails), Tasks/
│       └── routes/              ← AppRoutes (маршруты), ProtectedRoute (только для вошедших)
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

### app/models.py — четыре таблицы

**User** — пользователь:

| Поле | Тип | Описание |
|------|-----|----------|
| id | int (BigInteger в PG) | первичный ключ |
| username | str(100), unique | имя пользователя |
| email | str(255), unique | почта (логин) |
| hashed_password | str(255) | bcrypt-хэш, пароль в открытом виде не хранится |
| role | str(20), default "user" | роль (задел на будущее) |
| created_at | datetime | когда зарегистрировался |

**Project** — проект:

| Поле | Тип | Описание |
|------|-----|----------|
| id | int (BigInteger в PG) | первичный ключ |
| name | str(255) | название |
| description | text, nullable | описание |
| owner_id | FK → users.id, CASCADE | владелец; при удалении пользователя его проекты удаляются |
| created_at, updated_at | datetime | временные метки |

**Task** — задача:

| Поле | Тип | Описание |
|------|-----|----------|
| id, title, description, status, priority | — | status: TODO/IN_PROGRESS/DONE/CANCELLED, priority: 1–3 |
| creator_id | FK → users.id, CASCADE | кто создал; при удалении пользователя его задачи удаляются |
| assignee_id | FK → users.id, SET NULL | кто выполняет; при удалении пользователя поле обнуляется |
| assigned_by_id | FK → users.id, SET NULL | кто назначил текущего исполнителя |
| project_id | FK → projects.id, SET NULL | проект задачи (опционально); при удалении проекта задача остаётся |
| created_at, updated_at | datetime | временные метки |

**ProjectMember** — участник проекта:

| Поле | Тип | Описание |
|------|-----|----------|
| id | int (BigInteger в PG) | первичный ключ |
| project_id | FK → projects.id, CASCADE | проект |
| user_id | FK → users.id, CASCADE | пользователь |
| role | str(20), default "member" | роль в проекте: manager или member |
| created_at | datetime | когда добавлен |

На пару `(project_id, user_id)` стоит **UniqueConstraint** — один пользователь не может быть участником проекта дважды. Владелец в этой таблице **не хранится** — он определяется по `projects.owner_id`.

Плюс `relationship` в обе стороны (`creator`, `assignee`, `assigned_by`, `project`, `members`, `owner`) — чтобы API отдавал не только id, но и имена пользователей.

Все временные метки ставятся через `app/core/time.py::utcnow()` — текущее UTC-время без tzinfo (совместимо и с PostgreSQL, и с SQLite в тестах).

### app/schemas.py — формат данных

```python
class TaskStatus(str, Enum): ...        # TODO / IN_PROGRESS / DONE / CANCELLED
class TaskPriorityEnum(int, Enum): ...  # LOW=1, MEDIUM=2, HIGH=3

class UserCreate(BaseModel):            # регистрация
    username: str   # 3–100 символов
    email: EmailStr # pydantic сам проверяет формат почты
    password: str   # минимум 8 символов

class TaskCreate(BaseModel):
    ...
    assignee_id: int | None = None      # можно сразу назначить исполнителя

class TaskAssign(BaseModel):            # отдельная схема для /assign
    assignee_id: int | None = None      # null означает «снять исполнителя»

class TaskResponse(BaseModel):
    ...
    project_id: int | None              # к какому проекту относится задача
    creator: UserShortResponse          # вложенные объекты пользователей —
    assigned_by: UserShortResponse | None  # frontend показывает имена,
    assignee: UserShortResponse | None     # а не голые id

class ProjectCreate(BaseModel):         # создание проекта
    name: str        # 1–255 символов
    description: str | None = None

class ProjectResponse(BaseModel):
    id, name, description, owner_id
    task_count: int = 0                 # количество задач (считается в репозитории)
    created_at, updated_at

class ProjectRole(str, Enum):           # роли в проекте
    OWNER = "owner"; MANAGER = "manager"; MEMBER = "member"

class ProjectMemberCreate(BaseModel):   # добавление участника
    user_id: int
    role: ProjectRole = ProjectRole.MEMBER

class ProjectMemberResponse(BaseModel):
    project_id, user_id, role
    user: UserShortResponse             # имя участника для отображения

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

Зависимости собирает DI-контейнер **dishka**:

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
    # ... то же для UserRepository, ProjectRepository,
    #     TaskService, AuthService, ProjectService
```

В роутере пишем `service: FromDishka[TaskService]` (и `route_class=DishkaRoute` у роутера) — контейнер сам строит цепочку: сессия → репозитории → сервис.

### app/repositories/ — работа с БД

**task_repository.py**:

```python
def _visible_to(user_id):
    # Пользователь видит задачу, только если он её создатель ИЛИ исполнитель.
    return or_(Task.creator_id == user_id, Task.assignee_id == user_id)

def _with_users(stmt):
    # selectinload — жадная подгрузка creator/assigned_by/assignee одним
    # дополнительным запросом (иначе N+1 запросов при сериализации ответа).
    return stmt.options(selectinload(Task.creator), ...)
```

Все методы чтения (`get_by_id`, `get_all`, `get_stats`) фильтруют по `_visible_to(user_id)` — чужие задачи не видны вообще. Отдельный метод `get_by_project(project_id)` возвращает **все** задачи проекта — доступ к нему проверяет сервис проектов (только для участников).

**project_repository.py**:

```python
def _member_exists(self, user_id):
    # Коррелированный EXISTS: текущий пользователь — участник проекта.
    return select(ProjectMember.id).where(
        ProjectMember.project_id == Project.id,
        ProjectMember.user_id == user_id,
    ).exists()
```

`get_by_id` и `get_all` пускают к проекту **владельца ИЛИ участника** — чужие проекты не видны. `get_all` заодно считает `task_count` через `outerjoin` + `group_by` (одним запросом, без N+1).

Важно: репозитории делают **`flush()` вместо `commit()`**. Flush отправляет SQL в БД (и получает id), но не завершает транзакцию — коммитит сервис. Так несколько операций объединяются в одну атомарную транзакцию.

### app/services/task_service.py — бизнес-логика задач

```python
def create_task(self, data, user_id, project_id=None):
    # Если при создании указан исполнитель — проверяем, что он существует,
    # и записываем, кто назначил (текущий пользователь из JWT).
    # project_id приходит из роутера проектов (POST /api/projects/{id}/tasks).
    ...
    try:
        task = self.repo.create(task)   # flush
        self.db.commit()                # транзакция завершается здесь
    except Exception:
        self.db.rollback()              # при ошибке — откат, БД не портится
        raise
```

Правила доступа к задачам:

- **видеть/редактировать** задачу может создатель и исполнитель;
- **назначать, переназначать и снимать исполнителя** (`PATCH /{id}/assign`) может только создатель → иначе 403; `assignee_id: null` снимает исполнителя (вместе с ним обнуляется и «кто назначил»);
- **удалять** может только создатель → иначе 403;
- чужая задача выглядит как несуществующая → 404 (не раскрываем, что она есть).

### app/services/project_service.py — проекты, роли и права

Роль пользователя в проекте вычисляется так: владелец (`projects.owner_id`) → `owner`, иначе смотрим запись в `project_members` → `manager` / `member`, иначе доступа нет.

Правила доступа к проектам:

| Действие | Кому разрешено |
|----------|----------------|
| видеть проект, его задачи и участников | владелец и любой участник |
| изменять / удалять проект | только владелец → иначе 403 |
| добавлять / удалять участников | только владелец → иначе 403 |
| создавать задачи в проекте | владелец и `manager` → иначе 403 (`ensure_can_manage_tasks`) |
| чужой проект | выглядит как несуществующий → 404 |

Нюансы `add_member`: нельзя выдать роль `owner` (400), нельзя добавить самого владельца (400), несуществующего пользователя (404) или уже добавленного участника (409 Conflict).

`list_members` возвращает участников **плюс синтетическую запись владельца** с ролью `owner` (в таблице он не хранится) — frontend показывает полный состав команды одним списком.

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

app.include_router(tasks.router)        # + projects, auth, users
app.include_router(projects.router)

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

React 19 + TypeScript + Vite. Запросы через axios, роутинг через react-router-dom. Код разложен по слоям:

- **api/** — `client.ts` (axios-клиент: подставляет `VITE_API_URL` и токен в заголовок) + функции запросов по доменам: `authApi.ts`, `taskApi.ts`, `projectApi.ts`, `userApi.ts`;
- **types/** — TypeScript-типы по доменам: `auth.ts`, `project.ts`, `task.ts`, `user.ts`;
- **context/AuthContext.tsx** — React-контекст: хранит JWT-токен, знает, вошёл ли пользователь, отдаёт login/logout всему приложению; хук `useAuth` — короткий доступ к контексту;
- **hooks/** — логика страниц вынесена в хуки: `useProjects` (список проектов), `useProjectTasks` (задачи проекта), `useTasks` (общий список задач с фильтрами);
- **components/** — переиспользуемые блоки: `common/` (Button, Input, Loader, ErrorMessage), `projects/` (ProjectCard, ProjectForm), `tasks/` (TaskCard, TaskForm, TaskFilters, TaskList);
- **pages/** — `Login`, `Register`, `Projects` (список проектов), `ProjectDetails` (задачи и участники проекта), `Tasks` (общий список всех моих задач);
- **routes/** — `AppRoutes` (маршруты) и `ProtectedRoute` (пускает только вошедших, иначе редирект на /login).

Маршруты: после входа пользователь попадает на `/projects` (главная страница), оттуда — в конкретный проект `/projects/:projectId`; `/tasks` — общий список всех задач пользователя.

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

Всего **60 тестов** в трёх файлах:

- `test_takes.py` — **22 теста**: CRUD задач, фильтры, валидация (422), статистика, изоляция чужих задач (404), запрет удаления/назначения не-создателем (403), назначение исполнителя;
- `test_auth.py` — **11 тестов**: регистрация (в т.ч. дубликат email, короткий пароль, невалидная почта), вход (неверный пароль, неизвестный email), `/auth/me`, доступ без токена и с невалидным токеном (401);
- `test_projects.py` — **27 тестов**: CRUD проектов, невидимость чужих проектов, права владельца (403 для остальных), участники (добавление, дубликат → 409, запрет роли owner → 400, удаление), роли в задачах проекта (владелец/менеджер создают, обычный участник — нет), `task_count`.

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
| PATCH | /api/tasks/{id}/assign | JWT, только создатель | назначить/переназначить исполнителя; `assignee_id: null` — снять |
| DELETE | /api/tasks/{id} | JWT, только создатель | удалить (204) |
| POST | /api/projects | JWT | создать проект (201) |
| GET | /api/projects | JWT | мои проекты (владелец или участник) + task_count |
| GET | /api/projects/{id} | JWT, участник | один проект |
| PATCH | /api/projects/{id} | JWT, только владелец | изменить проект |
| DELETE | /api/projects/{id} | JWT, только владелец | удалить проект (204) |
| GET | /api/projects/{id}/tasks | JWT, участник | задачи проекта |
| POST | /api/projects/{id}/tasks | JWT, владелец/менеджер | создать задачу в проекте (201) |
| GET | /api/projects/{id}/members | JWT, участник | участники проекта (включая владельца) |
| POST | /api/projects/{id}/members | JWT, только владелец | добавить участника (201) |
| DELETE | /api/projects/{id}/members/{user_id} | JWT, только владелец | убрать участника (204) |

Все запросы с пометкой JWT требуют заголовок `Authorization: Bearer <token>`.

---

## Что изменилось со старой версии

1. **Проекты**: таблицы `projects` и `project_members`, задачи привязываются к проектам (`tasks.project_id`), роли участников (`owner` / `manager` / `member`), права проверяются в `ProjectService`; на frontend — страницы Projects и ProjectDetails, после входа пользователь попадает сразу в проекты.
2. **Монорепозиторий**: код разъехался по `backend/` и `frontend/`.
3. **Авторизация**: JWT-токены, bcrypt-хэши паролей, таблица users.
4. **Командная работа**: у задачи есть создатель, исполнитель и назначивший; права проверяются в сервисе (403/404), видимость — в репозитории; исполнителя можно снять (`assignee_id: null`).
5. **DI через dishka** вместо ручных `Depends`-фабрик; сервисы зависят от интерфейсов, а не реализаций.
6. **Транзакции**: репозиторий делает `flush`, коммитит сервис (с rollback при ошибке).
7. **Frontend переструктурирован**: слои api/types/context/hooks/components/pages/routes, переиспользуемые компоненты, логика страниц в хуках; тесты (vitest) и линтер (oxlint).
8. **Наблюдаемость**: логирование запросов, метрики Prometheus, дашборд Grafana.
9. **CI**: GitHub Actions гоняет тесты и сборку обеих частей.
10. **Деплой**: api и frontend задеплоены на Render (адреса видны в CORS и конфиге Prometheus).
11. **Тесты backend разбиты по доменам**: `test_takes.py` (задачи), `test_auth.py` (авторизация), `test_projects.py` (проекты) — всего 60 тестов.
