from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.providers import AppProvider, DatabaseProvider
from app.routers import auth, tasks

from app.core.logging import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware

app = FastAPI(
    title="Task Manager API",
    description="REST API для управления задачами — FastAPI + PostgreSQL",
    version="1.0.0",
)

setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend-928y.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

container = make_async_container(DatabaseProvider(), AppProvider())
setup_dishka(container, app=app)

app.include_router(tasks.router)
app.include_router(auth.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "docs": "/docs",
    }

app.add_middleware(LoggingMiddleware)

app.add_middleware(CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)