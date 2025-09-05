import threading, queue, time, uuid, traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"

@dataclass
class Task:
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

class TaskQueue:
    def __init__(self):
        self.q = queue.Queue()
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

    def enqueue(self, name: str, func: Callable, *args, **kwargs) -> str:
        tid = str(uuid.uuid4())
        t = Task(id=tid, name=name, func=func, args=args, kwargs=kwargs)
        with self.lock:
            self.tasks[tid] = t
        self.q.put(tid)
        return tid

    def get(self, task_id: str) -> Optional[Task]:
        with self.lock:
            return self.tasks.get(task_id)

    def all(self):
        with self.lock:
            return list(self.tasks.values())

    def _run(self):
        while True:
            tid = self.q.get()
            t = self.get(tid)
            if not t:
                continue
            try:
                t.status = TaskStatus.RUNNING
                t.started_at = time.time()
                t.result = t.func(*t.args, **t.kwargs)
                t.status = TaskStatus.DONE
            except Exception as e:
                t.error = f"{e}\n{traceback.format_exc()}"
                t.status = TaskStatus.ERROR
            finally:
                t.finished_at = time.time()
                self.q.task_done()

queue = TaskQueue()
