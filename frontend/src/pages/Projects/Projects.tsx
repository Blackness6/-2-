import { useAuth } from "../../hooks/useAuth";
import { useProjects } from "../../hooks/useProjects";
import Button from "../../components/common/Button";
import ErrorMessage from "../../components/common/ErrorMessage";
import Loader from "../../components/common/Loader";
import ProjectForm from "../../components/projects/ProjectForm";
import ProjectCard from "../../components/projects/ProjectCard";
import "../Tasks/TasksPage.css";

export default function Projects() {
  const { user, logout } = useAuth();
  const { projects, loading, error, createProject, removeProject } = useProjects();

  return (
    <div className="tasks-page">
      <header className="tasks-header">
        <h1>Мои проекты</h1>
        <div className="tasks-header-user">
          <span>{user?.username}</span>
          <Button variant="ghost" onClick={logout}>
            Выйти
          </Button>
        </div>
      </header>

      <ErrorMessage message={error} />

      <ProjectForm onCreate={createProject} />

      {loading ? (
        <Loader />
      ) : projects.length === 0 ? (
        <p className="empty-state">Проектов пока нет</p>
      ) : (
        <ul className="task-list">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} onDelete={removeProject} />
          ))}
        </ul>
      )}
    </div>
  );
}
