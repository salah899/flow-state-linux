"""Runtime UI localization.

Source strings in the code are Arabic. `en` maps Arabic -> English, and every
other language maps English -> target. Missing translations fall back to
English (never to Arabic). Qt is imported lazily so this module is testable
without a display.
"""
from functools import lru_cache

from flow_state.i18n.locales import load_packs

PACKS = load_packs()
SOURCE = "ar"
PIVOT = "en"
LANGUAGES = {code: pack.NAME for code, pack in PACKS.items()}
RTL = {code for code, pack in PACKS.items() if pack.RTL}
_current = SOURCE


def _pivot():
    return PACKS[PIVOT].MESSAGES


def set_language(code):
    global _current
    _current = code if code in PACKS else SOURCE


def language():
    return _current


def is_rtl(code=None):
    return (code or _current) in RTL


def qt_locale_name(code=None):
    return getattr(PACKS.get(code or _current), "QT_LOCALE", "en_US")


def tr(text):
    """Translate one Arabic source string to the current language."""
    if _current == SOURCE:
        return text
    english = _pivot().get(text, text)
    if _current == PIVOT:
        return english
    return PACKS[_current].MESSAGES.get(english, english)


@lru_cache(maxsize=1)
def _reverse_index():
    """visible text in ANY language -> Arabic source (prevents translating
    over already-translated text when switching languages repeatedly)."""
    reverse = {}
    for source, english in _pivot().items():
        reverse[source] = source
        reverse[english] = source
        for code, pack in PACKS.items():
            if code in (SOURCE, PIVOT):
                continue
            value = pack.MESSAGES.get(english)
            if value:
                reverse[value] = source
    return sorted(reverse.items(), key=lambda kv: len(kv[0]), reverse=True)


@lru_cache(maxsize=1)
def _sources_by_length():
    return sorted(_pivot(), key=len, reverse=True)


def translate_text(text):
    """Translate a full visible string (may contain several source phrases)."""
    if not text:
        return text
    result = text
    for visible, source in _reverse_index():
        if visible and visible in result:
            result = result.replace(visible, source)
    if _current == SOURCE:
        return result
    for source in _sources_by_length():
        if source in result:
            result = result.replace(source, tr(source))
    return result


def translate_tree(root):
    """Retranslate every label/button/combo/placeholder/header under root."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QGroupBox, QLabel, QLineEdit, QTableWidget

    root.setLayoutDirection(Qt.RightToLeft if is_rtl() else Qt.LeftToRight)
    if hasattr(root, "windowTitle") and root.windowTitle():
        root.setWindowTitle(translate_text(root.windowTitle()))
    widgets = set()
    for cls in (QLabel, QAbstractButton, QGroupBox):
        widgets.update(root.findChildren(cls))
    for widget in widgets:
        if isinstance(widget, QGroupBox):
            widget.setTitle(translate_text(widget.title()))
        else:
            widget.setText(translate_text(widget.text()))
    for combo in root.findChildren(QComboBox):
        for i in range(combo.count()):
            combo.setItemText(i, translate_text(combo.itemText(i)))
    for line in root.findChildren(QLineEdit):
        line.setPlaceholderText(translate_text(line.placeholderText()))
    for table in root.findChildren(QTableWidget):
        for col in range(table.columnCount()):
            item = table.horizontalHeaderItem(col)
            if item:
                item.setText(translate_text(item.text()))
