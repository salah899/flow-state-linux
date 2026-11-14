from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from flow_state.i18n import translate_tree


class ChooseTaskDialog(QDialog):
    """Pick one task from a list. Used by 'change current task' and the calendar."""

    def __init__(self, tasks, title, prompt, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(prompt))
        self.box = QComboBox()
        for t in tasks:
            self.box.addItem(t["title"], t["id"])
        lay.addWidget(self.box)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)
        translate_tree(self)

    def selected_id(self):
        return self.box.currentData()

    @classmethod
    def ask(cls, tasks, title, prompt, parent=None):
        dialog = cls(tasks, title, prompt, parent)
        return dialog.selected_id() if dialog.exec() == QDialog.Accepted else None
