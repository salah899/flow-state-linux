import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSplitter, QStackedWidget, QSystemTrayIcon, QVBoxLayout, QWidget)

from flow_state import APP_NAME
from flow_state.core.timer import PomodoroTimer
from flow_state.i18n import set_language, tr, translate_tree
from flow_state.paths import resource_path
from flow_state.ui.dialogs.settings_dialog import SettingsDialog
from flow_state.ui.pages.analytics_page import AnalyticsPage
from flow_state.ui.pages.calendar_page import CalendarPage
from flow_state.ui.pages.home_page import HomePage
from flow_state.ui.theme import apply_theme
from flow_state.ui.widgets.folder_panel import FolderPanel

PAGE_HOME, PAGE_ANALYTICS, PAGE_CALENDAR = range(3)


class MainWindow(QMainWindow):
    def __init__(self, services):
        super().__init__()
        self.services = services
        self.tray_controller = None
        self.setWindowTitle(APP_NAME)
        self.resize(1400, 860)
        self.setMinimumSize(1080, 700)
        self.timer = PomodoroTimer(services.settings.all(), services.policy)
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(resource_path("bell.wav")))
        self.sound.setVolume(.8)
        self.build_ui()
        self.connect_signals()
        self.load_layouts()
        self.set_layout_editing(False, announce=False)
        self.refresh_all()
        self.home.show_mode(self.timer.mode)
        self.timer.emit_state()
        self.home.show_running(False)
        translate_tree(self)

    # ---------------------------------------------------------------- UI
    def build_ui(self):
        root_widget = QWidget()
        root_widget.setObjectName("appRoot")
        root = QHBoxLayout(root_widget)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)
        side = self._build_sidebar()
        self.pages = QStackedWidget()
        self.home = HomePage(self.services)
        self.analytics = AnalyticsPage(self.services)
        self.calendar_page = CalendarPage(self.services)
        for page in (self.home, self.analytics, self.calendar_page):
            self.pages.addWidget(page)
        self.task_list = self.home.task_list
        self.app_splitter = QSplitter(Qt.Horizontal)
        self.app_splitter.setChildrenCollapsible(False)
        self.app_splitter.addWidget(side)
        self.app_splitter.addWidget(self.pages)
        self.app_splitter.setSizes([352, 1048])
        root.addWidget(self.app_splitter)
        self.setCentralWidget(root_widget)
        self.switch_page(PAGE_HOME)

    def _build_sidebar(self):
        side = QFrame()
        side.setObjectName("sidePanel")
        side.setMinimumWidth(260)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(18, 22, 18, 18)
        sl.setSpacing(10)
        brand = QLabel("◉  " + APP_NAME)
        brand.setObjectName("brand")
        sub = QLabel("خطط بوضوح، ركّز بعمق")
        sub.setObjectName("brandSub")
        sl.addWidget(brand)
        sl.addWidget(sub)
        sl.addSpacing(22)
        self.nav = []
        for text, index in [("⌂  الصفحة الرئيسية", PAGE_HOME), ("▥  الإحصائيات", PAGE_ANALYTICS),
                            ("▦  التقويم", PAGE_CALENDAR)]:
            b = QPushButton(text)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.clicked.connect(lambda _=False, i=index: self.switch_page(i))
            self.nav.append(b)
            sl.addWidget(b)
        self.folders_button = QPushButton("▤  المجلدات")
        self.folders_button.setObjectName("nav")
        self.folders_button.setCheckable(True)
        sl.addWidget(self.folders_button)
        self.folder_popup = QFrame()
        self.folder_popup.setObjectName("card")
        popup_lay = QVBoxLayout(self.folder_popup)
        popup_lay.setContentsMargins(4, 4, 4, 4)
        self.folder_panel = FolderPanel(self.services)
        popup_lay.addWidget(self.folder_panel)
        self.folder_popup.hide()
        sl.addWidget(self.folder_popup)
        sl.addStretch()
        self.save_layout_button = QPushButton("✓  حفظ التخطيط")
        self.save_layout_button.setObjectName("primary")
        self.save_layout_button.hide()
        sl.addWidget(self.save_layout_button)
        self.settings_button = QPushButton("⚙  الإعدادات")
        self.settings_button.setObjectName("nav")
        sl.addWidget(self.settings_button)
        return side

    def connect_signals(self):
        h, t = self.home, self.timer
        self.settings_button.clicked.connect(self.open_settings)
        self.save_layout_button.clicked.connect(self.save_layouts)
        self.folders_button.clicked.connect(self.toggle_folders)
        self.folder_panel.folder_selected.connect(self.select_folder)
        self.folder_panel.folders_changed.connect(self.refresh_all)
        h.change_task_button.clicked.connect(self.task_list.choose_current_task)
        h.start_button.clicked.connect(t.start)
        h.pause_button.clicked.connect(t.pause)
        h.skip_button.clicked.connect(t.skip)
        h.reset_button.clicked.connect(t.finish_early)
        for mode, b in h.mode_buttons.items():
            b.clicked.connect(lambda _=False, m=mode: t.set_mode(m))
        t.tick.connect(self.on_tick)
        t.mode_changed.connect(lambda mode, _sessions: h.show_mode(mode))
        t.finished.connect(self.on_finished)
        t.running_changed.connect(h.show_running)
        t.period_ended.connect(self.record_period)
        for lst in (self.task_list, self.calendar_page.tasks):
            lst.task_changed.connect(self.refresh_all)
            lst.current_task_changed.connect(self.refresh_all)

    # ---------------------------------------------------------- navigation
    def toggle_folders(self, checked):
        self.folder_popup.setVisible(checked)
        self.folders_button.setText(("▾  " if checked else "▤  ") + tr("المجلدات"))

    def select_folder(self, folder_id):
        self.switch_page(PAGE_HOME)
        self.task_list.set_folder(folder_id)
        self.task_list.filter_label.setText(self.services.folders.name(folder_id, tr("كل المهام")))

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, b in enumerate(self.nav):
            b.setChecked(i == index)
        if index == PAGE_ANALYTICS:
            self.analytics.refresh()
        elif index == PAGE_CALENDAR:
            self.calendar_page.refresh()

    def refresh_all(self):
        self.home.show_task(self.services.tasks.current())
        self.update_remaining_time()
        self.task_list.reload_tasks()
        self.analytics.refresh()
        self.calendar_page.refresh()
        translate_tree(self)

    # --------------------------------------------------------------- timer
    def live_focus_seconds(self):
        if self.timer.mode != "work":
            return 0
        return max(0, self.timer.duration_for_mode("work") - self.timer.remaining_seconds)

    def update_remaining_time(self):
        task = self.services.tasks.current()
        self.home.show_remaining(self.services.focus.remaining_seconds(task, self.live_focus_seconds()))

    def record_period(self, mode, fraction):
        if mode != "work" or fraction <= 0:
            return
        task = self.services.tasks.current()
        if task:
            self.services.focus.record(task["id"], fraction, self.timer.duration_for_mode("work"))
            self.refresh_all()

    def on_tick(self, text, seconds):
        self.home.show_time(text, seconds / max(1, self.timer.duration_for_mode(self.timer.mode)))
        self.update_remaining_time()

    def on_finished(self, old_mode):
        if self.sound.status() == QSoundEffect.Ready:
            self.sound.play()
        msg = "انتهت جلسة التركيز، حان وقت الراحة." if old_mode == "work" else "انتهت الراحة، لنعد إلى التركيز."
        self.statusBar().showMessage(tr(msg), 5000)

    # ------------------------------------------------------------ settings
    def open_settings(self):
        dialog = SettingsDialog(self.services.settings, self)
        if dialog.exec() != QDialog.Accepted:
            return
        values = dialog.get_values()
        set_language(values["language"])
        self.services.settings.update(values)
        self.services.reload_policy()
        self.timer.policy = self.services.policy
        self.timer.update_settings(self.services.settings.all())
        self.timer.reset_current_period()
        apply_theme(QApplication.instance(), values["theme_mode"])
        self.task_list.apply_column_mode()
        self.calendar_page.tasks.apply_column_mode()
        self.refresh_all()
        self.home.show_running(self.timer.is_running())
        if self.tray_controller:
            self.tray_controller.retranslate()
        if dialog.wants_layout_edit():
            self.set_layout_editing(True)

    # -------------------------------------------------------------- layout
    def set_layout_editing(self, enabled, announce=True):
        self.home.set_layout_editing(enabled)
        self.analytics.set_layout_editing(enabled)
        self.calendar_page.set_layout_editing(enabled)
        self.save_layout_button.setVisible(enabled)
        if announce:
            msg = ("وضع تعديل التخطيط: اسحب الفواصل داخل كل صفحة ثم اضغط حفظ التخطيط."
                   if enabled else "تم حفظ التخطيط.")
            self.statusBar().showMessage(tr(msg), 5000)

    def save_layouts(self):
        data = {"app": self.app_splitter.sizes(), **self.home.layout_sizes(),
                "analytics": self.analytics.layout_sizes(), "calendar": self.calendar_page.layout_sizes()}
        self.services.settings.set("window_layouts", json.dumps(data))
        self.set_layout_editing(False)

    def load_layouts(self):
        raw = self.services.settings.get("window_layouts", "")
        if not raw:
            return
        try:
            data = json.loads(raw)
            self.app_splitter.setSizes(data.get("app", [352, 1048]))
            self.home.apply_layout_sizes(data)
            self.analytics.apply_layout_sizes(data.get("analytics"))
            self.calendar_page.apply_layout_sizes(data.get("calendar"))
        except (ValueError, TypeError, AttributeError):
            pass

    # ------------------------------------------------------------ shutdown
    def _shutdown(self):
        self.task_list.save_column_widths()
        self.calendar_page.tasks.save_column_widths()
        self.timer.pause()
        self.services.close()

    def closeEvent(self, event):
        if QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
        else:
            self._shutdown()
            event.accept()

    def close_application(self):
        self._shutdown()
        QApplication.quit()
