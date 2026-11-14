from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from flow_state.i18n import tr, translate_tree
from flow_state.ui.dialogs.choose_task_dialog import ChooseTaskDialog
from flow_state.ui.dialogs.task_edit_dialog import TaskEditDialog
from flow_state.ui.formatting import PRIORITY_CHOICES, format_range, format_sessions, priority_label
from flow_state.ui.theme import PRIORITY_COLORS

COLUMNS = ["تم", "المهمة", "الموعد", "الأولوية", "الدورات", "تركيز", "تعديل", "حذف"]
COL_DONE, COL_TITLE, COL_RANGE, COL_PRIORITY, COL_SESSIONS, COL_FOCUS, COL_EDIT, COL_DELETE = range(len(COLUMNS))
SMART_FILTERS = {"today": "مهام اليوم", "upcoming": "المهام القادمة", "overdue": "المهام المتأخرة",
                 "completed": "المهام المكتملة"}


class TaskList(QWidget):
    task_changed = Signal()
    current_task_changed = Signal()

    def __init__(self, services, compact=False):
        super().__init__()
        self.services = services
        self.tasks = services.tasks
        self.folder_id = None
        self.priority_filter = None
        self.date_filter = None
        self.selected_date = None
        self.row_task_ids = {}
        self.show_completed = False
        self.compact = compact

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if not compact:
            self._build_toolbar(layout)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionsMovable(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        layout.addWidget(self.table)
        self.table.itemChanged.connect(self.item_changed)
        self.table.cellDoubleClicked.connect(
            lambda r, c: self.edit_task(self.row_task_ids[r]) if r in self.row_task_ids else None)
        self.apply_column_mode()

    def _build_toolbar(self, layout):
        add = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("اكتب اسم المهمة ثم اضغط إضافة...")
        self.priority_input = QComboBox()
        for t, v in PRIORITY_CHOICES:
            self.priority_input.addItem(t, v)
        self.add_button = QPushButton("＋ إضافة مهمة")
        self.add_button.setObjectName("primary")
        add.addWidget(self.title_input, 1)
        add.addWidget(self.priority_input)
        add.addWidget(self.add_button)
        layout.addLayout(add)

        filters = QHBoxLayout()
        self.filter_label = QLabel("كل المهام")
        self.filter_label.setObjectName("sectionTitle")
        self.priority_filter_combo = QComboBox()
        for t, v in [("كل الأولويات", None), ("عالية", 2), ("متوسطة", 1), ("منخفضة", 0), ("غير محددة", -1)]:
            self.priority_filter_combo.addItem(t, v)
        self.today_button = QPushButton("مهام اليوم")
        self.all_button = QPushButton("كل المهام")
        filters.addWidget(self.filter_label)
        filters.addStretch()
        filters.addWidget(self.priority_filter_combo)
        filters.addWidget(self.today_button)
        filters.addWidget(self.all_button)
        layout.addLayout(filters)

        self.add_button.clicked.connect(self.add_task)
        self.title_input.returnPressed.connect(self.add_task)
        self.priority_filter_combo.currentIndexChanged.connect(self.priority_changed)
        self.today_button.clicked.connect(lambda: self.set_smart_filter("today"))
        self.all_button.clicked.connect(self.show_all)

    # ------------------------------------------------------------ filters
    def set_folder(self, folder_id):
        self.folder_id, self.date_filter, self.selected_date = folder_id, None, None
        self.reload_tasks()

    def show_all(self):
        self.folder_id, self.date_filter, self.selected_date = None, None, None
        self.filter_label.setText(tr("كل المهام"))
        self.reload_tasks()

    def set_smart_filter(self, name):
        self.folder_id, self.date_filter, self.selected_date = None, name, None
        self.filter_label.setText(tr(SMART_FILTERS.get(name, "كل المهام")))
        self.reload_tasks()

    def set_selected_date(self, date):
        self.folder_id, self.date_filter = None, None
        self.selected_date = date.toString("yyyy-MM-dd")
        self.reload_tasks()

    def priority_changed(self):
        self.priority_filter = self.priority_filter_combo.currentData()
        self.reload_tasks()

    # ----------------------------------------------------------- commands
    def open_add_dialog(self, default_date=None):
        folder_id = self.folder_id or self.services.folders.default_id()
        if folder_id is None:
            QMessageBox.warning(self, tr("لا يوجد مشروع"), tr("أنشئ مشروعًا أولًا."))
            return
        dialog = TaskEditDialog(parent=self, default_date=default_date)
        if not self.compact:
            dialog.title_input.setText(self.title_input.text())
            dialog.priority_combo.setCurrentIndex(self.priority_input.currentIndex())
        if dialog.exec() == QDialog.Accepted:
            self.tasks.create(folder_id, dialog.data())
            if not self.compact:
                self.title_input.clear()
            self.reload_tasks()
            self.task_changed.emit()

    def add_task(self):
        self.open_add_dialog(QDate.fromString(self.selected_date, "yyyy-MM-dd") if self.selected_date else None)

    def edit_task(self, task_id):
        dialog = TaskEditDialog(self.tasks.get(task_id), self)
        if dialog.exec() == QDialog.Accepted:
            self.tasks.update(task_id, dialog.data())
            self._changed(current_too=True)

    def delete_task(self, task_id):
        if QMessageBox.question(self, tr("حذف المهمة"), tr("هل تريد حذف هذه المهمة؟"),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.tasks.delete(task_id)
            self._changed(current_too=True)

    def set_current_task(self, task_id):
        self.tasks.set_current(task_id)
        self.reload_tasks()
        self.current_task_changed.emit()

    def choose_current_task(self):
        rows = self.tasks.incomplete()
        if not rows:
            QMessageBox.information(self, tr("لا توجد مهام"), tr("أضف مهمة غير مكتملة أولًا."))
            return
        task_id = ChooseTaskDialog.ask(rows, "تغيير المهمة الحالية", "اختر المهمة التي تريد التركيز عليها:", self)
        if task_id is not None:
            self.set_current_task(task_id)

    def item_changed(self, item):
        if item.column() == COL_DONE and item.row() in self.row_task_ids:
            self.tasks.set_completed(self.row_task_ids[item.row()], item.checkState() == Qt.Checked)
            self._changed()

    def _changed(self, current_too=False):
        self.reload_tasks()
        self.task_changed.emit()
        if current_too:
            self.current_task_changed.emit()

    def toggle_completed(self):
        self.show_completed = not self.show_completed
        self.reload_tasks()

    # ------------------------------------------------------------- render
    def reload_tasks(self):
        self.table.blockSignals(True)
        self.table.clearSpans()
        self.table.setRowCount(0)
        self.row_task_ids = {}
        args = (self.folder_id, self.priority_filter, self.date_filter, self.selected_date)
        active = self.tasks.list(*args, completed=False)
        completed = self.tasks.list(*args, completed=True)
        row = 0
        for task in active:
            self._add_task_row(row, task)
            row += 1
        if completed:
            self.table.insertRow(row)
            self.table.setSpan(row, 0, 1, len(COLUMNS))
            toggle = QPushButton(("▲ " + tr("إخفاء") if self.show_completed else "▼ " + tr("عرض"))
                                 + f" {tr('المهام المكتملة')} ({len(completed)})")
            toggle.setObjectName("nav")
            toggle.clicked.connect(self.toggle_completed)
            self.table.setCellWidget(row, 0, toggle)
            self.table.setRowHeight(row, 42)
            row += 1
            if self.show_completed:
                for task in completed:
                    self._add_task_row(row, task)
                    row += 1
        if not active and not completed:
            self.table.setRowCount(1)
            empty = QTableWidgetItem(tr("لا توجد مهام في هذا العرض."))
            empty.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(0, 0, 1, len(COLUMNS))
            self.table.setItem(0, 0, empty)
        self.table.blockSignals(False)
        translate_tree(self)

    def _add_task_row(self, row, task):
        self.table.insertRow(row)
        tid = task["id"]
        self.row_task_ids[row] = tid
        done = QTableWidgetItem()
        done.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        done.setCheckState(Qt.Checked if task["completed"] else Qt.Unchecked)
        self.table.setItem(row, COL_DONE, done)
        title = QTableWidgetItem(task["title"])
        if task["completed"]:
            title.setForeground(QColor("gray"))
            font = title.font()
            font.setStrikeOut(True)
            title.setFont(font)
        self.table.setItem(row, COL_TITLE, title)
        self.table.setItem(row, COL_RANGE, QTableWidgetItem(format_range(task)))
        priority = QTableWidgetItem(tr(priority_label(task["priority"])))
        priority.setForeground(QColor(PRIORITY_COLORS.get(task["priority"], "#ffffff")))
        self.table.setItem(row, COL_PRIORITY, priority)
        self.table.setItem(row, COL_SESSIONS, QTableWidgetItem(format_sessions(task)))
        focus = QPushButton(tr("الحالية") if task["is_current"] else tr("اختيار"))
        focus.setEnabled(not task["is_current"] and not task["completed"])
        focus.clicked.connect(lambda _=False, t=tid: self.set_current_task(t))
        self.table.setCellWidget(row, COL_FOCUS, focus)
        edit = QPushButton(tr("تعديل"))
        edit.clicked.connect(lambda _=False, t=tid: self.edit_task(t))
        self.table.setCellWidget(row, COL_EDIT, edit)
        delete = QPushButton(tr("حذف"))
        delete.setObjectName("danger")
        delete.clicked.connect(lambda _=False, t=tid: self.delete_task(t))
        self.table.setCellWidget(row, COL_DELETE, delete)

    # ------------------------------------------------------------ columns
    def apply_column_mode(self):
        settings = self.services.settings
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        if settings.get("auto_columns", "1") == "1":
            for col in range(self.table.columnCount()):
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(COL_TITLE, QHeaderView.Stretch)
            return
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
        raw = settings.get("task_column_widths", "")
        if raw:
            try:
                for col, width in enumerate(int(x) for x in raw.split(",")):
                    if col < self.table.columnCount():
                        self.table.setColumnWidth(col, max(35, width))
            except ValueError:
                pass

    def save_column_widths(self):
        if self.services.settings.get("auto_columns", "1") == "0":
            widths = ",".join(str(self.table.columnWidth(i)) for i in range(self.table.columnCount()))
            self.services.settings.set("task_column_widths", widths)
