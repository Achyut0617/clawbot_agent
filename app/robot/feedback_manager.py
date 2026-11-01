"""Collect execution events and produce concise user-facing feedback."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionEvent:
    event: str
    message: str
    task_id: Optional[str] = None
    command_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = ""


class FeedbackManager:
    def __init__(self):
        self._lock = RLock()
        self._events: List[ExecutionEvent] = []

    def publish(self, event: str, message: str, task_id=None,
                command_id=None, details=None) -> ExecutionEvent:
        item = ExecutionEvent(
            event=event,
            message=message,
            task_id=task_id,
            command_id=command_id,
            details=details or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._events.append(item)
        return item

    def history(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [asdict(item) for item in self._events]

    def summary(self, task_id: str) -> str:
        with self._lock:
            matching = [e for e in self._events if e.task_id == task_id]
        if not matching:
            return "No execution feedback is available."
        last = matching[-1]
        return last.message
