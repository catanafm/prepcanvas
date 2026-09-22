#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/pytest" ]]; then
  echo "pytest is not installed in .venv. Run ./scripts/setup.sh first."
  exit 1
fi

if grep -q "anaconda3" .venv/pyvenv.cfg 2>/dev/null; then
  echo "Current .venv is based on Anaconda and may be unstable."
  echo "Run: bash scripts/rebuild_venv.sh"
  exit 1
fi

if ! .venv/bin/python -c "import pytest" >/dev/null 2>&1; then
  echo "pytest is missing from .venv."
  echo "Run: bash scripts/setup.sh"
  exit 1
fi

PYTHONPATH=src .venv/bin/pytest "$@"
