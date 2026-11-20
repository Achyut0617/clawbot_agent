import json
import sqlite3
import uuid
from pathlib import Path

class MemoryStore:
    """Explicit local memory. Search is SQL text matching, not semantic retrieval."""
    def __init__(self, path="data/clawbot_memory.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS memories (id TEXT PRIMARY KEY, content TEXT NOT NULL, tags TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, expires_at TEXT)")

    def _db(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def add(self, content: str, tags=(), expires_at=None) -> str:
        if not content.strip():
            raise ValueError("Memory cannot be empty")
        mid = str(uuid.uuid4())
        with self._db() as db:
            db.execute("INSERT INTO memories(id,content,tags,expires_at) VALUES(?,?,?,?)",
                       (mid, content.strip(), json.dumps(list(tags)), expires_at))
        return mid

    def search(self, query: str, tag=None, limit=10) -> list[dict]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be 1..100")
        with self._db() as db:
            rows = db.execute("SELECT * FROM memories WHERE content LIKE ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP) ORDER BY created_at DESC LIMIT ?",
                              (f"%{query.strip()}%", limit)).fetchall()
        result = []
        for row in rows:
            tags = json.loads(row["tags"])
            if tag is None or tag in tags:
                result.append({"id": row["id"], "content": row["content"], "tags": tags,
                               "created_at": row["created_at"], "expires_at": row["expires_at"]})
        return result

    def update(self, memory_id: str, content: str, tags=()) -> bool:
        if not content.strip():
            raise ValueError("Memory cannot be empty")
        with self._db() as db:
            cur = db.execute("UPDATE memories SET content=?, tags=? WHERE id=?",
                             (content.strip(), json.dumps(list(tags)), memory_id))
            return cur.rowcount > 0

    def delete(self, memory_id: str) -> bool:
        with self._db() as db:
            cur = db.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            return cur.rowcount > 0
