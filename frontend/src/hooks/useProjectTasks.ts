import { useCallback, useEffect, useState } from "react";
import * as taskApi from "../api/taskApi";
import type { Task, TaskCreate, TaskStatus, TaskUpdate } from "../types/task";

export function useProjectTasks(projectId: number) {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            setTasks(await taskApi.getProjectTasks(projectId));
        } catch {
            setError("Не удалось загрузить задачи");
        } finally {
            setLoading(false);
        }
    }, [projectId]);

    useEffect(() => { load(); }, [load]);

  const replaceTask = (u: Task) =>
    setTasks((prev) => prev.map((t) => (t.id === u.id ? u : t)));

  async function createTask(payload: TaskCreate) {
    try {
      await taskApi.createProjectTask(projectId, payload);
      await load();
      return true;
    } catch {
      setError("Не удалось создать задачу");
      return false;
    }
  }

  async function changeStatus(task: Task, status: TaskStatus) {
    try { replaceTask(await taskApi.updateTask(task.id, { status })); }
    catch { setError("Не удалось обновить статус"); }
  }

  async function saveTask(task: Task, payload: TaskUpdate) {
    try { replaceTask(await taskApi.updateTask(task.id, payload)); return true; }
    catch { setError("Не удалось обновить задачу"); return false; }
  }

  async function changeAssignee(task: Task, assigneeId: number | null) {
    try { replaceTask(await taskApi.assignTask(task.id, assigneeId)); }
    catch { setError("Не удалось изменить исполнителя"); }
  }

  async function removeTask(task: Task) {
    if (!confirm(`Удалить задачу "${task.title}"?`)) return;
    try {
      await taskApi.deleteTask(task.id);
      setTasks((prev) => prev.filter((t) => t.id !== task.id));
    } catch { setError("Не удалось удалить задачу"); }
  }

  return { tasks, loading, error, createTask, changeStatus, saveTask, changeAssignee, removeTask };
}