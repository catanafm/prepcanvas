#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

if grep -q "anaconda3" .venv/pyvenv.cfg 2>/dev/null; then
  echo "Current .venv is based on Anaconda and may hang on Streamlit startup."
  echo "Run: bash scripts/rebuild_venv.sh"
  exit 1
fi

if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  echo "pip is missing in .venv. Bootstrapping with ensurepip..."
  .venv/bin/python -m ensurepip --upgrade
fi

.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install pytest

echo "Environment is ready."
