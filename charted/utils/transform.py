def rotate(angle: float, width: float, height: float) -> str:
    return f"rotate({angle}, {width}, {height})"


def translate(x: float, y: float) -> str:
    return f"translate({x}, {y})"


def scale(x: float, y: float) -> str:
    return f"scale({x}, {y})"
