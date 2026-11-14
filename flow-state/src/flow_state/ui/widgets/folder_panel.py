from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QInputDialog, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget

from flow_state.i18n import tr, translate_tree


class FolderPanel(QWidget):
    folder_selected = Signal(int)
    folders_changed = Signal()

    def __init__(self, services):
        super().__init__()
        self.folders = services.folders
        self.setObjectName("folderPanel")
        self.folder_ids = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(10)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        buttons = QHBoxLayout()
        self.add_button = QPushButton("＋ جديد")
        self.delete_button = QPushButton("حذف")
        self.add_button.setObjectName("primary")
        self.delete_button.setObjectName("danger")
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.delete_button)
        layout.addLayout(buttons)
        self.add_button.clicked.connect(self.add_folder)
        self.delete_button.clicked.connect(self.delete_folder)
        self.list_widget.currentRowChanged.connect(self.on_current_row_changed)
        self.reload()

    def reload(self):
        self.list_widget.clear()
        self.folder_ids = []
        for folder in self.folders.list():
            self.folder_ids.append(folder["id"])
            self.list_widget.addItem(folder["name"])
        if self.folder_ids and self.list_widget.currentRow() == -1:
            self.list_widget.setCurrentRow(0)
        translate_tree(self)

    def current_folder_id(self):
        row = self.list_widget.currentRow()
        return self.folder_ids[row] if 0 <= row < len(self.folder_ids) else None

    def on_current_row_changed(self, row):
        if 0 <= row < len(self.folder_ids):
            self.folder_selected.emit(self.folder_ids[row])

    def add_folder(self):
        name, ok = QInputDialog.getText(self, tr("إضافة مجلد"), tr("اسم المجلد:"))
        if ok and name.strip():
            self.folders.add(name)
            self.reload()
            self.folders_changed.emit()

    def delete_folder(self):
        folder_id = self.current_folder_id()
        if folder_id is None:
            return
        reply = QMessageBox.question(self, tr("حذف المجلد"), tr("هل تريد حذف هذا المجلد وكل مهامه؟"),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.folders.delete(folder_id)
            self.reload()
            self.folders_changed.emit()
