import { useEffect, useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useTasks } from "../../hooks/useTasks";
import * as userApi from "../../api/userApi";
import Button from "../../components/common/Button";
import ErrorMessage from "../../components/common/ErrorMessage";
import Loader from "../../components/common/Loader";
import TaskFilters from "../../components/tasks/TaskFilters";
import TaskForm from "../../components/tasks/TaskForm";
import TaskList from "../../components/tasks/TaskList";
import { STATUS_LABELS, STATUSES } from "../../constants/taskOptions";
import type { TaskPriority, TaskStatus } from "../../types/task";
import type { UserShort } from "../../types/user";
import "./TasksPage.css";

export default function TasksPage() {
  const { user, logout } = useAuth();
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "">("");
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | "">("");
  const [users, setUsers] = useState<UserShort[]>([]);

  const {
    tasks,
    stats,
    loading,
    error,
    createTask,
    changeStatus,
    saveTask,
    changeAssignee,
    removeTask,
  } = useTasks(statusFilter, priorityFilter);

  useEffect(() => {
    userApi
      .getUsers()
      .then(setUsers)
      .catch(() => setUsers([]));
  }, []);

  return (
    <div className="tasks-page">
      <header className="tasks-header">
        <h1>Мои Задачи Важные:</h1>
        <div className="tasks-header-user">
          <span>{user?.username}</span>
          <Button variant="ghost" onClick={logout}>
            Выйти
          </Button>
        </div>
      </header>

      {stats && (
        <div className="stats-bar">
          {STATUSES.map((s) => (
            <div className="stat-pill" key={s}>
              <span className="stat-value">{stats[s]}</span>
              <span className="stat-label">{STATUS_LABELS[s]}</span>
            </div>
          ))}
        </div>
      )}

      <ErrorMessage message={error} />

      <TaskForm users={users} onCreate={createTask} />

      <TaskFilters
        status={statusFilter}
        priority={priorityFilter}
        onStatusChange={setStatusFilter}
        onPriorityChange={setPriorityFilter}
      />

      {loading ? (
        <Loader />
      ) : (
        <TaskList
          tasks={tasks}
          users={users}
          currentUserId={user?.id}
          onStatusChange={changeStatus}
          onAssigneeChange={changeAssignee}
          onSave={saveTask}
          onDelete={removeTask}
        />
      )}
    </div>
  );
}
