"""Data validation utilities for charted.

Extracted from Chart class to reduce coupling and improve testability.
"""

from typing import cast

from charted.utils.exceptions import (
    DataShapeError,
    InvalidValue,
    NoDataError,
)
from charted.utils.types import Vector, Vector2D


def validate_data(data: Vector | Vector2D | None) -> Vector2D | None:
    """Validate and normalize chart data.

    Args:
        data: Input data as Vector (1D) or Vector2D (2D).

    Returns:
        Normalized Vector2D (list of lists).

    Raises:
        Exception: If data is empty or inconsistent lengths.
    """
    if data is not None and len(data) == 0:
        raise NoDataError()

    if not data:
        return None

    # Normalize to 2D
    if type(data[0]) is not list:
        normalized: Vector2D = [cast("Vector", data)]
    else:
        normalized = data

    max_length = max([len(i) for i in normalized])

    if not all([len(i) == max_length for i in normalized]):
        raise DataShapeError(
            expected=f"all series length {max_length}",
            actual="series lengths differ",
            detail=f"Series lengths: {[len(i) for i in normalized]}",
        )

    return normalized


def validate_attribute_value(name: str, value: float) -> float:
    """Validate that an attribute value is non-negative.

    Args:
        name: Name of the attribute being validated.
        value: Value to validate.

    Returns:
        The validated value.

    Raises:
        InvalidValue: If value is negative.
    """
    if value < 0:
        raise InvalidValue(name, value)
    return value


def validate_padding(value: float, max_value: float = 1.0) -> float:
    """Validate padding value (should be between 0 and max_value).

    Args:
        value: Padding value to validate.
        max_value: Maximum allowed value (default 1.0 for ratio-based padding).

    Returns:
        The validated value.

    Raises:
        InvalidValue: If value is out of range.
    """
    if value > max_value:
        raise InvalidValue("padding", value)
    return validate_attribute_value("padding", value)


def validate_series_count(series_styles: list[object] | None, target: int) -> int:
    """Validate and normalize series count.

    Args:
        series_styles: Optional list of series style configurations.
        target: Target number of series.

    Returns:
        Validated series count.
    """
    if series_styles is None:
        return target
    return max(len(series_styles), target)


def match_data_series(x_data: Vector2D | None, y_data: Vector2D) -> Vector2D:
    """Ensure x_data matches y_data series count.

    Args:
        x_data: X-axis data (may be None or single series).
        y_data: Y-axis data (required).

    Returns:
        Normalized x_data matching y_data series count.

    Raises:
        Exception: If series counts don't match and can't be auto-expanded.
    """
    if not x_data and y_data:
        # Return one row per y_data series (needed for stacked rendering)
        return [[i for i in range(len(y_data[0]))] for _ in range(len(y_data))]

    x_data = [*x_data] if x_data else []
    y_len = len(y_data)

    if len(x_data) != y_len:
        if not len(x_data) == 1:
            raise DataShapeError(
                expected=f"x_data series count matches y_data ({y_len})",
                actual=f"x_data has {len(x_data)} series",
                detail=f"x_data has {len(x_data)} series but y_data has {y_len}. "
                "Either match the count or provide a single shared x series.",
            )
        x_data = x_data * y_len

    return x_data


def normalize_labels(labels: list[str] | None) -> list[str] | None:
    """Normalize labels to consistent format.

    Args:
        labels: Input labels (may be None).

    Returns:
        Validated labels list or None.
    """
    if not labels:
        return None
    return list(labels)


def create_default_labels(array_len: int) -> list[str]:
    """Create default blank labels for ordinal charts.

    Args:
        array_len: Number of labels to create.

    Returns:
        List of blank label strings.
    """
    return [" " for _ in range(array_len)]


def get_data_length(data: Vector2D | list[str] | None) -> int:
    """Get the length of data (1D or 2D).

    Args:
        data: Input data array.

    Returns:
        Length of the data.
    """
    if not data:
        return 0
    if type(data[0]) is list:
        return len(data[0])
    return len(data)
