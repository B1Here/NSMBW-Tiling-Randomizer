from typing import Literal

from PyQt6 import QtCore, QtWidgets

from data import globals_
from reggie.reggie_object import ReggieObject
from template.selection import Selection
from widgets.reloadable import GenericWidget


# TODO make three tabs with same structure for filler, start and end objects
class ObjectEditorTab(QtWidgets.QWidget, GenericWidget):
    def __init__(
        self,
        type: Literal["filler", "start", "end"],
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._init_widgets()
        self._create_layout()
        self.toggle_widgets()
        self.index = -1
        self.type = type

    def _init_widgets(self) -> None:
        # Labels
        self.tileset_slot_label = QtWidgets.QLabel("Tileset Slot", self)
        self.tileset_slot_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.resizable_label = QtWidgets.QLabel("Resizable", self)
        self.resizable_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.object_id_label = QtWidgets.QLabel("Object ID", self)
        self.object_id_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.layer_label = QtWidgets.QLabel("Layer", self)
        self.layer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.object_width_label = QtWidgets.QLabel("Width", self)
        self.object_width_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.object_height_label = QtWidgets.QLabel("Height", self)
        self.object_height_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # Object List
        self.object_list_widget = QtWidgets.QListWidget(self)
        self.object_list_widget.currentRowChanged.connect(self._on_object_changed)
        self.add_object_button = QtWidgets.QPushButton("Add Object", self)
        self.add_object_button.clicked.connect(self._on_add_object)
        self.add_object_button.setEnabled(False)
        self.remove_object_button = QtWidgets.QPushButton("Remove Object", self)
        self.remove_object_button.clicked.connect(self._on_remove_object)
        self.remove_object_button.setEnabled(False)

        # Editor
        self.tileset_slot_spin_box = QtWidgets.QSpinBox(self)
        self.tileset_slot_spin_box.setPrefix("Pa")
        self.tileset_slot_spin_box.setRange(0, 3)
        self.tileset_slot_spin_box.setValue(0)
        self.tileset_slot_spin_box.valueChanged.connect(self._on_tileset_slot_changed)
        self.resizable_check_box = QtWidgets.QCheckBox(self)
        self.resizable_check_box.stateChanged.connect(self._on_resizable_changed)
        self.object_id_spin_box = QtWidgets.QSpinBox(self)
        self.object_id_spin_box.setRange(0, 255)
        self.object_id_spin_box.setValue(0)
        self.object_id_spin_box.valueChanged.connect(self._on_object_id_changed)
        self.layer_combo_box = QtWidgets.QComboBox(self)
        self.layer_combo_box.addItems(["0", "1", "2"])
        self.layer_combo_box.setCurrentIndex(1)
        self.layer_combo_box.currentIndexChanged.connect(self._on_object_layer_changed)
        self.object_width_spin_box = QtWidgets.QSpinBox(self)
        self.object_width_spin_box.setRange(0, 255)
        self.object_width_spin_box.setValue(0)
        self.object_width_spin_box.valueChanged.connect(self._on_object_width_changed)
        self.object_height_spin_box = QtWidgets.QSpinBox(self)
        self.object_height_spin_box.setRange(0, 255)
        self.object_height_spin_box.setValue(0)
        self.object_height_spin_box.valueChanged.connect(self._on_object_height_changed)

    def _create_layout(self) -> None:
        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(5, 1)
        layout.setRowStretch(3, 2)
        layout.addWidget(self.tileset_slot_label, 0, 2)
        layout.addWidget(self.tileset_slot_spin_box, 0, 3)
        layout.addWidget(self.resizable_label, 0, 4)
        layout.addWidget(self.resizable_check_box, 0, 5)
        layout.addWidget(self.object_list_widget, 0, 0, 4, 2)
        layout.addWidget(self.add_object_button, 4, 0)
        layout.addWidget(self.remove_object_button, 4, 1)
        layout.addWidget(self.object_id_label, 1, 2)
        layout.addWidget(self.object_id_spin_box, 1, 3)
        layout.addWidget(self.layer_label, 1, 4)
        layout.addWidget(self.layer_combo_box, 1, 5)
        layout.addWidget(self.object_width_label, 2, 2)
        layout.addWidget(self.object_width_spin_box, 2, 3)
        layout.addWidget(self.object_height_label, 2, 4)
        layout.addWidget(self.object_height_spin_box, 2, 5)

        self.setLayout(layout)

    def reload(self) -> None:
        self.object_list_widget.clear()
        objects = self.get_objects()
        self.index = -1 if objects is None else min(self.index, len(objects) - 1)

        if objects is not None:
            self.object_list_widget.addItems(
                [f"Object {object.object_num}" for object in objects]
            )
            self.update_index()
        self._reload_buttons()
        self.toggle_widgets()

    def _reload_buttons(self) -> None:
        objects = self.get_objects()

        self.add_object_button.setEnabled(objects is not None)
        self.remove_object_button.setEnabled(objects is not None and len(objects) > 0)

    def _on_object_changed(self, index: int) -> None:
        objects = self.get_objects()

        self.index = min(index, -1 if objects is None else len(objects) - 1)
        self.object_index = self.index
        self.toggle_widgets()
        if self.index < 0 or objects is None:
            return

        object = objects[self.index]
        self.object_id_spin_box.setValue(object.object_num)
        self.layer_combo_box.setCurrentIndex(object.layer)
        self.resizable_check_box.setChecked(object.resizable)
        self.object_width_spin_box.setValue(object.width)
        self.object_height_spin_box.setValue(object.height)
        self.tileset_slot_spin_box.setValue(object.tileset_slot)

    def _on_object_id_changed(self, value: int) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects[self.index].object_num = value

    def _on_object_layer_changed(self, index: int) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects[self.index].layer = index

    def update_index(self) -> None:
        if self.index == -1 and self.get_objects():
            self.object_list_widget.setCurrentRow(0)
            self.index = 0

    def _on_add_object(self) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects.append(ReggieObject(1, 0, 1, 1, 1))
        self.object_list_widget.addItem("Object 0")
        self.update_index()
        self._reload_buttons()

    def _on_remove_object(self) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        index = self.object_list_widget.currentRow()
        if index == -1:
            index = len(objects) - 1

        objects.pop(index)
        self.object_list_widget.takeItem(index)
        self._reload_buttons()

    def _on_tileset_slot_changed(self, value: int) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects[self.index].tileset_slot = value

    def _on_resizable_changed(self, state: int) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects[self.index].resizable = state == QtCore.Qt.CheckState.Checked.value

    def _on_object_width_changed(self, value: int) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects[self.index].width = value

    def _on_object_height_changed(self, value: int) -> None:
        objects = self.get_objects()
        if objects is None:
            return

        objects[self.index].height = value

    def get_objects(self) -> list[ReggieObject] | None:
        selection = self.get_current_selection()
        if selection is None:
            return None
        if self.type == "start":
            return selection.starts
        elif self.type == "end":
            return selection.ends
        return selection.objects

    def get_current_selection(self) -> Selection | None:
        if globals_.current_selection_index == -1:
            return None
        return globals_.template.selections[globals_.current_selection_index]

    def toggle_widgets(self) -> None:
        disabled = globals_.current_selection_index == -1 or self.index == -1
        self.object_id_spin_box.setDisabled(disabled)
        self.layer_combo_box.setDisabled(disabled)
        self.object_height_spin_box.setDisabled(disabled)
        self.object_width_spin_box.setDisabled(disabled)
        self.resizable_check_box.setDisabled(disabled)
        self.tileset_slot_spin_box.setDisabled(disabled)


class ObjectEditor(QtWidgets.QTabWidget, GenericWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.filler_tab = ObjectEditorTab("filler", self)
        self.starts_tab = ObjectEditorTab("start", self)
        self.ends_tab = ObjectEditorTab("end", self)
        self.addTab(self.filler_tab, "Filler Objects")
        self.addTab(self.starts_tab, "Start Objects")
        self.addTab(self.ends_tab, "End Objects")

    def reload(self) -> None:
        self.filler_tab.reload()
        self.starts_tab.reload()
        self.ends_tab.reload()
