import { useState } from "react";
import type { FormEvent } from "react";
import Button from "../common/Button";
import Input from "../common/Input";
import type { ProjectCreate } from "../../types/project";

interface ProjectFormProps {
  onCreate: (payload: ProjectCreate) => Promise<boolean>;
}

export default function ProjectForm({ onCreate }: ProjectFormProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    const ok = await onCreate({
      name: name.trim(),
      description: description.trim() || null,
    });
    setCreating(false);
    if (ok) {
      setName("");
      setDescription("");
    }
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <Input
        type="text"
        placeholder="Название проекта"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <Input
        type="text"
        placeholder="Описание (необязательно)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <Button type="submit" disabled={creating}>
        {creating ? "Создание..." : "Создать проект"}
      </Button>
    </form>
  );
}
