"""Filesystem locations: user data directory and bundled resources."""
import os
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
LEGACY_APP_DIR = Path.home() / ".focus-todo"


def app_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "FlowState"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Flow State"
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "flow-state"


APP_DIR = app_data_dir()
DB_PATH = APP_DIR / "data.db"


def resource_path(name: str) -> str:
    """Path to a file in flow_state/resources (works with PyInstaller too)."""
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS) / "flow_state" / "resources" / name)
    return str(PACKAGE_DIR / "resources" / name)
