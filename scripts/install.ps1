$ErrorActionPreference = "Stop"
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw "Python 3.11+ is required. Install Python from https://www.python.org/downloads/" }
python -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ required'"
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev,voice]"
Write-Host "ClawBot installed. Next: install OpenClaw, run openclaw onboard, then clawbot doctor."
