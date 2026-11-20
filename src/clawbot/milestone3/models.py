from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    input_data: dict[str, Any] = field(default_factory=dict)
    parent_task_id: str | None = None
    created_at: str = field(default_factory=now_iso)

@dataclass(frozen=True)
class TaskResult:
    task_id: str
    status: str
    output: Any = None
    error: str | None = None
