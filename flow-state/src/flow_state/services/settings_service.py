class SettingsService:
    def __init__(self, db):
        self.db = db

    def all(self) -> dict:
        return self.db.get_settings()

    def get(self, key, default=None):
        return self.all().get(key, default)

    def get_int(self, key, default):
        try:
            return int(self.get(key, default))
        except (TypeError, ValueError):
            return default

    def work_minutes(self) -> int:
        return max(1, self.get_int("work_duration", 25))

    def set(self, key, value):
        self.db.update_setting(key, value)

    def update(self, values: dict):
        self.db.update_settings(values)
