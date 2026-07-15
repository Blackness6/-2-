from abc import ABC, abstractmethod

from app.models import Task

class ITaskRepository(ABC):

    @abstractmethod
    def create(self , task : Task) ->  Task:
        pass


    @abstractmethod
    def get_by_id(self, task_id : int, user_id: int) -> Task | None:
        pass

    @abstractmethod
    def get_all(
        self,
        user_id: int,
        status: str | None = None,
        priority: int | None = None,
        project_id: int | None = None,
        ) ->  list[Task]:
        pass

    @abstractmethod
    def update(self, task: Task ) -> Task:
        pass

    @abstractmethod
    def delete(self, task:Task) -> None:
        pass

    @abstractmethod
    def get_stats(self, user_id: int) ->  dict [str, int]:
        pass

    @abstractmethod
    def get_by_project(self, project_id: int) -> "list[Task]":
        pass