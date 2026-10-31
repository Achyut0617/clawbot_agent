
#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"
MODEL_NAME="qwen2.5:1.5b"
VOSK_DIR="models/vosk/vosk-model-small-en-us-0.15"
VOSK_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

echo "=== Clawbot Jetson deployment ==="

if [[ "$(uname -m)" != "aarch64" ]]; then
    echo "ERROR: Run this script on the ARM64 Jetson, not Windows."
    exit 1
fi

if [[ ! -f /etc/nv_tegra_release ]]; then
    echo "ERROR: Jetson Linux/JetPack not detected. Stop here."
    exit 1
fi

echo "--- Jetson Linux version ---"
cat /etc/nv_tegra_release

echo "--- Installing system dependencies ---"
sudo apt-get update
sudo apt-get install -y \
    python3-venv python3-pip python3-dev \
    build-essential curl ca-certificates unzip \
    portaudio19-dev libportaudio2 \
    espeak-ng libespeak1 alsa-utils

echo "--- Creating Python environment ---"
if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

echo "--- Installing Python packages ---"
python -m pip install numpy scipy sounddevice vosk pyttsx3 streamlit requests

echo "--- Checking Vosk model ---"
if [[ ! -f "$VOSK_DIR/conf/model.conf" ]]; then
    mkdir -p models/vosk
    tmpdir="$(mktemp -d)"
    trap 'rm -rf "$tmpdir"' EXIT
    curl -fL --retry 3 "$VOSK_URL" -o "$tmpdir/vosk.zip"
    unzip -q "$tmpdir/vosk.zip" -d models/vosk
    rm -rf "$tmpdir"
    trap - EXIT
fi

if [[ ! -f "$VOSK_DIR/conf/model.conf" ]]; then
    echo "ERROR: Vosk model missing after download."
    exit 1
fi
echo "PASS: Vosk model files found."

echo "--- Installing Ollama if needed ---"
if ! command -v ollama >/dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh
    sudo sh /tmp/ollama-install.sh
    rm -f /tmp/ollama-install.sh
fi

if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl enable --now ollama || true
fi

echo "--- Waiting for Ollama ---"
ready=0
for attempt in $(seq 1 30); do
    if curl -fsS http://localhost:11434/api/tags >/dev/null; then
        ready=1
        break
    fi
    sleep 2
done
if [[ "$ready" != 1 ]]; then
    echo "ERROR: Ollama API not responding. Check Ollama service."
    exit 1
fi

echo "--- Downloading LLM if needed ---"
if ! ollama list | awk 'NR>1 {print $1}' | grep -Fxq "$MODEL_NAME"; then
    ollama pull "$MODEL_NAME"
fi

echo "--- Enforcing simulation-only mode ---"
python - <<'PY'
import json
from pathlib import Path

p = Path("config/settings.json")
settings = json.loads(p.read_text(encoding="utf-8-sig"))
settings["mode"] = "simulation"
settings["robot_hardware_enabled"] = False
p.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
print("Simulation enabled; physical hardware disabled.")
PY

echo "--- Checking imports ---"
python - <<'PY'
import numpy, scipy, sounddevice, vosk, pyttsx3, streamlit
print("PASS: required Python imports")
PY

echo "--- Checking Vosk model loads ---"
python - <<'PY'
from vosk import Model
Model("models/vosk/vosk-model-small-en-us-0.15")
print("PASS: Vosk model loads")
PY

echo "--- Checking TTS initialization ---"
python - <<'PY'
import pyttsx3
engine = pyttsx3.init()
print("PASS: TTS engine initializes")
engine.stop()
PY

echo "--- Checking local LLM response ---"
response="$(ollama run "$MODEL_NAME" "Reply with only READY.")"
echo "$response"
if ! grep -qi "READY" <<< "$response"; then
    echo "ERROR: LLM readiness check did not return READY."
    exit 1
fi

echo "--- Running unit tests ---"
python -m unittest discover -s tests -v

echo
echo "=== Deployment checks completed ==="
echo "Review all output for failures."
echo "Hardware remains disabled."
echo
echo "Start dashboard with:"
echo "source .venv/bin/activate"
echo "python -m streamlit run app/ui.py"
