from flow_state.core.scoring import DefaultScoringPolicy, FullSessionsOnlyPolicy, get_policy


def test_fraction_is_clamped_and_rounded():
    p = DefaultScoringPolicy()
    assert p.session_fraction(750, 1500) == 0.5
    assert p.session_fraction(3000, 1500) == 1.0
    assert p.session_fraction(10, 0) == 0.0


def test_default_reward_is_proportional():
    r = DefaultScoringPolicy().evaluate_session(0.5, 1500)
    assert (r.fraction, r.focus_seconds, r.reward) == (0.5, 750, 0.5)


def test_full_sessions_only_policy():
    p = FullSessionsOnlyPolicy()
    assert p.evaluate_session(0.9, 1500).reward == 0.0
    assert p.evaluate_session(1.0, 1500).reward == 1.0
    assert p.evaluate_session(0.9, 1500).focus_seconds == 1350  # real focus still counted


def test_unknown_policy_falls_back_to_default():
    assert get_policy("nope").name == "default"
