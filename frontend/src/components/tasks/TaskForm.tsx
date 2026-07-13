import { useState } from "react";
import type { FormEvent } from "react";
import Button from "../common/Button";
import Input from "../common/Input";
import { PRIORITIES, PRIORITY_LABELS } from "../../constants/taskOptions";
import type { TaskCreate, TaskPriority } from "../../types/task";
import type { UserShort } from "../../types/user";

interface TaskFormProps {
  users: UserShort[];
  onCreate: (payload: TaskCreate) => Promise<boolean>;
}

export default function TaskForm({ users, onCreate }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>(2);
  const [assigneeId, setAssigneeId] = useState<number | "">("");
  const [creating, setCreating] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    const created = await onCreate({
      title: title.trim(),
      description: description.trim() || null,
      priority,
      assignee_id: assigneeId || null,
    });
    setCreating(false);
    if (created) {
      setTitle("");
      setDescription("");
      setPriority(2);
      setAssigneeId("");
    }
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <Input
        type="text"
        placeholder="Название задачи"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <Input
        type="text"
        placeholder="Описание (необязательно)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <select
        value={priority}
        onChange={(e) => setPriority(Number(e.target.value) as TaskPriority)}
      >
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {PRIORITY_LABELS[p]}
          </option>
        ))}
      </select>
      <select
        value={assigneeId}
        onChange={(e) => setAssigneeId(e.target.value ? Number(e.target.value) : "")}
      >
        <option value="">Без исполнителя</option>
        {users.map((u) => (
          <option key={u.id} value={u.id}>
            {u.username}
          </option>
        ))}
      </select>
      <Button type="submit" disabled={creating}>
        {creating ? "Добавление..." : "Добавить"}
      </Button>
    </form>
  );
}
