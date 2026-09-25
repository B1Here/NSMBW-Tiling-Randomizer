from PyQt6 import QtCore, QtWidgets

from data import globals_
from reggie.reggie_object import ReggieObject
from reggie.reggieclip import ReggieClip
from template import generator
from template.randomization_type import RandomizationType
from widgets.reloadable import GenericWidget


class GeneratorTabWidget(QtWidgets.QWidget, GenericWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_widgets()
        self._setup_layout()
        self._update_offset_spin_box()

    def _init_widgets(self) -> None:
        # labels
        self.width_label = QtWidgets.QLabel("Filler Width", self)
        self.width_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.height_label = QtWidgets.QLabel("Filler Height", self)
        self.height_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.offset_label = QtWidgets.QLabel("Start at row", self)
        self.offset_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.random_offset_label = QtWidgets.QLabel("Start with random row", self)
        self.random_offset_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.add_edges_label = QtWidgets.QLabel("Add edges", self)
        self.add_edges_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.reggie_clip_label = QtWidgets.QLabel("ReggieClip", self)

        self.width_spin_box = QtWidgets.QSpinBox(self)
        self.width_spin_box.setRange(1, 255)
        self.height_spin_box = QtWidgets.QSpinBox(self)
        self.height_spin_box.setRange(1, 255)
        self.random_offset_check_box = QtWidgets.QCheckBox(self)
        self.random_offset_check_box.setDisabled(True)
        self.random_offset_check_box.stateChanged.connect(self._update_offset_spin_box)
        self.offset_spin_box = QtWidgets.QSpinBox(self)
        self.add_edges_check_box = QtWidgets.QCheckBox(self)
        self.generate_button = QtWidgets.QPushButton("Generate", self)
        self.generate_button.clicked.connect(self.generate)
        self.reggie_clip_text_area = QtWidgets.QTextEdit(self)
        self.reggie_clip_text_area.setReadOnly(True)

    def _setup_layout(self) -> None:
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.setColumnStretch(3, 1)

        layout.addWidget(self.width_label, 0, 0)
        layout.addWidget(self.width_spin_box, 0, 1, 1, 3)
        layout.addWidget(self.height_label, 1, 0)
        layout.addWidget(self.height_spin_box, 1, 1, 1, 3)
        layout.addWidget(self.random_offset_label, 2, 0)
        layout.addWidget(self.random_offset_check_box, 2, 1)
        layout.addWidget(self.offset_label, 2, 2)
        layout.addWidget(self.offset_spin_box, 2, 3)
        layout.addWidget(self.add_edges_label, 3, 0)
        layout.addWidget(self.add_edges_check_box, 3, 1)
        layout.addWidget(self.generate_button, 4, 0, 1, 2)
        layout.addWidget(self.reggie_clip_label, 5, 0)
        layout.addWidget(self.reggie_clip_text_area, 6, 0, 1, 4)

    def reload(self) -> None:
        self._update_offset_check_box()
        self._update_offset_spin_box(True)

    def _update_offset_check_box(self) -> None:
        self.random_offset_check_box.setDisabled(len(globals_.template.selections) <= 1)

    def _update_offset_spin_box(self, update_range: bool | int = False) -> None:
        self.offset_spin_box.setEnabled(
            not self.random_offset_check_box.isChecked()
            and len(globals_.template.selections) > 1
        )
        if isinstance(update_range, bool) and update_range:
            self.offset_spin_box.setRange(
                min(1, len(globals_.template.selections)),
                len(globals_.template.selections),
            )

    def validate(self) -> bool:
        if not self.validate_width() or not self.validate_height():
            return False
        result = generator.validate(
            self.width_spin_box.value(), self.add_edges_check_box.isChecked()
        )
        if result is not None:
            self.reggie_clip_text_area.setPlainText(result)
            return False
        return True

    def validate_width(self) -> bool:
        if self.width_spin_box.value() % 1 != 0:
            return all(
                object.width % 1 != 0
                for selection in globals_.template.selections
                for object in selection.objects
            )
        return True

    def validate_height(self) -> bool:
        if self.height_spin_box.value() % 1 != 0:
            return all(
                object.height % 1 != 0
                for selection in globals_.template.selections
                for object in selection.objects
            )
        return True

    def generate(self) -> None:
        if not self.validate():
            return

        result: list[ReggieObject] | str = ""
        width = self.width_spin_box.value()
        height = self.height_spin_box.value()
        add_edges = self.add_edges_check_box.isChecked()
        if globals_.template.type == RandomizationType.RANDOM:
            result = generator.generate_random(width, height, add_edges)
        elif globals_.template.type in [
            RandomizationType.RANDOM_ROWS,
            RandomizationType.ORDERED_ROWS,
        ]:
            result = generator.generate_rows(
                width,
                height,
                -1
                if self.random_offset_check_box.isChecked()
                else self.offset_spin_box.value(),
                add_edges,
            )
        elif globals_.template.type == RandomizationType.INTERTWINED_ROWS:
            result = generator.generate_intertwined(width, height, add_edges)

        if isinstance(result, str):
            self.reggie_clip_text_area.setPlainText(result)
        else:
            self.reggie_clip_text_area.setPlainText(ReggieClip().write(result))
