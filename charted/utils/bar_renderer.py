"""Bar chart rendering utilities.

Extracts rendering logic from BarChart to reduce code complexity
and address long function issues (Issue #70).
"""

from __future__ import annotations

from charted.html.element import G, Path


class BarRenderer:
    """Renderer for horizontal bar chart visualization.

    Handles all SVG element generation for bar charts including:
    - Horizontal bars (single and multi-series)
    - Stacked and side-by-side layouts
    - Border rendering
    """

    def __init__(self, chart):
        """Initialize bar renderer.

        Args:
            chart: BarChart instance to render
        """
        self.chart = chart

    def render(self) -> G:
        """Generate complete bar chart SVG elements.

        Returns:
            G element containing all chart components
        """
        slot_height = self.chart.y_height
        gap = slot_height * self.chart.bar_gap
        start_y = gap

        num_series = len(self.chart.x_values) if self.chart.x_values else 1
        series_thickness = (
            slot_height / num_series
            if (num_series > 0 and not self.chart.x_stacked)
            else slot_height
        )

        # Mirror of ColumnChart's dy: for stacked charts with negative values,
        # shift the drawing group right so negative-magnitude bars (which draw
        # leftward from x_offset) land at the correct zero-relative position.
        # Non-stacked uses absolute zero_x from the reprojection and doesn't
        # need this compensation.
        dx = 0
        if self.chart.x_stacked and self.chart.x_axis.axis_dimension.min_value < 0:
            dx = self.chart.x_axis.reproject(
                abs(self.chart.x_axis.axis_dimension.min_value)
            )

        bars_g = G(
            opacity="0.8",
            transform=f"translate({self.chart.left_padding + dx}, {self.chart.top_padding})",
        )

        if self.chart.x_stacked:
            self._render_stacked(bars_g, series_thickness)
        else:
            self._render_side_by_side(bars_g, start_y, series_thickness)

        # Plot borders — all four sides.
        self._render_borders(bars_g)

        result = G()
        result.add_children(bars_g)
        return result

    def _render_stacked(self, bars_g: G, series_thickness: float) -> None:
        """Render stacked horizontal bars.

        Args:
            bars_g: Parent G element for bars
            series_thickness: Height of each bar slot
        """
        start_y = self.chart.y_height  # slot_height, same as start_y in render()

        # Iterate series, accumulate offsets along the value axis (x here).
        # x_offsets is pre-computed and already reprojected by Chart.x_offsets setter.
        for series_idx, (x_values_series, x_offsets_series, color) in enumerate(
            zip(self.chart.x_values, self.chart.x_offsets, self.chart.colors)
        ):
            # Apply fill override from series_styles
            fill = self._get_effective_fill(series_idx, color)

            paths = []
            for bar_idx, (x, x_offset_val) in enumerate(
                zip(x_values_series, x_offsets_series)
            ):
                slot_y = start_y + bar_idx * (
                    series_thickness + series_thickness * self.chart.bar_gap
                )
                # x_offset_val is the reprojected cumulative start position
                # and x is the reprojected signed value. Use the leftmost
                # point and positive width regardless of sign so that a
                # positive value stacked on top of a negative cumulative
                # offset (or vice versa) renders correctly.
                left_x = min(x_offset_val, x_offset_val + x)
                width = abs(x)
                paths.append(Path.get_path(left_x, slot_y, width, series_thickness))
            bars_g.add_child(Path(d=paths, fill=fill))

    def _render_side_by_side(
        self, bars_g: G, start_y: float, series_thickness: float
    ) -> None:
        """Render side-by-side horizontal bars.

        Args:
            bars_g: Parent G element for bars
            start_y: Starting y position for first bar
            series_thickness: Height of each series within a slot
        """
        zero_x = self.chart.x_axis.zero

        for series_idx, (x_values_series, color) in enumerate(
            zip(self.chart.x_values, self.chart.colors)
        ):
            # Apply fill override from series_styles
            fill = self._get_effective_fill(series_idx, color)

            paths = []
            for bar_idx, x in enumerate(x_values_series):
                slot_y = start_y + bar_idx * (
                    series_thickness + series_thickness * self.chart.bar_gap
                )
                bar_y = slot_y + series_idx * series_thickness
                if x >= zero_x:
                    paths.append(
                        Path.get_path(zero_x, bar_y, x - zero_x, series_thickness)
                    )
                else:
                    paths.append(Path.get_path(x, bar_y, zero_x - x, series_thickness))
            bars_g.add_child(Path(d=paths, fill=fill))

    def _render_borders(self, bars_g: G) -> None:
        """Render plot border lines.

        Args:
            bars_g: Parent G element to add borders to
        """
        grid_color = "#CCCCCC"
        if isinstance(self.chart.theme, dict):
            grid_color = self.chart.theme.get("h_grid", {}).get("stroke", "#CCCCCC")

        border_transform = (
            f"translate({self.chart.left_padding}, {self.chart.top_padding})"
        )
        borders = [
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 {self.chart.plot_height} h{self.chart.plot_width}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 h{self.chart.plot_width}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 v{self.chart.plot_height}"],
                transform=border_transform,
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M{self.chart.plot_width} 0 v{self.chart.plot_height}"],
                transform=border_transform,
            ),
        ]
        bars_g.add_children(*borders)

    def _get_effective_fill(self, series_idx: int, default_color: str) -> str:
        """Get effective fill color for a series.

        Args:
            series_idx: Index of the series
            default_color: Default color from chart.colors

        Returns:
            Effective fill color (may be overridden by series_styles)
        """
        fill = default_color
        if self.chart.series_styles and series_idx < len(self.chart.series_styles):
            style = self.chart.series_styles[series_idx] or {}
            if style.get("fill"):
                fill = style["fill"]
        return fill
