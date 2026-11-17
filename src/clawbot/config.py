from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from platformdirs import user_config_dir, user_data_dir
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CLAWBOT_", extra="ignore")

    name: str = "ClawBot"
    data_dir: str = ""
    openclaw_command: str = "openclaw"
    openclaw_timeout: int = 180
    openclaw_mode: str = "cli"
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:1.5b"
    vosk_model_path: str = "models/vosk/vosk-model-small-en-us-0.15"
    tts_enabled: bool = True
    voice_enabled: bool = True
    require_approval: bool = True
    allow_shell_tools: bool = False

    @property
    def resolved_data_dir(self) -> Path:
        return Path(self.data_dir).expanduser() if self.data_dir else Path(user_data_dir("clawbot"))

    @property
    def db_path(self) -> Path:
        return self.resolved_data_dir / "clawbot.sqlite3"


def _flatten_config(data: dict[str, Any]) -> dict[str, Any]:
    app = data.get("app", {})
    orch = data.get("orchestration", {})
    voice = data.get("voice", {})
    safety = data.get("safety", {})
    models = data.get("models", {})
    return {
        "name": app.get("name", "ClawBot"),
        "data_dir": app.get("data_dir", ""),
        "openclaw_command": orch.get("command", "openclaw"),
        "openclaw_timeout": orch.get("timeout_seconds", 180),
        "openclaw_mode": orch.get("mode", "cli"),
        "ollama_url": models.get("ollama_url", "http://127.0.0.1:11434"),
        "ollama_model": models.get("ollama_model", "qwen2.5:1.5b"),
        "vosk_model_path": voice.get("model_path", "models/vosk/vosk-model-small-en-us-0.15"),
        "tts_enabled": voice.get("tts_enabled", True),
        "voice_enabled": voice.get("enabled", True),
        "require_approval": safety.get("require_approval", True),
        "allow_shell_tools": safety.get("allow_shell_tools", False),
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    candidates = [Path("config/settings.yaml"), Path(user_config_dir("clawbot")) / "settings.yaml"]
    loaded: dict[str, Any] = {}
    for candidate in candidates:
        if candidate.is_file():
            loaded = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
            break
    return Settings(**_flatten_config(loaded))
