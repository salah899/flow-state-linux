# Flow State

Linux desktop Pomodoro + task manager — Python, PySide6, SQLite.

## Quick start
```bash
./scripts/setup.sh      # once: creates .venv, installs PySide6 + pytest + pyinstaller
./scripts/run.sh        # start the app
./scripts/test.sh       # run tests (do this before every increment)
./scripts/build.sh      # tests + standalone ./dist/FlowState
./scripts/dump_project.sh   # regenerate PROJECT_SOURCE.txt (whole project in one .txt)
```
Manual run: `PYTHONPATH=src python -m flow_state`

Your data stays in `~/.local/share/flow-state/data.db` (unchanged from v1).
Old databases are upgraded automatically and safely by versioned migrations.

## Layout
```
src/flow_state/
├── __main__.py / app.py     entry point
├── paths.py                 data dir + bundled resources
├── core/                    pure logic (no DB, no widgets)
│   ├── timer.py             PomodoroTimer
│   └── scoring.py           ★ calculation & reward rules
├── data/                    SQL only
│   ├── database.py
│   └── migrations/          ★ 001_initial, 002_subtasks, ...
├── services/                business layer — the ONLY thing the UI calls
│   ├── task_service.py      ★ includes subtasks API
│   ├── focus_service.py
│   ├── analytics_service.py
│   ├── folder_service.py
│   └── settings_service.py
├── i18n/
│   ├── __init__.py          tr(), translate_tree()
│   └── locales/             ★ one file per language (auto-discovered)
├── ui/
│   ├── main_window.py  tray.py  theme.py  formatting.py
│   ├── pages/               home, analytics, calendar
│   ├── widgets/             task_list, folder_panel, charts, timer_ring
│   └── dialogs/             task_edit, settings, choose_task
└── resources/bell.wav
tests/                       pytest (no display needed except test_timer)
docs/                        architecture guide + history reports
```
★ = extension points. See **docs/ARCHITECTURE.md** for step-by-step recipes.
