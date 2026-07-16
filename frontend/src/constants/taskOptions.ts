import type { TaskPriority, TaskStatus } from "../types/task";

export const STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: "К выполнению",
  IN_PROGRESS: "В работе",
  DONE: "Готово",
  CANCELLED: "Отменено",
};

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
  1: "Низкий",
  2: "Средний",
  3: "Высокий",
};

export const STATUSES: TaskStatus[] = ["TODO", "IN_PROGRESS", "DONE", "CANCELLED"];

export const PRIORITIES: TaskPriority[] = [1, 2, 3];
