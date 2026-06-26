"""
Тесты для Task Manager API.
Используется SQLite in-memory через conftest.py.
"""
import pytest
from fastapi.testclient import TestClient


# ─── Вспомогательная функция ───────────────────────────────────────────────

def create_task(client: TestClient, title="Test task", priority=2, description=None):
    payload = {"title": title, "priority": priority}
    if description:
        payload["description"] = description
    return client.post("/api/tasks", json=payload)


# ─── Обязательные тесты (7 штук) ───────────────────────────────────────────

def test_create_task(client):
    """1. Создание задачи."""
    resp = create_task(client, title="Реализовать API", priority=3)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Реализовать API"
    assert data["status"] == "TODO"
    assert data["priority"] == 3
    assert "id" in data
    assert "created_at" in data


def test_get_tasks_list(client):
    """2. Получение списка задач."""
    create_task(client, "Task A")
    create_task(client, "Task B")
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_task_by_id(client):
    """3. Получение задачи по ID."""
    task_id = create_task(client, "Task C").json()["id"]
    resp = client.get(f"/api/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


def test_update_status(client):
    """4. Обновление статуса задачи."""
    task_id = create_task(client).json()["id"]
    resp = client.patch(f"/api/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"


def test_update_priority(client):
    """5. Обновление приоритета задачи."""
    task_id = create_task(client, priority=1).json()["id"]
    resp = client.patch(f"/api/tasks/{task_id}", json={"priority": 3})
    assert resp.status_code == 200
    assert resp.json()["priority"] == 3


def test_delete_task(client):
    """6. Удаление задачи."""
    task_id = create_task(client).json()["id"]
    resp = client.delete(f"/api/tasks/{task_id}")
    assert resp.status_code == 204
    # После удаления — 404
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_get_nonexistent_task(client):
    """7. Ошибка при получении несуществующей задачи."""
    resp = client.get("/api/tasks/99999")
    assert resp.status_code == 404


# ─── Дополнительные тесты (Junior+) ────────────────────────────────────────

def test_filter_by_status(client):
    """Фильтрация по статусу."""
    task_id = create_task(client, "T1").json()["id"]
    create_task(client, "T2")
    client.patch(f"/api/tasks/{task_id}", json={"status": "DONE"})

    resp = client.get("/api/tasks?status=DONE")
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "DONE"


def test_filter_by_priority(client):
    """Фильтрация по приоритету."""
    create_task(client, "Low", priority=1)
    create_task(client, "High", priority=3)

    resp = client.get("/api/tasks?priority=1")
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["priority"] == 1 for t in tasks)


def test_invalid_status(client):
    """Неправильный статус — 422 Unprocessable Entity."""
    task_id = create_task(client).json()["id"]
    resp = client.patch(f"/api/tasks/{task_id}", json={"status": "FLYING"})
    assert resp.status_code == 422


def test_empty_title(client):
    """Пустой title — 422."""
    resp = client.post("/api/tasks", json={"title": "", "priority": 2})
    assert resp.status_code == 422


def test_missing_required_fields(client):
    """Создание без обязательного поля title — 422."""
    resp = client.post("/api/tasks", json={"priority": 2})
    assert resp.status_code == 422


def test_stats_endpoint(client):
    """Endpoint статистики с GROUP BY."""
    create_task(client, "T1")
    create_task(client, "T2")
    t3_id = create_task(client, "T3").json()["id"]
    client.patch(f"/api/tasks/{t3_id}", json={"status": "DONE"})

    resp = client.get("/api/tasks/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["TODO"] == 2
    assert stats["DONE"] == 1
    assert stats["IN_PROGRESS"] == 0
