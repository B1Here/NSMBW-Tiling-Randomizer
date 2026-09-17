from enum import Enum


class RandomizationType(Enum):
    RANDOM = (0, "Random (Currently not implemented)")
    RANDOM_ROWS = (1, "Random Rows")
    ORDERED_ROWS = (2, "Ordered Rows")
    INTERTWINED_ROWS = (3, "Intertwined Rows")

    @classmethod
    def from_id(cls, id: int) -> "RandomizationType":
        for type in cls:
            if type.value[0] == id:
                return type
        raise ValueError(f"Invalid randomization type id: {id}")
