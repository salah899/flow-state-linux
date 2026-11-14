import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from flow_state import APP_NAME
from flow_state.data.database import Database
from flow_state.i18n import set_language
from flow_state.services import AppServices
from flow_state.ui.main_window import MainWindow
from flow_state.ui.theme import apply_theme
from flow_state.ui.tray import TrayController


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    tray_available = QSystemTrayIcon.isSystemTrayAvailable()
    app.setQuitOnLastWindowClosed(not tray_available)

    services = AppServices(Database())
    settings = services.settings.all()
    set_language(settings.get("language", "ar"))
    apply_theme(app, settings.get("theme_mode", "system"))

    window = MainWindow(services)
    window.show()
    if tray_available:
        window.tray_controller = TrayController(window, window.timer)
        window.tray_controller.show()
    sys.exit(app.exec())
