"""SQLite data-access layer. Only SQL lives here; no business rules, no UI."""
import shutil
import sqlite3
from pathlib import Path

from flow_state.data.migrations import migrate
from flow_state.paths import APP_DIR, DB_PATH, LEGACY_APP_DIR

DEFAULT_SETTINGS = {
    "work_duration": "25",
    "short_break": "5",
    "long_break": "15",
    "sessions_before_long_break": "4",
    "theme_mode": "system",
    "language": "ar",
    "scoring_policy": "default",
}


def _migrate_legacy_data():
    """One-time, non-destructive copy of the old ~/.focus-todo database."""
    if DB_PATH.exists():
        return
    legacy_db = LEGACY_APP_DIR / "data.db"
    if not legacy_db.exists():
        return
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_db, LEGACY_APP_DIR / "data.db.pre-migration-backup")
        shutil.copy2(legacy_db, DB_PATH)
    except OSError:
        pass


class Database:
    def __init__(self, db_path=DB_PATH):
        if str(db_path) != ":memory:":
            db_path = Path(db_path)
            if db_path == DB_PATH:
                _migrate_legacy_data()
            db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.schema_version = migrate(self.conn)
        self.insert_default_settings()
        self.ensure_default_folder()

    # ------------------------------------------------------------ settings
    def insert_default_settings(self):
        with self.conn:
            for key, value in DEFAULT_SETTINGS.items():
                self.conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    def get_settings(self):
        return {r["key"]: r["value"] for r in self.conn.execute("SELECT key, value FROM settings")}

    def update_setting(self, key, value):
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    def update_settings(self, settings: dict):
        with self.conn:
            for key, value in settings.items():
                self.conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    # ------------------------------------------------------------- folders
    def ensure_default_folder(self):
        if self.conn.execute("SELECT COUNT(*) FROM folders").fetchone()[0] == 0:
            self.add_folder("Inbox")

    def get_folders(self):
        return self.conn.execute("SELECT id, name FROM folders ORDER BY name COLLATE NOCASE").fetchall()

    def add_folder(self, name):
        name = name.strip()
        if not name:
            return None
        with self.conn:
            return self.conn.execute("INSERT INTO folders (name) VALUES (?)", (name,)).lastrowid

    def get_folder_name(self, folder_id):
        row = self.conn.execute("SELECT name FROM folders WHERE id = ?", (folder_id,)).fetchone()
        return row["name"] if row else None

    def delete_folder(self, folder_id):
        with self.conn:
            self.conn.execute("DELETE FROM focus_sessions WHERE task_id IN "
                              "(SELECT id FROM tasks WHERE folder_id = ?)", (folder_id,))
            self.conn.execute("DELETE FROM folders WHERE id = ?", (folder_id,))

    # --------------------------------------------------------------- tasks
    def add_task(self, folder_id, title, priority=0, notes="", start_at=None, end_at=None,
                 estimated_sessions=None, parent_id=None):
        title = title.strip()
        if not title:
            return None
        with self.conn:
            cur = self.conn.execute("""
                INSERT INTO tasks (folder_id, title, priority, notes, due_at, start_at, end_at,
                                   estimated_sessions, parent_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (folder_id, title, priority, notes, end_at, start_at, end_at, estimated_sessions, parent_id))
        return cur.lastrowid

    def update_task(self, task_id, title, priority, notes="", start_at=None, end_at=None, estimated_sessions=None):
        with self.conn:
            self.conn.execute("""
                UPDATE tasks SET title = ?, priority = ?, notes = ?, due_at = ?, start_at = ?, end_at = ?,
                                 estimated_sessions = ?
                WHERE id = ?""",
                (title.strip(), priority, notes, end_at, start_at, end_at, estimated_sessions, task_id))

    def delete_task(self, task_id):
        with self.conn:
            # history of the task and all its subtasks
            self.conn.execute("""
                WITH RECURSIVE tree(id) AS (
                    SELECT ? UNION ALL SELECT t.id FROM tasks t JOIN tree ON t.parent_id = tree.id)
                DELETE FROM focus_sessions WHERE task_id IN (SELECT id FROM tree)""", (task_id,))
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.execute("DELETE FROM tags WHERE id NOT IN (SELECT DISTINCT tag_id FROM task_tags)")

    def set_completed(self, task_id, completed):
        flag = 1 if completed else 0
        with self.conn:
            self.conn.execute("""
                UPDATE tasks
                SET completed = ?,
                    completed_at = CASE WHEN ? THEN datetime('now', 'localtime') ELSE NULL END,
                    is_current = CASE WHEN ? THEN 0 ELSE is_current END
                WHERE id = ?""", (flag, flag, flag, task_id))

    def set_current_task(self, task_id):
        with self.conn:
            self.conn.execute("UPDATE tasks SET is_current = 0")
            self.conn.execute("UPDATE tasks SET is_current = 1 WHERE id = ?", (task_id,))

    def clear_current_task(self):
        with self.conn:
            self.conn.execute("UPDATE tasks SET is_current = 0")

    def get_current_task(self):
        return self.conn.execute("SELECT * FROM tasks WHERE is_current = 1 LIMIT 1").fetchone()

    def get_task(self, task_id):
        return self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    def get_subtasks(self, parent_id):
        return self.conn.execute("SELECT * FROM tasks WHERE parent_id = ? ORDER BY position, id",
                                 (parent_id,)).fetchall()

    def get_tasks(self, folder_id=None, priority_filter=None, date_filter=None,
                  selected_date=None, completed_filter=None, top_level_only=True):
        query = "SELECT tasks.* FROM tasks WHERE 1 = 1"
        params = []
        if top_level_only:
            query += " AND tasks.parent_id IS NULL"
        if folder_id is not None:
            query += " AND tasks.folder_id = ?"
            params.append(folder_id)
        if priority_filter is not None:
            query += " AND tasks.priority = ?"
            params.append(priority_filter)
        today = "date('now', 'localtime')"
        if selected_date:
            if completed_filter is True:
                query += " AND date(tasks.completed_at) = date(?)"
                params.append(selected_date)
            else:
                query += (" AND date(COALESCE(tasks.start_at, tasks.due_at)) <= date(?)"
                          " AND date(COALESCE(tasks.end_at, tasks.due_at)) >= date(?)")
                params.extend([selected_date, selected_date])
        elif date_filter == "today":
            query += f" AND date(tasks.due_at) = {today}"
        elif date_filter == "upcoming":
            query += f" AND date(tasks.due_at) > {today}"
        elif date_filter == "overdue":
            query += " AND datetime(tasks.due_at) < datetime('now', 'localtime')"
        elif date_filter == "completed":
            completed_filter = True
        if completed_filter is not None:
            query += " AND tasks.completed = ?"
            params.append(1 if completed_filter else 0)
        query += " ORDER BY completed ASC, due_at IS NULL ASC, due_at ASC, priority DESC, id DESC"
        return self.conn.execute(query, params).fetchall()

    # -------------------------------------------------------- focus history
    def add_focus_session(self, task_id, fraction, focus_seconds, reward):
        with self.conn:
            self.conn.execute("UPDATE tasks SET completed_sessions = "
                              "ROUND(COALESCE(completed_sessions, 0) + ?, 2) WHERE id = ?", (reward, task_id))
            self.conn.execute("INSERT INTO focus_sessions(task_id, fraction, focus_seconds) VALUES (?, ?, ?)",
                              (task_id, fraction, max(0, int(focus_seconds))))

    def get_task_focus_seconds(self, task_id):
        row = self.conn.execute("SELECT COALESCE(SUM(focus_seconds), 0) FROM focus_sessions WHERE task_id = ?",
                                (task_id,)).fetchone()
        return int(row[0])

    # ------------------------------------------------------- raw analytics
    def analytics_raw(self):
        """Raw totals only. Calculations are done by the scoring policy."""
        c = self.conn
        tasks = c.execute("SELECT COUNT(*) total, COALESCE(SUM(completed),0) done FROM tasks "
                          "WHERE parent_id IS NULL").fetchone()
        estimated = c.execute("SELECT COALESCE(SUM(estimated_sessions),0) FROM tasks "
                              "WHERE estimated_sessions IS NOT NULL").fetchone()[0]
        focus_all = c.execute("SELECT COALESCE(SUM(focus_seconds),0) FROM focus_sessions").fetchone()[0]
        focus_estimated = c.execute("""
            SELECT COALESCE(SUM(fs.focus_seconds),0) FROM focus_sessions fs
            JOIN tasks t ON t.id = fs.task_id WHERE t.estimated_sessions IS NOT NULL""").fetchone()[0]
        return {"total_tasks": int(tasks["total"]), "done_tasks": int(tasks["done"]),
                "estimated_sessions": float(estimated or 0), "focus_seconds": int(focus_all or 0),
                "estimated_focus_seconds": int(focus_estimated or 0)}

    def weekly_analytics(self):
        return self.conn.execute("""
            WITH RECURSIVE days(d) AS (
                SELECT date('now','localtime','-6 days')
                UNION ALL SELECT date(d,'+1 day') FROM days WHERE d < date('now','localtime'))
            SELECT d,
              (SELECT COUNT(*) FROM tasks WHERE completed=1 AND parent_id IS NULL
                                           AND date(completed_at)=d) completed_tasks,
              (SELECT COALESCE(SUM(focus_seconds),0) FROM focus_sessions WHERE date(created_at)=d) focus_seconds
            FROM days ORDER BY d""").fetchall()

    def task_counts(self):
        row = self.conn.execute("""
            SELECT
              SUM(CASE WHEN date(due_at) = date('now','localtime') AND completed=0 THEN 1 ELSE 0 END) today,
              SUM(CASE WHEN date(due_at) > date('now','localtime') AND completed=0 THEN 1 ELSE 0 END) upcoming,
              SUM(CASE WHEN datetime(due_at) < datetime('now','localtime') AND completed=0 THEN 1 ELSE 0 END) overdue,
              SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) completed
            FROM tasks WHERE parent_id IS NULL""").fetchone()
        return {k: int(row[k] or 0) for k in ("today", "upcoming", "overdue", "completed")}

    def close(self):
        self.conn.close()
