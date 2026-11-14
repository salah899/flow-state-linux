# Flow State: Technical Audit Report (v1)

## Implemented
- Renamed the complete product identity from Focus To-Do to Flow State.
- Added 12 selectable languages: Arabic, English, French, German, Spanish, Italian, Portuguese, Turkish, Russian, Simplified Chinese, Japanese, and Korean.
- Arabic uses RTL; all other included languages use LTR.
- Added dark-mode styling for date/time editors and their controls.
- Added theme-aware checkbox indicators for checked, unchecked, hover, and disabled states.
- Preserved Light, Dark, and System appearance modes.

## Fixed bugs
1. White date and time fields in Dark Mode: fixed by styling QDateEdit, QTimeEdit, and QDateTimeEdit.
2. White native checkboxes in Dark Mode: fixed with theme-aware indicators.
3. Inconsistent product name across window, app metadata, tray, README, and build instructions: centralized under Flow State naming.
4. Western languages previously inherited RTL: language selection now updates direction.
5. Historical focus duration accuracy: new sessions use recorded focus seconds instead of recalculating from a later timer duration.
6. Existing completed tasks without completion timestamps: migrated safely with an initial timestamp so analytics do not fail.

## Known limitations
- Historical sessions created before focus_sessions existed cannot be assigned to their true original dates because that information was never stored.
- A packaged build must be created on its target OS. Linux builds do not produce native Windows or macOS binaries.
- Translation is runtime UI localization. User-created task and folder names are intentionally not translated.

## Supported desktop targets
- Linux: current primary target (Ubuntu, Debian, Linux Mint, openSUSE, ...).
- Windows: Windows 10 and Windows 11.
- macOS: macOS 13 or later, Intel and Apple Silicon.
