from reggie.reggie_object import ReggieObject


class Selection:
    def __init__(
        self,
        objects: list[ReggieObject],
        *,
        starts: list[ReggieObject] | None = None,
        ends: list[ReggieObject] | None = None,
    ) -> None:
        self.objects: list[ReggieObject] = objects
        if starts is None:
            starts = []
        if ends is None:
            ends = []
        if len(starts) != len(ends):
            raise ValueError("start and end must have the same amount of objects")
        self.starts = starts
        self.ends = ends

    def get_height(self) -> int:
        if not self.objects:
            return 0
        return self.objects[0].height

    def get_min_width(self) -> int:
        if not self.objects:
            return 0
        return min(obj.width for obj in self.objects)

    @classmethod
    def from_json(cls, data: dict) -> "Selection":
        return cls(
            objects=[ReggieObject.from_json(obj) for obj in data["objects"]],
            starts=[ReggieObject.from_json(start) for start in data["starts"]],
            ends=[ReggieObject.from_json(end) for end in data["ends"]],
        )

    def json(self) -> dict:
        return {
            "starts": [start.json() for start in self.starts],
            "ends": [end.json() for end in self.ends],
            "objects": [obj.json() for obj in self.objects],
        }
