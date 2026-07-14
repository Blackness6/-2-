import { api } from "./client";
import type { Project, ProjectCreate, ProjectUpdate } from "../types/project";

export async function getProjects() {
  const { data } = await api.get<Project[]>("/api/projects");
  return data;
}

export async function getProject(id: number) {
  const { data } = await api.get<Project>(`/api/projects/${id}`);
  return data;
}

export async function createProject(payload: ProjectCreate) {
  const { data } = await api.post<Project>("/api/projects", payload);
  return data;
}

export async function updateProject(id: number, payload: ProjectUpdate) {
  const { data } = await api.patch<Project>(`/api/projects/${id}`, payload);
  return data;
}

export async function deleteProject(id: number) {
  await api.delete(`/api/projects/${id}`);
}