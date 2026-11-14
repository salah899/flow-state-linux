"""Base schema. Idempotent so databases created by Flow State v1
(which have no user_version) upgrade safely without data loss."""
VERSION = 1


def upgrade(conn):
    from flow_state.data.migrations import column_names
    conn.execute("""CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        folder_id INTEGER,
        title TEXT NOT NULL,
        priority INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        is_current INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        due_at TEXT DEFAULT NULL,
        start_at TEXT DEFAULT NULL,
        end_at TEXT DEFAULT NULL,
        estimated_sessions INTEGER DEFAULT NULL,
        completed_sessions REAL DEFAULT 0,
        completed_at TEXT DEFAULT NULL,
        FOREIGN KEY(folder_id) REFERENCES folders(id) ON DELETE CASCADE)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS task_tags (
        task_id INTEGER, tag_id INTEGER,
        PRIMARY KEY(task_id, tag_id),
        FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
        FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS focus_sessions (
        id INTEGER PRIMARY KEY,
        task_id INTEGER,
        fraction REAL NOT NULL,
        focus_seconds INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT)""")
    # Columns added during v1 development (old databases may miss them).
    existing = column_names(conn, "tasks")
    for name, definition in (("due_at", "TEXT DEFAULT NULL"), ("start_at", "TEXT DEFAULT NULL"),
                             ("end_at", "TEXT DEFAULT NULL"), ("estimated_sessions", "INTEGER DEFAULT NULL"),
                             ("completed_sessions", "REAL DEFAULT 0"), ("completed_at", "TEXT DEFAULT NULL")):
        if name not in existing:
            conn.execute(f"ALTER TABLE tasks ADD COLUMN {name} {definition}")
    conn.execute("UPDATE tasks SET start_at = COALESCE(start_at, due_at), "
                 "end_at = COALESCE(end_at, due_at) WHERE due_at IS NOT NULL")
