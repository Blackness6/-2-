from fastapi import FastAPI

from app.routers import auth, tasks

app = FastAPI(
    title="Task Manager API",
    description="REST API для управления задачами — FastAPI + PostgreSQL",
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "docs": "/docs",
    }


# Подключение роутеров
app.include_router(tasks.router)
app.include_router(auth.router)