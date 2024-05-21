from typing import List, NamedTuple, Tuple, Union

Vector = List[float]
Vector2D = List[Vector]


class RectDimensions(NamedTuple):
    column_width: float
    column_gap: float
    rect_coordinates: float
    centre_coordinates: float


def calculate_column_width(
    width: float,
    no_columns: int,
    spacing: float = 0.25,
) -> Tuple[float, float]:
    """
    Calculate the width of each column and the gap between columns based on the total width and the number of columns.

    Args:
        width (float): The total width available for the columns.
        no_columns (int): The number of columns.
        spacing (float, optional): The spacing between columns as a fraction of the column width. Defaults to 0.25.

    Returns:
        Tuple[float, float]: A tuple containing the width of each column and the gap between columns.
    """
    total_width = width - (no_columns + 1) * spacing * width / (2 * no_columns)
    column_width = total_width / no_columns
    column_gap = column_width * spacing
    calculated_width = (column_width * no_columns) + (column_gap * (no_columns + 1))
    factor = width / calculated_width
    return column_width * factor, column_gap * factor


def calculate_rect_dimensions(
    width: float,
    no_columns: int,
    gap: float = 0.5,
) -> RectDimensions:
    """Calculate the dimensions of a rectangle based on the width, number of columns, and gap.

    Args:
        width (float): The total width of the rectangle.
        no_columns (int): The number of columns in the rectangle.
        gap (float): The gap between columns.

    Returns:
        RectDimensions: A tuple containing the dimensions of the rectangle:
            - The list of x-coordinates for each column.
            - The width of each column.
            - The gap between columns.
    """
    column_width, column_gap = calculate_column_width(width, no_columns, gap)
    current_position = column_gap
    rect_coordinates = []
    for i in range(no_columns):
        rect_coordinates.append(current_position)
        current_position += column_width + column_gap
    centre_coordinates = [i + (column_width / 2) for i in rect_coordinates]
    return RectDimensions(
        column_width,
        column_gap,
        rect_coordinates,
        centre_coordinates,
    )


def calculate_svg_rotate(width: float, height: float) -> str:
    """Calculate the SVG transform attribute to rotate the element 180 degrees around its center.

    Args:
        width (float): The width of the SVG element.
        height (float): The height of the SVG element.

    Returns:
        str: The transform attribute string for rotating the SVG element.
    """
    cx = width / 2
    cy = height / 2
    return f"rotate(180, {cx}, {cy})"


def calculate_viewbox(width: float, height: float) -> str:
    """Calculate the viewBox attribute for an SVG element.

    Args:
        width (float): The width of the SVG element.
        height (float): The height of the SVG element.

    Returns:
        str: The viewBox attribute string in the format "0 0 width height".
    """
    return f"0 0 {width} {height}"


def calculate_vector_offsets(vectors: Union[Vector2D, Vector]) -> Vector2D:
    """
    Calculate the cumulative offsets for a list of vectors.

    If a single vector is provided, it will be treated as a list containing one vector.
    The function returns a list of vectors where each vector contains the cumulative
    offsets of the original vectors.

    Args:
        vectors (Union[Vector2D, Vector]): A list of vectors or a single vector.

    Returns:
        Vector2D: A list of vectors containing the cumulative offsets.
    """
    if isinstance(vectors[0], float):
        vectors = [vectors]

    offsets = [[0] * len(vectors[0])]

    for i in range(1, len(vectors)):
        current_offset = []
        for j in range(len(vectors[i])):
            offset_value = offsets[i - 1][j] + vectors[i - 1][j]
            current_offset.append(offset_value)
        offsets.append(current_offset)

    return offsets


def calculate_vector_attributes(
    vectors: Union[Vector, Vector2D], zero_index: bool = True
) -> Tuple[float, float, int]:
    """
    Calculate the minimum and maximum values from a list of vectors.

    If a single vector is provided, it will be treated as a list containing one vector.
    The function returns a tuple with the minimum and maximum values found across all vectors.

    Args:
        vectors (Union[Vector, Vector2D]): A list of vectors or a single vector.

    Returns:
        Tuple[float, float]: A tuple containing the minimum and maximum values.
    """
    if isinstance(vectors[0], float):
        vectors = [vectors]

    no_columns = max([len(vector) for vector in vectors])
    column_sum = [0 for i in range(no_columns)]

    for vector in vectors:
        for i, value in enumerate(vector):
            column_sum[i] += value

    min_value = min(column_sum)
    max_value = max(column_sum)

    if min_value > 0 and zero_index:
        min_value = 0

    return min_value, max_value, no_columns


def calculate_tick_value(max_value: float, min_value: float) -> float:
    """
    Calculate the tick value based on the maximum and minimum values of the axis.

    Args:
        max_value (float): The maximum value of the axis.
        min_value (float): The minimum value of the axis.

    Returns:
        float: The calculated tick value.
    """
    value_range = int(abs(min_value - max_value))
    length = len(str(value_range))
    return 5**length


def calculate_axis_coordinates(length: float, no_ticks: int) -> Vector:
    """
    Calculate the coordinates for ticks along the axis.

    Args:
        length (float): The length of the axis.
        no_ticks (int): The number of ticks to be placed along the axis.

    Returns:
        Vector: A list of coordinates for the ticks along the axis.
    """
    tick = length / no_ticks
    return [(i + 1) * tick for i in range(no_ticks)]


def calculate_svg_transform(
    width: float,
    height: float,
    max_value: float,
    padding: float = 0,
) -> str:
    """
    Calculate the SVG transform string for scaling and translating.

    This function calculates the SVG transform string required for scaling and translating
    based on the provided height and maximum value.

    Args:
        height (float): The height value.
        max_value (float): The maximum value.

    Returns:
        str: The SVG transform string.
    """
    # Calculate the scale and translation values
    x_scale_factor = 1 - padding
    y_scale_factor = (height / max_value) - (padding / 2)
    translation_y = (max_value - height) + (padding * max_value)
    translation_x = (width * padding) / 2

    # Construct and return the SVG transform string
    return f"scale({x_scale_factor}, {y_scale_factor}) translate({translation_x}, {translation_y})"
