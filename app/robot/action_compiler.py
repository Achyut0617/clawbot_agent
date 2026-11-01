"""Compile an LLM-produced JSON action plan into safe, typed commands.

This compiler validates data and maps allowlisted actions. It never evaluates
or executes source code from the model.
"""
import json
from typing import Any, Dict, List, Union

from .command_models import (
    MoveCommand, TurnCommand, StopCommand, WaitCommand, SpeakCommand,
    RobotCommand,
)


class ActionCompilationError(ValueError):
    """Raised when an action plan is malformed or outside policy."""


class ActionCompiler:
    ALLOWED_DIRECTIONS = {"forward", "backward"}
    ALLOWED_TURNS = {"left", "right"}
    MAX_ACTIONS = 20
    MAX_MOVE_SECONDS = 2.0
    MAX_TURN_SECONDS = 2.0
    MAX_WAIT_SECONDS = 30.0
    MAX_SPEECH_CHARS = 300

    def compile(self, payload: Union[str, Dict[str, Any]]) -> List[RobotCommand]:
        plan = self._load_payload(payload)

        allowed_plan_keys = {"task_id", "robot", "actions"}
        unknown = set(plan) - allowed_plan_keys
        if unknown:
            raise ActionCompilationError(f"Unknown plan fields: {sorted(unknown)}")

        actions = plan.get("actions")
        if not isinstance(actions, list) or not actions:
            raise ActionCompilationError("'actions' must be a non-empty list")
        if len(actions) > self.MAX_ACTIONS:
            raise ActionCompilationError(
                f"Too many actions; maximum is {self.MAX_ACTIONS}"
            )

        commands: List[RobotCommand] = []
        for index, action in enumerate(actions):
            try:
                commands.append(self._compile_action(action))
            except ActionCompilationError as exc:
                raise ActionCompilationError(f"actions[{index}]: {exc}") from exc
        return commands

    @staticmethod
    def _load_payload(payload: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ActionCompilationError(f"Invalid JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ActionCompilationError("Plan must be a JSON object")
        return payload

    def _compile_action(self, action: Any) -> RobotCommand:
        if not isinstance(action, dict):
            raise ActionCompilationError("Each action must be an object")

        kind = action.get("action")
        if not isinstance(kind, str):
            raise ActionCompilationError("Missing string field 'action'")

        if kind == "move":
            self._check_keys(action, {"action", "direction", "duration"})
            direction = action.get("direction")
            if direction not in self.ALLOWED_DIRECTIONS:
                raise ActionCompilationError(
                    f"direction must be one of {sorted(self.ALLOWED_DIRECTIONS)}"
                )
            duration = self._number(action.get("duration"), "duration")
            self._range(duration, 0.1, self.MAX_MOVE_SECONDS, "duration")
            return MoveCommand(direction=direction, duration=duration,
                               source_action=kind)

        if kind == "turn":
            self._check_keys(action, {"action", "direction", "duration"})
            direction = action.get("direction")
            if direction not in self.ALLOWED_TURNS:
                raise ActionCompilationError(
                    f"direction must be one of {sorted(self.ALLOWED_TURNS)}"
                )
            duration = self._number(action.get("duration"), "duration")
            self._range(duration, 0.1, self.MAX_TURN_SECONDS, "duration")
            return TurnCommand(direction=direction, duration=duration,
                               source_action=kind)

        if kind == "stop":
            self._check_keys(action, {"action", "reason"})
            reason = action.get("reason", "requested")
            if not isinstance(reason, str) or len(reason) > 120:
                raise ActionCompilationError("'reason' must be a short string")
            return StopCommand(reason=reason, source_action=kind)

        if kind == "wait":
            self._check_keys(action, {"action", "duration"})
            duration = self._number(action.get("duration"), "duration")
            self._range(duration, 0.0, self.MAX_WAIT_SECONDS, "duration")
            return WaitCommand(duration=duration, source_action=kind)

        if kind == "speak":
            self._check_keys(action, {"action", "text"})
            text = action.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ActionCompilationError("'text' must be a non-empty string")
            if len(text) > self.MAX_SPEECH_CHARS:
                raise ActionCompilationError("Speech text is too long")
            return SpeakCommand(text=text.strip(), source_action=kind)

        raise ActionCompilationError(f"Unsupported action: {kind!r}")

    @staticmethod
    def _check_keys(action: Dict[str, Any], allowed: set) -> None:
        unknown = set(action) - allowed
        if unknown:
            raise ActionCompilationError(f"Unknown fields: {sorted(unknown)}")

    @staticmethod
    def _number(value: Any, field_name: str) -> float:
        # bool is a subclass of int, so explicitly reject it.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ActionCompilationError(f"'{field_name}' must be numeric")
        return float(value)

    @staticmethod
    def _range(value: float, minimum: float, maximum: float,
               field_name: str) -> None:
        if not minimum <= value <= maximum:
            raise ActionCompilationError(
                f"'{field_name}' must be between {minimum} and {maximum}"
            )
