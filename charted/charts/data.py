"""Chart data management module.

Extracts data handling responsibilities from the Chart class to improve
maintainability and testability.
"""

from typing import Any

from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.colors import generate_complementary_colors
from charted.utils.types import Labels, SeriesStyleConfig, Vector, Vector2D


class ChartData:
    """Encapsulates chart data, validation, and calculations.

    This class handles all data-related responsibilities that were previously
    in the Chart base class, including:
    - Data validation
    - X/Y data storage and access
    - Offset calculations for stacked charts
    - Value transformations
    - Color generation based on series count

    Attributes:
        x_data: Validated x-axis data as Vector2D
        y_data: Validated y-axis data as Vector2D
        series_names: Names of data series
        series_styles: Style configurations for each series
        colors: Auto-generated color palette for series
    """

    def __init__(
        self,
        x_data: Vector | Vector2D | None = None,
        y_data: Vector | Vector2D | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        x_stacked: bool = False,
        y_stacked: bool = False,
    ):
        """Initialize chart data.

        Args:
            x_data: X-axis data points
            y_data: Y-axis data points  
            series_names: Names for each data series
            series_styles: Style configurations for series
            x_stacked: Whether to stack along x-axis
            y_stacked: Whether to stack along y-axis
        """
        self.series_names = series_names
        self.series_styles = series_styles or []
        self.x_stacked = x_stacked
        self.y_stacked = y_stacked

        # Data properties with validation
        self._x_data: Vector2D | None = None
        self._y_data: Vector2D | None = None
        self.x_data = x_data  # Triggers validation
        self.y_data = y_data  # Triggers validation

        # Derived calculations
        self._x_offsets: Vector2D = []
        self._y_offsets: Vector2D = []
        self._x_values: Vector2D = []
        self._y_values: Vector2D = []
        self._colors: list[str] = []

    @classmethod
    def _validate_data(cls, data: Vector | Vector2D | None) -> Vector2D | None:
        """Validate and normalize data to Vector2D format.

        Args:
            data: Raw data in Vector or Vector2D format

        Returns:
            Normalized Vector2D or None if no data

        Raises:
            Exception: If data is empty or inconsistent lengths
        """
        if data is not None and len(data) == 0:
            raise Exception("No data was provided.")

        if not data:
            return None

        # Convert Vector to Vector2D
        if type(data[0]) is not list:
            data = [data]

        max_length = max([len(i) for i in data])

        if not all([len(i) == max_length for i in data]):
            raise Exception("Not all vectors were same length")

        return data

    @property
    def x_data(self) -> Vector2D | None:
        """Get validated x-axis data."""
        return self._x_data

    @x_data.setter
    def x_data(self, data: Vector | Vector2D | None) -> None:
        """Set and validate x-axis data."""
        self._x_data = self._validate_data(data)

    @property
    def y_data(self) -> Vector2D | None:
        """Get validated y-axis data."""
        return self._y_data

    @y_data.setter
    def y_data(self, data: Vector | Vector2D | None) -> None:
        """Set and validate y-axis data."""
        self._y_data = self._validate_data(data)

    @property
    def x_count(self) -> int:
        """Count of x-axis data points."""
        if not self.x_data:
            return 0
        return len(self.x_data[0])

    @property
    def y_count(self) -> int:
        """Count of y-axis data series."""
        if not self.y_data:
            return 0
        return len(self.y_data)

    @property
    def colors(self) -> list[str]:
        """Get color palette for series."""
        return self._colors

    @colors.setter
    def colors(self, colors: list[str] | None = None) -> None:
        """Generate or set color palette based on series count."""
        if not colors:
            colors = [*DEFAULT_COLORS]

        new_colors = [*colors]
        series_count = max(self.y_count, self.x_count)

        # Generate complementary colors if needed
        while series_count > len(new_colors):
            for color in generate_complementary_colors(colors):
                if len(new_colors) >= series_count:
                    break
                new_colors.append(color)

        self._colors = new_colors

    @property
    def x_values(self) -> Vector2D:
        """Get transformed x-axis values."""
        return self._x_values

    @x_values.setter
    def x_values(self, x_data: Vector2D | None = None) -> None:
        """Calculate transformed x-values based on axis projection.

        Args:
            x_data: Raw x data or None to use existing x_data
        """
        if not x_data and self.x_labels:
            x_data = [[i for i in range(len(self.x_labels))]]
        else:
            x_data = [*x_data] if x_data else []

        y_len = len(self.y_data) if self.y_data else 0
        if len(x_data) != y_len:
            if not len(x_data) == 1:
                raise Exception("x and y data series do not match")
            x_data = x_data * y_len

        # Note: projection logic moved to Chart class (needs axis reference)
        self._x_values = x_data

    @property
    def y_values(self) -> Vector2D:
        """Get transformed y-axis values."""
        return self._y_values

    @y_values.setter
    def y_values(self, y_data: Vector2D | None = None) -> None:
        """Calculate transformed y-values based on axis projection.

        Args:
            y_data: Raw y data or None to use existing y_data
        """
        if not y_data:
            self._y_values = [[0] * self.y_count]
            return

        # Note: projection logic moved to Chart class (needs axis reference)
        self._y_values = y_data

    @property
    def x_offsets(self) -> Vector2D:
        """Get x-axis stacking offsets."""
        return self._x_offsets

    @x_offsets.setter
    def x_offsets(self, x_data: Vector2D | None = None) -> None:
        """Calculate x-axis stacking offsets.

        For stacked charts, accumulates positive and negative values separately.
        """
        if not x_data or not self.x_stacked:
            offsets = [[0] * self.x_count]
            self._x_offsets = offsets
            return

        # Accumulate stacking offsets (projection moved to Chart class)
        offsets = []
        # Size by number of data points per series (row length), not number of series
        num_points = len(x_data[0]) if x_data else 0
        negative_offsets = [0] * num_points
        positive_offsets = [0] * num_points

        for row in x_data:
            row_offsets = []
            for i, x in enumerate(row):
                current_offset = 0
                if x >= 0:
                    current_offset = positive_offsets[i]
                    positive_offsets[i] += x
                elif x < 0:
                    current_offset = negative_offsets[i]
                    negative_offsets[i] -= abs(x)
                row_offsets.append(current_offset)
            offsets.append(row_offsets)

        self._x_offsets = offsets

    @property
    def y_offsets(self) -> Vector2D:
        """Get y-axis stacking offsets."""
        return self._y_offsets

    @y_offsets.setter
    def y_offsets(self, y_data: Vector2D | None = None) -> None:
        """Calculate y-axis stacking offsets.

        For stacked charts, accumulates positive and negative values separately.
        """
        if not y_data:
            offsets = [[0] * self.y_count]
            self._y_offsets = offsets
            return

        # Accumulate stacking offsets (projection moved to Chart class)
        offsets = []
        # Size by number of data points per series (row length), not number of series
        num_points = len(y_data[0]) if y_data else 0
        negative_offsets = [0] * num_points
        positive_offsets = [0] * num_points

        for row in y_data:
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

        self._y_offsets = offsets
