"""
Тесты для функционала проектов (Projects API).
Используется та же фикстура `client` и SQLite in-memory из conftest.py.
В conftest засеяны два пользователя: alice (id=1) и bob (id=2).
По умолчанию текущий пользователь — alice (id=1).
"""
from fastapi.testclient import TestClient

from app.core.security import get_current_user_id
from app.main import app


# ─── Вспомогательные функции ───────────────────────────────────────────────

def create_project(client: TestClient, name="Test project", description=None):
    payload = {"name": name}
    if description is not None:
        payload["description"] = description
    return client.post("/api/projects", json=payload)


def add_member(client: TestClient, project_id: int, user_id: int, role="member"):
    return client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": user_id, "role": role},
    )


def login_as(user_id: int):
    """Подменяем текущего пользователя (в conftest по умолчанию user_id=1)."""
    app.dependency_overrides[get_current_user_id] = lambda: user_id


# ─── CRUD проектов ─────────────────────────────────────────────────────────

def test_create_project(client):
    """Создание проекта: владельцем становится текущий пользователь."""
    resp = create_project(client, name="Backend", description="API проект")
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Backend"
    assert data["description"] == "API проект"
    assert data["owner_id"] == 1
    assert data["task_count"] == 0
    assert "id" in data
    assert "created_at" in data


