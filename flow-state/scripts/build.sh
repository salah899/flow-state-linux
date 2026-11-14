#!/usr/bin/env bash
# Builds a standalone executable with PyInstaller. Run ./scripts/setup.sh first.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
    echo "No virtual environment found. Run ./scripts/setup.sh first." >&2
    exit 1
fi
. .venv/bin/activate
python -m pytest -q
pyinstaller \
  --noconfirm \
  --name FlowState \
  --onefile \
  --windowed \
  --paths src \
  --collect-submodules flow_state \
  --add-data "src/flow_state/resources/bell.wav:flow_state/resources" \
  src/flow_state/__main__.py
echo "Build complete: ./dist/FlowState"
