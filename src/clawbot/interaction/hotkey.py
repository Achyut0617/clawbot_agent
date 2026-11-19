from __future__ import annotations

import threading


class GlobalHotkey:
    \"\"\"Small adapter around the keyboard package's global hotkey registration.\"\"\"

    def __init__(self, shortcut: str, callback) -> None:
        self.shortcut = shortcut
        self.callback = callback
        self._keyboard = None
        self._handle = None
        self._lock = threading.Lock()

    def register(self) -> None:
        try:
            import keyboard
        except ImportError as exc:
            raise RuntimeError("Install the keyboard dependency first") from exc
        with self._lock:
            if self._handle is None:
                self._keyboard = keyboard
                self._handle = keyboard.add_hotkey(
                    self.shortcut, self.callback, suppress=False, trigger_on_release=False
                )

    def unregister(self) -> None:
        with self._lock:
            if self._keyboard is not None and self._handle is not None:
                self._keyboard.remove_hotkey(self._handle)
            self._handle = None
            self._keyboard = None
