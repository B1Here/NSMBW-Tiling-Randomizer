class ReggieObject:
    def __init__(
        self,
        tileset_slot: int,
        object_num: int,
        width: int,
        height: int,
        layer: int,
        *,
        resizable: bool = False,
    ) -> None:
        self.tileset_slot = tileset_slot
        self.object_num = object_num
        self.layer = layer
        self.x: int = 0
        self.y: int = 0
        self.width = width
        self.height = height
        self.resizable = resizable

    def data(self) -> tuple[int, int, int, int, int, int, int]:
        return (
            self.tileset_slot,
            self.object_num,
            self.layer,
            self.x,
            self.y,
            self.width,
            self.height,
        )

    @classmethod
    def from_json(cls, data: dict) -> "ReggieObject":
        return cls(
            data["tileset_slot"],
            data["object_num"],
            data["width"],
            data["height"],
            layer=data["layer"],
            resizable=data.get("resizable", False),
        )

    def json(self) -> dict:
        return {
            "tileset_slot": self.tileset_slot,
            "object_num": self.object_num,
            "width": self.width,
            "height": self.height,
            "layer": self.layer,
            "resizable": self.resizable if self.resizable else None,
        }
