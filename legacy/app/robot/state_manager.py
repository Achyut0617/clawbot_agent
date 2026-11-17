"""Thread-safe snapshot of the high-level robot/application state."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Optional


@dataclass
class RobotState:
    status: str = "idle"  # idle, running, stopping, completed, failed, cancelled
    task_id: Optional[str] = None
    current_command_id: Optional[str] = None
    current_action: Optional[str] = None
    last_error: Optional[str] = None
    updated_at: str = ""


class StateManager:
    VALID_STATUSES = {
        "idle", "running", "stopping", "completed", "failed", "cancelled"
    }

    def __init__(self):
        self._lock = RLock()
        self._state = RobotState()
        self._touch()

    def _touch(self):
        self._state.updated_at = datetime.now(timezone.utc).isoformat()

    def update(self, **changes):
        with self._lock:
            if "status" in changes and changes["status"] not in self.VALID_STATUSES:
                raise ValueError(f"Invalid robot status: {changes['status']}")
            for key, value in changes.items():
                if not hasattr(self._state, key):
                    raise AttributeError(f"Unknown state field: {key}")
                setattr(self._state, key, value)
            self._touch()
            return self.snapshot()

    def snapshot(self):
        with self._lock:
            return asdict(self._state)
