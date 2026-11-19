from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class CancellationToken:
    _event: threading.Event = field(default_factory=threading.Event)

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._event.wait(timeout)


class InterruptionController:
    \"\"\"Thread-safe, idempotent cancellation for the active interaction.\"\"\"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active: CancellationToken | None = None

    def begin(self) -> CancellationToken:
        with self._lock:
            if self._active is not None:
                self._active.cancel()
            self._active = CancellationToken()
            return self._active

    def interrupt(self) -> bool:
        with self._lock:
            if self._active is None:
                return False
            self._active.cancel()
            self._active = None
            return True

    def finish(self, token: CancellationToken) -> None:
        with self._lock:
            if self._active is token:
                self._active = None
