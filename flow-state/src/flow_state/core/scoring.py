"""Calculation & reward rules for Flow State.

Every number the app shows about progress comes from ONE policy object.
To change how progress / rewards are computed, subclass ScoringPolicy
(or edit DefaultScoringPolicy) and register it in get_policy().
No UI or database code needs to change.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionResult:
    """Outcome of one focus period, produced by the policy."""
    fraction: float        # part of a full work session (0..1), 2 decimals
    focus_seconds: int     # real focused seconds to store in history
    reward: float          # what is added to task.completed_sessions (🍅)


class ScoringPolicy:
    """Base policy. Override any method to change the rules."""

    name = "base"

    # ---- focus sessions -------------------------------------------------
    def session_fraction(self, elapsed_seconds: float, full_seconds: float) -> float:
        if full_seconds <= 0:
            return 0.0
        return round(max(0.0, min(1.0, elapsed_seconds / full_seconds)), 2)

    def evaluate_session(self, fraction: float, work_seconds: int) -> SessionResult:
        fraction = round(max(0.0, min(1.0, float(fraction))), 2)
        seconds = max(0, round(fraction * work_seconds))
        return SessionResult(fraction, seconds, self.reward_for(fraction))

    def reward_for(self, fraction: float) -> float:
        """Tomatoes earned for a session. Default: proportional."""
        return round(fraction, 2)

    # ---- analytics ------------------------------------------------------
    @staticmethod
    def percent(part: float, whole: float) -> int:
        return min(100, round(part * 100 / whole)) if whole else 0

    def task_rate(self, done: int, total: int) -> int:
        return self.percent(done, total)

    def estimated_minutes(self, estimated_sessions: float, work_minutes: int) -> float:
        return float(estimated_sessions or 0) * work_minutes

    def remaining_minutes(self, total_minutes: float, elapsed_estimated_minutes: float) -> float:
        return max(0.0, total_minutes - elapsed_estimated_minutes)

    def time_rate(self, elapsed_estimated_minutes: float, total_minutes: float) -> int:
        return self.percent(elapsed_estimated_minutes, total_minutes)


class DefaultScoringPolicy(ScoringPolicy):
    """Current Flow State behaviour (identical to v1)."""
    name = "default"


class FullSessionsOnlyPolicy(ScoringPolicy):
    """Example alternative: only a finished session (>= 100%) earns a tomato."""
    name = "full_sessions_only"

    def reward_for(self, fraction: float) -> float:
        return 1.0 if fraction >= 1.0 else 0.0


POLICIES = {p.name: p for p in (DefaultScoringPolicy, FullSessionsOnlyPolicy)}


def get_policy(name: str = "default") -> ScoringPolicy:
    return POLICIES.get(name, DefaultScoringPolicy)()
