#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

pick_python() {
  candidates=(
    "$(command -v python3.12 || true)"
    "$(command -v python3.11 || true)"
    "$(command -v python3.10 || true)"
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "/usr/bin/python3"
    "$(command -v python3 || true)"
  )
  for bin in "${candidates[@]}"; do
    if [ -x "$bin" ]; then
      # Skip Apple's CommandLineTools Python which can cause UnicodeDecodeError
      exe_path="$($bin -c 'import sys; print(sys.executable)')" || continue
      case "$exe_path" in
        *CommandLineTools*) continue ;;
      esac
      echo "$bin"
      return 0
    fi
  done
  return 1
}

PYBIN="$(pick_python)" || {
  echo "No suitable python3 found. Please install Python 3.11+ (e.g., brew install python@3.11)." >&2
  exit 1
}
echo "Using Python: $PYBIN"

if [ -d .venv ]; then
  # If venv was created with a broken interpreter, recreate it
  VENV_PY=".venv/bin/python"
  if [ ! -x "$VENV_PY" ]; then
    rm -rf .venv
  fi
fi

if [ ! -d .venv ]; then
  "$PYBIN" -m venv .venv
fi
source .venv/bin/activate

export PIP_DISABLE_PIP_VERSION_CHECK=1
# Ensure pip exists in this venv (some Python builds omit pip)
if ! python -m pip --version >/dev/null 2>&1; then
  python -m ensurepip --upgrade || {
    curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm -f get-pip.py
  }
fi

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# load .env if present (python-dotenv also loads but we pass PORT)
if [ -f .env ]; then
  set -a; source .env; set +a
fi

PORT="${PORT:-8000}"
exec uvicorn app:app --host 0.0.0.0 --port "$PORT"


