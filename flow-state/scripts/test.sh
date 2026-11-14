#!/usr/bin/env bash
# Run the test suite (run before every increment / release).
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
python -m pytest -q "$@"
