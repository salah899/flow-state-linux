# Flow State Regression Report (v1)

## Fixed in this build
- The running-state label is translated at the moment it is generated.
- Folder-button text remains in the selected UI language after toggling the folder panel.
- Priority cell values are translated when each row is built; task/folder names stay unchanged.
- Date ranges, editor date patterns and 12/24-hour display follow the selected language locale.
- Deleting a task deletes its focus-session history; deleting a folder deletes history for all its tasks.
- Reopening a completed task clears its completion date.

## Statistics interaction test
(Automated as tests/test_services.py::test_statistics_scenario_from_regression_report)
Expected final state after deleting the unestimated task:
- Total tasks 1, completed 1, completion rate 100%
- Total estimated 100 min, elapsed 25 min, remaining 75 min, time rate 25%
- Weekly focus 1500 seconds. After deleting the final task everything returns to zero.
