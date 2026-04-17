from __future__ import annotations

import math

from charted.charts.chart import Chart
from charted.html.element import G, Path
from charted.utils.themes import Theme
from charted.utils.types import Labels, Vector, Vector2D


class PieChart(Chart):
    """Pie chart with optional doughnut mode.

    Creates a pie chart from categorical data. Set `doughnut=True` and
    `inner_radius` (0-1) to create a doughnut chart.
    """

    def __init__(
        self,
        data: Vector | Vector2D,
        labels: Labels = None,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        doughnut: bool = False,
        inner_radius: float = 0.3,
    ):
        """Initialize pie chart.

        Args:
            data: Values for each slice. Can be a single list [10, 20, 30]
                  or multiple series [[10, 20], [15, 25]].
            labels: Labels for each slice category.
            width: Chart width in pixels.
            height: Chart height in pixels.
            title: Optional chart title.
            theme: Theme configuration or name.
            series_names: Names for multiple data series.
            doughnut: If True, renders as doughnut chart.
            inner_radius: Inner radius ratio (0-1) for doughnut mode.
        """
        self.doughnut = doughnut
        self.inner_radius = min(max(inner_radius, 0.0), 1.0)

        # Store original data for pie slice calculations (x_values gets transformed by parent)
        if not isinstance(data, list) or not data or isinstance(data[0], (int, float)):
            self._pie_data = [list(data)]  # Single series as list of lists
        else:
            self._pie_data = [list(series) for series in data]  # Multiple series

        # Normalize data format for parent class
        if not isinstance(data, list) or not data or isinstance(data[0], (int, float)):
            x_data = [data]
        else:
            x_data = data

        if not x_data or not x_data[0]:
            raise ValueError("No data was provided to the PieChart element.")

        num_slices = len(x_data[0]) if x_data else 0
        num_series = len(x_data) if x_data else 0

        if num_slices <= 0:
            raise ValueError("At least one data point is required for PieChart.")

        # Create dummy y_data for parent (unused in pie chart)
        y_data = [[i for i in range(num_slices)] for _ in range(num_series)]

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            y_labels=labels,
            title=title,
            zero_index=False,
            theme=theme,
            series_names=series_names,
        )

    @property
    def representation(self) -> G:
        """Generate SVG paths for pie slices."""
        center_x = self.width / 2
        center_y = self.height / 2
        outer_radius = min(self.width, self.height) / 2 * 0.85

        # Group for all pie slices
        pie_g = G(
            transform=f"translate({center_x}, {center_y})",
        )

        # Process each series
        color_cycle = self.colors  # Access the color cycle from base class

        for series_idx, pie_data_series in enumerate(self._pie_data):
            # Calculate total for this series
            total = sum(pie_data_series) if pie_data_series else 1
            if total == 0:
                continue

            current_angle = -90  # Start at top (12 o'clock)
            slice_idx = 0  # Track slice index for color cycling

            for value in pie_data_series:
                if total != 0:
                    slice_angle = (value / total) * 360
                else:
                    slice_angle = 0

                # Get color for this slice, cycling through the palette
                slice_color = color_cycle[slice_idx % len(color_cycle)]
                # Calculate slice endpoints
                start_angle_rad = math.radians(current_angle)
                end_angle_rad = math.radians(current_angle + slice_angle)

                # Coordinates for outer arc
                x1 = outer_radius * math.cos(start_angle_rad)
                y1 = outer_radius * math.sin(start_angle_rad)
                x2 = outer_radius * math.cos(end_angle_rad)
                y2 = outer_radius * math.sin(end_angle_rad)

                # Inner coordinates for doughnut
                inner_r = outer_radius * self.inner_radius if self.doughnut else 0
                ix1 = inner_r * math.cos(start_angle_rad)
                iy1 = inner_r * math.sin(start_angle_rad)
                ix2 = inner_r * math.cos(end_angle_rad)
                iy2 = inner_r * math.sin(end_angle_rad)

                # Determine arc flag
                large_arc = 1 if slice_angle > 180 else 0

                # Build path
                if self.doughnut:
                    # Doughnut slice (path with hole)
                    path_d = [
                        f"M {x1} {y1}",
                        f"A {outer_radius} {outer_radius} 0 {large_arc} 1 {x2} {y2}",
                        f"L {ix2} {iy2}",
                        f"A {inner_r} {inner_r} 0 {large_arc} 0 {ix1} {iy1}",
                        "Z",
                    ]
                else:
                    # Regular pie slice (wedge from center)
                    path_d = [
                        "M 0 0",
                        f"L {x1} {y1}",
                        f"A {outer_radius} {outer_radius} 0 {large_arc} 1 {x2} {y2}",
                        "Z",
                    ]

                pie_g.add_child(
                    Path(d=path_d, fill=slice_color, stroke="#333333", stroke_width=1)
                )

                current_angle += slice_angle
                slice_idx += 1  # Increment for next slice's color

        return pie_g
