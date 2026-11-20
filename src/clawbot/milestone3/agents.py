import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable
from .models import Task, TaskResult

@dataclass(frozen=True)
class DelegationContext:
    permissions: frozenset[str]
    depth: int
    parent_task_id: str | None

Worker = Callable[[Task, DelegationContext], Awaitable[object]]

class AgentCoordinator:
    """Bounded delegation. Workers receive caller permissions; no privilege escalation."""
    def __init__(self, max_depth=2, max_concurrency=3, timeout_seconds=60):
        if max_depth < 1 or max_concurrency < 1 or timeout_seconds <= 0:
            raise ValueError("Invalid delegation limits")
        self.max_depth = max_depth
        self.timeout_seconds = timeout_seconds
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._workers: dict[str, Worker] = {}

    def register(self, name: str, worker: Worker):
        if not name or name in self._workers:
            raise ValueError("Invalid or duplicate worker")
        self._workers[name] = worker

    async def delegate(self, name: str, task: Task, permissions: frozenset[str], depth=0):
        worker = self._workers.get(name)
        if worker is None:
            raise KeyError(f"Unregistered worker: {name}")
        if depth >= self.max_depth:
            raise ValueError("Maximum delegation depth exceeded")
        context = DelegationContext(frozenset(permissions), depth + 1, task.task_id)
        async with self._semaphore:
            try:
                output = await asyncio.wait_for(worker(task, context), self.timeout_seconds)
                return TaskResult(task.task_id, "completed", output=output)
            except asyncio.TimeoutError:
                return TaskResult(task.task_id, "timeout", error="Worker timed out")
            except Exception as exc:
                return TaskResult(task.task_id, "failed", error=str(exc))
