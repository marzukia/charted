from __future__ import annotations

import math

from typing import TYPE_CHECKING

from charted.charts.chart import Chart
from charted.html.element import G, Path, Text, Tspan

if TYPE_CHECKING:
    from charted.utils.themes import Theme
    from charted.utils.types import Labels


class PieChart(Chart):
    """A pie chart representing categorical data as slices of a circle.

        Unlike other charts that use x/y data, a pie chart operates on a single
    dataset where values represent portions of a whole.
    """

    def __init__(
        self,
        values: list[float],
        labels: Labels = None,
        colors: list[str] | None = None,
        width: float = 500,
        height: float = 500,
        title: str | None = None,
        theme: Theme | None = None,
        inner_radius: float = 0.0,
    ):
        """Initialize a PieChart.

        Args:
            values: List of numeric values representing slice sizes.
            labels: Optional list of category labels.
            colors: Optional list of colors for slices.
            width: SVG width in pixels.
            height: SVG height in pixels.
            title: Optional chart title.
            theme: Optional theme for styling.
            inner_radius: Inner radius for doughnut mode

            (0.0-1.0, 0 = pie, >0 = doughnut).

        Raises:
            ValueError: If values list is empty, contains
            only zeros, or all values are invalid.
            ValueError: If values contain negative numbers or NaN.
        """
        # Validate input is not empty
        if not values:
            raise ValueError("values list cannot be empty")

        # Validate and process each value
        validated_values: list[float] = []
        for v in values:
            if not isinstance(v, (int, float)):
                raise TypeError(
                    f"All values must be numbers, got {type(v).__name__}: {v!r}"
                )
            if math.isnan(v):
                raise ValueError(f"NaN values are not allowed: {v!r}")
            if v < 0:
                raise ValueError(f"Negative values are not allowed: {v!r}")
            validated_values.append(float(v))

        self._raw_values = validated_values

        # Store parameters (use _custom_colors to avoid triggering property setter)
        self._custom_colors = colors if colors is not None else None
        self.labels = labels if labels is not None else []
        self.inner_radius = inner_radius

        # Validate inner_radius range
        if not 0.0 <= inner_radius <= 1.0:
            raise ValueError(
                f"inner_radius must be between 0.0 and 1.0, got {inner_radius!r}"
            )

        # Calculate total and validate at least one positive value
        total = sum(validated_values)
        if total == 0:
            raise ValueError("At least one value must be greater than 0")

        self._total = total

        # Compute angles for each slice
        self._angles: list[tuple[float, float]] = []
        current_angle = 0.0
        for v in validated_values:
            if v > 0:
                angle_span = (v / total) * 360.0
                self._angles.append((current_angle, current_angle + angle_span))
                current_angle += angle_span
            else:
                # Zero values get a zero-span angle
                self._angles.append((current_angle, current_angle))

        self.render_axes = (
            False  # Set BEFORE super().__init__ to prevent axes from being added
        )
        # Call parent Chart constructor with minimal setup
        # Pie chart doesn't use axes, so we pass minimal data
        super().__init__(
            width=width,
            height=height,
            x_data=[[0]],
            y_data=[[0]],
            title=title,
            theme=theme,
            x_stacked=False,
        )
        # Disable axes - pie charts don't use x/y axes
        self.render_axes = False

    def _slice_path(
        self,
        cx: float,
        cy: float,
        outer_radius: float,
        start_angle: float,
        end_angle: float,
        inner_radius: float = 0.0,
    ) -> str:
        """Generate SVG path data for a pie slice.

        Uses the convention: 0° = top (12 o'clock), clockwise is positive.

        Args:
            cx, cy: Center coordinates of the pie.
            outer_radius: Outer radius of the slice.
            start_angle, end_angle: Start and end angles in
            degrees (0 = top, clockwise).
            inner_radius: Inner radius for doughnut holes (0 = full slice).

        Returns:
            SVG path data string.
        """
        # Special case: single slice covering entire pie (360°)
        angle_diff = (end_angle - start_angle) % 360
        is_full_circle = abs(angle_diff) < 1e-6 or abs(abs(angle_diff) - 360) < 1e-6

        if is_full_circle and inner_radius == 0:
            # Full pie: simple circle
            return (
                f"M {cx + outer_radius} {cy} "
                f"A {outer_radius} {outer_radius} 0 1 1 "
                f"{cx - outer_radius} {cy} "
                f"A {outer_radius} {outer_radius} 0 1 1 "
                f"{cx + outer_radius} {cy} Z"
            )

        # Convert angles to radians (subtract 90° to align: 0°=top, positive=clockwise)
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)

        # Calculate outer arc points
        ox1 = cx + outer_radius * math.cos(start_rad)
        oy1 = cy + outer_radius * math.sin(start_rad)
        ox2 = cx + outer_radius * math.cos(end_rad)
        oy2 = cy + outer_radius * math.sin(end_rad)

        # Determine large_arc flag
        large_arc = 1 if angle_diff > 180 else 0

        # Build path
        path_cmds: list[str] = []

        if inner_radius > 0:
            # Doughnut slice with inner hole
            inner_rad = inner_radius * outer_radius
            ix1 = cx + inner_rad * math.cos(start_rad)
            iy1 = cy + inner_rad * math.sin(start_rad)
            ix2 = cx + inner_rad * math.cos(end_rad)
            iy2 = cy + inner_rad * math.sin(end_rad)

            # Start at outer start, arc to outer end, line to inner end,
            # arc back to inner start, line to outer start
            path_cmds = [
                f"M {ox1} {oy1}",
                f"A {outer_radius} {outer_radius} 0 {large_arc} 1 {ox2} {oy2}",
                f"L {ix2} {iy2}",
                f"A {inner_rad} {inner_rad} 0 {large_arc} 0 {ix1} {iy1}",
                "Z",
            ]
        else:
            # Full pie slice (triangle-like with curved edge)
            path_cmds = [
                f"M {cx} {cy}",
                f"L {ox1} {oy1}",
                f"A {outer_radius} {outer_radius} 0 {large_arc} 1 {ox2} {oy2}",
                "Z",
            ]

        return " ".join(path_cmds)

    def _get_colors(self) -> list[str]:
        """Get colors for slices, using custom colors or theme colors."""
        if self._custom_colors:
            return self._custom_colors[: len(self._angles)]
        if self.colors:
            return self.colors[: len(self._angles)]
        return self.theme.get("colors", [])[: len(self._angles)]

    @property
    def representation(self):
        """Generate the SVG G element containing the pie chart."""
        # Calculate dimensions
        center_x = self.width / 2
        center_y = self.height / 2

        # Calculate radius (fit within bounds with some margin)
        available_radius = min(self.width, self.height) / 2
        outer_radius = available_radius * 0.9  # Leave 10% margin

        if outer_radius <= 0:
            outer_radius = 50  # Minimum radius

        # Get colors
        slice_colors = self._get_colors()

        # Create groups for the pie chart
        slices_g = G()

        for i, (start_angle, end_angle) in enumerate(self._angles):
            # Skip zero-value slices (they have no angle span)
            if start_angle == end_angle:
                continue

            color = (
                slice_colors[i % len(slice_colors)]
                if slice_colors and len(slice_colors) > 0
                else f"#{(hash(str(i)) % 0xFFFFFF):06x}"
            )

            path_d = self._slice_path(
                cx=center_x,
                cy=center_y,
                outer_radius=outer_radius,
                start_angle=start_angle,
                end_angle=end_angle,
                inner_radius=self.inner_radius,
            )

            slices_g.add_child(Path(d=path_d, fill=color))

            # Add label inside the slice
            # Calculate midpoint angle of the slice
            midpoint_angle = (start_angle + end_angle) / 2

            # Calculate label position (70% of the way to the edge)
            label_radius = outer_radius * 0.7
            # Convert angle to radians (same convention as _slice_path)
            label_rad = math.radians(midpoint_angle - 90)
            label_x = center_x + label_radius * math.cos(label_rad)
            label_y = center_y + label_radius * math.sin(label_rad)

            # Get label text and value
            label_text = self.labels[i] if i < len(self.labels) else f"Slice {i + 1}"
            value = self._raw_values[i]
            percentage = (value / self._total) * 100

            # Format text: label\n<value>\n<%>
            lines = [label_text, str(value), f"{percentage:.1f}%"]

            # Create text element with proper font and multi-line support via tspan
            text_elem = Text(
                x=label_x,
                y=label_y,
                text_anchor="middle",
                dominant_baseline="middle",
                fill="white",
                font_size=11,
                font_weight="600",
                font_family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
            )

            # Add each line as a tspan for proper line breaks in SVG
            line_height = 14  # Slightly more than font_size for line spacing
            for idx, line in enumerate(lines):
                y_offset = (idx - len(lines) // 2) * line_height
                tspan = Tspan(
                    text=line,
                    x=label_x,
                    y=label_y + y_offset,
                )
                text_elem.add_child(tspan)

            slices_g.add_child(text_elem)

        return slices_g

    @property
    def x_stacked(self) -> bool:
        """Pie chart doesn't use x_stacked."""
        return False
