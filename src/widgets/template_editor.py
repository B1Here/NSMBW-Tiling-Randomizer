from PyQt6 import QtCore, QtWidgets

from data import globals_
from template.selection import Selection
from widgets.object_editor import ObjectEditor
from widgets.reloadable import GenericWidget
from widgets.template_config import TemplateConfigWidget


class TemplateEditorWidget(QtWidgets.QWidget, GenericWidget):
    list_updated = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._init_widgets()
        self._setup_layout()

    def _init_widgets(self):
        self.selection_list = QtWidgets.QListWidget(self)
        self.selection_list.currentRowChanged.connect(self._on_selection_changed)
        self.template_config = TemplateConfigWidget(self)
        self.add_selection_button = QtWidgets.QPushButton("Add Selection", self)
        self.add_selection_button.clicked.connect(self._add_selection)
        self.remove_selection_button = QtWidgets.QPushButton("Remove Selection", self)
        self.remove_selection_button.clicked.connect(self._remove_selection)
        self.remove_selection_button.setEnabled(False)
        self.object_editor = ObjectEditor()
        self.update_selection_list()

    def _setup_layout(self):
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnStretch(2, 1)
        layout.addWidget(self.template_config, 0, 0, 1, 3)
        layout.addWidget(self.selection_list, 1, 0, 1, 2)
        layout.addWidget(self.add_selection_button, 2, 0)
        layout.addWidget(self.remove_selection_button, 2, 1)
        layout.addWidget(self.object_editor, 1, 2, 2, 1)
        self.setLayout(layout)

    def reload(self):
        self.update_selection_list()
        self.template_config.reload()
        self.object_editor.reload()
        self._reload_buttons()

    def update_selection_list(self):
        self.selection_list.clear()
        self.selection_list.addItems(
            f"Selection {i + 1}" for i in range(len(globals_.template.selections))
        )
        self.update_index()

    def update_index(self):
        if globals_.current_selection_index == -1 and len(globals_.template.selections):
            self.selection_list.setCurrentRow(0)
            globals_.current_selection_index = 0

    def _on_selection_changed(self, index: int):
        index = min(index, len(globals_.template.selections) - 1)
        globals_.current_selection_index = index

        if index >= 0:
            self.object_editor.reload()

    def _add_selection(self):
        globals_.template.selections.append(Selection([]))
        self.selection_list.addItem(f"Selection {len(globals_.template.selections)}")
        self.update_index()
        self.list_updated.emit("tpl")
        self.object_editor.reload()
        self._reload_buttons()

    def _remove_selection(self):
        if len(globals_.template.selections) <= 0:
            return

        index = self.selection_list.currentRow() if self.selection_list.currentRow() != -1 else len(globals_.template.selections) - 1
        globals_.template.selections.pop(index)
        self.selection_list.takeItem(index)
        self.list_updated.emit("tpl")
        self.object_editor.reload()
        self._reload_buttons()

    def _reload_buttons(self):
        self.remove_selection_button.setEnabled(len(globals_.template.selections) > 0)
