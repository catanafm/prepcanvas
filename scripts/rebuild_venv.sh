#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

echo "Rebuilding .venv with $PYTHON_BIN"
rm -rf .venv
"$PYTHON_BIN" -m venv .venv

if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  echo "pip is missing in .venv. Bootstrapping with ensurepip..."
  .venv/bin/python -m ensurepip --upgrade
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install pytest

echo "New .venv is ready."
