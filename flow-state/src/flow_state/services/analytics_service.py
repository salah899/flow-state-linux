import datetime


class AnalyticsService:
    def __init__(self, db, settings, policy):
        self.db = db
        self.settings = settings
        self.policy = policy

    def summary(self):
        raw = self.db.analytics_raw()
        p = self.policy
        total_minutes = p.estimated_minutes(raw["estimated_sessions"], self.settings.work_minutes())
        elapsed = raw["focus_seconds"] / 60
        elapsed_estimated = raw["estimated_focus_seconds"] / 60
        return {
            "total_tasks": raw["total_tasks"],
            "done_tasks": raw["done_tasks"],
            "task_rate": p.task_rate(raw["done_tasks"], raw["total_tasks"]),
            "total_minutes": total_minutes,
            "elapsed_minutes": elapsed,
            "remaining_minutes": p.remaining_minutes(total_minutes, elapsed_estimated),
            "time_rate": p.time_rate(elapsed_estimated, total_minutes),
        }

    def counts(self):
        return self.db.task_counts()

    def weekly(self):
        """List of dicts: date, weekday (0=Sunday), completed_tasks, focus_minutes."""
        result = []
        for row in self.db.weekly_analytics():
            d = datetime.date.fromisoformat(row["d"])
            result.append({"date": d, "weekday": (d.weekday() + 1) % 7,
                           "completed_tasks": int(row["completed_tasks"]),
                           "focus_minutes": round(int(row["focus_seconds"]) / 60, 1)})
        return result
