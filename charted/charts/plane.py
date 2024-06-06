from collections import defaultdict
from typing import Tuple
from charted.utils.types import Vector, Vector2D


class Plane(object):
    def __init__(
        self,
        height: float,
        width: float,
        data: Vector2D,
    ):
        self.bounds = data
        self.data = data
        self.height = height
        self.width = width

    @classmethod
    def get_bounds(cls, data: Vector2D):
        agg = defaultdict(list)
        n = len(data[0])
        for i in range(n):
            for arr in data:
                agg[i].append(arr[i])

        min_x = 0
        max_x = n - 1
        max_y = max([sum([x for x in i if x >= 0]) for i in agg.values()])
        min_y = min([sum([x for x in i if x <= 0]) for i in agg.values()])

        return (min_x, min_y, max_x, max_y)

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        return self._bounds

    @bounds.setter
    def bounds(self, data: Vector2D) -> None:
        self._bounds = self.get_bounds(data)

    @property
    def min_x(self) -> float:
        return self.bounds[0]

    @property
    def min_y(self) -> float:
        return self.bounds[1]

    @property
    def max_x(self) -> float:
        return self.bounds[2]

    @property
    def max_y(self) -> float:
        return self.bounds[3]

    @property
    def x_range(self) -> float:
        return self.max_x - self.min_x

    @property
    def y_range(self) -> float:
        return self.max_y - self.min_y

    @property
    def n(self) -> int:
        return len(self.data[0])

    @classmethod
    def _reproject(
        cls,
        value: float,
        max_value: float,
        min_value: float,
        length: float,
    ) -> float:
        value_range = max_value - min_value
        normalised_value = value / value_range
        return normalised_value * length

    def _reproject_x(self, value: float) -> float:
        return self._reproject(value, self.max_x, self.min_x, self.width)

    def _reproject_y(self, value: float) -> float:
        return self._reproject(value, self.max_y, self.min_y, self.height)

    def reproject(self, coordinate: Tuple[float, float]) -> Tuple[float, float]:
        return [self._reproject_x(coordinate[0]), self._reproject_y(coordinate[1])]

    @property
    def column_width(self, spacing: float = 0.5) -> float:
        width = self.width / (self.n + (self.n + 1) * spacing)
        return width

    @property
    def x_ticks(self) -> Vector:
        return [
            ((self.width / self.n) * i) + (self.column_width / 4)
            for i in range(0, self.n)
        ]

    @property
    def y_values(self) -> Vector2D:
        data = []
        for arr in self.data:
            row = []
            for y in arr:
                v = self._reproject_y(abs(y))
                if y < 0:
                    v = -v
                row.append(v)
            data.append(row)
        return data

    @property
    def y_offset(self) -> Vector2D:
        offsets = []
        negative_offsets = [0] * self.n
        positive_offsets = [0] * self.n

        for row in self.data:
            row_offsets = []
            for i, y in enumerate(row):
                current_offset = 0
                if y >= 0:
                    current_offset = positive_offsets[i]
                    positive_offsets[i] += y
                elif y < 0:
                    current_offset = negative_offsets[i]
                    negative_offsets[i] -= abs(y)
                row_offsets.append(current_offset)
            offsets.append(row_offsets)

        return [[self._reproject_y(y) for y in arr] for arr in offsets]
