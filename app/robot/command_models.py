"""Typed, hardware-independent robot command models.

These objects describe intent. They do not contain motor-driver instructions.
"""
from dataclasses import dataclass, field
from typing import Union
from uuid import uuid4


@dataclass(frozen=True)
class BaseCommand:
    command_id: str = field(default_factory=lambda: str(uuid4()))
    source_action: str = ""


@dataclass(frozen=True)
class MoveCommand(BaseCommand):
    direction: str = "forward"
    duration: float = 1.0


@dataclass(frozen=True)
class TurnCommand(BaseCommand):
    direction: str = "left"
    duration: float = 1.0


@dataclass(frozen=True)
class StopCommand(BaseCommand):
    reason: str = "requested"


@dataclass(frozen=True)
class WaitCommand(BaseCommand):
    duration: float = 1.0


@dataclass(frozen=True)
class SpeakCommand(BaseCommand):
    text: str = ""


RobotCommand = Union[
    MoveCommand, TurnCommand, StopCommand, WaitCommand, SpeakCommand
]
