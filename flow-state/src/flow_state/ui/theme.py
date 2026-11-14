from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

LIGHT = {
    "bg": "#f7f8fc", "surface": "#ffffff", "surface2": "#f3f5fb", "text": "#11162d",
    "muted": "#6d7690", "border": "#e5e8f2", "primary": "#5964ed", "primary2": "#777ffc",
    "success": "#17a673", "warning": "#f39a32", "danger": "#ef5261", "shadow": "#dfe3f0",
}
DARK = {
    "bg": "#111522", "surface": "#1a2030", "surface2": "#22293b", "text": "#f7f8ff",
    "muted": "#a8b0c7", "border": "#30384d", "primary": "#7882ff", "primary2": "#9ba2ff",
    "success": "#35c995", "warning": "#ffb55c", "danger": "#ff7280", "shadow": "#0b0e17",
}
# Accent colours used by charts / cards (shared, theme-independent)
ACCENTS = {"primary": "#626cf2", "blue": "#3b82f6", "green": "#20b486", "orange": "#f59e42", "red": "#ef5261"}
PRIORITY_COLORS = {2: "#ef5261", 1: "#f2c94c", 0: "#27ae60", -1: "#ffffff"}


def stylesheet(c):
    return f"""
    * {{ font-family: 'Cairo', 'Noto Sans Arabic', 'DejaVu Sans'; }}
    QMainWindow, QDialog, QWidget#appRoot {{ background: {c['bg']}; color: {c['text']}; }}
    QWidget {{ color: {c['text']}; font-size: 13px; }}
    QFrame#card, QFrame#sidePanel, QFrame#topBar {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 16px; }}
    QFrame#sidePanel {{ border-radius: 0px; border-top: 0; border-bottom: 0; }}
    QLabel#brand {{ font-size: 22px; font-weight: 800; color: {c['text']}; }}
    QLabel#brandSub, QLabel#muted, QLabel#statCaption {{ color: {c['muted']}; }}
    QLabel#sectionTitle {{ font-size: 17px; font-weight: 800; }}
    QLabel#focusTitle {{ font-size: 23px; font-weight: 800; }}
    QLabel#timerText {{ font-size: 48px; font-weight: 800; }}
    QLabel#statValue {{ font-size: 26px; font-weight: 800; }}
    QLabel#dangerText {{ color: {c['danger']}; font-weight: 700; }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{ background: {c['surface2']}; border: 1px solid {c['border']}; border-radius: 9px; padding: 8px 10px; selection-background-color: {c['primary']}; }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{ border: 2px solid {c['primary']}; }}
    QComboBox {{ color: {c['text']}; background: {c['surface2']}; }}
    QComboBox::drop-down {{ width: 28px; border: 0; background: {c['surface2']}; }}
    QComboBox QAbstractItemView {{ color: {c['text']}; background: {c['surface']}; border: 1px solid {c['border']}; selection-background-color: {c['primary']}; selection-color: white; outline: 0; }}
    QComboBox QAbstractItemView::item {{ min-height: 30px; padding: 5px 9px; }}
    QComboBox:disabled {{ color: {c['muted']}; background: {c['border']}; }}
    QDateEdit, QTimeEdit, QDateTimeEdit {{ color: {c['text']}; background: {c['surface2']}; selection-background-color: {c['primary']}; selection-color: white; }}
    QDateEdit::drop-down, QTimeEdit::drop-down, QDateTimeEdit::drop-down {{ width: 24px; border: 0; background: {c['surface2']}; }}
    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ background: {c['surface2']}; border: 0; width: 22px; }}
    QCheckBox {{ spacing: 9px; color: {c['text']}; }}
    QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 2px solid {c['muted']}; background: {c['surface2']}; }}
    QCheckBox::indicator:hover {{ border-color: {c['primary']}; }}
    QCheckBox::indicator:checked {{ background: {c['primary']}; border-color: {c['primary2']}; }}
    QCheckBox::indicator:disabled {{ background: {c['border']}; border-color: {c['border']}; }}
    QPushButton {{ background: {c['surface2']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 9px; padding: 8px 13px; font-weight: 700; }}
    QPushButton:hover {{ border-color: {c['primary']}; background: {c['surface']}; }}
    QPushButton#primary {{ color: white; border: 0; background: {c['primary']}; padding: 10px 18px; }}
    QPushButton#primary:hover {{ background: {c['primary2']}; }}
    QPushButton#danger {{ color: {c['danger']}; background: transparent; }}
    QPushButton#nav {{ background: transparent; border: 0; text-align: right; padding: 10px 12px; font-size: 14px; }}
    QPushButton#nav:hover, QPushButton#nav:checked {{ background: {c['surface2']}; color: {c['primary']}; }}
    QListWidget {{ background: transparent; border: 0; outline: 0; }}
    QListWidget::item {{ padding: 9px; margin: 2px 0; border-radius: 8px; }}
    QListWidget::item:selected {{ background: {c['surface2']}; color: {c['primary']}; }}
    QTableWidget {{ background: transparent; border: 0; gridline-color: {c['border']}; alternate-background-color: {c['surface2']}; }}
    QHeaderView::section {{ background: {c['surface2']}; color: {c['muted']}; border: 0; border-bottom: 1px solid {c['border']}; padding: 10px; font-weight: 700; }}
    QProgressBar {{ background: {c['surface2']}; border: 0; border-radius: 4px; height: 8px; text-align: center; color: transparent; }}
    QProgressBar::chunk {{ background: {c['primary']}; border-radius: 4px; }}
    QCalendarWidget QWidget {{ alternate-background-color: {c['surface']}; }}
    QCalendarWidget QAbstractItemView {{ background: {c['surface']}; color: {c['text']}; selection-background-color: {c['primary']}; border: 0; }}
    QCalendarWidget QToolButton {{ color: {c['text']}; background: transparent; border: 0; }}
    QMenu {{ background: {c['surface']}; border: 1px solid {c['border']}; }}
    QStatusBar {{ background: {c['surface']}; color: {c['muted']}; }}
    QScrollBar:vertical {{ background: transparent; width: 9px; }}
    QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 4px; min-height: 30px; }}
    """


def system_is_dark(app):
    try:
        return app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        return app.palette().color(QPalette.Window).lightness() < 128


def apply_theme(app, mode):
    effective = mode
    if mode == "system":
        effective = "dark" if system_is_dark(app) else "light"
    app.setStyleSheet(stylesheet(DARK if effective == "dark" else LIGHT))
    return effective
