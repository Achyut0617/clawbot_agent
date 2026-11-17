# ClawBot Agent

Cross-platform, local-first voice and text assistant with OpenClaw orchestration.

> This is an integration foundation, not yet a fully autonomous desktop operator.
> Physical robot control is disabled. Voice is optional; text input always works.

## What is included
- Unified text-first interactive CLI (`clawbot chat`)
- Optional offline Vosk push-to-talk (`/voice`)
- OpenClaw CLI adapter (`openclaw agent --message ...`)
- Explicit approval required by default
- SQLite task and event history
- OS-specific data directory
- Setup and diagnostics commands
- CI matrix for Windows, Linux and macOS
- Tagged GitHub Release workflow
- Atomic development ledger (`ROADMAP.yaml`)

## Requirements
- Python 3.11+
- OpenClaw installed and onboarded
- Node.js version required by the current OpenClaw release
- Optional: microphone, Vosk model and voice extras

## Install

### Windows PowerShell
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,voice]"
```

Install OpenClaw using its official PowerShell installer:
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
openclaw onboard
openclaw gateway status
```

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,voice]"
```

Install OpenClaw using its official installer:
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard
openclaw gateway status
```

### Install ClawBot with helper scripts
- Linux/macOS: `bash scripts/install.sh`
- Windows: `.\scripts\install.ps1`

The helper scripts install ClawBot only; OpenClaw onboarding remains a separate, interactive step.

## Run
```bash
clawbot doctor
clawbot chat
```

Commands inside the chat:
- Type any task to send it to OpenClaw (approval required by default).
- `/voice` captures one voice command if microphone + Vosk are installed.
- `/history` lists recent tasks.
- `/help` lists commands.
- `/quit` exits.

One-shot task:
```bash
clawbot run "Explain the architecture of this repository" --approve
```

Without `--approve`, one-shot execution records the task and reports that approval is required.

## Voice model
Download the Vosk small English model from the official Vosk model catalogue and extract it to:
`models/vosk/vosk-model-small-en-us-0.15/`

Voice is optional. If no microphone, audio library, or model exists, use typed commands. TTS failure does not stop the agent.

## Configuration
Defaults are in `config/settings.yaml`. Environment variables override settings:
- `CLAWBOT_OPENCLAW_COMMAND`
- `CLAWBOT_OPENCLAW_TIMEOUT`
- `CLAWBOT_REQUIRE_APPROVAL`
- `CLAWBOT_VOSK_MODEL_PATH`
- `CLAWBOT_TTS_ENABLED`

OpenClaw model/provider credentials are configured by OpenClaw itself, not duplicated in ClawBot.

## Development
```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```
See `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/DEVELOPMENT.md` and `ROADMAP.yaml`.

## Current limitations / next milestones
- Session continuity needs verification against the installed OpenClaw CLI version.
- Gateway health and auth diagnostics are not yet queried through a dedicated API.
- Push-to-talk is implemented; always-on wake-word and hotkey listener are roadmap items.
- FastAPI service, GUI, packaged binaries and Jetson-specific setup profile are roadmap items.
- The previous Streamlit prototype and robot simulator are retained in the source snapshot, but this new `src/clawbot` runtime is the recommended entry point.
