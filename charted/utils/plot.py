from charted.utils.types import Bounds


def calculate_plot_corners(
    width: float,
    height: float,
    padding: float = 0,
) -> Bounds:
    x_padding = width * padding
    y_padding = height * padding
    x1 = 0 + x_padding
    x2 = width - x_padding
    y1 = 0 + y_padding
    y2 = height - y_padding
    return Bounds(x1, x2, y1, y2)
