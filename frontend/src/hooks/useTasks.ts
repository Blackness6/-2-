import { useCallback, useEffect, useState } from "react";
import * as taskApi from "../api/taskApi";
import type { Task, TaskCreate, TaskPriority, TaskStats, TaskStatus, TaskUpdate } from "../types/task";

export function useTasks(statusFilter: TaskStatus | "", priorityFilter: TaskPriority | "") {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [taskList, taskStats] = await Promise.all([
        taskApi.getTasks({
          status: statusFilter || undefined,
          priority: priorityFilter || undefined,
        }),
        taskApi.getStats(),
      ]);
      setTasks(taskList);
      setStats(taskStats);
    } catch {
      setError("Не удалось загрузить задачи");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  useEffect(() => {
    load();
  }, [load]);

  function replaceTask(updated: Task) {
    setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
  }

  async function createTask(payload: TaskCreate) {
    try {
      await taskApi.createTask(payload);
      await load();
      return true;
    } catch {
      setError("Не удалось создать задачу");
      return false;
    }
  }

  async function changeStatus(task: Task, status: TaskStatus) {
    setTasks((prev) => prev.map((t) => (t.id === task.id ? { ...t, status } : t)));
    try {
      await taskApi.updateTask(task.id, { status });
      setStats(await taskApi.getStats());
    } catch {
      setError("Не удалось обновить статус");
      load();
    }
  }

  async function saveTask(task: Task, payload: TaskUpdate) {
    try {
      replaceTask(await taskApi.updateTask(task.id, payload));
      return true;
    } catch {
      setError("Не удалось обновить задачу");
      return false;
    }
  }

  async function changeAssignee(task: Task, assigneeId: number | null) {
    try {
      replaceTask(await taskApi.assignTask(task.id, assigneeId));
    } catch {
      setError("Не удалось изменить исполнителя");
    }
  }

  async function removeTask(task: Task) {
    if (!confirm(`Удалить задачу "${task.title}"?`)) return;
    try {
      await taskApi.deleteTask(task.id);
      setTasks((prev) => prev.filter((t) => t.id !== task.id));
      setStats(await taskApi.getStats());
    } catch {
      setError("Не удалось удалить задачу");
    }
  }

  return {
    tasks,
    stats,
    loading,
    error,
    createTask,
    changeStatus,
    saveTask,
    changeAssignee,
    removeTask,
  };
}
