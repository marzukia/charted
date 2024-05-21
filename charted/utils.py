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
    gap: float,
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


def calculate_svg_transform(width: float, height: float) -> str:
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


def normalise_vector(vector: Vector, length: int, zero_index=True) -> Vector:
    """Normalise a list of values to a specified range and scale them to a given length.

    Args:
        vector (Vector): The list of float values to be normalised.
        length (int): The length to which the normalised values should be scaled.
        zero_index (bool): If True, the minimum value is treated as zero for normalisation. Defaults to True.

    Returns:
        Vector: A list of normalised and scaled float values.

    Raises:
        ValueError: If the input vector list is empty.

    Example:
        >>> vector = [10, 20, 30, 40, 50]
        >>> length = 100
        >>> normalise_values(vector, length)
        [0.0, 25.0, 50.0, 75.0, 100.0]
    """
    max_value = max(vector)
    min_value = min(vector)
    if zero_index and min_value > 0:
        min_value = 0
    normalised = [(n - min_value) / (max_value - min_value) for n in vector]
    scaled = [n * length for n in normalised]
    return scaled


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
