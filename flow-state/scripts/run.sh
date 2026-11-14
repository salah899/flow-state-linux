#!/usr/bin/env bash
# Everyday launcher.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
    echo "No virtual environment found. Run ./scripts/setup.sh first." >&2
    exit 1
fi
. .venv/bin/activate
PYTHONPATH=src exec python -m flow_state "$@"
