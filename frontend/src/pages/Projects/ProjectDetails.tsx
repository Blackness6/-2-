import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useProjectTasks } from "../../hooks/useProjectTasks";
import * as projectApi from "../../api/projectApi";
import * as userApi from "../../api/userApi";
import Button from "../../components/common/Button";
import ErrorMessage from "../../components/common/ErrorMessage";
import Loader from "../../components/common/Loader";
import TaskForm from "../../components/tasks/TaskForm";
import TaskList from "../../components/tasks/TaskList";
import type { Project } from "../../types/project";
import type { UserShort } from "../../types/user";
import "../Tasks/TasksPage.css";

export default function ProjectDetails() {
  const { projectId } = useParams();
  const id = Number(projectId);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [users, setUsers] = useState<UserShort[]>([]);

  const { tasks, loading, error, createTask, changeStatus, saveTask, changeAssignee, removeTask } =
    useProjectTasks(id);

  useEffect(() => {
    projectApi.getProject(id).then(setProject).catch(() => setProject(null));
    userApi.getUsers().then(setUsers).catch(() => setUsers([]));
  }, [id]);

  return (
    <div className="tasks-page">
      <header className="tasks-header">
        <div>
          <Button variant="ghost" onClick={() => navigate("/projects")}>← К проектам</Button>
          <h1>{project?.name ?? "Проект"}</h1>
        </div>
        <div className="tasks-header-user"><span>{user?.username}</span></div>
      </header>

      <ErrorMessage message={error} />
      <TaskForm users={users} onCreate={createTask} />

      {loading ? <Loader /> : (
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