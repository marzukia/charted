from typing import List, NamedTuple


Labels = List[str]

Vector = List[float]
Vector2D = List[Vector]


class Bounds(NamedTuple):
    x1: float
    x2: float
    y1: float
    y2: float


class RectDimensions(NamedTuple):
    column_width: float
    column_gap: float
    rect_coordinates: float


class MeasuredText(NamedTuple):
    text: str
    width: float


class Coordinate(NamedTuple):
    x: float
    y: float
