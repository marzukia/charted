import math
from typing import List
from charted.utils.types import Vector


def calculate_axis_coordinates(length: float, no_ticks: int, zero: float = 0) -> Vector:
    positive_length = zero
    negative_length = length - zero

    tick = length / no_ticks
    positive_ticks = math.floor(positive_length / tick)
    negative_ticks = math.floor(negative_length / tick)
    while no_ticks > (positive_ticks + negative_ticks):
        positive_ticks = math.floor(positive_length / tick)
        negative_ticks = math.floor(negative_length / tick)
        tick = tick * 0.9

    ticks = []

    for i in range(positive_ticks):
        ticks.append(zero - (tick * (i + 1)))

    for i in range(negative_ticks):
        ticks.append(zero + (tick * (i + 1)))

    return ticks


def get_path(x: float, y: float, width: float, height: float) -> List[str]:
    return " ".join(
        [
            f"M{x} {y}",
            f"h{width}",
            f"v{height}",
            f"h{-width}",
            f"v{-1 * height}Z",
        ]
    )
