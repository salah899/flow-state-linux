# Changelog

## 2.0.0 — Restructure
- New package layout `src/flow_state/` (core / data / services / i18n / ui).
- UI talks only to services; SQL removed from widgets.
- Versioned migrations with `PRAGMA user_version`; v1 databases upgrade automatically.
- Scoring policy (`core/scoring.py`) + Settings option "نظام الحساب".
- Subtasks data layer (`parent_id`) + service API (UI is the next increment).
- One file per language, auto-discovered.
- `TaskEditDialog`, `HomePage`, `ChooseTaskDialog`, formatting helpers split into own files.
- Removed unused `stats_panel.py`, unused tags code paths, unused `resources.qrc`.
- Fixed: folder delete dialog had mixed Arabic/English text.
- Fixed: `build.sh` now bundles all modules and runs tests first.
- Added pytest suite (scoring, migrations, services, i18n, timer).
- Added `scripts/dump_project.sh` → `PROJECT_SOURCE.txt`.
