"""Data model for chart data validation and normalization.

Extracted from Chart class to reduce architectural debt and improve separation of concerns.
"""

import math

from charted.utils.exceptions import (
    InvalidDataError,
    LabelMismatchError,
    NoDataError,
)
from charted.utils.helpers import calculate_text_dimensions
from charted.utils.types import Labels, MeasuredText, Vector, Vector2D


class DataModel:
    """Encapsulates chart data validation and normalization.

    Responsibilities:
    - Validate and normalize x_data, y_data
    - Manage x_labels, y_labels with text dimension calculations
    - Provide default label generation
    - Handle zero_index logic

    This class replaces the data-related properties and validation methods
    that were previously in the Chart base class.
    """

    def __init__(
        self,
        x_data: Vector2D | None = None,
        y_data: Vector2D | None = None,
        x_labels: Labels | None = None,
        y_labels: Labels | None = None,
        zero_index: bool = True,
        skip_label_length_validation: bool = False,
    ) -> None:
        self._skip_label_length_validation = skip_label_length_validation
        self._x_data: Vector2D | None = None
        self._y_data: Vector2D | None = None
        self._x_labels: list[MeasuredText] | None = None
        self._y_labels: list[MeasuredText] | None = None
        self.zero_index = zero_index

        # Set data with validation
        self.x_data = x_data
        self.y_data = y_data
        self.x_labels = x_labels
        self.y_labels = y_labels

        # Cross-check that any provided label axis matches the category count of
        # the data it annotates.
        self._validate_label_lengths()

    def _validate_label_lengths(self) -> None:
        """Ensure provided labels line up with the data they label.

        Labels are optional, so this only fires when both a label set and the
        data it annotates are present.

        The labels describe the *category axis*, and multi-series data shares
        one set of category labels (you do not get one label per series). The
        tricky part is that chart types disagree on which dimension of a 2D
        list is the category axis. Bar, line, and area treat the inner length
        as the categories (one label per point), while a stacked column chart
        treats the outer length as the categories (each inner list is one
        category's stacked segments). To stay correct for every type, a label
        count is accepted when it matches either the inner length or the number
        of series; it is rejected only when it matches neither, which is the
        case that silently truncates or misaligns the chart.

        Across chart types the category axis is wired one of two ways:
        - x-axis charts (column, line, area, ...) pass the category labels as
          ``x_labels`` and the values as ``y_data``.
        - y-axis / categorical charts (bar, pie, ...) pass the category labels
          as ``y_labels`` and the values as ``x_data``.

        Both cross-pairings are validated so every chart type inherits the
        guard.

        Raises:
            LabelMismatchError: If a label count matches neither the per-series
                length nor the number of series of the corresponding data axis.
        """
        if self._skip_label_length_validation:
            return

        if self._x_labels is not None and self._y_data:
            self._check_axis(self._x_labels, self._y_data, axis="x")

        if self._y_labels is not None and self._x_data:
            self._check_axis(self._y_labels, self._x_data, axis="y")

    @staticmethod
    def _check_axis(labels: list[MeasuredText], data: Vector2D, axis: str) -> None:
        """Raise LabelMismatchError if ``labels`` fit no valid orientation of ``data``.

        Accepted counts:
        - ``per_series``: one label per point (bar, line, area, pie, ...).
        - ``n_series``: one label per category for transposed stacks (column).
        - ``per_series + 1``: boundary labels for ``per_series`` intervals
          (histogram bin edges), where N bins are labelled by N+1 edges.

        Everything else means the labels truncate or misalign the data, which
        is the silent failure this guard exists to surface.
        """
        n_labels = len(labels)
        per_series = len(data[0])
        n_series = len(data)
        if n_labels not in (per_series, n_series, per_series + 1):
            raise LabelMismatchError(n_labels=n_labels, n_data=per_series, axis=axis)

    # =========================================================================
    # Data Properties (with validation)
    # =========================================================================

    @classmethod
    def validate_data(cls, data: Vector | Vector2D | None) -> Vector2D | None:
        """Validate and normalize chart data.

        Args:
            data: Single series (list of values) or multi-series (list of lists)

        Returns:
            Normalized 2D array (list of lists) or None

        Raises:
            NoDataError: If data is empty
            InvalidDataError: If data has mismatched lengths or invalid values
        """
        if data is not None and len(data) == 0:
            raise NoDataError("No data was provided.")

        if not data:
            return None

        # Convert single series to 2D
        if not isinstance(data[0], list):
            data = [data]

        max_length = max([len(i) for i in data])

        if not all([len(i) == max_length for i in data]):
            raise InvalidDataError("Not all data vectors were the same length")

        # Validate values (no NaN)
        for series in data:
            for value in series:
                if not isinstance(value, (int, float)):
                    raise InvalidDataError(
                        f"Invalid data value: {value!r} - expected numeric type"
                    )
                if isinstance(value, float) and (value != value):  # NaN check
                    raise InvalidDataError("NaN values are not allowed in chart data")
                if isinstance(value, float) and math.isinf(value):
                    raise InvalidDataError(
                        "Infinite values are not allowed in chart data"
                    )

        return data

    @classmethod
    def create_default_labels(cls, array_len: int) -> Labels:
        """Create default numeric labels for ordinal charts.

        Args:
            array_len: Number of labels to generate

        Returns:
            List of string labels ["0", "1", "2", ...]
        """
        return [str(i) for i in range(array_len)]

    @property
    def x_data(self) -> Vector2D:
        """Get validated x-axis data."""
        return self._x_data  # type: ignore

    @x_data.setter
    def x_data(self, data: Vector | Vector2D | None = None) -> None:
        """Set and validate x-axis data."""
        self._x_data = self.validate_data(data)

    @property
    def y_data(self) -> Vector2D:
        """Get validated y-axis data."""
        return self._y_data  # type: ignore

    @y_data.setter
    def y_data(self, data: Vector | Vector2D | None = None) -> None:
        """Set and validate y-axis data."""
        self._y_data = self.validate_data(data)

    @property
    def x_labels(self) -> list[MeasuredText] | None:
        """Get x-axis labels with text dimensions."""
        return self._x_labels

    @x_labels.setter
    def x_labels(self, x_labels: Labels | None) -> None:
        """Set x-axis labels and calculate text dimensions."""
        if x_labels:
            self._x_labels = [calculate_text_dimensions(label) for label in x_labels]
        else:
            self._x_labels = None

    @property
    def y_labels(self) -> list[MeasuredText] | None:
        """Get y-axis labels with text dimensions."""
        return self._y_labels

    @y_labels.setter
    def y_labels(self, y_labels: Labels | None) -> None:
        """Set y-axis labels and calculate text dimensions."""
        if y_labels:
            self._y_labels = [calculate_text_dimensions(label) for label in y_labels]
        else:
            self._y_labels = None

    # =========================================================================
    # Count Properties
    # =========================================================================

    @property
    def x_count(self) -> int:
        """Calculate count of x-axis data points."""
        if not self._x_data:
            return len(self._x_labels) if self._x_labels else 0
        return len(self._x_data[0])

    @property
    def y_count(self) -> int:
        """Calculate count of y-axis data points."""
        if not self._y_data:
            return len(self._y_labels) if self._y_labels else 0
        return len(self._y_data[0])
