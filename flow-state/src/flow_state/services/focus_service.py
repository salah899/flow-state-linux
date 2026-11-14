class FocusService:
    """Records focus periods using the active scoring policy."""

    def __init__(self, db, settings, policy):
        self.db = db
        self.settings = settings
        self.policy = policy

    def work_seconds(self):
        return self.settings.work_minutes() * 60

    def record(self, task_id, fraction, work_seconds=None):
        if task_id is None or fraction <= 0:
            return None
        result = self.policy.evaluate_session(fraction, work_seconds or self.work_seconds())
        self.db.add_focus_session(task_id, result.fraction, result.focus_seconds, result.reward)
        return result

    def task_focus_seconds(self, task_id):
        return self.db.get_task_focus_seconds(task_id)

    def remaining_seconds(self, task, live_seconds=0):
        """Seconds left on a task's estimate, or None if it has no estimate."""
        if not task or task["estimated_sessions"] is None:
            return None
        estimated = int(task["estimated_sessions"]) * self.work_seconds()
        return max(0, round(estimated - self.task_focus_seconds(task["id"]) - live_seconds))

    def estimated_minutes(self, task):
        if not task or task["estimated_sessions"] is None:
            return None
        return self.policy.estimated_minutes(task["estimated_sessions"], self.settings.work_minutes())
