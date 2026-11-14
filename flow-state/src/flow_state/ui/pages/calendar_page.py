from PySide6.QtCore import QDate
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (QCalendarWidget, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QSplitter,
                               QVBoxLayout, QWidget)

from flow_state.i18n import tr, translate_tree
from flow_state.ui.dialogs.choose_task_dialog import ChooseTaskDialog
from flow_state.ui.widgets.task_list import TaskList


class CalendarPage(QWidget):
    def __init__(self, services):
        super().__init__()
        self.services = services
        lay = QVBoxLayout(self)
        head = QHBoxLayout()
        title = QLabel("التقويم والمهام اليومية")
        title.setObjectName("brand")
        self.add = QPushButton("＋ مهمة جديدة")
        self.add.setObjectName("primary")
        self.from_list = QPushButton("إضافة من قائمة المهام")
        head.addWidget(title)
        head.addStretch()
        head.addWidget(self.from_list)
        head.addWidget(self.add)
        lay.addLayout(head)

        self.splitter = QSplitter()
        self.splitter.setChildrenCollapsible(False)
        cal_card = QFrame()
        cal_card.setObjectName("card")
        cl = QVBoxLayout(cal_card)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.apply_today_style()
        cl.addWidget(self.calendar)
        tasks_card = QFrame()
        tasks_card.setObjectName("card")
        tl = QVBoxLayout(tasks_card)
        self.date_title = QLabel("مهام اليوم")
        self.date_title.setObjectName("sectionTitle")
        tl.addWidget(self.date_title)
        self.tasks = TaskList(services, compact=True)
        tl.addWidget(self.tasks)
        self.splitter.addWidget(cal_card)
        self.splitter.addWidget(tasks_card)
        self.splitter.setSizes([420, 760])
        lay.addWidget(self.splitter, 1)

        self.calendar.clicked.connect(self.select_date)
        self.add.clicked.connect(lambda: self.tasks.open_add_dialog(self.calendar.selectedDate()))
        self.from_list.clicked.connect(self.assign_existing_task)
        self.tasks.task_changed.connect(self.refresh)
        self.select_date(QDate.currentDate())

    def apply_today_style(self):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#ede9fe"))
        fmt.setForeground(QColor("#4f46e5"))
        fmt.setFontWeight(700)
        self.calendar.setDateTextFormat(QDate.currentDate(), fmt)

    def select_date(self, date):
        self.date_title.setText(tr("مهام يوم ") + date.toString("yyyy-MM-dd"))
        self.tasks.set_selected_date(date)
        translate_tree(self)

    def assign_existing_task(self):
        rows = self.services.tasks.incomplete()
        if not rows:
            QMessageBox.information(self, tr("لا توجد مهام"), tr("لا توجد مهام غير مكتملة في قائمة المهام."))
            return
        task_id = ChooseTaskDialog.ask(rows, "إضافة من قائمة المهام", "اختر مهمة لإضافتها إلى اليوم المحدد:", self)
        if task_id is not None:
            self.services.tasks.schedule_on_day(task_id, self.calendar.selectedDate().toString("yyyy-MM-dd"))
            self.refresh()
            self.tasks.task_changed.emit()

    def refresh(self):
        self.tasks.reload_tasks()
        translate_tree(self)

    def set_layout_editing(self, enabled):
        self.splitter.setHandleWidth(9 if enabled else 2)

    def layout_sizes(self):
        return self.splitter.sizes()

    def apply_layout_sizes(self, sizes):
        if sizes and len(sizes) == 2:
            self.splitter.setSizes(sizes)
