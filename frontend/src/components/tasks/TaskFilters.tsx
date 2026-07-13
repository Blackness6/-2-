import { PRIORITIES, PRIORITY_LABELS, STATUS_LABELS, STATUSES } from "../../constants/taskOptions";
import type { TaskPriority, TaskStatus } from "../../types/task";

interface TaskFiltersProps {
  status: TaskStatus | "";
  priority: TaskPriority | "";
  onStatusChange: (status: TaskStatus | "") => void;
  onPriorityChange: (priority: TaskPriority | "") => void;
}

export default function TaskFilters({
  status,
  priority,
  onStatusChange,
  onPriorityChange,
}: TaskFiltersProps) {
  return (
    <div className="filters">
      <select
        value={status}
        onChange={(e) => onStatusChange(e.target.value as TaskStatus | "")}
      >
        <option value="">Все статусы</option>
        {STATUSES.map((s) => (
          <option key={s} value={s}>
            {STATUS_LABELS[s]}
          </option>
        ))}
      </select>
      <select
        value={priority}
        onChange={(e) =>
          onPriorityChange(e.target.value ? (Number(e.target.value) as TaskPriority) : "")
        }
      >
        <option value="">Все приоритеты</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {PRIORITY_LABELS[p]}
          </option>
        ))}
      </select>
    </div>
  );
}
