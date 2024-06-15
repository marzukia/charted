from typing import NamedTuple


Labels = list[str]

Vector = list[float]
Vector2D = list[Vector]


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
    count: float

    @property
    def value_range(self) -> float:
        return self.max_value - self.min_value
