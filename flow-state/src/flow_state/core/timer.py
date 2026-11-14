from PySide6.QtCore import QObject, QTimer, Signal

from flow_state.core.scoring import ScoringPolicy, get_policy


class PomodoroTimer(QObject):
    tick = Signal(str, int)
    mode_changed = Signal(str, int)
    finished = Signal(str)
    skipped = Signal(str)
    running_changed = Signal(bool)
    period_ended = Signal(str, float)

    VALID_MODES = {"work", "short_break", "long_break"}

    def __init__(self, settings: dict, policy: ScoringPolicy = None):
        super().__init__()
        self.policy = policy or get_policy()
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)
        self.settings = {}
        self.mode = "work"
        self.remaining_seconds = 0
        self.completed_work_sessions = 0
        self.update_settings(settings)
        self.remaining_seconds = self.duration_for_mode(self.mode)

    def update_settings(self, settings: dict):
        def positive_int(key, default):
            try:
                return max(1, int(settings.get(key, default)))
            except (TypeError, ValueError):
                return default
        self.settings = {
            "work_duration": positive_int("work_duration", 25),
            "short_break": positive_int("short_break", 5),
            "long_break": positive_int("long_break", 15),
            "sessions_before_long_break": positive_int("sessions_before_long_break", 4),
        }

    def duration_for_mode(self, mode):
        if mode == "work":
            return self.settings["work_duration"] * 60
        if mode == "short_break":
            return self.settings["short_break"] * 60
        if mode == "long_break":
            return self.settings["long_break"] * 60
        raise ValueError(f"Unknown timer mode: {mode}")

    def start(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.duration_for_mode(self.mode)
            self.emit_state()
        if not self.timer.isActive():
            self.timer.start()
            self.running_changed.emit(True)

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.running_changed.emit(False)

    def is_running(self):
        return self.timer.isActive()

    def reset(self, reset_sessions=False):
        self.pause()
        self.mode = "work"
        if reset_sessions:
            self.completed_work_sessions = 0
        self.remaining_seconds = self.duration_for_mode(self.mode)
        self.mode_changed.emit(self.mode, self.completed_work_sessions)
        self.emit_state()

    def reset_current_period(self):
        self.pause()
        self.remaining_seconds = self.duration_for_mode(self.mode)
        self.mode_changed.emit(self.mode, self.completed_work_sessions)
        self.emit_state()

    def set_mode(self, mode):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unknown timer mode: {mode}")
        self.pause()
        self.mode = mode
        self.remaining_seconds = self.duration_for_mode(mode)
        self.mode_changed.emit(self.mode, self.completed_work_sessions)
        self.emit_state()

    def skip(self):
        was_running = self.timer.isActive()
        self.skipped.emit(self.mode)
        self._move_to_next_period(completed=False)
        if was_running:
            self.timer.start()

    def finish_early(self):
        old_mode = self.mode
        full = self.duration_for_mode(old_mode)
        elapsed = max(0, full - self.remaining_seconds)
        fraction = self.policy.session_fraction(elapsed, full) if old_mode == "work" else 0.0
        self.pause()
        self.period_ended.emit(old_mode, fraction)
        self._move_to_next_period(completed=False)

    def _on_tick(self):
        if self.remaining_seconds <= 0:
            return
        self.remaining_seconds -= 1
        if self.remaining_seconds == 0:
            old_mode = self.mode
            self.period_ended.emit(old_mode, 1.0 if old_mode == "work" else 0.0)
            self.finished.emit(old_mode)
            self._move_to_next_period(completed=True)
        else:
            self.emit_state()

    def _move_to_next_period(self, completed):
        if self.mode == "work":
            if completed:
                self.completed_work_sessions += 1
            if completed and self.completed_work_sessions % self.settings["sessions_before_long_break"] == 0:
                self.mode = "long_break"
            else:
                self.mode = "short_break"
        else:
            self.mode = "work"
        self.remaining_seconds = self.duration_for_mode(self.mode)
        self.mode_changed.emit(self.mode, self.completed_work_sessions)
        self.emit_state()

    def formatted_time(self):
        minutes, seconds = divmod(max(0, self.remaining_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def emit_state(self):
        self.tick.emit(self.formatted_time(), self.remaining_seconds)
