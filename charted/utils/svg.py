def calculate_viewbox(width: float, height: float) -> str:
    """Calculate the viewBox attribute for an SVG element.

    Args:
        width (float): The width of the SVG element.
        height (float): The height of the SVG element.

    Returns:
        str: The viewBox attribute string in the format "0 0 width height".
    """
    return f"0 0 {width} {height}"
