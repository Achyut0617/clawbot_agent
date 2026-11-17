from .config import Settings
from .models import TaskStatus
from .orchestrator import OpenClawAdapter
from .safety import inspect_request
from .store import TaskStore


class AgentRuntime:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.store = TaskStore(settings.db_path)
        self.orchestrator = OpenClawAdapter(settings.openclaw_command,
                                             settings.openclaw_timeout)

    def submit(self, text: str, source: str = "text", approved: bool = False,
               session_id: str | None = None) -> tuple[str, str]:
        task_id = self.store.create(text, source)
        decision = inspect_request(text, self.settings.require_approval)
        if not decision.allowed:
            self.store.update(task_id, TaskStatus.REJECTED, decision.reason)
            return task_id, decision.reason
        if decision.requires_approval and not approved:
            self.store.update(task_id, TaskStatus.AWAITING_APPROVAL,
                              "Approval required before sending to OpenClaw.")
            return task_id, "APPROVAL_REQUIRED"
        self.store.update(task_id, TaskStatus.RUNNING)
        result = self.orchestrator.run(text, session_id)
        status = TaskStatus.COMPLETED if result.ok else TaskStatus.FAILED
        self.store.update(task_id, status, result.output)
        return task_id, result.output
