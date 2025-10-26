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
    "/opt/local/bin/python3.12"
    "/usr/bin/python3"
    "$(command -v python3 || true)"
  )
  for bin in "${candidates[@]}"; do
    if [ -x "$bin" ]; then
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

PYBIN="$(pick_python)" || { echo "No suitable python3 found." >&2; exit 1; }
echo "Using Python: $PYBIN"

if [ -d .venv ]; then
  if [ ! -x .venv/bin/python ]; then rm -rf .venv; fi
fi
if [ ! -d .venv ]; then
  "$PYBIN" -m venv .venv
fi
source .venv/bin/activate

export PIP_DISABLE_PIP_VERSION_CHECK=1
if ! python -m pip --version >/dev/null 2>&1; then
  python -m ensurepip --upgrade || { curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py; python get-pip.py; rm -f get-pip.py; }
fi
python -m pip install --upgrade pip setuptools wheel >/dev/null
python -m pip install -r requirements.txt >/dev/null

if [ -f .env ]; then
  set -a; source .env; set +a
fi

export BACKEND_BASE=${BACKEND_BASE:-http://localhost:8020}
exec streamlit run app.py --server.port=4020 --server.headless=true


