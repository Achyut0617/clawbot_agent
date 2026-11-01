"""Orchestrate a complete command sequence with status and feedback tracking."""
from dataclasses import dataclass
from threading import Event, Lock
from typing import List, Optional
from uuid import uuid4

from .command_models import RobotCommand
from .command_executor import CommandExecutor
from .state_manager import StateManager
from .feedback_manager import FeedbackManager


@dataclass
class ExecutionResult:
    task_id: str
    status: str
    completed_commands: int
    total_commands: int
    message: str


class ExecutionManager:
    def __init__(self, executor: CommandExecutor,
                 state_manager: StateManager,
                 feedback_manager: FeedbackManager):
        self.executor = executor
        self.state = state_manager
        self.feedback = feedback_manager
        self._cancel_event = Event()
        self._run_lock = Lock()

    def cancel(self) -> None:
        self._cancel_event.set()
        self.state.update(status="stopping")
        self.feedback.publish("cancellation_requested",
                              "Cancellation requested.")

    def execute_plan(self, commands: List[RobotCommand],
                     task_id: Optional[str] = None) -> ExecutionResult:
        task_id = task_id or str(uuid4())
        if not commands:
            raise ValueError("Cannot execute an empty command list")

        if not self._run_lock.acquire(blocking=False):
            raise RuntimeError("Another robot task is already running")

        completed = 0
        total = len(commands)
        self._cancel_event.clear()
        self.state.update(status="running", task_id=task_id,
                          current_command_id=None, current_action=None,
                          last_error=None)
        self.feedback.publish("task_started", "Robot task started.",
                              task_id=task_id,
                              details={"total_commands": total})

        try:
            for command in commands:
                if self._cancel_event.is_set():
                    raise InterruptedError("Task cancelled")

                self.state.update(
                    current_command_id=command.command_id,
                    current_action=command.source_action,
                )
                self.feedback.publish(
                    "command_started", f"Executing {command.source_action}.",
                    task_id=task_id, command_id=command.command_id
                )

                self.executor.execute(command, self._cancel_event)
                completed += 1
                self.feedback.publish(
                    "command_completed", f"Completed {command.source_action}.",
                    task_id=task_id, command_id=command.command_id
                )

            self.state.update(status="completed", current_command_id=None,
                              current_action=None)
            message = f"Task completed: {completed}/{total} commands."
            self.feedback.publish("task_completed", message, task_id=task_id)
            return ExecutionResult(task_id, "completed", completed, total, message)

        except InterruptedError as exc:
            self._safe_stop()
            self.state.update(status="cancelled", current_command_id=None,
                              current_action=None, last_error=str(exc))
            message = f"Task cancelled after {completed}/{total} commands."
            self.feedback.publish("task_cancelled", message, task_id=task_id)
            return ExecutionResult(task_id, "cancelled", completed, total, message)

        except Exception as exc:
            self._safe_stop()
            self.state.update(status="failed", current_command_id=None,
                              current_action=None, last_error=str(exc))
            message = f"Task failed after {completed}/{total} commands: {exc}"
            self.feedback.publish("task_failed", message, task_id=task_id)
            return ExecutionResult(task_id, "failed", completed, total, message)

        finally:
            self._run_lock.release()

    def _safe_stop(self) -> None:
        try:
            self.executor.robot.emergency_stop()
        except Exception as stop_error:
            self.feedback.publish(
                "emergency_stop_error",
                f"Emergency stop request failed: {stop_error}"
            )
