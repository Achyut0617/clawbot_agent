import json
import random
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = 0.25
    max_delay: float = 5.0
    jitter: float = 0.1

def retry_call(operation, policy=None, retry_on=(TimeoutError, ConnectionError), sleep=time.sleep):
    policy = policy or RetryPolicy()
    if policy.max_attempts < 1 or policy.base_delay < 0 or policy.max_delay < policy.base_delay:
        raise ValueError("Invalid retry policy")
    for attempt in range(policy.max_attempts):
        try:
            return operation()
        except retry_on:
            if attempt + 1 == policy.max_attempts:
                raise
            delay = min(policy.base_delay * (2 ** attempt), policy.max_delay)
            sleep(max(0, delay * (1 + random.uniform(-policy.jitter, policy.jitter))))
    raise RuntimeError("Unreachable")

class CheckpointStore:
    """SQLite checkpoints; they do not make external side effects transactional."""
    def __init__(self, path="data/clawbot_checkpoints.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS checkpoints(task_id TEXT PRIMARY KEY, state TEXT NOT NULL, updated_at TEXT NOT NULL)")

    def save(self, task_id, state):
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO checkpoints VALUES(?,?,?) ON CONFLICT(task_id) DO UPDATE SET state=excluded.state, updated_at=excluded.updated_at",
                       (task_id, json.dumps(state), datetime.now(timezone.utc).isoformat()))

    def load(self, task_id):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT state FROM checkpoints WHERE task_id=?", (task_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def delete(self, task_id):
        with sqlite3.connect(self.path) as db:
            cur = db.execute("DELETE FROM checkpoints WHERE task_id=?", (task_id,))
            return cur.rowcount > 0
