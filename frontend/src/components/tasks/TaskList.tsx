import TaskCard from "./TaskCard";
import type { Task, TaskStatus, TaskUpdate } from "../../types/task";
import type { UserShort } from "../../types/user";

interface TaskListProps {
  tasks: Task[];
  users: UserShort[];
  currentUserId: number | undefined;
  onStatusChange: (task: Task, status: TaskStatus) => void;
  onAssigneeChange: (task: Task, assigneeId: number | null) => void;
  onSave: (task: Task, payload: TaskUpdate) => Promise<boolean>;
  onDelete: (task: Task) => void;
}

export default function TaskList({
  tasks,
  users,
  currentUserId,
  onStatusChange,
  onAssigneeChange,
  onSave,
  onDelete,
}: TaskListProps) {
  if (tasks.length === 0) {
    return <p className="empty-state">Задач не найдено</p>;
  }

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          users={users}
          canAssign={task.creator_id === currentUserId}
          onStatusChange={onStatusChange}
          onAssigneeChange={onAssigneeChange}
          onSave={onSave}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
