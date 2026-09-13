from reggie.reggie_object import ReggieObject


class ReggieClip:
    _start = "ReggieClip"
    _object_structure = (
        "0:%d:%d:%d:%d:%d:%d:%d"  # tileset, object_num, layer, x, y, width, height
    )
    _delimiter = "|"
    _end = "%"

    def __init__(self):
        self.items: list[str] = [self._start]

    def write(self, objects: list[ReggieObject]):
        for object in objects:
            self.items.append(self._object_structure % object.data())
        self.items.append(self._end)
        return self._delimiter.join(self.items)

    @staticmethod
    def is_valid(reggieclip: str) -> bool:
        return (
            reggieclip.startswith(ReggieClip._start)
            and reggieclip.count(":") % 7 == 0
            and reggieclip.endswith(ReggieClip._end)
        )
