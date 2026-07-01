export type TaskStatus = "TODO" | "IN_PROGRESS" | "DONE" | "CANCELLED";

export type TaskPriority = 1 | 2 | 3;

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
}

export interface TaskStats {
  TODO: number;
  IN_PROGRESS: number;
  DONE: number;
  CANCELLED: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}
