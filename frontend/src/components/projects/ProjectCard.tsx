import { useNavigate } from "react-router-dom";
import Button from "../common/Button";
import type { Project } from "../../types/project";

interface ProjectCardProps {
  project: Project;
  onDelete: (project: Project) => void;
}

export default function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const navigate = useNavigate();
  const open = () => navigate(`/projects/${project.id}`);

  return (
    <li className="task-card">
      <div className="task-main" style={{ cursor: "pointer" }} onClick={open}>
        <h3>{project.name}</h3>
        {project.description && <p>{project.description}</p>}
        <span className="task-priority">{project.task_count} задач</span>
      </div>
      <div className="task-actions">
        <Button variant="ghost" onClick={open}>
          Открыть
        </Button>
        <Button variant="danger" onClick={() => onDelete(project)}>
          Удалить
        </Button>
      </div>
    </li>
  );
}
