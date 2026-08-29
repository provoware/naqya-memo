from __future__ import annotations
from dataclasses import dataclass
from queue import Queue
from threading import Thread, Event, Lock
from typing import Callable, Any
import uuid, time

@dataclass
class MutationJob:
    job_id: str
    name: str
    fn: Callable[[], Any]

class MutationQueue:
    """Single-writer mutation queue for the reference core.

    Goal: all state-changing operations are serialized. Read operations may
    remain concurrent at a higher layer.
    """
    def __init__(self):
        self._q: Queue = Queue()
        self._stop = Event()
        self._worker: Thread | None = None
        self._results: dict[str, tuple[bool, Any]] = {}
        self._lock = Lock()

    def start(self):
        if self._worker and self._worker.is_alive():
            return
        self._worker = Thread(target=self._run, name="provoware-mutation-queue", daemon=True)
        self._worker.start()

    def submit(self, name: str, fn: Callable[[], Any]) -> str:
        job_id = str(uuid.uuid4())
        self._q.put(MutationJob(job_id, name, fn))
        return job_id

    def wait(self, job_id: str, timeout: float = 10.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                if job_id in self._results:
                    ok, value = self._results.pop(job_id)
                    if ok:
                        return value
                    raise value
            time.sleep(0.01)
        raise TimeoutError(f"MUTATION_QUEUE_TIMEOUT:{job_id}")

    def stop(self):
        self._stop.set()
        self._q.put(None)
        if self._worker:
            self._worker.join(timeout=5)

    def _run(self):
        while not self._stop.is_set():
            job = self._q.get()
            if job is None:
                break
            try:
                value = job.fn()
                result = (True, value)
            except Exception as exc:
                result = (False, exc)
            with self._lock:
                self._results[job.job_id] = result
            self._q.task_done()
