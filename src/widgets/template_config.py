from PyQt6 import QtCore, QtWidgets

from data import globals_
from template.randomization_type import RandomizationType


class TemplateConfigWidget(QtWidgets.QGroupBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("Config")

        self._init_widgets()
        self._create_layout()

    def _init_widgets(self) -> None:
        self.type_label = QtWidgets.QLabel("Randomization Type", self)
        self.type_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.type_combo_box = QtWidgets.QComboBox(self)
        self.type_combo_box.addItems(
            [rand_type.value[1] for rand_type in RandomizationType]
        )
        self.type_combo_box.currentIndexChanged.connect(self._on_type_changed)
        self.selection_min_width_label = QtWidgets.QLabel("Group Min Width", self)
        self.selection_min_width_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.selection_min_width_spin_box = QtWidgets.QSpinBox(self)
        self.selection_min_width_spin_box.setRange(1, 255)
        self.selection_min_width_spin_box.valueChanged.connect(
            self._on_selection_min_width_changed
        )
        self.selection_max_width_label = QtWidgets.QLabel("Group Max Width", self)
        self.selection_max_width_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.selection_max_width_spin_box = QtWidgets.QSpinBox(self)
        self.selection_max_width_spin_box.setRange(1, 255)
        self.selection_max_width_spin_box.setValue(255)
        self.selection_max_width_spin_box.valueChanged.connect(
            self._on_selection_max_width_changed
        )

        self.selection_min_width_label.setVisible(False)
        self.selection_min_width_spin_box.setVisible(False)
        self.selection_max_width_label.setVisible(False)
        self.selection_max_width_spin_box.setVisible(False)

    def _create_layout(self) -> None:
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.type_label, 0, 0)
        layout.addWidget(self.type_combo_box, 0, 1)
        layout.addWidget(self.selection_min_width_label, 1, 0)
        layout.addWidget(self.selection_min_width_spin_box, 1, 1)
        layout.addWidget(self.selection_max_width_label, 1, 2)
        layout.addWidget(self.selection_max_width_spin_box, 1, 3)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        self.setLayout(layout)

    def reload(self) -> None:
        self.type_combo_box.setCurrentIndex(globals_.template.type.value[0])
        self.selection_min_width_spin_box.setValue(
            globals_.template.selection_min_width
        )
        self.selection_max_width_spin_box.setValue(
            globals_.template.selection_max_width
        )
        self.selection_min_width_spin_box.setMaximum(
            globals_.template.selection_max_width
        )
        self.selection_max_width_spin_box.setMinimum(
            globals_.template.selection_min_width
        )

    def _on_type_changed(self, index: int) -> None:
        globals_.template.type = RandomizationType.from_id(index)
        intertwined = globals_.template.type == RandomizationType.INTERTWINED_ROWS
        self.selection_min_width_label.setVisible(intertwined)
        self.selection_min_width_spin_box.setVisible(intertwined)
        self.selection_max_width_label.setVisible(intertwined)
        self.selection_max_width_spin_box.setVisible(intertwined)

    def _on_selection_min_width_changed(self, value: int) -> None:
        globals_.template.selection_min_width = value
        self.selection_max_width_spin_box.setMinimum(value)

    def _on_selection_max_width_changed(self, value: int) -> None:
        globals_.template.selection_max_width = value
        self.selection_min_width_spin_box.setMaximum(value)
