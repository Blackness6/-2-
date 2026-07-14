import { useCallback, useEffect, useState } from "react";
import * as projectApi from "../api/projectApi";
import type { Project, ProjectCreate } from "../types/project";

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setProjects(await projectApi.getProjects());
    } catch {
      setError("Не удалось загрузить проекты");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function createProject(payload: ProjectCreate) {
    try {
      await projectApi.createProject(payload);
      await load();
      return true;
    } catch {
      setError("Не удалось создать проект");
      return false;
    }
  }

  async function removeProject(project: Project) {
    if (!confirm(`Удалить проект "${project.name}"?`)) return;
    try {
      await projectApi.deleteProject(project.id);
      setProjects((prev) => prev.filter((p) => p.id !== project.id));
    } catch {
      setError("Не удалось удалить проект");
    }
  }

  return { projects, loading, error, createProject, removeProject };
}