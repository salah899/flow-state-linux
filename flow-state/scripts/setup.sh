#!/usr/bin/env bash
# One-time setup: creates .venv and installs runtime + dev dependencies.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
echo "Setup complete. Use ./scripts/run.sh to start Flow State."
