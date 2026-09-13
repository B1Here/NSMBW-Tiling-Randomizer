import copy
import random

from data import globals_
from reggie.reggie_object import ReggieObject
from template.randomization_type import RandomizationType
from template.selection import Selection


def get_merged_object_list() -> list[ReggieObject]:
    return [
        obj for selection in globals_.template.selections for obj in selection.objects
    ]


def generate_random(
    width: int, y: int, add_edges: bool = False
) -> list[ReggieObject] | str:
    objects = get_merged_object_list()

    _fixed_objects = [obj for obj in objects if obj.fixed_size]
    _resizable_objects = [obj for obj in objects if not obj.fixed_size]
    return "Not implemented yet..."


def generate_row(
    selection: Selection, width: int, x: int, y: int, add_edges: bool = False
) -> list[ReggieObject] | str:
    iteration = 0
    object_list: list[ReggieObject] = []
    offset_by_edge = get_highest_width(selection.starts)
    edge_widths = offset_by_edge + get_highest_width(selection.ends)
    if add_edges:
        width -= edge_widths
        if width < 0:
            return f"Width must be at least {edge_widths} to accommodate edges"

    original_width = width

    if len(selection.objects) == 1 and not selection.objects[0].fixed_size:
        obj_copy = copy.copy(selection.objects[0])
        obj_copy.width = width
        obj_copy.x = x + offset_by_edge
        obj_copy.y = y
        object_list.append(obj_copy)
        width = 0
    else:
        previous_index = -1
        index = -1
        while width > 0:
            obj: ReggieObject | None = None
            if width == 1:
                single_tile_objects = (
                    o for o in selection.objects if o is not None and o.width == 1
                )
                if original_width == width:
                    obj = next(single_tile_objects)
            else:
                index = random.randint(0, len(selection.objects) - 1)
                while index == previous_index:
                    index = random.randint(0, len(selection.objects) - 1)
                obj = selection.objects[index]

            if obj is None or obj.width > width:
                object_list.clear()
                width = original_width
                iteration += 1
                if iteration > 100:
                    break
                continue
            obj_copy = copy.copy(obj)
            obj_copy.x = original_width - width + x + offset_by_edge
            obj_copy.y = y
            object_list.append(obj_copy)
            width -= obj.width
            previous_index = index

    if not add_edges or selection.starts is None or selection.ends is None:
        return object_list

    edge_tile_index = random.randint(0, len(selection.starts) - 1)
    start_copy = copy.copy(selection.starts[edge_tile_index])
    start_copy.x = x
    start_copy.y = y
    object_list.insert(0, start_copy)
    width -= selection.starts[edge_tile_index].width

    end_copy = copy.copy(selection.ends[edge_tile_index])
    end_copy.x = x + original_width - width
    end_copy.y = y
    object_list.append(end_copy)

    return object_list


def generate_rows(
    width: int, height: int, offset: int, add_edges: bool = False
) -> list[ReggieObject] | str:
    object_list: list[ReggieObject] = []
    pos_y = 0
    selection_index = 0
    if offset == -1:
        selection_index = random.randint(0, len(globals_.template.selections) - 1)
    else:
        selection_index = offset - 1

    while pos_y < height:
        selection = globals_.template.selections[selection_index]
        result = generate_row(
            selection,
            width,
            0,
            pos_y,
            add_edges,
        )
        if not result:
            result = "Failed to generate sequence"

        if isinstance(result, str):
            return result
        object_list.extend(result)
        if globals_.template.type == RandomizationType.RANDOM_ROWS:
            previous_index = selection_index
            while selection_index == previous_index:
                selection_index = random.randint(
                    0, len(globals_.template.selections) - 1
                )
        else:
            selection_index = (selection_index + 1) % len(globals_.template.selections)
        pos_y += selection.get_height()

    return object_list


def generate_intertwined(
    width: int,
    height: int,
    add_edges: bool = False,
) -> list[ReggieObject] | str:
    selections = globals_.template.selections
    min_width = globals_.template.selection_min_width
    max_width = globals_.template.selection_max_width

    if not selections:
        return []

    object_one_height = selections[0].objects[0].height
    for selection in selections:
        for obj in selection.objects:
            if obj.height != object_one_height:
                return "All objects must have the same height"

    object_list: list[ReggieObject] = []
    original_width = width
    y = 0
    while height > 0:
        while width > 0:
            random_width = random.randint(min_width, max_width)
            if width - random_width < min_width:
                random_width = width
            selection_index = random.randint(0, len(selections) - 1)
            result = generate_row(
                selections[selection_index],
                random_width,
                original_width - width,
                y,
                add_edges,
            )
            if isinstance(result, str):
                return result
            object_list.extend(result)
            width -= random_width
        height -= object_one_height
        y += object_one_height
        width = original_width

    return object_list


def validate(width: int, add_edges: bool) -> str | None:
    if len(globals_.template.selections) == 0:
        return "No selections available"

    if globals_.template.type == RandomizationType.RANDOM:
        if not len(get_merged_object_list()):
            return "No objects available"
        if not any(selection.starts for selection in globals_.template.selections):
            return "One or more selections have no starting objects"
        if not any(selection.ends for selection in globals_.template.selections):
            return "One or more selections have no ending objects"
    else:
        for selection in globals_.template.selections:
            if not selection.objects:
                return "No objects available in one or more selections"
            if add_edges:
                if not selection.starts:
                    return "One or more selections have no starting objects"
                if not selection.ends:
                    return "One or more selections have no ending objects"

    # While heights are allowed to overflow, widths should never exceed the spin box value
    for selection in globals_.template.selections:
        if selection.get_min_width() > width:
            return "One or more selections have insufficient object widths"

def get_highest_width(object_list: list[ReggieObject] | None) -> int:
    return max([obj.width for obj in object_list]) if object_list else 0
