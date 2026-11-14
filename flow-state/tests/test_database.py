import sqlite3

from flow_state.data.database import Database
from flow_state.data.migrations import current_version
from flow_state.services.task_service import TaskData


def test_fresh_database_is_fully_migrated():
    db = Database(":memory:")
    assert current_version(db.conn) == 2
    assert db.get_folders()[0]["name"] == "Inbox"


def test_v1_database_upgrades_without_data_loss(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE folders (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, folder_id INTEGER, title TEXT NOT NULL,"
                 " priority INTEGER DEFAULT 0, completed INTEGER DEFAULT 0, is_current INTEGER DEFAULT 0,"
                 " notes TEXT DEFAULT '', due_at TEXT)")
    conn.execute("INSERT INTO folders VALUES (1, 'Work')")
    conn.execute("INSERT INTO tasks (folder_id, title, due_at) VALUES (1, 'old task', '2026-01-01T10:00:00')")
    conn.commit()
    conn.close()
    db = Database(path)
    task = db.get_tasks()[0]
    assert task["title"] == "old task"
    assert task["start_at"] == "2026-01-01T10:00:00"
    assert task["parent_id"] is None


def test_delete_task_removes_focus_history(services):
    tid = services.tasks.create(services.folders.default_id(), TaskData("t", estimated_sessions=2))
    services.focus.record(tid, 1.0, 1500)
    services.tasks.delete(tid)
    assert services.analytics.summary()["elapsed_minutes"] == 0
