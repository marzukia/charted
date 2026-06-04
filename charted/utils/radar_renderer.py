"""Radar chart rendering utilities.

Extracts rendering logic from RadarChart to reduce code complexity
and address long function issues (Issue #70).
"""

from __future__ import annotations

import math

from charted.constants import (
    DEFAULT_PADDING,
    FULL_CIRCLE,
    RIGHT_ANGLE,
)
from charted.html.element import Circle, G, Path, Rect, Text
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE


class RadarRenderer:
    """Renderer for radar chart visualization.

    Handles all SVG element generation for radar charts including:
    - Concentric grid circles
    - Axis spokes
    - Axis labels
    - Data series polygons and markers
    """

    def __init__(self, chart):
        """Initialize radar renderer.

        Args:
            chart: RadarChart instance to render
        """
        self.chart = chart

    def render(self) -> G:
        """Generate complete radar chart SVG elements.

        Returns:
            G element containing all chart components
        """
        g = G(transform=[*self.chart.get_base_transform()])
        # Grid, spokes and the semi-transparent data polygons share one 0.8
        # opacity group. The numeric ring labels are kept OUT of this group so
        # they render at full opacity on top of the data instead of inheriting
        # the dimming (a nested opacity=1 would still multiply down to 0.8).
        body = G(opacity=0.8)
        g.add_child(body)

        # Calculate chart center and max radius
        cx = self.chart.width / 2
        cy = self.chart.height / 2
        min_dim = min(self.chart.width, self.chart.height)
        self._max_radius = (min_dim / 2 - DEFAULT_PADDING * 2) * self.chart.radius

        # Ring labels are collected while drawing the grid but rendered last
        # (on top of the data series) so the polygons cannot obscure them.
        self._ring_label_specs: list[tuple[float, float, str]] = []

        # Render concentric grid circles
        self._render_grid(body, cx, cy)

        # Render axis spokes and labels
        self._render_axes(body, cx, cy)

        # Render data series
        self._render_series(body, cx, cy)

        # Render the numeric ring labels on top of everything else (full
        # opacity, not inside the dimmed body) so they stay readable even
        # where a data polygon covers a ring.
        self._render_ring_labels(g)

        return g

    def _ring_color(self) -> str:
        """Theme-aware colour for the radial ring lines.

        Prefers the theme's resolved grid colour (which respects light/dark/
        high-contrast presets and custom overrides) and falls back to the raw
        ``grid_color`` attribute, then a light grey, when no theme is present.
        """
        theme = self.chart.theme
        resolved = getattr(theme, "resolved_grid_color", None)
        if resolved:
            return resolved
        return getattr(theme, "grid_color", "#e0e0e0")

    def _ring_label_color(self) -> str:
        """High-contrast colour for the numeric ring labels.

        The faint grid colour reads fine for the ring lines but is nearly
        invisible for text on a dark background. Use the theme's full-opacity
        label colour so the numbers stay legible on every preset.
        """
        theme = self.chart.theme
        resolved = getattr(theme, "resolved_label_color", None)
        if resolved:
            return resolved
        return getattr(theme, "title_color", "#333")

    def _ring_label_halo(self) -> str:
        """Background colour used as a halo behind ring labels.

        A thick stroke in the background colour, drawn behind the glyphs,
        keeps the numbers readable where a data polygon sits underneath them.
        """
        theme = self.chart.theme
        return getattr(theme, "background_color", "#ffffff")

    def _render_grid(self, g: G, cx: float, cy: float) -> None:
        """Render concentric grid circles and numeric ring labels.

        Args:
            g: Parent G element
            cx: Center x coordinate
            cy: Center y coordinate
        """
        grid_color = self._ring_color()
        grid_width = getattr(self.chart.theme, "grid_width", None) or 1

        # Value at the outermost ring, used to label each ring level.
        max_value = max(max(abs(v) for v in s) for s in self.chart._series_data)
        if max_value == 0:
            max_value = 1

        for level in range(self.chart.grid_levels):
            radius = self._get_grid_radius(level)
            circle = Circle(
                cx=cx,
                cy=cy,
                r=radius,
                fill="none",
                stroke=grid_color,
                stroke_width=grid_width,
            )
            g.add_child(circle)

            if getattr(self.chart, "show_radial_labels", False):
                ring_value = max_value * (level + 1) / self.chart.grid_levels
                self._collect_ring_label(cx, cy, radius, ring_value)

    def _collect_ring_label(
        self,
        cx: float,
        cy: float,
        radius: float,
        value: float,
    ) -> None:
        """Record a numeric ring label for later (top-of-stack) rendering.

        The label sits just inside the ring along the vertical (12 o'clock)
        spoke so it reads upright. Collecting the specs here and drawing them
        after the data series keeps the numbers on top of the polygons.
        """
        from charted.utils.value_format import format_value

        text = format_value(value)
        label_x = cx + 3
        label_y = cy - radius + DEFAULT_FONT_SIZE * 0.5
        self._ring_label_specs.append((label_x, label_y, text))

    def _render_ring_labels(self, g: G) -> None:
        """Draw all collected ring labels on top of the data.

        Each number is drawn with a background-coloured halo (a thick stroke
        behind the glyphs via ``paint-order: stroke``) so it stays legible
        even where a data polygon covers the ring, and in a high-contrast
        label colour so it reads on dark themes.
        """
        if not self._ring_label_specs:
            return

        # Draw each number as a solid badge: a pill filled with the
        # high-contrast label colour (white on dark themes) carrying the text
        # in the background colour. Dark-on-light (or light-on-dark) badges
        # read unambiguously over both the dark canvas and the data polygons.
        pill_color = self._ring_label_color()
        text_color = self._ring_label_halo()
        font_size = DEFAULT_FONT_SIZE
        # Full-opacity subgroup: the parent group is drawn at 0.8 opacity,
        # which would otherwise dim the badges.
        label_group = G(opacity=1)
        for label_x, label_y, text in self._ring_label_specs:
            char_w = font_size * 0.62
            pad_x = 3
            pad_y = 2
            box_w = len(text) * char_w + pad_x * 2
            box_h = font_size + pad_y * 2
            label_group.add_child(
                Rect(
                    x=label_x - pad_x,
                    y=label_y - font_size + pad_y,
                    width=box_w,
                    height=box_h,
                    rx=2,
                    fill=pill_color,
                    fill_opacity=1,
                )
            )
            label_group.add_child(
                Text(
                    x=label_x,
                    y=label_y,
                    text=text,
                    fill=text_color,
                    font_size=font_size,
                    font_family=DEFAULT_FONT,
                    font_weight="bold",
                    text_anchor="start",
                )
            )
        g.add_child(label_group)

    def _render_axes(self, g: G, cx: float, cy: float) -> None:
        """Render axis spokes and labels.

        Args:
            g: Parent G element
            cx: Center x coordinate
            cy: Center y coordinate
        """
        grid_color = self._ring_color()
        grid_width = getattr(self.chart.theme, "grid_width", None) or 1

        for i, label in enumerate(self.chart._radar_labels):
            angle = self._get_angle(i)
            end_x, end_y = self._polar_to_cartesian(cx, cy, self._max_radius, angle)

            # Render axis spoke
            spoke = Path(
                d=f"M{cx} {cy} L{end_x} {end_y}",
                stroke=grid_color,
                stroke_width=grid_width,
            )
            g.add_child(spoke)

            # Render axis label
            if self.chart.show_axis_labels:
                self._render_axis_label(g, cx, cy, label, angle, end_x, end_y)

    def _render_axis_label(
        self,
        g: G,
        cx: float,
        cy: float,
        label: str,
        angle: float,
        end_x: float,
        end_y: float,
    ) -> None:
        """Render a single axis label, kept upright for legibility.

        Spoke labels are drawn horizontally (never rotated to the spoke
        angle). Rotating each label to its spoke direction made the top and
        bottom labels vertical, where they collided with the vertical ring
        badges and read as garbled, clipped text. Instead the label's
        horizontal anchor and vertical baseline are chosen from its position
        around the circle so the full string sits just outside the grid and
        reads left-to-right on every spoke.

        Args:
            g: Parent G element
            cx, cy: Chart center coordinates
            label: Label text
            angle: Angle in degrees
            end_x, end_y: End point of axis spoke
        """
        label_radius = self._max_radius + self.chart.label_offset
        label_x, label_y = self._polar_to_cartesian(cx, cy, label_radius, angle)

        # Normalize the spoke direction onto the unit circle to decide which
        # side of the point the text should sit on. cos drives the horizontal
        # anchor, sin drives the vertical baseline nudge.
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Horizontal anchoring: labels on the right read from the start, on
        # the left from the end, and labels near the vertical (top/bottom)
        # spokes are centered so they don't drift off the spoke.
        eps = 1e-3
        if cos_a > eps:
            text_anchor = "start"
            x_align = label_x + 5
        elif cos_a < -eps:
            text_anchor = "end"
            x_align = label_x - 5
        else:
            text_anchor = "middle"
            x_align = label_x

        # Vertical baseline: drop top labels above the grid, raise bottom
        # labels below it. sin > 0 is the top half in SVG (y grows downward,
        # but _polar_to_cartesian already negates y), so a positive sin means
        # the point is above center and the text should sit a touch higher.
        if sin_a > eps:
            y_align = label_y - 2
        elif sin_a < -eps:
            y_align = label_y + DEFAULT_FONT_SIZE
        else:
            y_align = label_y + 4

        label_text = Text(
            x=x_align,
            y=y_align,
            text=label,
            fill=getattr(self.chart.theme, "title_color", "#333"),
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
            text_anchor=text_anchor,
        )
        g.add_child(label_text)

    def _render_series(self, g: G, cx: float, cy: float) -> None:
        """Render all data series.

        Args:
            g: Parent G element
            cx: Center x coordinate
            cy: Center y coordinate
        """
        # Calculate max value for scaling
        max_value = max(max(abs(v) for v in s) for s in self.chart._series_data)
        if max_value == 0:
            max_value = 1

        for series_idx, (y_values, color) in enumerate(
            zip(self.chart._series_data, self.chart.colors)
        ):
            self._render_single_series(
                g, cx, cy, y_values, color, series_idx, max_value
            )

    def _render_single_series(
        self,
        g: G,
        cx: float,
        cy: float,
        y_values: list[float],
        color: str,
        series_idx: int,
        max_value: float,
    ) -> None:
        """Render a single data series.

        Args:
            g: Parent G element
            cx, cy: Chart center coordinates
            y_values: Data values for this series
            color: Series color
            series_idx: Index of this series
            max_value: Maximum value for scaling
        """
        # Get effective style for this series
        style = {}
        if self.chart.series_styles and series_idx < len(self.chart.series_styles):
            style = self.chart.series_styles[series_idx] or {}

        stroke = style.get("stroke") or color
        stroke_width = style.get("stroke_width", 2)
        fill = style.get("fill")
        fill_opacity = style.get("fill_opacity", 0.2)
        marker_shape = style.get("marker_shape", "circle")
        marker_size = style.get("marker_size", 4)

        # Build polygon path
        points = []
        for i, value in enumerate(y_values):
            x, y = self._get_data_point(cx, cy, i, value, max_value)
            points.append((x, y))

        # Create polygon
        if points:
            points_str = " ".join(f"{x},{y}" for x, y in points)
            polygon = Path(
                d=f"M{points_str} Z",
                fill=fill or stroke,
                fill_opacity=fill_opacity,
                stroke=stroke,
                stroke_width=stroke_width,
            )
            g.add_child(polygon)

            # Render markers
            self._render_markers(g, points, marker_shape, marker_size, stroke)

    def _render_markers(
        self,
        g: G,
        points: list[tuple[float, float]],
        marker_shape: str,
        marker_size: float,
        stroke: str,
    ) -> None:
        """Render markers for data points.

        Args:
            g: Parent G element
            points: List of (x, y) coordinates
            marker_shape: 'circle', 'square', or 'diamond'
            marker_size: Size of the marker
            stroke: Marker fill color
        """
        for x, y in points:
            if marker_shape == "circle":
                marker = Circle(
                    cx=x,
                    cy=y,
                    r=marker_size,
                    fill=stroke,
                    stroke="white",
                    stroke_width=1,
                )
            elif marker_shape == "square":
                half = marker_size
                marker = Rect(
                    x=x - half,
                    y=y - half,
                    width=marker_size * 2,
                    height=marker_size * 2,
                    fill=stroke,
                    stroke="white",
                    stroke_width=1,
                )
            else:  # diamond
                points_str = (
                    f"{x},{y - marker_size} "
                    f"{x + marker_size},{y} "
                    f"{x},{y + marker_size} "
                    f"{x - marker_size},{y}"
                )
                marker = Path(
                    d=f"M{points_str} Z",
                    fill=stroke,
                    stroke="white",
                    stroke_width=1,
                )
            g.add_child(marker)

    def _get_angle(self, index: int) -> float:
        """Get angle in degrees for axis index (0 = top, clockwise).

        Args:
            index: Axis index

        Returns:
            Angle in degrees
        """
        return (index * FULL_CIRCLE / len(self.chart._radar_labels)) - RIGHT_ANGLE

    def _polar_to_cartesian(
        self, cx: float, cy: float, radius: float, angle_deg: float
    ) -> tuple[float, float]:
        """Convert polar coordinates to Cartesian.

        Args:
            cx, cy: Center point
            radius: Distance from center
            angle_deg: Angle in degrees

        Returns:
            Tuple of (x, y) coordinates
        """
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy - radius * math.sin(angle_rad)  # negate y for SVG coordinate system
        return x, y

    def _get_grid_radius(self, level: int) -> float:
        """Get radius for grid level (0 = center, max = outer).

        Args:
            level: Grid level index

        Returns:
            Radius for this grid level
        """
        return (level + 1) * (self._max_radius / self.chart.grid_levels)

    def _get_data_point(
        self, cx: float, cy: float, axis_index: int, value: float, max_value: float
    ) -> tuple[float, float]:
        """Get cartesian coordinates for a data point.

        Args:
            cx, cy: Chart center
            axis_index: Which axis this point is on
            value: Data value
            max_value: Maximum value for scaling

        Returns:
            Tuple of (x, y) coordinates
        """
        if max_value == 0:
            radius = 0
        else:
            radius = (value / max_value) * self._max_radius
        angle = self._get_angle(axis_index)
        return self._polar_to_cartesian(cx, cy, radius, angle)
