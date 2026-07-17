import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../common/Button";
import Input from "../common/Input";
import type { Project, ProjectUpdate } from "../../types/project";

interface ProjectCardProps {
  project: Project;
  onSave: (project: Project, payload: ProjectUpdate) => Promise<boolean>;
  onDelete: (project: Project) => void;
}

export default function ProjectCard({ project, onSave, onDelete }: ProjectCardProps) {
  const navigate = useNavigate();
  const open = () => navigate(`/projects/${project.id}`);

  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [saving, setSaving] = useState(false);

  function startEdit() {
    setEditName(project.name);
    setEditDescription(project.description ?? "");
    setEditing(true);
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!editName.trim()) return;
    setSaving(true);
    const saved = await onSave(project, {
      name: editName.trim(),
      description: editDescription.trim() || null,
    });
    setSaving(false);
    if (saved) setEditing(false);
  }

  if (editing) {
    return (
      <li className="task-card">
        <form className="task-edit-form" onSubmit={handleSave}>
          <Input
            type="text"
            placeholder="Название проекта"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            required
          />
          <Input
            type="text"
            placeholder="Описание (необязательно)"
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
          />
          <div className="task-actions">
            <Button type="submit" variant="primary" disabled={saving}>
              {saving ? "Сохранение..." : "Сохранить"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => setEditing(false)}>
              Отмена
            </Button>
          </div>
        </form>
      </li>
    );
  }

  return (
    <li className="task-card">
      <div className="task-main" style={{ cursor: "pointer" }} onClick={open}>
        <h3>{project.name}</h3>
        {project.description && <p>{project.description}</p>}
        <span className="task-priority">{project.task_count} задач</span>
      </div>
      <div className="task-actions">
        <Button variant="ghost" onClick={open}>
          Открыть
        </Button>
        <Button variant="ghost" onClick={startEdit}>
          Изменить
        </Button>
        <Button variant="danger" onClick={() => onDelete(project)}>
          Удалить
        </Button>
      </div>
    </li>
  );
}
