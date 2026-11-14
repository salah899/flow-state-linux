# Flow State — Architecture & Extension Guide

## Layers (dependencies point DOWN only)
```
ui  ──►  services  ──►  data (database + migrations)
 │           │
 └──► core ◄─┘          core = timer + scoring (no SQL, no widgets)
i18n is used by ui only.
```
Rules
1. Widgets never import `Database` and never write SQL. They receive one
   `AppServices` object (`services.tasks`, `.focus`, `.analytics`, `.folders`, `.settings`).
2. `database.py` contains SQL only — no percentages, no rewards, no Qt.
3. Every number shown to the user (rewards, rates, remaining time) comes from
   `core/scoring.py`.
4. Schema changes are new migration files; released migrations are never edited.
5. Each increment ends with `./scripts/test.sh` green.

---

## Recipe 1 — Add a language (≈10 minutes, zero code changes)
1. `cp src/flow_state/i18n/locales/fr.py src/flow_state/i18n/locales/nl.py`
2. Edit the header:
   ```python
   CODE = 'nl'; NAME = 'Nederlands'; RTL = False; QT_LOCALE = 'nl_NL'; ORDER = 12
   ```
   (`RTL = True` for Hebrew, Persian, Urdu …)
3. Translate the values of `MESSAGES` (keys are the English strings in `en.py`).
4. `./scripts/test.sh -s` — `test_report_missing_translations` prints what is still missing
   (missing keys fall back to English, never Arabic).
The language appears in Settings automatically.

New UI text? Write it in Arabic in the code, add `'arabic': 'English'` to `en.py`,
then add the English key to the other language files.

---

## Recipe 2 — Subtasks (data layer is READY)
Already done in this version:
- Migration `002_subtasks.py` adds `tasks.parent_id` (+ `position` for ordering).
- Deleting a parent deletes its subtasks and their focus history.
- Main lists / analytics show top-level tasks only.
- API: `services.tasks.add_subtask(parent_id, title)`, `.subtasks(parent_id)`,
  `.subtask_progress(parent_id) -> (done, total)`.
- Tests: `tests/test_services.py::test_subtasks_are_hidden_from_main_list`.

Next increment (UI only):
1. `ui/widgets/subtask_list.py` — small checklist widget (QListWidget with checkboxes)
   using `services.tasks.subtasks / add_subtask / set_completed / delete`.
2. Put it inside `ui/dialogs/task_edit_dialog.py` (only when editing an existing task).
3. In `ui/widgets/task_list.py` show `done/total` next to the title
   using `subtask_progress`.
4. Add the Arabic strings to `en.py` and other locales.
5. Optional rule: auto-complete the parent when all subtasks are done →
   implement in `TaskService.set_completed`, never in the widget.

---

## Recipe 3 — Change the calculation / reward system
All rules live in `core/scoring.py`:

| Method | Controls |
|---|---|
| `session_fraction(elapsed, full)` | how much of a session counts when you press Finish |
| `reward_for(fraction)` | 🍅 added to the task (`completed_sessions`) |
| `evaluate_session(...)` | fraction + real focus seconds + reward together |
| `task_rate`, `time_rate`, `remaining_minutes`, `estimated_minutes` | analytics cards & donut |

Steps:
1. Subclass `ScoringPolicy`, give it a unique `name`, override what you need.
   Example already included: `FullSessionsOnlyPolicy` (only a full session earns 🍅).
2. Register it in `POLICIES`.
3. Add it to `SCORING_CHOICES` in `ui/dialogs/settings_dialog.py` (+ translations).
4. Add tests in `tests/test_scoring.py`.

The user picks the policy in Settings → "نظام الحساب" (saved as `scoring_policy`).
Focus history (`focus_sessions.focus_seconds`) always stores REAL time, so
changing the reward rule never corrupts time statistics.

Ideas for later: XP / levels / streaks → new table via a migration
(`003_rewards.py`), a `RewardService`, and `ScoringPolicy.xp_for(result)`.

---

## Recipe 4 — Change the database schema
1. Create `data/migrations/003_<name>.py` with `VERSION = 3` and `upgrade(conn)`.
2. Append `"003_<name>"` to `_MODULES` in `data/migrations/__init__.py`.
3. Add SQL methods in `database.py`, logic in a service, then UI.
4. Add a test that upgrades an old database (see `tests/test_database.py`).

---

## Sharing the project as one text file
`./scripts/dump_project.sh` writes `PROJECT_SOURCE.txt` with the file tree and every
source file separated by `===== FILE: path =====` lines.
