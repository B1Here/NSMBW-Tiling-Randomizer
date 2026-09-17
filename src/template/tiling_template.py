import json
from io import TextIOWrapper
from typing import Any

from template.randomization_type import RandomizationType
from template.selection import Selection


class TilingTemplate:
    def __init__(
        self,
        type: RandomizationType,
        selections: list[Selection],
        file_name: str | None = None,
    ):
        self.type: RandomizationType = type
        self.selections = selections
        self.file_name = file_name
        self.selection_min_width: int = 1
        self.selection_max_width: int = 255

    def from_json(self, data: TextIOWrapper):
        json_data = json.load(data)
        self.type = RandomizationType.from_id(json_data["type"])
        selections = []
        for selection_data in json_data["selections"]:
            selections.append(Selection.from_json(selection_data))
        self.selections = selections
        self.file_name = data.name
        if self.type == RandomizationType.INTERTWINED_ROWS:
            self.selection_min_width = json_data.get("selection_min_width", 1)
            self.selection_max_width = json_data.get("selection_max_width", 1)

    def json(self) -> dict[str, Any]:
        return {
            "type": self.type.value[0],
            "selections": [selection.json() for selection in self.selections],
            "selection_min_width": self.selection_min_width
            if self.type == RandomizationType.INTERTWINED_ROWS
            else None,
            "selection_max_width": self.selection_max_width
            if self.type == RandomizationType.INTERTWINED_ROWS
            else None,
        }
