"""Prepare subtasks: a task may have a parent task.
Top-level tasks have parent_id = NULL. Deleting a parent deletes its subtasks."""
VERSION = 2


def upgrade(conn):
    from flow_state.data.migrations import column_names
    if "parent_id" not in column_names(conn, "tasks"):
        conn.execute("ALTER TABLE tasks ADD COLUMN parent_id INTEGER DEFAULT NULL "
                     "REFERENCES tasks(id) ON DELETE CASCADE")
    if "position" not in column_names(conn, "tasks"):
        conn.execute("ALTER TABLE tasks ADD COLUMN position INTEGER DEFAULT 0")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id)")
