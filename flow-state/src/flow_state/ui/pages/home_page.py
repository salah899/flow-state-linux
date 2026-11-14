from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QSplitter, QStackedLayout, QVBoxLayout,
                               QWidget)

from flow_state.i18n import tr
from flow_state.ui.formatting import format_hms, format_minutes, format_range, format_sessions, priority_label
from flow_state.ui.widgets.task_list import TaskList
from flow_state.ui.widgets.timer_ring import TimerRing

MODE_LABELS = {"work": "تركيز", "short_break": "استراحة قصيرة", "long_break": "استراحة طويلة"}


def card():
    w = QFrame()
    w.setObjectName("card")
    return w


class HomePage(QWidget):
    """Current task card + timer + task list. Pure view: no timer logic here."""

    def __init__(self, services):
        super().__init__()
        self.services = services
        lay = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("الصفحة الرئيسية")
        title.setObjectName("brand")
        self.add_button = QPushButton("＋ إضافة مهمة")
        self.add_button.setObjectName("primary")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.add_button)
        lay.addLayout(header)

        self.outer_splitter = QSplitter(Qt.Vertical)
        self.outer_splitter.setChildrenCollapsible(False)
        self.upper_splitter = QSplitter(Qt.Horizontal)
        self.upper_splitter.setChildrenCollapsible(False)
        self.upper_splitter.addWidget(self._build_current_card())
        self.upper_splitter.addWidget(self._build_timer_card())
        self.upper_splitter.setSizes([650, 430])
        self.outer_splitter.addWidget(self.upper_splitter)

        tasks_card = card()
        task_l = QVBoxLayout(tasks_card)
        self.task_list = TaskList(services)
        task_l.addWidget(self.task_list)
        self.outer_splitter.addWidget(tasks_card)
        self.outer_splitter.setSizes([330, 470])
        lay.addWidget(self.outer_splitter, 1)
        self.add_button.clicked.connect(lambda: self.task_list.open_add_dialog())

    def _build_current_card(self):
        current = card()
        cur = QVBoxLayout(current)
        row = QHBoxLayout()
        t = QLabel("◎ المهمة الحالية")
        t.setObjectName("sectionTitle")
        self.change_task_button = QPushButton("✎ تغيير")
        row.addWidget(t)
        row.addStretch()
        row.addWidget(self.change_task_button)
        cur.addLayout(row)
        self.current_title = QLabel()
        self.current_title.setObjectName("focusTitle")
        self.current_title.setWordWrap(True)
        self.current_due = QLabel()
        self.current_due.setObjectName("muted")
        self.current_priority = QLabel()
        self.current_sessions = QLabel()
        self.current_sessions.setObjectName("sectionTitle")
        self.current_estimate = QLabel()
        self.current_estimate.setObjectName("muted")
        self.current_remaining = QLabel()
        self.current_remaining.setObjectName("sectionTitle")
        for w in (self.current_title, self.current_due, self.current_priority, self.current_sessions,
                  self.current_estimate, self.current_remaining):
            cur.addWidget(w)
        cur.addStretch()
        self.show_task(None)
        return current

    def _build_timer_card(self):
        timer_card = card()
        tl = QVBoxLayout(timer_card)
        tabs = QHBoxLayout()
        self.mode_buttons = {}
        for mode, text in MODE_LABELS.items():
            b = QPushButton(text)
            self.mode_buttons[mode] = b
            tabs.addWidget(b)
        tl.addLayout(tabs)
        ring = QWidget()
        stack = QStackedLayout(ring)
        stack.setStackingMode(QStackedLayout.StackAll)
        self.ring = TimerRing()
        stack.addWidget(self.ring)
        overlay = QWidget()
        ov = QVBoxLayout(overlay)
        ov.setAlignment(Qt.AlignCenter)
        self.mode_label = QLabel("تركيز")
        self.time_label = QLabel("25:00")
        self.time_label.setObjectName("timerText")
        self.start_button = QPushButton("▶ ابدأ")
        self.start_button.setObjectName("primary")
        ov.addStretch()
        ov.addWidget(self.mode_label, 0, Qt.AlignCenter)
        ov.addWidget(self.time_label, 0, Qt.AlignCenter)
        ov.addWidget(self.start_button, 0, Qt.AlignCenter)
        ov.addStretch()
        stack.addWidget(overlay)
        stack.setCurrentWidget(overlay)
        tl.addWidget(ring, 1)
        controls = QHBoxLayout()
        self.pause_button = QPushButton("Ⅱ إيقاف")
        self.skip_button = QPushButton("⏭ تخطي")
        self.reset_button = QPushButton("■ إنهاء")
        for b in (self.pause_button, self.skip_button, self.reset_button):
            controls.addWidget(b)
        tl.addLayout(controls)
        return timer_card

    # ------------------------------------------------------------ display
    def show_task(self, task):
        if not task:
            self.current_title.setText(tr("اختر مهمة وابدأ التركيز"))
            self.current_due.setText(tr("بدون موعد"))
            self.current_priority.setText(tr("الأولوية: ") + tr("غير محددة"))
            self.current_sessions.setText("0 🍅")
            self.current_estimate.setText(tr("الوقت المقدر: غير محدد"))
            self.current_remaining.setText(tr("الوقت المتبقي: غير محدد"))
            return
        self.current_title.setText(task["title"])
        self.current_priority.setText(tr("الأولوية: ") + tr(priority_label(task["priority"])))
        self.current_due.setText(tr("المدة: ") + format_range(task))
        self.current_sessions.setText(format_sessions(task))
        minutes = self.services.focus.estimated_minutes(task)
        self.current_estimate.setText(tr("الوقت المقدر: ") + format_minutes(minutes) if minutes is not None
                                      else tr("الوقت المقدر: غير محدد"))

    def show_remaining(self, seconds):
        self.current_remaining.setText(tr("الوقت المتبقي: غير محدد") if seconds is None
                                       else tr("الوقت المتبقي: ") + format_hms(seconds))

    def show_running(self, running):
        self.start_button.setEnabled(not running)
        self.start_button.setText(tr("يعمل الآن") if running else "▶ " + tr("ابدأ"))
        self.pause_button.setEnabled(running)

    def show_mode(self, mode):
        self.mode_label.setText(tr(MODE_LABELS.get(mode, mode)))

    def show_time(self, text, progress):
        self.time_label.setText(text)
        self.ring.set_progress(progress)

    # ------------------------------------------------------------- layout
    def set_layout_editing(self, enabled):
        for s in (self.outer_splitter, self.upper_splitter):
            s.setHandleWidth(9 if enabled else 2)

    def layout_sizes(self):
        return {"home_outer": self.outer_splitter.sizes(), "home_upper": self.upper_splitter.sizes()}

    def apply_layout_sizes(self, data):
        self.outer_splitter.setSizes(data.get("home_outer", [330, 470]))
        self.upper_splitter.setSizes(data.get("home_upper", [650, 430]))
