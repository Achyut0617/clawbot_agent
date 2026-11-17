import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import TaskStatus


class TaskStore:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, text TEXT NOT NULL, source TEXT NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                result TEXT, metadata TEXT NOT NULL DEFAULT '{}'
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT,
                event_type TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            )""")

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def create(self, text: str, source: str) -> str:
        task_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute("INSERT INTO tasks(task_id,text,source,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                       (task_id, text, source, TaskStatus.RECEIVED.value, now, now))
        self.event(task_id, "task_received", "Task accepted", {"source": source})
        return task_id

    def update(self, task_id: str, status: TaskStatus, result: str | None = None):
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute("UPDATE tasks SET status=?, result=COALESCE(?,result), updated_at=? WHERE task_id=?",
                       (status.value, result, now, task_id))
        self.event(task_id, "status_changed", status.value, {})

    def event(self, task_id: str | None, event_type: str, message: str, metadata: dict):
        with self._connect() as db:
            db.execute("INSERT INTO events(task_id,event_type,message,created_at,metadata) VALUES(?,?,?,?,?)",
                       (task_id, event_type, message, datetime.now(timezone.utc).isoformat(),
                        json.dumps(metadata)))

    def recent(self, limit: int = 20):
        with self._connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]
