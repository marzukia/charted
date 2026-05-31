from dataclasses import dataclass
from typing import NamedTuple, TypedDict

# Re-export exceptions from exceptions.py for backward compatibility


class SeriesStyleConfig(TypedDict, total=False):
    """Per-series styling overrides."""

    fill: str | None
    stroke: str | None
    stroke_width: float | None
    stroke_dasharray: str | None
    marker_shape: str | None  # "circle" | "square" | "diamond" | "none"
    marker_size: float | None
    fill_opacity: float | None
    stroke_opacity: float | None
    area_fill: bool | None
    area_fill_opacity: float | None
    show_markers: bool | None


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


@dataclass
class AxisValues:
    """Structured container for axis data to avoid connascence of position.

    Replaces the tuple (data, labels, zero_index) that was prone to
    ordering errors. Using a dataclass provides:
    - Self-documenting field names
    - Type safety via dataclass validation
    - Easier refactoring and maintenance
    """

    data: Vector2D | None = None
    labels: list[str] | None = None
    zero_index: bool = True
