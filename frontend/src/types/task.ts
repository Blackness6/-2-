import type { UserShort } from "./user";

export type TaskStatus = "TODO" | "IN_PROGRESS" | "DONE" | "CANCELLED";

export type TaskPriority = 1 | 2 | 3;

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  creator_id: number;
  assigned_by_id: number | null;
  assignee_id: number | null;
  creator: UserShort;
  assigned_by: UserShort | null;
  assignee: UserShort | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  assignee_id?: number | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
}

export interface TaskStats {
  TODO: number;
  IN_PROGRESS: number;
  DONE: number;
  CANCELLED: number;
}
