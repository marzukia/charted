from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    QUADRANT_BOTTOM_MARGIN_FACTOR,
    QUADRANT_LABEL_LINE_GAP,
)
from charted.html.element import Circle, G, Path, Rect, Text
from charted.themes.core import Theme
from charted.utils.types import SeriesStyleConfig, Vector, Vector2D


class ScatterChart(Chart):
    """Scatter plot for displaying relationships between two variables.

    Plots individual data points at (x, y) coordinates to show
    correlations, clusters, or distributions. Supports multi-series
    data with custom marker shapes and sizes.

    Args:
        data: Single series (list of y-values with x=indices) or
              multi-series (list of lists) or list of (x, y) tuples
        x_data: Optional x-coordinates for each point
        labels: Optional series names
        width, height: Chart dimensions in pixels
        zero_index: Whether to include zero in both axes
        title: Optional chart title
        theme: Optional theme configuration
        series_names: Names for each series (shown in legend)
        series_styles: Per-series style overrides (marker_shape, marker_size)

    Example:
        >>> from charted import ScatterChart
        >>> # Basic scatter plot
        >>> chart = ScatterChart(data=[5, 8, 12, 15], x_data=[1, 2, 3, 4])
        >>> chart.save('correlation.svg')
        >>>
        >>> # Multi-series with custom markers
        >>> chart = ScatterChart(
        ...     data=[[5, 8, 12], [7, 10, 14]],
        ...     x_data=[1, 2, 3],
        ...     series_styles=[{'marker_shape': 'circle'}, {'marker_shape': 'square'}]
        ... )
    """

    def __init__(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        subtitle: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        quadrant_labels: list[str] | None = None,
        x_scale: object | None = None,
        y_scale: object | None = None,
        reference_lines: list[dict] | None = None,
        colors: list[str] | None = None,
    ):
        self._quadrant_labels = quadrant_labels
        super().__init__(
            y_data=y_data,
            x_data=x_data,
            width=width,
            height=height,
            title=title,
            subtitle=subtitle,
            theme=theme,
            series_names=series_names,
            chart_type="scatter",
            series_styles=series_styles,
            data_labels=data_labels,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            x_scale=x_scale,
            y_scale=y_scale,
            reference_lines=reference_lines,
            colors=colors,
        )

    @property
    def representation(self) -> G:
        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
            clip_path="url(#plot-clip)",
        )
        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(self.y_values, self.y_offsets, self.x_values, self.colors),
        ):
            # Apply style overrides from series_styles
            fill = color
            marker_size = 4  # default
            marker_shape = "circle"  # default
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = style["fill"]
                if style.get("marker_size"):
                    marker_size = style["marker_size"]
                if style.get("marker_shape"):
                    marker_shape = style["marker_shape"]

            series = G(fill=fill)
            x_offset = self.x_offset

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += x_offset
                y = self._apply_stacking(y, y_offset)
                # Render marker based on shape
                if marker_shape == "square":
                    half = marker_size / 2
                    series.add_child(
                        Rect(
                            x=x - half,
                            y=y - half,
                            width=marker_size,
                            height=marker_size,
                        )
                    )
                elif marker_shape == "diamond":
                    points_str = (
                        f"{x},{y - marker_size} "
                        f"{x + marker_size},{y} "
                        f"{x},{y + marker_size} "
                        f"{x - marker_size},{y}"
                    )
                    series.add_child(Path(d=f"M{points_str} Z", fill=fill))
                elif marker_shape != "none":  # circle
                    series.add_child(Circle(cx=x, cy=y, r=marker_size))
            g.add_children(series)

        # Data labels and quadrant labels rendered outside the clip group
        # so they don't get clipped at chart edges
        wrapper = G()
        wrapper.add_child(g)

        data_labels_g = self._render_data_labels()
        if data_labels_g:
            unclipped = G(
                transform=[*self.get_base_transform()],
            )
            unclipped.add_child(data_labels_g)
            wrapper.add_child(unclipped)

        quadrant_g = self._render_quadrant_labels()
        if quadrant_g:
            unclipped_q = G(
                transform=[*self.get_base_transform()],
            )
            unclipped_q.add_child(quadrant_g)
            wrapper.add_child(unclipped_q)

        return wrapper

    def _render_quadrant_labels(self) -> G | None:
        """Render text labels in each quadrant of the scatter plot.

        Expects a list of 4 strings: [top-left, top-right, bottom-left, bottom-right].
        Each string may contain newlines for multi-line labels.
        """
        if not self._quadrant_labels:
            return None

        labels = self._quadrant_labels
        if len(labels) < 4:
            labels = list(labels) + [""] * (4 - len(labels))

        g = G()
        font_size = max(8, self.theme.title_font_size - 4)
        font_family = self.theme.title_font_family
        font_color = self.theme.resolved_quadrant_label_color
        pw = self.plot_width
        ph = self.plot_height
        padding = 8

        # In the flipped coordinate system, high Y = top of chart
        # Corner-aligned: top labels hug top edge growing down,
        # bottom labels hug bottom edge growing up
        line_height = font_size + QUADRANT_LABEL_LINE_GAP
        top_margin = padding + font_size
        bottom_margin = padding * QUADRANT_BOTTOM_MARGIN_FACTOR

        for idx, label_text in enumerate(labels):
            if not label_text:
                continue
            lines = str(label_text).split("\n")
            is_left = idx % 2 == 0
            is_top = idx < 2
            anchor = "start" if is_left else "end"
            x = padding if is_left else pw - padding

            for line_idx, line in enumerate(lines):
                if is_top:
                    ty = ph - top_margin - line_idx * line_height
                else:
                    ty = (
                        bottom_margin
                        + font_size
                        + (len(lines) - 1 - line_idx) * line_height
                    )
                g.add_child(
                    Text(
                        text=line,
                        x=x,
                        y=ty,
                        fill=font_color,
                        font_size=font_size,
                        font_family=font_family,
                        text_anchor=anchor,
                        opacity=0.8,
                        transform=f"translate({x},{ty}) scale(1,-1) translate({-x},{-ty})",
                    )
                )

        return g
