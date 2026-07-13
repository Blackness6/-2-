import { api } from "./client";
import type { Task, TaskCreate, TaskFilters, TaskStats, TaskUpdate } from "../types/task";

export async function getTasks(filters: TaskFilters) {
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

export async function assignTask(id: number, assigneeId: number | null) {
  const { data } = await api.patch<Task>(`/api/tasks/${id}/assign`, {
    assignee_id: assigneeId,
  });
  return data;
}

export async function deleteTask(id: number) {
  await api.delete(`/api/tasks/${id}`);
}
