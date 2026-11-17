"""Dispatch typed commands to a robot interface.

The interface is deliberately abstract. Implement it separately for a simulator
or a physical robot. This module contains no GPIO, PWM, or motor-driver code.
"""
from typing import Optional, Protocol
from threading import Event

from .command_models import (
    RobotCommand, MoveCommand, TurnCommand, StopCommand, WaitCommand,
    SpeakCommand,
)


class RobotInterface(Protocol):
    def move(self, direction: str, duration: float,
             cancel_event: Optional[Event] = None) -> None: ...
    def turn(self, direction: str, duration: float,
             cancel_event: Optional[Event] = None) -> None: ...
    def stop(self, reason: str = "requested") -> None: ...
    def speak(self, text: str) -> None: ...
    def emergency_stop(self) -> None: ...


class CommandExecutor:
    def __init__(self, robot: RobotInterface):
        self.robot = robot

    def execute(self, command: RobotCommand,
                cancel_event: Optional[Event] = None) -> None:
        if cancel_event and cancel_event.is_set():
            raise InterruptedError("Execution cancelled before command")

        if isinstance(command, MoveCommand):
            self.robot.move(command.direction, command.duration, cancel_event)
        elif isinstance(command, TurnCommand):
            self.robot.turn(command.direction, command.duration, cancel_event)
        elif isinstance(command, StopCommand):
            self.robot.stop(command.reason)
        elif isinstance(command, WaitCommand):
            if cancel_event and cancel_event.wait(command.duration):
                raise InterruptedError("Execution cancelled during wait")
            if cancel_event is None:
                Event().wait(command.duration)
        elif isinstance(command, SpeakCommand):
            self.robot.speak(command.text)
        else:
            raise TypeError(f"Unsupported command object: {type(command).__name__}")