def test_get_projects_list(client):
    """Получение списка проектов текущего пользователя."""
    create_project(client, "P1")
    create_project(client, "P2")
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_project_by_id(client):
    """Получение проекта по ID."""
    project_id = create_project(client, "P3").json()["id"]
    resp = client.get(f"/api/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


def test_update_project(client):
    """Владелец может изменить проект."""
    project_id = create_project(client, "Old name").json()["id"]
    resp = client.patch(f"/api/projects/{project_id}", json={"name": "New name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New name"


def test_delete_project(client):
    """Владелец может удалить проект; затем он недоступен (404)."""
    project_id = create_project(client, "To delete").json()["id"]
    resp = client.delete(f"/api/projects/{project_id}")
    assert resp.status_code == 204
    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_get_nonexistent_project(client):
    """Ошибка при получении несуществующего проекта."""
    resp = client.get("/api/projects/99999")
    assert resp.status_code == 404


# ─── Валидация ─────────────────────────────────────────────────────────────

def test_empty_name(client):
    """Пустое имя проекта — 422."""
    resp = client.post("/api/projects", json={"name": ""})
    assert resp.status_code == 422


def test_missing_name(client):
    """Создание без обязательного поля name — 422."""
    resp = client.post("/api/projects", json={"description": "нет имени"})
    assert resp.status_code == 422


# ─── Разграничение доступа ─────────────────────────────────────────────────

def test_stranger_does_not_see_project(client):
    """Посторонний пользователь не видит чужой проект."""
    project_id = create_project(client, "Private").json()["id"]

    login_as(2)
    assert client.get(f"/api/projects/{project_id}").status_code == 404
    assert client.get("/api/projects").json() == []


def test_only_owner_can_update(client):
    """Участник (не владелец) не может изменить проект — 403."""
    project_id = create_project(client, "Owned").json()["id"]
    add_member(client, project_id, user_id=2)

    login_as(2)
    resp = client.patch(f"/api/projects/{project_id}", json={"name": "hacked"})
    assert resp.status_code == 403


def test_only_owner_can_delete(client):
    """Участник (не владелец) не может удалить проект — 403."""
    project_id = create_project(client, "Owned").json()["id"]
    add_member(client, project_id, user_id=2)

    login_as(2)
    resp = client.delete(f"/api/projects/{project_id}")
    assert resp.status_code == 403


# ─── Участники проекта ─────────────────────────────────────────────────────

def test_owner_listed_as_member(client):
    """Владелец присутствует в списке участников с ролью owner."""
    project_id = create_project(client, "Team").json()["id"]
    resp = client.get(f"/api/projects/{project_id}/members")
    assert resp.status_code == 200
    members = resp.json()
    assert len(members) == 1
    assert members[0]["user_id"] == 1
    assert members[0]["role"] == "owner"


def test_add_member(client):
    """Владелец добавляет участника."""
    project_id = create_project(client, "Team").json()["id"]
    resp = add_member(client, project_id, user_id=2, role="member")
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == 2
    assert data["role"] == "member"
    assert data["user"]["username"] == "bob"

    # Теперь в списке владелец + добавленный участник
    members = client.get(f"/api/projects/{project_id}/members").json()
    assert {m["user_id"] for m in members} == {1, 2}


def test_member_sees_project(client):
    """Добавленный участник видит проект в своём списке."""
    project_id = create_project(client, "Shared").json()["id"]
    add_member(client, project_id, user_id=2)

    login_as(2)
    assert client.get(f"/api/projects/{project_id}").status_code == 200
    assert [p["id"] for p in client.get("/api/projects").json()] == [project_id]


def test_add_member_unknown_user(client):
    """Добавление несуществующего пользователя — 404."""
    project_id = create_project(client, "Team").json()["id"]
    resp = add_member(client, project_id, user_id=999)
    assert resp.status_code == 404


def test_add_member_owner_role_forbidden(client):
    """Нельзя выдать роль owner — 400."""
    project_id = create_project(client, "Team").json()["id"]
    resp = add_member(client, project_id, user_id=2, role="owner")
    assert resp.status_code == 400


def test_add_owner_as_member(client):
    """Нельзя добавить владельца участником — 400."""
    project_id = create_project(client, "Team").json()["id"]
    resp = add_member(client, project_id, user_id=1)
    assert resp.status_code == 400


def test_add_duplicate_member(client):
    """Повторное добавление того же участника — 409."""
    project_id = create_project(client, "Team").json()["id"]
    assert add_member(client, project_id, user_id=2).status_code == 201
    resp = add_member(client, project_id, user_id=2)
    assert resp.status_code == 409


def test_only_owner_can_add_member(client):
    """Участник не может добавлять других участников — 403."""
    project_id = create_project(client, "Team").json()["id"]
    add_member(client, project_id, user_id=2)

    login_as(2)
    resp = client.post(
        f"/api/projects/{project_id}/members",
        json={"user_id": 1, "role": "member"},
    )
    assert resp.status_code == 403


def test_remove_member(client):
    """Владелец удаляет участника; тот теряет доступ к проекту."""
    project_id = create_project(client, "Team").json()["id"]
    add_member(client, project_id, user_id=2)

    resp = client.delete(f"/api/projects/{project_id}/members/2")
    assert resp.status_code == 204

    login_as(2)
    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_remove_nonexistent_member(client):
    """Удаление того, кто не участник, — 404."""
    project_id = create_project(client, "Team").json()["id"]
    resp = client.delete(f"/api/projects/{project_id}/members/2")
    assert resp.status_code == 404


# ─── Задачи внутри проекта ─────────────────────────────────────────────────

def test_owner_creates_project_task(client):
    """Владелец создаёт задачу в проекте — у задачи проставлен project_id."""
    project_id = create_project(client, "With tasks").json()["id"]
    resp = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Первая задача", "priority": 2},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Первая задача"
    assert data["project_id"] == project_id


def test_project_task_count(client):
    """task_count в проекте отражает число задач."""
    project_id = create_project(client, "Counting").json()["id"]
    client.post(f"/api/projects/{project_id}/tasks", json={"title": "A", "priority": 1})
    client.post(f"/api/projects/{project_id}/tasks", json={"title": "B", "priority": 1})

    project = next(p for p in client.get("/api/projects").json() if p["id"] == project_id)
    assert project["task_count"] == 2


def test_get_project_tasks(client):
    """Получение списка задач проекта."""
    project_id = create_project(client, "Listing").json()["id"]
    client.post(f"/api/projects/{project_id}/tasks", json={"title": "A", "priority": 1})

    resp = client.get(f"/api/projects/{project_id}/tasks")
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["project_id"] == project_id


def test_manager_can_create_task(client):
    """Участник с ролью manager может создавать задачи."""
    project_id = create_project(client, "Managed").json()["id"]
    add_member(client, project_id, user_id=2, role="manager")

    login_as(2)
    resp = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "От менеджера", "priority": 2},
    )
    assert resp.status_code == 201


def test_plain_member_cannot_create_task(client):
    """Обычный участник (member) не может создавать задачи — 403."""
    project_id = create_project(client, "Restricted").json()["id"]
    add_member(client, project_id, user_id=2, role="member")

    login_as(2)
    resp = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Нельзя", "priority": 2},
    )
    assert resp.status_code == 403


def test_stranger_cannot_view_project_tasks(client):
    """Посторонний не видит задачи чужого проекта — 404."""
    project_id = create_project(client, "Hidden").json()["id"]
    client.post(f"/api/projects/{project_id}/tasks", json={"title": "A", "priority": 1})

    login_as(2)
    assert client.get(f"/api/projects/{project_id}/tasks").status_code == 404
