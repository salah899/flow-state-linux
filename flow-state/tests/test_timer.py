import pytest

pytest.importorskip("PySide6")

from flow_state.core.timer import PomodoroTimer  # noqa: E402


def test_finish_early_emits_fraction():
    t = PomodoroTimer({"work_duration": 10})
    got = []
    t.period_ended.connect(lambda mode, f: got.append((mode, f)))
    t.remaining_seconds = 300
    t.finish_early()
    assert got == [("work", 0.5)]
    assert t.mode == "short_break"


def test_long_break_after_n_sessions():
    t = PomodoroTimer({"sessions_before_long_break": 2})
    t._move_to_next_period(True)
    t.set_mode("work")
    t._move_to_next_period(True)
    assert t.mode == "long_break"
