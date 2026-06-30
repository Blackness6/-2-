from abc import ABC, abstractmethod

from app.models import Task

class ITaskRepository(ABC):

    @abstractmethod
    def create(self , task : Task) ->  Task:
        pass


    @abstractmethod
    def get_by_id(self, task_id : int) -> Task | None:
        pass

    @abstractmethod
    def get_all(
        self, 
        status: str | None = None,
        priority: int | None = None,
        ) ->  list[Task]:
        pass

    @abstractmethod
    def update(self, task: Task ) -> Task:
        pass

    @abstractmethod
    def delete(self, task:Task) -> None:
        pass

    @abstractmethod
    def get_stats(self) ->  dict [str, int]:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass