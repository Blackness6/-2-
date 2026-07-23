from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.providers import AppProvider, DatabaseProvider
from app.routers import auth, projects, tasks, users

from app.core.logging import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware

from app.middleware.metrics_middleware import MetricsMiddleware

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPAuthorizationCredentials

from app.core.config import settings

app = FastAPI(
    title="Task Manager API",
    description="REST API для управления задачами — FastAPI + PostgreSQL",
    version="1.0.0",
)

setup_logging()

app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)


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


container = make_async_container(
    DatabaseProvider(), 
    AppProvider())

setup_dishka(container, app=app)


app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(users.router)

_metrics_basic = HTTPBasic()

def _check_metrics_auth(credentials: HTTPBasicCredentials = Depends(_metrics_basic)) -> None:
    user_ok = secrets.compare_digest(credentials.username, settings.METRICS_USER)
    pass_ok = secrets.compare_digest(credentials.password, settings.METRICS_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "docs": "/docs",
    }

@app.get("/metrics", include_in_schema=False)
def metrics(_: None = Depends(_check_metrics_auth)):
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)