import json
import sys
from collections.abc import Callable
from typing import Literal

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QKeySequence

from data import globals_
from template.randomization_type import RandomizationType
from template.tiling_template import TilingTemplate
from widgets.generator_tab import GeneratorTabWidget
from widgets.reloadable import GenericWidget
from widgets.template_editor import TemplateEditorWidget

RandomizerSource = Literal["", "tpl", "gen"]


class TilingRandomizer(QtWidgets.QMainWindow, GenericWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"NSMBW Tiling Randomizer v{globals_.version}")
        self.setGeometry(100, 100, 800, 600)

        self._create_menu()
        self._init_widgets()
        self._setup_layout()

    def _create_menu(self) -> None:
        menu = self.menuBar()
        if menu is None:
            return

        file_menu = menu.addMenu("File")
        if file_menu is None:
            return

        self._add_action(
            file_menu,
            "New Template",
            self._new_action,
            icon="page_white.png",
            shortcut=QKeySequence.StandardKey.New,
        )

        self._add_action(
            file_menu,
            "Load Template",
            self._load_action,
            icon="folder.png",
            shortcut=QKeySequence.StandardKey.Open,
        )

        file_menu.addSeparator()

        self._add_action(
            file_menu,
            "Save Template",
            self._save_action_guard,
            icon="disk.png",
            shortcut=QKeySequence.StandardKey.Save,
        )

        self._add_action(
            file_menu,
            "Save Template As",
            self._save_as_action,
            icon="disk_multiple.png",
            shortcut=QKeySequence.StandardKey.SaveAs,
        )

        file_menu.addSeparator()

        self._add_action(
            file_menu,
            "Quit",
            self.close,
            icon="cross.png",
            shortcut=QKeySequence.StandardKey.Quit,
        )

        help_menu = menu.addMenu("Help")
        if help_menu is None:
            return

        self._add_action(
            help_menu,
            "About",
            self._about_action,
            icon="information.png",
        )

    def _add_action(
        self,
        menu: QtWidgets.QMenu,
        text: str,
        callback: Callable[..., None | bool] | QtCore.pyqtBoundSignal,
        *,
        shortcut: QKeySequence | QKeySequence.StandardKey | None = None,
        icon: str | None = None,
    ) -> None:
        action = menu.addAction(text)
        if action is None:
            return

        action.triggered.connect(callback)
        if icon is not None:
            action.setIcon(QtGui.QIcon(f"./image/icon/{icon}"))
        if shortcut is not None:
            action.setShortcut(shortcut)

    def _init_widgets(self) -> None:
        self.central_widget = QtWidgets.QWidget()
        self.tab_list = QtWidgets.QTabWidget(self)

        self.generator_tab_widget = GeneratorTabWidget(self)
        self.template_editor_widget = TemplateEditorWidget(self)
        self.template_editor_widget.list_updated.connect(self.reload)

        self.tab_list.addTab(self.generator_tab_widget, "Generator")
        self.tab_list.addTab(self.template_editor_widget, "Template Editor")

    def _setup_layout(self) -> None:
        self.setCentralWidget(self.central_widget)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tab_list)

        self.central_widget.setLayout(layout)

    def _new_action(self) -> None:
        globals_.template = TilingTemplate(RandomizationType.RANDOM_ROWS, [])
        self.reload()

    def _load_action(self) -> None:
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load Template",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_name:
            with open(file_name, "r") as f:
                globals_.template.from_json(f)
            globals_.template.file_name = file_name
            self.reload()

    def _save_action_guard(self) -> None:
        if globals_.template.file_name is None:
            self._save_as_action()
        else:
            self._save_action()

    def _save_action(self) -> None:
        with open(f"{globals_.template.file_name}", "w") as f:
            f.write(json.dumps(globals_.template.json(), indent=2))

    def _save_as_action(self) -> None:
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Template",
            globals_.template.file_name or "template.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_name:
            globals_.template.file_name = file_name
            self._save_action()

    def _about_action(self) -> None:
        QtWidgets.QMessageBox.about(
            self,
            "About",
            f"NSMBW Tiling Randomizer v{globals_.version}",
        )

    def reload(self, source: RandomizerSource = "") -> None:
        if source != "tpl":
            self.template_editor_widget.reload()
        if source != "gen":
            self.generator_tab_widget.reload()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = TilingRandomizer()
    main_window.show()
    sys.exit(app.exec())
