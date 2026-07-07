import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import * as tasksApi from "../api/tasks";
import type { Task, TaskPriority, TaskStats, TaskStatus } from "../api/types";

const STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: "К выполнению",
  IN_PROGRESS: "В работе",
  DONE: "Готово",
  CANCELLED: "Отменено",
};

const PRIORITY_LABELS: Record<TaskPriority, string> = {
  1: "Низкий",
  2: "Средний",
  3: "Высокий",
};

const STATUSES: TaskStatus[] = ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"];

export default function Tasks() {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<TaskStatus | "">("");
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | "">("");

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>(2);
  const [creating, setCreating] = useState(false);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editPriority, setEditPriority] = useState<TaskPriority>(2);
  const [saving, setSaving] = useState(false);

  const filters = useMemo(
    () => ({
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
    }),
    [statusFilter, priorityFilter],
  );

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [taskList, taskStats] = await Promise.all([
        tasksApi.getTasks(filters),
        tasksApi.getStats(),
      ]);
      setTasks(taskList);
      setStats(taskStats);
    } catch {
      setError("Не удалось загрузить задачи");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, priorityFilter]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    try {
      await tasksApi.createTask({
        title: title.trim(),
        description: description.trim() || null,
        priority,
      });
      setTitle("");
      setDescription("");
      setPriority(2);
      await load();
    } catch {
      setError("Не удалось создать задачу");
    } finally {
      setCreating(false);
    }
  }

  async function handleStatusChange(task: Task, status: TaskStatus) {
    setTasks((prev) => prev.map((t) => (t.id === task.id ? { ...t, status } : t)));
    try {
      await tasksApi.updateTask(task.id, { status });
      const taskStats = await tasksApi.getStats();
      setStats(taskStats);
    } catch {
      setError("Не удалось обновить статус");
      load();
    }
  }

  function startEdit(task: Task) {
    setEditingId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description ?? "");
    setEditPriority(task.priority);
  }

  function cancelEdit() {
    setEditingId(null);
  }

  async function handleUpdate(e: FormEvent, task: Task) {
    e.preventDefault();
    if (!editTitle.trim()) return;
    setSaving(true);
    try {
      const updated = await tasksApi.updateTask(task.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || null,
        priority: editPriority,
      });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
      setEditingId(null);
    } catch {
      setError("Не удалось обновить задачу");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(task: Task) {
    if (!confirm(`Удалить задачу "${task.title}"?`)) return;
    try {
      await tasksApi.deleteTask(task.id);
      setTasks((prev) => prev.filter((t) => t.id !== task.id));
      const taskStats = await tasksApi.getStats();
      setStats(taskStats);
    } catch {
      setError("Не удалось удалить задачу");
    }
  }

  return (
    <div className="tasks-page">
      <header className="tasks-header">
        <h1>Мои Задачи:
        </h1>
        <div className="tasks-header-user">
          <span>{user?.username}</span>
          <button className="btn-ghost" onClick={logout}>
            Выйти
          </button>
        </div>
      </header>

      {stats && (
        <div className="stats-bar">
          {STATUSES.map((s) => (
            <div className="stat-pill" key={s}>
              <span className="stat-value">{stats[s]}</span>
              <span className="stat-label">{STATUS_LABELS[s]}</span>
            </div>
          ))}
        </div>
      )}

      {error && <div className="form-error">{error}</div>}

      <form className="task-form" onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="Название задачи"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Описание (необязательно)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <select
          value={priority}
          onChange={(e) => setPriority(Number(e.target.value) as TaskPriority)}
        >
          {([1, 2, 3] as TaskPriority[]).map((p) => (
            <option key={p} value={p}>
              {PRIORITY_LABELS[p]}
            </option>
          ))}
        </select>
        <button type="submit" disabled={creating}>
          {creating ? "Добавление..." : "Добавить"}
        </button>
      </form>

      <div className="filters">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as TaskStatus | "")}
        >
          <option value="">Все статусы</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
        <select
          value={priorityFilter}
          onChange={(e) =>
            setPriorityFilter(e.target.value ? (Number(e.target.value) as TaskPriority) : "")
          }
        >
          <option value="">Все приоритеты</option>
          {([1, 2, 3] as TaskPriority[]).map((p) => (
            <option key={p} value={p}>
              {PRIORITY_LABELS[p]}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="empty-state">Загрузка...</p>
      ) : tasks.length === 0 ? (
        <p className="empty-state">Задач не найдено</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li className={`task-card priority-${task.priority}`} key={task.id}>
              {editingId === task.id ? (
                <form className="task-edit-form" onSubmit={(e) => handleUpdate(e, task)}>
                  <input
                    type="text"
                    placeholder="Название задачи"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Описание (необязательно)"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                  />
                  <select
                    value={editPriority}
                    onChange={(e) => setEditPriority(Number(e.target.value) as TaskPriority)}
                  >
                    {([1, 2, 3] as TaskPriority[]).map((p) => (
                      <option key={p} value={p}>
                        {PRIORITY_LABELS[p]}
                      </option>
                    ))}
                  </select>
                  <div className="task-actions">
                    <button type="submit" disabled={saving}>
                      {saving ? "Сохранение..." : "Сохранить"}
                    </button>
                    <button type="button" className="btn-ghost" onClick={cancelEdit}>
                      Отмена
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <div className="task-main">
                    <h3>{task.title}</h3>
                    {task.description && <p>{task.description}</p>}
                    <span className="task-priority">{PRIORITY_LABELS[task.priority]}</span>
                  </div>
                  <div className="task-actions">
                    <select
                      value={task.status}
                      onChange={(e) => handleStatusChange(task, e.target.value as TaskStatus)}
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {STATUS_LABELS[s]}
                        </option>
                      ))}
                    </select>
                    <button onClick={() => startEdit(task)}>Изменить</button>
                    <button className="btn-danger" onClick={() => handleDelete(task)}>
                      Удалить
                    </button>
                  </div>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
