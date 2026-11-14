from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel,
                               QSpinBox, QVBoxLayout)

from flow_state.i18n import LANGUAGES, translate_tree

SCORING_CHOICES = [("افتراضي (تقدم جزئي)", "default"), ("الجلسات الكاملة فقط", "full_sessions_only")]


class SettingsDialog(QDialog):
    def __init__(self, settings_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.setMinimumWidth(460)
        s = settings_service.all()
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.work_duration = self.spin(1, 180, int(s.get("work_duration", 25)))
        self.short_break = self.spin(1, 60, int(s.get("short_break", 5)))
        self.long_break = self.spin(1, 120, int(s.get("long_break", 15)))
        self.sessions = self.spin(1, 12, int(s.get("sessions_before_long_break", 4)))
        self.theme = self.combo([("فاتح", "light"), ("داكن", "dark"), ("حسب النظام", "system")],
                                s.get("theme_mode", "system"))
        self.language = self.combo([(name, code) for code, name in LANGUAGES.items()], s.get("language", "ar"))
        self.scoring = self.combo(SCORING_CHOICES, s.get("scoring_policy", "default"))
        form.addRow("لغة التطبيق:", self.language)
        form.addRow("مدة التركيز بالدقائق:", self.work_duration)
        form.addRow("الاستراحة القصيرة:", self.short_break)
        form.addRow("الاستراحة الطويلة:", self.long_break)
        form.addRow("الجلسات قبل الاستراحة الطويلة:", self.sessions)
        form.addRow("نظام الحساب:", self.scoring)
        form.addRow("مظهر التطبيق:", self.theme)
        lay.addLayout(form)
        self.auto_columns = QCheckBox("الوضع التلقائي للأعمدة")
        self.auto_columns.setChecked(s.get("auto_columns", "1") == "1")
        lay.addWidget(self.auto_columns)
        self.edit_layout = QCheckBox("تعديل النوافذ الداخلية بعد حفظ الإعدادات")
        lay.addWidget(self.edit_layout)
        note = QLabel("يمكنك شد الفواصل بين البطاقات في كل صفحة، ثم الضغط على «حفظ التخطيط».")
        note.setWordWrap(True)
        note.setObjectName("muted")
        lay.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)
        translate_tree(self)

    @staticmethod
    def spin(a, b, v):
        x = QSpinBox()
        x.setRange(a, b)
        x.setValue(v)
        return x

    @staticmethod
    def combo(items, current):
        box = QComboBox()
        for text, data in items:
            box.addItem(text, data)
        box.setCurrentIndex(max(0, box.findData(current)))
        return box

    def get_values(self):
        return {
            "work_duration": self.work_duration.value(),
            "short_break": self.short_break.value(),
            "long_break": self.long_break.value(),
            "sessions_before_long_break": self.sessions.value(),
            "theme_mode": self.theme.currentData(),
            "language": self.language.currentData(),
            "scoring_policy": self.scoring.currentData(),
            "auto_columns": "1" if self.auto_columns.isChecked() else "0",
        }

    def wants_layout_edit(self):
        return self.edit_layout.isChecked()
