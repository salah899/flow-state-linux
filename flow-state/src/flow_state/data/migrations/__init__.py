"""Versioned schema migrations.

Each migration is a module named NNN_description.py exposing
    VERSION: int
    def upgrade(conn): ...
The current version is stored in `PRAGMA user_version`.
To add a migration: create the next numbered file and append it to MIGRATIONS.
Never edit a migration that has already been released.
"""
import importlib

_MODULES = [
    "001_initial",
    "002_subtasks",
]

MIGRATIONS = [importlib.import_module(f"{__name__}.{m}") for m in _MODULES]


def current_version(conn) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrate(conn) -> int:
    version = current_version(conn)
    for module in sorted(MIGRATIONS, key=lambda m: m.VERSION):
        if module.VERSION > version:
            with conn:
                module.upgrade(conn)
                conn.execute(f"PRAGMA user_version = {int(module.VERSION)}")
            version = module.VERSION
    return version


def column_names(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
