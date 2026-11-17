from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    RECEIVED = "received"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TaskRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    source: str = "text"
    session_id: str | None = None


class TaskRecord(BaseModel):
    task_id: str
    text: str
    source: str
    status: TaskStatus
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    result: str | None = None
