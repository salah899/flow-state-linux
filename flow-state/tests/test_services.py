from flow_state.services.task_service import TaskData


def test_statistics_scenario_from_regression_report(services):
    folder = services.folders.default_id()
    est = services.tasks.create(folder, TaskData("estimated", estimated_sessions=4))
    free = services.tasks.create(folder, TaskData("free"))
    services.focus.record(est, 1.0, 1500)
    services.focus.record(free, 1.0, 1500)
    services.tasks.set_completed(est, True)
    services.tasks.delete(free)
    s = services.analytics.summary()
    assert (s["total_tasks"], s["done_tasks"], s["task_rate"]) == (1, 1, 100)
    assert s["total_minutes"] == 100
    assert s["elapsed_minutes"] == 25
    assert s["remaining_minutes"] == 75
    assert s["time_rate"] == 25
    assert sum(d["focus_minutes"] for d in services.analytics.weekly()) == 25


def test_partial_session_reward(services):
    tid = services.tasks.create(services.folders.default_id(), TaskData("t"))
    services.focus.record(tid, 0.5, 1500)
    assert services.tasks.get(tid)["completed_sessions"] == 0.5


def test_remaining_seconds(services):
    tid = services.tasks.create(services.folders.default_id(), TaskData("t", estimated_sessions=2))
    services.focus.record(tid, 1.0, 1500)
    assert services.focus.remaining_seconds(services.tasks.get(tid), live_seconds=100) == 1400


def test_subtasks_are_hidden_from_main_list(services):
    parent = services.tasks.create(services.folders.default_id(), TaskData("parent"))
    services.tasks.add_subtask(parent, "child 1")
    child2 = services.tasks.add_subtask(parent, "child 2")
    services.tasks.set_completed(child2, True)
    assert [t["title"] for t in services.tasks.list()] == ["parent"]
    assert services.tasks.subtask_progress(parent) == (1, 2)
    services.tasks.delete(parent)
    assert services.tasks.subtasks(parent) == []


def test_reopening_task_clears_completion_date(services):
    tid = services.tasks.create(services.folders.default_id(), TaskData("t"))
    services.tasks.set_completed(tid, True)
    services.tasks.set_completed(tid, False)
    assert services.tasks.get(tid)["completed_at"] is None
