import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class OrchestrationResult:
    ok: bool
    output: str
    return_code: int | None = None


class OpenClawAdapter:
    """Thin adapter around the supported OpenClaw CLI.

    OpenClaw handles provider/model configuration, sessions, skills and tools.
    ClawBot deliberately does not shell-execute model-generated text itself.
    """

    def __init__(self, command: str = "openclaw", timeout: int = 180):
        self.command = command
        self.timeout = timeout

    def available(self) -> bool:
        return shutil.which(self.command) is not None

    def run(self, message: str, session_id: str | None = None) -> OrchestrationResult:
        if not self.available():
            return OrchestrationResult(False,
                "OpenClaw CLI was not found. Install it and complete `openclaw onboard`.")
        args = [self.command, "agent", "--message", message]
        if session_id:
            args += ["--session-id", session_id]
        try:
            completed = subprocess.run(args, capture_output=True, text=True,
                                       timeout=self.timeout, check=False)
        except subprocess.TimeoutExpired:
            return OrchestrationResult(False, f"OpenClaw timed out after {self.timeout}s.")
        except OSError as exc:
            return OrchestrationResult(False, f"Could not start OpenClaw: {exc}")
        output = (completed.stdout or "").strip()
        error = (completed.stderr or "").strip()
        if completed.returncode != 0:
            return OrchestrationResult(False, error or output or "OpenClaw returned an error.",
                                       completed.returncode)
        return OrchestrationResult(True, output or "OpenClaw completed without textual output.",
                                   completed.returncode)
