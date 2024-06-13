from typing import NamedTuple


Labels = list[str]

Vector = list[float]
Vector2D = list[Vector]


class Bounds(NamedTuple):
    x1: float
    x2: float
    y1: float
    y2: float


class RectDimensions(NamedTuple):
    x_width: float
    column_gap: float
    rect_coordinates: float


class MeasuredText(NamedTuple):
    text: str
    width: float
    height: float


class Coordinate(NamedTuple):
    x: float
    y: float


class AxisDimension(NamedTuple):
    min_value: float
    max_value: float
    raw_min_value: float
    raw_max_value: float
    count: float

    @property
    def value_range(self) -> float:
        return self.max_value - self.min_value
