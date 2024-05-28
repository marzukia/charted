def rotate(angle: float, width: float, height: float) -> str:
    """Calculate the SVG transform attribute to rotate the element 180 degrees around its center.

    Args:
        width (float): The width of the SVG element.
        height (float): The height of the SVG element.

    Returns:
        str: The transform attribute string for rotating the SVG element.
    """
    return f"rotate({angle}, {width}, {height})"


def translate(x: float, y: float) -> str:
    """
    Generate an SVG translation string.

    This function generates an SVG translation string that can be used to translate
    an SVG element by the specified x and y coordinates.

    Parameters:
        x (float): The x-coordinate for translation.
        y (float): The y-coordinate for translation.

    Returns:
        str: The SVG translation string in the format "translate(x, y)".

    Example:
        >>> translate(10.0, 20.0)
        'translate(10.0, 20.0)'
    """
    return f"translate({x}, {y})"
