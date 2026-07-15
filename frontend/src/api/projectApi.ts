import { api } from "./client";
import type {
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProjectMember,
  ProjectMemberCreate,
} from "../types/project";

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

export async function getMembers(projectId: number) {
  const { data } = await api.get<ProjectMember[]>(`/api/projects/${projectId}/members`);
  return data;
}

export async function addMember(projectId: number, payload: ProjectMemberCreate) {
  const { data } = await api.post<ProjectMember>(`/api/projects/${projectId}/members`, payload);
  return data;
}

export async function removeMember(projectId: number, userId: number) {
  await api.delete(`/api/projects/${projectId}/members/${userId}`);
}