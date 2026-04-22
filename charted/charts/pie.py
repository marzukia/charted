from __future__ import annotations

import math

from charted.charts.chart import Chart
from charted.config import get_pie_label_font_size
from charted.html.element import G, Path, Text
from charted.utils.colors import complementary_color, get_contrast_color
from charted.utils.defaults import DEFAULT_COLORS
from charted.utils.themes import Theme
from charted.utils.types import Labels, SeriesStyleConfig, Vector


class PieChart(Chart):
    """Pie chart for displaying categorical data as proportional slices.

    Renders data as a circular chart divided into slices where each
    slice's arc length (and area) is proportional to its value.
    Supports doughnut mode, slice explosion, and custom labeling.

    Args:
        data: Values for each slice (must be non-negative, sum > 0)
        labels: Optional labels for each slice
        width, height: Chart dimensions in pixels
        title: Optional chart title
        theme: Optional theme configuration
        inner_radius: Ratio (0.0-1.0) for doughnut hole; 0 = regular pie
        explode: Single value or list to offset slices from center (pixels)
        start_angle: Starting angle in degrees (0 = top, clockwise)
        series_styles: Optional per-slice styling overrides

    Example:
        >>> from charted import PieChart
        >>> # Basic pie chart
        >>> chart = PieChart(
        ...     data=[25, 35, 40],
        ...     labels=['Product A', 'Product B', 'Product C']
        ... )
        >>> chart.save('market_share.svg')
        >>>
        >>> # Doughnut chart with exploded slice
        >>> chart = PieChart(
        ...     data=[15, 25, 35, 25],
        ...     labels=['Q1', 'Q2', 'Q3', 'Q4'],
        ...     inner_radius=0.5,
        ...     explode=[10, 0, 0, 0]
        ... )
    """

    """Pie chart for displaying categorical data as proportional slices."""
    render_axes = False  # Pie charts don't need axes or grid lines
    render_axes = False  # Pie charts don't need axes or grid lines

    def __init__(
        self,
        data: Vector,
        labels: Labels = None,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
        inner_radius: float = 0,
        explode: float | Vector = 0,
        start_angle: float = 0,
        series_styles: list[SeriesStyleConfig] | None = None,
    ):
        """Initialize pie chart.

        Args:
            data: Values for each slice (must be non-negative, sum > 0)
            labels: Optional labels for each slice
            width, height: Chart dimensions in pixels
            title: Optional chart title
            theme: Optional theme configuration
            inner_radius: Ratio (0.0-1.0) for doughnut hole; 0 = regular pie
            explode: Single value or list to offset slices from center (pixels)
            start_angle: Starting angle in degrees (0 = top, clockwise)
            series_styles: Optional per-slice styling overrides
        """
        # Validate inputs
        if not data or len(data) == 0:
            raise ValueError("Data cannot be empty")
        if any(
            not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v)
            for v in data
        ):
            raise ValueError("Data must contain only valid numbers")

        if any(v < 0 for v in data):
            raise ValueError("Data values cannot be negative")

        total = sum(data)
        if total == 0:
            raise ValueError("Total of all values must be greater than 0")

        self.inner_radius = inner_radius
        self.explode = explode if isinstance(explode, list) else [explode] * len(data)
        self.start_angle = start_angle
        self._pie_data = list(data)  # Store original data for rendering
        self._pie_labels = labels
        self.series_styles = series_styles

        # Create synthetic x_data and y_data for Chart base class compatibility
        x_data = [[i for i in range(len(data))]]
        y_data = [[0, 1]]  # Minimal y range

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            y_labels=labels,
            title=title,
            zero_index=True,
            theme=theme,
            chart_type="pie",
        )

        # Override colors to match data length
        self.colors = data  # Will trigger color generation

    @property
    def colors(self) -> list[str]:
        return self._colors

    @colors.setter
    def colors(self, data: Vector) -> None:
        """Generate colors based on data length."""
        if not data:
            self._colors = list(DEFAULT_COLORS)
            return

        n = len(data)
        # Use DEFAULT_COLORS as base and generate complementary colors
        base_colors = list(DEFAULT_COLORS)
        self._colors = []
        for i in range(n):
            color_idx = i % len(base_colors)
            if i < len(base_colors):
                self._colors.append(base_colors[color_idx])
            else:
                # Generate additional complementary colors
                self._colors.append(complementary_color(base_colors[color_idx]))

    def _get_slice_path(
        self, cx: float, cy: float, radius: float, start_angle: float, end_angle: float
    ) -> str:
        """Generate SVG path data for a pie slice.

        Args:
            cx, cy: center coordinates
            radius: radius of the pie
            start_angle, end_angle: in degrees (0 = top, clockwise)
        """
        # Convert angles to radians (subtract 90deg to shift: 0deg->top, positive=clockwise)
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)

        # Calculate start and end points on circumference
        x1 = cx + radius * math.cos(start_rad)
        y1 = cy + radius * math.sin(start_rad)
        x2 = cx + radius * math.cos(end_rad)
        y2 = cy + radius * math.sin(end_rad)

        # Determine large_arc flag (1 if arc > 180deg, else 0)
        angle_span = (end_angle - start_angle) % 360
        large_arc = 1 if angle_span > 180 else 0

        # Build path: move to center, line to start, arc to end, close

        if self.inner_radius > 0:
            # Doughnut mode: need inner path too
            # inner_radius is a ratio (0.0-1.0) of the outer radius
            actual_inner_radius = radius * self.inner_radius
            inner_x1 = cx + actual_inner_radius * math.cos(start_rad)
            inner_y1 = cy + actual_inner_radius * math.sin(start_rad)
            inner_x2 = cx + actual_inner_radius * math.cos(end_rad)
            inner_y2 = cy + actual_inner_radius * math.sin(end_rad)

            path = [
                f"M {x1} {y1}",  # Start at outer edge
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2}",  # Arc to end
                f"L {inner_x2} {inner_y2}",  # Line to inner edge
                f"A {actual_inner_radius} {actual_inner_radius} 0 {large_arc} 0 {inner_x1} {inner_y1}",
                # Inner arc
                "Z",  # Close
            ]
        else:
            # Standard pie: move to center, line to start, arc to end, close
            path = [
                f"M {cx} {cy}",  # Move to center
                f"L {x1} {y1}",  # Line to start point
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2}",  # Arc to end
                "Z",  # Close (back to center)
            ]

        return " ".join(path)

    def _get_full_circle_path(self, cx: float, cy: float, radius: float) -> list[str]:
        """Generate SVG path for a full circle (100% slice case)."""
        if self.inner_radius > 0:
            # Doughnut: use two circles with different fill rules
            actual_inner_radius = radius * self.inner_radius
            return [
                f"M {cx} {cy - radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy + radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy - radius}",
                "Z",
                f"M {cx} {cy - actual_inner_radius}",
                f"A {actual_inner_radius} {actual_inner_radius} 0 1 0 {cx} {cy + actual_inner_radius}",
                f"A {actual_inner_radius} {actual_inner_radius} 0 1 0 {cx} {cy - actual_inner_radius}",
                "Z",
            ]

        else:
            return [
                f"M {cx} {cy - radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy + radius}",
                f"A {radius} {radius} 0 1 1 {cx} {cy - radius}",
                "Z",
            ]

    @property
    def representation(self) -> G:
        """Render the pie chart."""
        result = G()

        # Calculate center and radius
        cx = self.width / 2
        cy = self.height / 2
        radius = min(self.width, self.height) / 2 * 0.8

        # Get data and labels (use stored values, not x_data which is synthetic)
        data = self._pie_data
        labels = self._pie_labels or [str(i) for i in range(len(data))]

        total = sum(data)
        current_angle = self.start_angle

        # Render each slice
        for i, (value, label) in enumerate(zip(data, labels)):
            angle = (value / total) * 360
            start_angle = current_angle
            end_angle = current_angle + angle

            # Calculate explode offset
            explode_offset = self.explode[i] if i < len(self.explode) else 0
            transform = ""
            if explode_offset > 0:
                # Angle to midpoint of slice
                slice_angle = (start_angle + end_angle) / 2
                slice_rad = math.radians(slice_angle - 90)
                offset_x = explode_offset * math.cos(slice_rad)
                offset_y = explode_offset * math.sin(slice_rad)
                transform = f"translate({offset_x}, {offset_y})"

            # Get slice-specific style if available
            slice_color = self.colors[i % len(self.colors)]
            slice_opacity = 0.8
            if self.series_styles and i < len(self.series_styles):
                style = self.series_styles[i] or {}
                if style.get("fill"):
                    slice_color = style["fill"]
                if style.get("fill_opacity"):
                    slice_opacity = style["fill_opacity"]

            # Handle 100% single-slice edge case
            if angle >= 359.9:
                path_data = self._get_full_circle_path(cx, cy, radius)
                slice_path = Path(
                    d=path_data,
                    fill=slice_color,
                    fill_rule="evenodd" if self.inner_radius > 0 else "nonzero",
                    opacity=slice_opacity,
                )
            else:
                path_data = self._get_slice_path(cx, cy, radius, start_angle, end_angle)
                slice_path = Path(
                    d=path_data,
                    fill=slice_color,
                    opacity=slice_opacity,
                )

            # Wrap in group with transform if exploded
            if transform:
                slice_g = G(transform=transform)
                slice_g.add_child(slice_path)
                result.add_child(slice_g)
            else:
                result.add_child(slice_path)

            # Add label inside slice with color-aware text
            label_angle = (start_angle + end_angle) / 2
            label_rad = math.radians(label_angle - 90)

            # Position label in the middle of the ring for donut, 60% for regular pie

            if self.inner_radius > 0:
                actual_inner_radius = radius * self.inner_radius
                # Place label in the middle of the ring
                label_radius = (actual_inner_radius + radius) / 2
            else:
                label_radius = radius * 0.6

            label_x = cx + label_radius * math.cos(label_rad)
            label_y = cy + label_radius * math.sin(label_rad)

            # Use contrast-aware text color
            text_color = get_contrast_color(slice_color)

            label_text = Text(
                x=label_x,
                y=label_y,
                text=str(label),
                fill=text_color,
                font_size=get_pie_label_font_size(),
                font_family="Helvetica",
                text_anchor="middle",
                dominant_baseline="middle",
            )
            result.add_child(label_text)

            current_angle = end_angle

        return result
