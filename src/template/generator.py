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


def merge_selections(selections: list[Selection]) -> Selection:
    result = Selection([])
    for selection in selections:
        result.objects.extend(selection.objects)
        result.starts.extend(selection.starts)
        result.ends.extend(selection.ends)

    return result


def validate_coverage(obj: ReggieObject, x: int, y: int, map: list[list[bool]]) -> bool:
    x_max = x + obj.width
    y_max = y + obj.height

    if x_max > len(map[0]) or y_max > len(map):
        return False

    for i in range(y, y_max):
        for j in range(x, x_max):
            if map[i][j]:
                return False

    return True


def validate_near_presence(
    objects: list[ReggieObject], obj: ReggieObject, x: int, y: int
) -> bool:
    if len(objects) == 0:
        return False
    x_range = range(x - obj.width - 1, x + obj.width * 2 + 1)
    y_range = range(y - obj.height - 1, y + obj.height * 2 + 1)

    for o in objects:
        if o.object_num == obj.object_num and o.x in x_range and o.y in y_range:
            return True
    return False


def update_coverage(obj: ReggieObject, x: int, y: int, map: list[list[bool]]) -> None:
    x_max = x + obj.width
    y_max = y + obj.height
    for i in range(y, y_max):
        for j in range(x, x_max):
            map[i][j] = True


def fill_empty(
    objects: list[ReggieObject], one: ReggieObject, map: list[list[bool]]
) -> None:
    obj: ReggieObject | None = None
    vertical_stretch = True
    for i in range(len(map[0])):
        horizontal_stretch = True
        for j in range(len(map)):
            if map[j][i] or j == len(map) and i + 1 < len(map[0]) and map[j][i + 1]:
                if obj is not None:
                    objects.append(obj)
                    obj = None
                    vertical_stretch = True
                    horizontal_stretch = True
                continue
            if obj is None:
                obj = copy.copy(one)
                obj.x = i
                obj.y = j

            if vertical_stretch and j + 1 < len(map) and not map[j + 1][i]:
                j_initial = j
                while j + 1 < len(map) and not map[j + 1][i]:
                    obj.height += 1
                    j += 1
                    map[j][i] = True
                vertical_stretch = False
                horizontal_stretch = False
                j = j_initial

            if horizontal_stretch and i + 1 < len(map[0]) and not map[j][i + 1]:
                i_initial = i
                while (
                    i + 1 < len(map[0])
                    and not map[j][i + 1]
                    and (j == len(map) - 1 or (j + 1 < len(map) and map[j + 1][i + 1]))
                    and (j == 0 or (j - 1 >= 0 and map[j - 1][i + 1]))
                ):
                    obj.width += 1
                    i += 1
                    map[j][i] = True
                horizontal_stretch = False
                i = i_initial
            map[j][i] = True
        if obj is not None:
            objects.append(obj)
            obj = None


def generate_random(
    width: int, height: int, add_edges: bool = False
) -> list[ReggieObject] | str:
    object_list: list[ReggieObject] = []
    selection = merge_selections(globals_.template.selections)
    if not add_edges:
        selection.starts.clear()
        selection.ends.clear()

    singles = [object for object in selection.objects if not object.fixed_size]
    one_by_one: ReggieObject | None = None
    if singles:
        one_by_one = singles[0]
        selection.objects.remove(one_by_one)
    else:
        print("[Warning] - No filler found. Empty spaces will not be filled")

    map: list[list[bool]] = [[] for _ in range(height)]
    for row in map:
        row.extend([False] * width)

    x = 0
    if selection.starts and selection.ends:
        x += selection.starts[0].width
        for row in map:
            for index, _item in enumerate(row):
                if index == 0 or index == width - 1:
                    row[index] = True
        width -= selection.ends[0].width
    y = 0
    attempts = 0
    prev_index = -1
    initial_variance = True
    height_var = False
    width_var = False
    while y < height:
        if all(entry for entry in map[y]):
            y += 1
            continue
        if selection.starts:
            x = selection.starts[0].x
        else:
            x = 0
        while x < width:
            index = -1
            while index == -1 or index == prev_index:
                index = random.randint(0, len(selection.objects) - 1)

            if attempts > 10:
                attempts = 0
                initial_variance = True
                x += 1
                continue
            obj = copy.copy(selection.objects[index])
            if initial_variance:
                initial_variance = False
                height_var = y + obj.height < height and random.random() > 0.75
                width_var = x + obj.width < width and random.random() > 0.75
            attempts += 1
            if x + obj.width > width or y + obj.height > height:
                continue
            if not validate_coverage(obj, x + int(width_var), y + int(height_var), map):
                if not validate_coverage(obj, x, y, map):
                    continue
                height_var = False
                width_var = False
            if obj.width + obj.height <= len(
                selection.objects
            ) and validate_near_presence(object_list, obj, x, y):
                continue

            if height_var:
                y += 1
            if width_var:
                x += 1
            update_coverage(obj, x, y, map)

            obj.x = x
            obj.y = y
            x += obj.width
            prev_index = index
            attempts = 0
            object_list.append(obj)
            if height_var:
                y -= 1
            if width_var:
                x -= 1

            height_var = y + obj.height < height and random.random() > 0.75
            width_var = x + obj.width < width and random.random() > 0.75
        y += 1
    if one_by_one:
        fill_empty(object_list, one_by_one, map)

    if selection.starts and selection.ends:
        start = selection.starts[0]
        end = selection.ends[0]
        start.height = height
        end.height = height
        end.x = width
        object_list.insert(0, start)
        object_list.append(end)

    return object_list


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
        if add_edges and not any(
            selection.starts for selection in globals_.template.selections
        ):
            return "One or more selections have no starting objects"
        if add_edges and not any(
            selection.ends for selection in globals_.template.selections
        ):
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
