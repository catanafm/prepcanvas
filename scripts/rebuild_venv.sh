#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source "$ROOT_DIR/scripts/_python.sh"
PYTHON_BIN="$(find_python)"
warn_if_outdated "$PYTHON_BIN"

echo "Rebuilding .venv with $PYTHON_BIN"
rm -rf .venv
"$PYTHON_BIN" -m venv .venv

if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  echo "pip is missing in .venv. Bootstrapping with ensurepip..."
  .venv/bin/python -m ensurepip --upgrade
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "New .venv is ready."
