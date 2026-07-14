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
