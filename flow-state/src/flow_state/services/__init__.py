"""Business layer. The UI talks ONLY to these services, never to Database."""
from flow_state.core.scoring import get_policy
from flow_state.services.analytics_service import AnalyticsService
from flow_state.services.focus_service import FocusService
from flow_state.services.folder_service import FolderService
from flow_state.services.settings_service import SettingsService
from flow_state.services.task_service import TaskService


class AppServices:
    """Single container passed to every UI component."""

    def __init__(self, db):
        self.db = db
        self.settings = SettingsService(db)
        self.policy = get_policy(self.settings.get("scoring_policy", "default"))
        self.folders = FolderService(db)
        self.tasks = TaskService(db)
        self.focus = FocusService(db, self.settings, self.policy)
        self.analytics = AnalyticsService(db, self.settings, self.policy)

    def reload_policy(self):
        self.policy = get_policy(self.settings.get("scoring_policy", "default"))
        self.focus.policy = self.policy
        self.analytics.policy = self.policy

    def close(self):
        self.db.close()
