"""Line chart rendering utilities.

Extracts rendering logic from LineChart to reduce code complexity
and address long function issues (Issue #70).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from charted.html.element import Circle, G, Path, Rect
from charted.utils.color_manager import ColorManager
from charted.utils.curves import curve_path

if TYPE_CHECKING:
    from charted.themes.core import Theme
    from charted.utils.series_style import SeriesStyleConfig
    from charted.utils.types import Vector2D


class _LineHost(Protocol):
    """Structural type for the line chart consumed by :class:`LineRenderer`.

    Declared for the type checker only so the renderer can reference the chart's
    attributes without importing the concrete (and, during this typing pass,
    not-yet-typed) ``LineChart`` class.
    """

    theme: Theme
    series_styles: list[SeriesStyleConfig] | None

    @property
    def plot_width(self) -> float: ...

    @property
    def x_offset(self) -> float: ...

    @property
    def x_count(self) -> int: ...

    @property
    def y_offsets(self) -> Vector2D: ...

    @property
    def y_values(self) -> Vector2D: ...

    def get_base_transform(self) -> list[str]: ...

    def _apply_stacking(self, y: float, y_offset: float) -> float: ...


def round_coordinate(value: float, decimals: int = 1) -> float:
    """Round a coordinate value to specified decimal places.

    Args:
        value: The coordinate value to round.
        decimals: Number of decimal places (default: 1).

    Returns:
        Rounded coordinate value.
    """
    return round(value, decimals)


def format_svg_value(value: float) -> str:
    """Format a numeric value for SVG attributes.

    Converts floats to integers when the value is a whole number
    (e.g., 3.0 -> "3") to match expected SVG output.

    Args:
        value: The numeric value to format.

    Returns:
        String representation of the value as int if whole, else float.
    """
    rounded = round(value, 1)
    if rounded == int(rounded):
        return str(int(rounded))
    return str(rounded)


class LineRenderer:
    """Renderer for line chart visualization.

    Handles all SVG element generation for line charts including:
    - Line paths connecting data points
    - Area fills under lines
    - Markers at data points (circle, square, diamond)
    - Series styling (stroke, width, opacity, dash patterns)
    """

    def __init__(self, chart: _LineHost):
        """Initialize line renderer.

        Args:
            chart: LineChart instance to render
        """
        self.chart = chart

        # Initialize ColorManager for automatic color cycling. Use the theme's
        # contrast-floor-adjusted palette (identical to colors unless a floor
        # is set, e.g. the high-contrast theme).
        self._color_manager = ColorManager(colors=self.chart.theme.resolved_colors)

    def render(self) -> G:
        """Generate complete line chart SVG elements.

        Returns:
            G element containing all chart components
        """
        g = G(
            opacity=0.8,
            transform=[*self.chart.get_base_transform()],
        )

        num_series = len(self.chart.y_values or [])

        # X positions: use the chart's reprojected band centers so the line
        # vertices land on the same category positions as columns/x-ticks.
        # For an ordinal LineChart (pad_x_labels=False, x_offset=0) these are
        # identical to the previous i/(n-1)*plot_w spacing; for ComboChart they
        # honour the column-band label padding so bars and the line coincide.
        chart_x_values = getattr(self.chart, "x_values", None)
        if chart_x_values:
            x_positions_by_series = [list(row) for row in chart_x_values]
            # Match against y_values length in case the proxy exposes fewer rows.
            while len(x_positions_by_series) < num_series:
                x_positions_by_series.append(list(x_positions_by_series[0]))
        else:
            n = self.chart.x_count
            plot_w = self.chart.plot_width
            if n > 1:
                x_positions = [i / (n - 1) * plot_w for i in range(n)]
            else:
                x_positions = [plot_w / 2]
            x_positions_by_series = [x_positions] * num_series

        # Honour the chart's resolved per-series colors (so the rendered line
        # matches its legend swatch) rather than re-deriving by line position.
        colors = getattr(self.chart, "colors", None)
        if not colors:
            colors = self._color_manager.ensure_palette_size(num_series)

        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(
                self.chart.y_values,
                self.chart.y_offsets,
                x_positions_by_series,
                colors,
            )
        ):
            self._render_series(g, y_values, y_offsets, x_values, color, series_idx)

        return g

    def _render_series(
        self,
        g: G,
        y_values: list[float],
        y_offsets: list[float],
        x_values: list[float],
        color: str,
        series_idx: int,
    ) -> None:
        """Render a single data series.

        Args:
            g: Parent G element
            y_values: Y-axis data values
            y_offsets: Stacking offsets for y-values
            x_values: X-axis data values
            color: Series color
            series_idx: Index of this series
        """
        # Get effective style for this series
        style = self._get_series_style(series_idx)

        # Extract style properties
        stroke = style.get("stroke") or color
        stroke_width = (
            style.get("stroke_width") or self.chart.theme.resolved_series_stroke_width
        )
        stroke_dasharray = style.get("stroke_dasharray")
        # Fall back to the chart's redundant dash cycle when this series has no
        # explicit dash of its own. No-op unless dash_cycle was enabled.
        if not stroke_dasharray:
            dash_fn = getattr(self.chart, "_series_dasharray", None)
            if dash_fn is not None:
                stroke_dasharray = dash_fn(series_idx)
        stroke_opacity = style.get("stroke_opacity")
        area_fill = style.get("area_fill", False)
        area_fill_opacity = style.get("area_fill_opacity", 0.3)
        marker_shape = style.get("marker_shape", "circle")
        marker_size = style.get("marker_size") or self.chart.theme.marker_size

        # Create series group with common styles. Dash/opacity are passed as
        # constructor kwargs so they actually emit (the Element ``attributes``
        # property is read-only, so post-hoc item assignment was a silent
        # no-op). Omitting them when unset keeps solid lines byte-for-byte.
        group_attrs = {"fill": "white", "stroke": stroke, "stroke_width": stroke_width}
        if stroke_dasharray:
            group_attrs["stroke_dasharray"] = stroke_dasharray
        if stroke_opacity:
            group_attrs["stroke_opacity"] = stroke_opacity
        series = G(**group_attrs)

        # Build markers (always on the ORIGINAL data points) and collect
        # the boundary coordinates that the line path will be drawn through.
        points = []
        markers = []

        for x, y, y_offset in zip(x_values, y_values, y_offsets):
            x += self.chart.x_offset
            y = self._apply_stacking(y, y_offset)
            points.append((x, y))

            # Render marker if enabled (sits on the data point, not the curve)
            marker = self._get_marker(
                x,
                y,
                style,
                cast("str", stroke),
                cast("str", marker_shape),
                cast("float", marker_size),
            )
            if marker:
                markers.append(marker)

        # Build the line path according to the chart's curve setting.
        # "linear" reuses the exact M/L string the chart has always emitted.
        # Charts that borrow the renderer without a curve setting (e.g. the
        # combo chart's line proxy) default to linear.
        line_d = curve_path(getattr(self.chart, "curve", "linear"), points)

        # Add line to series
        line = Path(d=line_d, fill="none")
        series.add_children(line, *markers)

        # Add area fill if enabled, closing off the same curved boundary.
        if area_fill and points:
            area_d = self._create_area_path(line_d, x_values, y_values)
            area = Path(
                d=area_d,
                fill=stroke,
                fill_opacity=area_fill_opacity,
            )
            g.add_child(area)

        g.add_children(series)

    def _get_series_style(self, index: int) -> dict[str, object]:
        """Get effective style for a series, merging theme defaults with overrides.

        Args:
            index: Series index

        Returns:
            Dictionary of style properties
        """
        # Start with theme series_style as base
        base_style = getattr(self.chart.theme, "series_style", {}) or {}

        # Apply per-series override if available
        if self.chart.series_styles and index < len(self.chart.series_styles):
            override = self.chart.series_styles[index] or {}
            style = {**base_style, **cast("dict[str, object]", override)}
        else:
            style = dict(base_style)

        # Disable markers by default unless chart-level markers=True or per-series overrides it
        chart_markers = getattr(self.chart, "markers", False)
        if not chart_markers and "show_markers" not in style:
            style["show_markers"] = False

        return style

    def _get_marker(
        self,
        x: float,
        y: float,
        style: dict[str, object],
        stroke: str,
        marker_shape: str,
        marker_size: float,
    ) -> Path | Rect | Circle | None:
        """Create a marker element for a data point.

        Args:
            x, y: Point coordinates
            style: Series style configuration
            stroke: Stroke color
            marker_shape: Shape type ('circle', 'square', 'diamond')
            marker_size: Marker size

        Returns:
            Marker element or None if markers are disabled
        """
        show_markers = style.get("show_markers")

        # Check if markers should be shown
        if show_markers is False:
            return None
        if show_markers is not True and not (marker_shape != "none" and marker_size):
            return None

        # Create marker based on shape with rounded coordinates
        if marker_shape == "square":
            half = marker_size / 2
            return Rect(
                x=round_coordinate(x - half),
                y=round_coordinate(y - half),
                width=round_coordinate(marker_size),
                height=round_coordinate(marker_size),
            )
        elif marker_shape == "diamond":
            points_str = (
                f"{round_coordinate(x)},{round_coordinate(y - marker_size)} "
                f"{round_coordinate(x + marker_size)},{round_coordinate(y)} "
                f"{round_coordinate(x)},{round_coordinate(y + marker_size)} "
                f"{round_coordinate(x - marker_size)},{round_coordinate(y)}"
            )
            return Path(d=f"M{points_str} Z", fill=stroke)
        else:  # circle
            return Circle(
                cx=round_coordinate(x),
                cy=round_coordinate(y),
                r=format_svg_value(marker_size),
            )

    def _create_area_path(
        self,
        line_d: str,
        x_values: list[float],
        y_values: list[float],
    ) -> str:
        """Close a line path into a filled area.

        Takes the already-built line path (linear or curved) and appends
        the segments that drop down to the baseline and close the shape, so
        the fill follows the exact same top boundary as the line.

        Args:
            line_d: The line's SVG path ``d`` string.
            x_values: X-axis values.
            y_values: Y-axis values.

        Returns:
            The closed area-fill ``d`` string.
        """
        last_y = round_coordinate(y_values[-1] if y_values else 0)
        first_x = round_coordinate(x_values[0] + self.chart.x_offset)

        # The line path already ends at the last curve point, so close the
        # area straight from there across to the first x at the baseline.
        return " ".join([line_d, f"L{first_x} {last_y}", "Z"])

    def _apply_stacking(self, y: float, y_offset: float) -> float:
        """Apply stacking offset to a y-value.

        Args:
            y: Original y-value
            y_offset: Stacking offset

        Returns:
            Stacked y-value
        """
        return self.chart._apply_stacking(y, y_offset)
