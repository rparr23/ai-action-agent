from threading import Lock

from .models import Task


class TaskStore:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._lock = Lock()
        self._executed: set[str] = set()

    def save(self, task: Task):
        with self._lock:
            self._tasks[task.id] = task

    def get(self, task_id: str) -> Task:
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(task_id)
            return self._tasks[task_id]

    def all(self) -> list[Task]:
        with self._lock:
            return list(reversed(self._tasks.values()))

    def claim(self, fingerprint: str) -> bool:
        with self._lock:
            if fingerprint in self._executed:
                return False
            self._executed.add(fingerprint)
            return True


store = TaskStore()
