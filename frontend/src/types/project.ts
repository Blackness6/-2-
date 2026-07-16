import type { UserShort } from "./user";

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  task_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
}

export interface ProjectUpdate {
  name?: string;
  description?: string | null;
}

export type ProjectRole = "owner" | "manager" | "member";

export interface ProjectMember {
  id: number | null;        // null у владельца (синтетическая запись)
  project_id: number;
  user_id: number;
  role: ProjectRole;
  user: UserShort;
}

export interface ProjectMemberCreate {
  user_id: number;
  role: ProjectRole;        // "manager" | "member"
}
