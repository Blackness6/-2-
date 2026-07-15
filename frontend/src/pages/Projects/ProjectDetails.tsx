import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useProjectTasks } from "../../hooks/useProjectTasks";
import * as projectApi from "../../api/projectApi";
import * as userApi from "../../api/userApi";
import Button from "../../components/common/Button";
import ErrorMessage from "../../components/common/ErrorMessage";
import Loader from "../../components/common/Loader";
import TaskForm from "../../components/tasks/TaskForm";
import TaskList from "../../components/tasks/TaskList";
import type { Project, ProjectMember, ProjectRole } from "../../types/project";
import type { UserShort } from "../../types/user";
import "../Tasks/TasksPage.css";

export default function ProjectDetails() {
  const { projectId } = useParams();
  const id = Number(projectId);
  const { user } = useAuth();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [users, setUsers] = useState<UserShort[]>([]);
  const [members, setMembers] = useState<ProjectMember[]>([]);

  // форма добавления участника
  const [newUserId, setNewUserId] = useState<number | "">("");
  const [newRole, setNewRole] = useState<ProjectRole>("member");
  const [memberError, setMemberError] = useState<string | null>(null);

  const { tasks, loading, error, createTask, changeStatus, saveTask, changeAssignee, removeTask } =
    useProjectTasks(id);

  const loadMembers = useCallback(() => {
    projectApi.getMembers(id).then(setMembers).catch(() => setMembers([]));
  }, [id]);

  useEffect(() => {
    projectApi.getProject(id).then(setProject).catch(() => setProject(null));
    userApi.getUsers().then(setUsers).catch(() => setUsers([]));
    loadMembers();
  }, [id, loadMembers]);

  // роль текущего пользователя в проекте (в списке участников есть и владелец)
  const myRole = members.find((m) => m.user_id === user?.id)?.role;
  const isOwner = myRole === "owner";
  const canManage = myRole === "owner" || myRole === "manager";

  // пользователи, которых ещё нет в проекте
  const memberIds = new Set(members.map((m) => m.user_id));
  const availableUsers = users.filter((u) => !memberIds.has(u.id));

  async function handleAddMember(e: FormEvent) {
    e.preventDefault();
    if (newUserId === "") return;
    setMemberError(null);
    try {
      await projectApi.addMember(id, { user_id: Number(newUserId), role: newRole });
      setNewUserId("");
      setNewRole("member");
      loadMembers();
    } catch {
      setMemberError("Не удалось добавить участника");
    }
  }

  async function handleRemoveMember(m: ProjectMember) {
    if (!confirm(`Удалить участника ${m.user.username}?`)) return;
    setMemberError(null);
    try {
      await projectApi.removeMember(id, m.user_id);
      loadMembers();
    } catch {
      setMemberError("Не удалось удалить участника");
    }
  }

  return (
    <div className="tasks-page">
      <header className="tasks-header">
        <div>
          <Button variant="ghost" onClick={() => navigate("/projects")}>← К проектам</Button>
          <h1>{project?.name ?? "Проект"}</h1>
        </div>
        <div className="tasks-header-user"><span>{user?.username}</span></div>
      </header>

      {/* --- Участники проекта --- */}
      <section className="project-members">
        <h2>Участники</h2>
        <ul className="members-list">
          {members.map((m) => (
            <li key={m.user_id}>
              <span>{m.user.username} — <b>{m.role}</b></span>
              {isOwner && m.role !== "owner" && (
                <Button variant="danger" onClick={() => handleRemoveMember(m)}>удалить</Button>
              )}
            </li>
          ))}
        </ul>

        {isOwner && (
          <form onSubmit={handleAddMember} className="task-form">
            <select
              value={newUserId}
              onChange={(e) => setNewUserId(e.target.value ? Number(e.target.value) : "")}
            >
              <option value="">— выберите пользователя —</option>
              {availableUsers.map((u) => (
                <option key={u.id} value={u.id}>{u.username}</option>
              ))}
            </select>
            <select value={newRole} onChange={(e) => setNewRole(e.target.value as ProjectRole)}>
              <option value="member">member</option>
              <option value="manager">manager</option>
            </select>
            <Button type="submit" disabled={newUserId === ""}>Добавить</Button>
          </form>
        )}
        <ErrorMessage message={memberError} />
      </section>

      <ErrorMessage message={error} />

      {/* Создавать задачи могут владелец и менеджер */}
      {canManage && <TaskForm users={users} onCreate={createTask} />}

      {loading ? <Loader /> : (
        <TaskList
          tasks={tasks}
          users={users}
          currentUserId={user?.id}
          onStatusChange={changeStatus}
          onAssigneeChange={changeAssignee}
          onSave={saveTask}
          onDelete={removeTask}
        />
      )}
    </div>
  );
}
