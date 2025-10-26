#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Prefer system Python to avoid Conda interference
PYTHON_BIN="/usr/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  else
    echo "python3 not found. Please install Python 3.10+." >&2
    exit 1
  fi
fi

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_PYTHON_VERSION_WARNING=1

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

if [ -f .env ]; then
  echo ".env found. The app will load it via python-dotenv."
else
  echo "No .env found. Copy .env.example to .env and fill in keys."
fi

echo "Setup complete. To activate later: source .venv/bin/activate"


