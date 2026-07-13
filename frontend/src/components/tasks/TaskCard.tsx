import { useState } from "react";
import type { FormEvent } from "react";
import Button from "../common/Button";
import Input from "../common/Input";
import { PRIORITIES, PRIORITY_LABELS, STATUS_LABELS, STATUSES } from "../../constants/taskOptions";
import type { Task, TaskPriority, TaskStatus, TaskUpdate } from "../../types/task";
import type { UserShort } from "../../types/user";

interface TaskCardProps {
  task: Task;
  users: UserShort[];
  canAssign: boolean;
  onStatusChange: (task: Task, status: TaskStatus) => void;
  onAssigneeChange: (task: Task, assigneeId: number | null) => void;
  onSave: (task: Task, payload: TaskUpdate) => Promise<boolean>;
  onDelete: (task: Task) => void;
}

export default function TaskCard({
  task,
  users,
  canAssign,
  onStatusChange,
  onAssigneeChange,
  onSave,
  onDelete,
}: TaskCardProps) {
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editPriority, setEditPriority] = useState<TaskPriority>(2);
  const [saving, setSaving] = useState(false);

  function startEdit() {
    setEditTitle(task.title);
    setEditDescription(task.description ?? "");
    setEditPriority(task.priority);
    setEditing(true);
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!editTitle.trim()) return;
    setSaving(true);
    const saved = await onSave(task, {
      title: editTitle.trim(),
      description: editDescription.trim() || null,
      priority: editPriority,
    });
    setSaving(false);
    if (saved) setEditing(false);
  }

  if (editing) {
    return (
      <li className={`task-card priority-${task.priority}`}>
        <form className="task-edit-form" onSubmit={handleSave}>
          <Input
            type="text"
            placeholder="Название задачи"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            required
          />
          <Input
            type="text"
            placeholder="Описание (необязательно)"
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
          />
          <div className="task-edit-row">
            <select
              value={editPriority}
              onChange={(e) => setEditPriority(Number(e.target.value) as TaskPriority)}
            >
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {PRIORITY_LABELS[p]}
                </option>
              ))}
            </select>
            <div className="task-actions">
              <Button type="submit" variant="primary" disabled={saving}>
                {saving ? "Сохранение..." : "Сохранить"}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setEditing(false)}>
                Отмена
              </Button>
            </div>
          </div>
        </form>
      </li>
    );
  }

  return (
    <li className={`task-card priority-${task.priority}`}>
      <div className="task-main">
        <h3>{task.title}</h3>
        {task.description && <p>{task.description}</p>}
        <span className="task-priority">{PRIORITY_LABELS[task.priority]}</span>
        <span className="task-people">
          Создатель: {task.creator?.username ?? "—"}
          {task.assignee && <> · Исполнитель: {task.assignee.username}</>}
          {task.assignee && task.assigned_by && <> · Назначил: {task.assigned_by.username}</>}
        </span>
      </div>
      <div className="task-actions task-actions-stacked">
        <div className="task-actions-row">
          <select
            value={task.status}
            onChange={(e) => onStatusChange(task, e.target.value as TaskStatus)}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s]}
              </option>
            ))}
          </select>
          {canAssign && (
            <select
              title="Назначить исполнителя"
              value={task.assignee_id ?? ""}
              onChange={(e) =>
                onAssigneeChange(task, e.target.value ? Number(e.target.value) : null)
              }
            >
              <option value="">Без исполнителя</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.username}
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="task-actions-row">
          <Button variant="ghost" onClick={startEdit}>
            Изменить
          </Button>
          <Button variant="danger" onClick={() => onDelete(task)}>
            Удалить
          </Button>
        </div>
      </div>
    </li>
  );
}
