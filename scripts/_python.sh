# Shared by setup.sh and rebuild_venv.sh: choose the newest supported Python.
# Override with PYTHON_BIN=/path/to/python3.

find_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    echo "$PYTHON_BIN"
    return
  fi
  local candidate
  for candidate in python3.13 python3.12 python3.11 python3.10 /usr/bin/python3 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return
    fi
  done
  echo "No Python 3 interpreter found. Install Python 3.12 from https://www.python.org/downloads/" >&2
  exit 1
}

warn_if_outdated() {
  local python_bin="$1"
  if ! "$python_bin" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    echo "Note: $("$python_bin" --version 2>&1) is supported but past or near end of life."
    echo "      Python 3.12 is recommended: https://www.python.org/downloads/"
  fi
}
