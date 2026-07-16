from abc import ABC, abstractmethod

from app.models import Project, ProjectMember


class IProjectRepository(ABC):

    @abstractmethod
    def create(self, project: Project) -> Project:
        pass

    @abstractmethod
    def get_by_id(self, project_id: int, user_id: int) -> Project | None:
        pass

    @abstractmethod
    def get_all(self, user_id: int) -> list[Project]:
        pass

    @abstractmethod
    def update(self, project: Project) -> Project:
        pass

    @abstractmethod
    def delete(self, project: Project) -> None:
        pass

    @abstractmethod
    def get_member(self, project_id: int, user_id: int) -> "ProjectMember | None":
        pass

    @abstractmethod
    def list_members(self, project_id: int) -> "list[ProjectMember]":
        pass

    @abstractmethod
    def add_member(self, member: "ProjectMember") -> "ProjectMember":
        pass

    @abstractmethod
    def remove_member(self, member: "ProjectMember") -> None:
        pass