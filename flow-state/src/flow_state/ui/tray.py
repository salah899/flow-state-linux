from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from flow_state import APP_NAME
from flow_state.i18n import tr


class TrayController(QObject):
    def __init__(self, window, timer):
        super().__init__()
        self.window = window
        self.timer = timer
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon.fromTheme("appointment-new"))
        self.tray.setToolTip(APP_NAME)
        menu = QMenu()
        self.show_hide_action = QAction()
        self.start_pause_action = QAction()
        self.quit_action = QAction()
        menu.addAction(self.show_hide_action)
        menu.addAction(self.start_pause_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)
        self.tray.setContextMenu(menu)
        self.menu = menu
        self.show_hide_action.triggered.connect(self.toggle_window)
        self.start_pause_action.triggered.connect(self.toggle_timer)
        self.quit_action.triggered.connect(self.window.close_application)
        self.timer.tick.connect(lambda text, _s: self.tray.setToolTip(f"{APP_NAME} | {text}"))
        self.timer.running_changed.connect(self.update_start_pause_text)
        self.retranslate()

    def show(self):
        self.tray.show()

    def toggle_window(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()
        self.update_show_hide_text()

    def toggle_timer(self):
        self.timer.pause() if self.timer.is_running() else self.timer.start()

    def update_start_pause_text(self, running=None):
        running = self.timer.is_running() if running is None else running
        self.start_pause_action.setText(tr("إيقاف") if running else tr("ابدأ"))

    def update_show_hide_text(self):
        self.show_hide_action.setText(tr("إخفاء") if self.window.isVisible() else tr("عرض"))

    def retranslate(self):
        """QAction is not a QWidget, so translate_tree() cannot reach it."""
        self.update_show_hide_text()
        self.update_start_pause_text()
        self.quit_action.setText(tr("خروج"))
