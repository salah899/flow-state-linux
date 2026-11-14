# Flow State Final Bug Report (v1)

## Fixed
- Replaced translation-over-translation behavior with canonical source recovery, so repeated language switches work.
- Expanded translation coverage for every Arabic UI literal. User-created task and folder names remain untouched.
- Added runtime retranslation after task-list, analytics, calendar, and dashboard refreshes.
- Full Dark Mode styling for combo boxes, including popup lists, selected rows, dropdown areas, disabled state, and text colors.
- Calendar: active tasks appear throughout their scheduled range; completed tasks appear only on completed_at.
- Elapsed-time analytics use all actual focus_seconds. Remaining time and rate use only focus tied to estimated tasks.
- Removed misleading backfill of old sessions and old completion dates.

## Data limitation
Sessions recorded before focus_sessions existed have no trustworthy day. They remain in task totals but are absent from daily history.

## Regression tests (now automated in tests/)
- Repeated en > fr > de > ja switching.
- Completed task shown only on completion day; active task across its range.
- Actual focus includes unestimated tasks; rate and remaining use estimated tasks only.
