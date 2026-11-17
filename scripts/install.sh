#!/usr/bin/env bash
set -Eeuo pipefail
python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required")
print("Python version OK:", sys.version.split()[0])
PY
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,voice]"
echo "ClawBot installed. Next: install OpenClaw, run onboarding, then clawbot doctor."
