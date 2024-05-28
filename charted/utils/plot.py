from charted.utils.types import Bounds


def calculate_plot_corners(
    width: float,
    height: float,
    padding: float = 0,
) -> Bounds:
    """
    Calculate the corners of a plot area with optional padding.

    Args:
        width (float): The width of the plot area.
        height (float): The height of the plot area.
        padding (float, optional): The padding ratio to be applied to all sides of the plot. Defaults to 0.

    Returns:
        Bounds: A tuple containing the coordinates of the corners (x1, x2, y1, y2).
    """
    x_padding = width * padding
    y_padding = height * padding
    x1 = 0 + x_padding
    x2 = width - x_padding
    y1 = 0 + y_padding
    y2 = height - y_padding
    return Bounds(x1, x2, y1, y2)
