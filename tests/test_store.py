from clawbot.store import TaskStore
from clawbot.models import TaskStatus


def test_task_lifecycle(tmp_path):
    store = TaskStore(tmp_path / "tasks.sqlite3")
    task_id = store.create("hello", "text")
    store.update(task_id, TaskStatus.COMPLETED, "world")
    row = store.recent(1)[0]
    assert row["task_id"] == task_id
    assert row["status"] == "completed"
    assert row["result"] == "world"
