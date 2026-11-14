from PySide6.QtCore import QDate, QDateTime, Qt, QTime
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout,
                               QLineEdit, QMessageBox, QSpinBox, QTextEdit, QTimeEdit, QVBoxLayout)

from flow_state.i18n import language, tr, translate_tree
from flow_state.services.task_service import TaskData
from flow_state.ui.formatting import PRIORITY_CHOICES, locale_date_pattern


class TaskEditDialog(QDialog):
    def __init__(self, task=None, parent=None, default_date=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("تعديل المهمة" if task else "إضافة مهمة")
        self.setMinimumWidth(470)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_input = QLineEdit()
        self.priority_combo = QComboBox()
        for text, val in PRIORITY_CHOICES:
            self.priority_combo.addItem(text, val)
        self.estimate_enabled = QCheckBox("تحديد عدد دورات مقدر")
        self.estimated_sessions = QSpinBox()
        self.estimated_sessions.setRange(1, 999)
        self.estimated_sessions.setEnabled(False)
        self.estimate_enabled.toggled.connect(self.estimated_sessions.setEnabled)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)

        self.has_due = QCheckBox("تحديد مدة للمهمة")
        initial = default_date if default_date and default_date.isValid() else QDate.currentDate()
        self.start_date = QDateEdit(initial)
        self.due_date = QDateEdit(initial)
        for edit in (self.start_date, self.due_date):
            edit.setCalendarPopup(True)
            edit.setDisplayFormat(locale_date_pattern())
        self.due_time = QTimeEdit(QTime.currentTime().addSecs(3600))
        self.due_time.setDisplayFormat("hh:mm AP" if language() == "en" else "HH:mm")
        self.has_due.toggled.connect(self.set_due_enabled)
        self.set_due_enabled(bool(default_date))
        self.has_due.setChecked(bool(default_date))

        if task:
            self._load(task)

        form.addRow("العنوان:", self.title_input)
        form.addRow("الأولوية:", self.priority_combo)
        form.addRow("", self.estimate_enabled)
        form.addRow("الدورات المقدرة:", self.estimated_sessions)
        form.addRow("", self.has_due)
        form.addRow("من يوم:", self.start_date)
        form.addRow("إلى يوم:", self.due_date)
        form.addRow("الوقت:", self.due_time)
        form.addRow("ملاحظات:", self.notes_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        translate_tree(self)

    def _load(self, task):
        self.title_input.setText(task["title"])
        self.priority_combo.setCurrentIndex(max(0, self.priority_combo.findData(task["priority"])))
        self.notes_input.setPlainText(task["notes"] or "")
        if task["estimated_sessions"] is not None:
            self.estimated_sessions.setValue(int(task["estimated_sessions"]))
            self.estimate_enabled.setChecked(True)
        if task["end_at"] or task["due_at"]:
            start = QDateTime.fromString(task["start_at"] or task["due_at"], Qt.ISODate)
            end = QDateTime.fromString(task["end_at"] or task["due_at"], Qt.ISODate)
            if start.isValid() and end.isValid():
                self.start_date.setDate(start.date())
                self.due_date.setDate(end.date())
                self.due_time.setTime(end.time())
                self.has_due.setChecked(True)

    def set_due_enabled(self, enabled):
        for w in (self.start_date, self.due_date, self.due_time):
            w.setEnabled(enabled)

    def validate(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, tr("بيانات ناقصة"), tr("اكتب عنوان المهمة."))
            return
        if self.has_due.isChecked() and self.start_date.date() > self.due_date.date():
            QMessageBox.warning(self, tr("مدة غير صحيحة"), tr("تاريخ البداية يجب أن يسبق تاريخ النهاية."))
            return
        self.accept()

    def data(self) -> TaskData:
        start = end = None
        if self.has_due.isChecked():
            start = QDateTime(self.start_date.date(), QTime(0, 0)).toString(Qt.ISODate)
            end = QDateTime(self.due_date.date(), self.due_time.time()).toString(Qt.ISODate)
        return TaskData(
            title=self.title_input.text().strip(),
            priority=self.priority_combo.currentData(),
            notes=self.notes_input.toPlainText(),
            start_at=start,
            end_at=end,
            estimated_sessions=self.estimated_sessions.value() if self.estimate_enabled.isChecked() else None,
        )
