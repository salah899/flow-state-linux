from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskData:
    """Values coming from the task editor."""
    title: str
    priority: int = -1
    notes: str = ""
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    estimated_sessions: Optional[int] = None


class TaskService:
    def __init__(self, db):
        self.db = db

    # queries
    def get(self, task_id):
        return self.db.get_task(task_id)

    def list(self, folder_id=None, priority=None, date_filter=None, selected_date=None, completed=None):
        return self.db.get_tasks(folder_id, priority, date_filter, selected_date, completed)

    def incomplete(self):
        return [t for t in self.db.get_tasks() if not t["completed"]]

    def current(self):
        return self.db.get_current_task()

    # commands
    def create(self, folder_id, data: TaskData, parent_id=None):
        return self.db.add_task(folder_id, data.title, data.priority, data.notes, data.start_at,
                                data.end_at, data.estimated_sessions, parent_id)

    def update(self, task_id, data: TaskData):
        self.db.update_task(task_id, data.title, data.priority, data.notes, data.start_at,
                            data.end_at, data.estimated_sessions)

    def delete(self, task_id):
        self.db.delete_task(task_id)

    def set_completed(self, task_id, completed: bool):
        self.db.set_completed(task_id, completed)

    def set_current(self, task_id):
        self.db.set_current_task(task_id)

    def schedule_on_day(self, task_id, day_iso: str):
        """Put an existing task on one calendar day (yyyy-MM-dd)."""
        task = self.get(task_id)
        if not task:
            return
        self.update(task_id, TaskData(task["title"], task["priority"], task["notes"] or "",
                                      day_iso + "T00:00:00", day_iso + "T23:59:00",
                                      task["estimated_sessions"]))

    # ---- subtasks (data layer ready; UI can be added in a later increment)
    def subtasks(self, parent_id):
        return self.db.get_subtasks(parent_id)

    def add_subtask(self, parent_id, title, priority=-1):
        parent = self.get(parent_id)
        if not parent:
            return None
        return self.create(parent["folder_id"], TaskData(title, priority), parent_id=parent_id)

    def subtask_progress(self, parent_id):
        subs = self.subtasks(parent_id)
        done = sum(1 for s in subs if s["completed"])
        return done, len(subs)
