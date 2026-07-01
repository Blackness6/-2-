import { api } from "./api";
import type { Task, TaskCreate, TaskUpdate, TaskStats, TaskStatus } from "./types";

export async function getTasks(filters: { status?: TaskStatus; priority?: number }) {
  const { data } = await api.get<Task[]>("/api/tasks", { params: filters });
  return data;
}

export async function getStats() {
  const { data } = await api.get<TaskStats>("/api/tasks/stats");
  return data;
}

export async function createTask(payload: TaskCreate) {
  const { data } = await api.post<Task>("/api/tasks", payload);
  return data;
}

export async function updateTask(id: number, payload: TaskUpdate) {
  const { data } = await api.patch<Task>(`/api/tasks/${id}`, payload);
  return data;
}

export async function deleteTask(id: number) {
  await api.delete(`/api/tasks/${id}`);
}
