from fastapi import FastAPI

from app.routers.tasks import router as tasks_router


app = FastAPI(
    title="Task Manager API",
    description="REST API для управления задачами — FastAPI + PostgreSQL",
    version="1.0.0",
)

app.include_router(tasks_router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "docs": "/docs"}