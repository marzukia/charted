"""Layout calculation utilities for charted.

Extracted from Chart class to reduce coupling and improve testability.
"""

from charted.utils.helpers import (
    calculate_rotation_angle,
    calculate_text_dimensions,
    rotate_coordinate,
)
from charted.utils.types import MeasuredText, Vector2D


def calculate_plot_dimensions(width: float, height: float,
                              left_padding: float, right_padding: float,
                              top_padding: float, bottom_padding: float) -> tuple[float, float]:
    """Calculate available plot area dimensions.

    Args:
        width: Total chart width.
        height: Total chart height.
        left_padding: Left padding in pixels.
        right_padding: Right padding in pixels.
        top_padding: Top padding in pixels.
        bottom_padding: Bottom padding in pixels.

    Returns:
        Tuple of (plot_width, plot_height).
    """
    plot_width = width - (left_padding + right_padding)
    plot_height = height - (top_padding + bottom_padding)
    return plot_width, plot_height


def calculate_padding_from_labels(labels: list[MeasuredText] | list[str] | None,
                                  h_pad: float,
                                  axis_reproject_func=None) -> float:
    """Calculate horizontal padding needed for y-axis labels.

    Args:
        labels: Y-axis labels (MeasuredText objects or strings).
        h_pad: Base horizontal padding in pixels.
        axis_reproject_func: Optional function to convert numbers to text.

    Returns:
        Total left padding in pixels.
    """
    if not labels:
        return h_pad

    max_width = 0.0
    for label in labels:
        if hasattr(label, "width"):
            width = label.width
        else:
            width = calculate_text_dimensions(str(label)).width
        if width > max_width:
            max_width = width

    return h_pad + max_width


def calculate_top_padding(v_pad: float, title: MeasuredText | None) -> float:
    """Calculate top padding including title space.

    Args:
        v_pad: Base vertical padding in pixels.
        title: Chart title if present.

    Returns:
        Total top padding in pixels.
    """
    offset = 0
    if title:
        offset += title.height * 1.5
    return v_pad + offset


def calculate_bottom_padding(v_pad: float, x_label_rotation: tuple | None) -> float:
    """Calculate bottom padding including rotated label space.

    Args:
        v_pad: Base vertical padding in pixels.
        x_label_rotation: Rotation tuple (angle, width) if labels are rotated.

    Returns:
        Total bottom padding in pixels.
    """
    if not x_label_rotation:
        return v_pad

    rotation_angle, width = x_label_rotation
    x, y = (width, 0)
    _, dy = rotate_coordinate(x, y, rotation_angle)
    return v_pad + abs((dy - y))


def calculate_x_label_rotation(labels: list[MeasuredText] | None,
                               x_width: float) -> tuple[float, float] | None:
    """Calculate optimal rotation angle for x-axis labels.

    Args:
        labels: X-axis labels with width information.
        x_width: Available width per label.

    Returns:
        Tuple of (rotation_angle, max_label_width) or None if no labels.
    """
    if not labels:
        return None

    rotation_angle = 0
    width = 0
    for label in labels:
        angle = calculate_rotation_angle(label.width, x_width)
        width = max(width, label.width)
        if angle and (angle > rotation_angle):
            rotation_angle = max(angle, rotation_angle)

    return rotation_angle, width


def calculate_bar_width(plot_width: float, count: int) -> float:
    """Calculate width for each bar in a bar chart.

    Args:
        plot_width: Total available plot width.
        count: Number of bars.

    Returns:
        Width per bar.
    """
    if count == 0:
        return 0
    return plot_width / count


def calculate_viewbox(width: float, height: float) -> str:
    """Calculate SVG viewBox attribute.

    Args:
        width: Chart width.
        height: Chart height.

    Returns:
        ViewBox string (e.g., "0 0 500 500").
    """
    return f"0 0 {width} {height}"


def get_base_transform(h_pad: float, bottom_padding: float,
                       plot_width: float, width: float, height: float) -> list:
    """Get base transformation matrix for chart coordinates.

    Args:
        h_pad: Horizontal padding.
        bottom_padding: Bottom padding.
        plot_width: Plot area width.
        width: Total chart width.
        height: Total chart height.

    Returns:
        List of transformation operations.
    """
    from charted.utils.transform import rotate, scale, translate

    return [
        translate(-h_pad, -bottom_padding),
        rotate(180, width / 2, height / 2),
        scale(-1, 1),
        translate(-plot_width, 0),
    ]


def calculate_x_offset(x_labels: list | None, x_data: Vector2D | None,
                       axis_reproject_func) -> float:
    """Calculate x-offset for ordinal charts.

    Args:
        x_labels: X-axis labels (for ordinal charts).
        x_data: Explicit x-data (for XY charts).
        axis_reproject_func: Function to reproject values.

    Returns:
        Offset value (0 for XY charts, tick width for ordinal charts).
    """
    if x_labels and x_data is None:
        return axis_reproject_func(1)
    return 0


def calculate_stacked_value(y: float, y_offset: float,
                           stacked: bool) -> float:
    """Apply stacking offset to a value.

    Args:
        y: Base value.
        y_offset: Stacking offset.
        stacked: Whether stacking is enabled.

    Returns:
        Stacked or unstacked value.
    """
    return y + y_offset if stacked else y
