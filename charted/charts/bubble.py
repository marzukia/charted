from __future__ import annotations

from charted.charts.scatter import ScatterChart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import Circle, G
from charted.themes.core import Theme
from charted.utils.types import SeriesStyleConfig, Vector, Vector2D

DEFAULT_BUBBLE_MIN_RADIUS = 4.0
DEFAULT_BUBBLE_MAX_RADIUS = 24.0


class BubbleChart(ScatterChart):
    """Bubble chart: a scatter plot where marker radius encodes a third value.

    Each point is drawn as a circle at its (x, y) position, exactly like a
    scatter plot, but the circle radius is scaled from a third data
    dimension (``sizes``) into a configurable ``[min_radius, max_radius]``
    range.

    Sizes map linearly to the circle *radius*, not its area. Because a
    circle's area grows with the square of its radius, large values look
    more than proportionally bigger than their value warrants. This is
    intentional; if you want perceived size to track value, pre-transform
    your data with ``sqrt`` before passing it as ``sizes``.

    For multi-series charts, ``sizes`` applies per point index across every
    series (``sizes[i]`` sets the radius of point ``i`` in all series), and
    its length is validated against the point count of the first series.

    Args:
        x_data: X-coordinates for each point.
        y_data: Y-coordinates for each point.
        sizes: Third dimension; one non-negative value per point. Mapped
            linearly onto ``[min_radius, max_radius]`` (radius, not area).
        min_radius: Smallest rendered marker radius in pixels.
        max_radius: Largest rendered marker radius in pixels.
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        series_names: Names for each series (shown in legend).

    Example:
        >>> from charted import BubbleChart
        >>> chart = BubbleChart(
        ...     x_data=[1, 2, 3],
        ...     y_data=[10, 20, 15],
        ...     sizes=[5, 30, 12],
        ... )
        >>> chart.save('bubble.svg')
    """

    def __init__(
        self,
        x_data: Vector | Vector2D,
        y_data: Vector | Vector2D,
        sizes: Vector,
        min_radius: float = DEFAULT_BUBBLE_MIN_RADIUS,
        max_radius: float = DEFAULT_BUBBLE_MAX_RADIUS,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        data_labels: list[str] | list[list[str]] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        quadrant_labels: list[str] | None = None,
        value_labels: bool | str | dict | None = None,
        legend: str = "none",
        domain_padding: float | None = None,
    ):
        if sizes is None:
            raise ValueError("sizes is required for a bubble chart")
        if any(s < 0 for s in sizes):
            raise ValueError("sizes cannot be negative")
        if min_radius < 0 or max_radius < 0:
            raise ValueError("min_radius and max_radius cannot be negative")
        if max_radius < min_radius:
            raise ValueError("max_radius must be >= min_radius")

        # sizes applies per point index across every series, so validate it
        # against every series length, not just the first.
        is_multi_series = bool(y_data) and isinstance(y_data[0], list)
        if is_multi_series:
            series_lengths = [len(series) for series in y_data]
        else:
            series_lengths = [len(y_data)]
        for series_idx, point_count in enumerate(series_lengths):
            if len(sizes) != point_count:
                raise ValueError(
                    f"sizes length ({len(sizes)}) must match number of points "
                    f"in series {series_idx} ({point_count}); sizes apply per "
                    f"point index across all series"
                )

        self.sizes = list(sizes)
        self.min_radius = min_radius
        self.max_radius = max_radius

        super().__init__(
            x_data=x_data,
            y_data=y_data,
            width=width,
            height=height,
            title=title,
            theme=theme,
            series_names=series_names,
            series_styles=series_styles,
            data_labels=data_labels,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            quadrant_labels=quadrant_labels,
            value_labels=value_labels,
            legend=legend,
            domain_padding=domain_padding,
        )

    def _scaled_radii(self) -> list[float]:
        """Map each size onto the [min_radius, max_radius] range."""
        if not self.sizes:
            return []
        lo = min(self.sizes)
        hi = max(self.sizes)
        if hi == lo:
            # All equal: use the midpoint of the radius range.
            mid = (self.min_radius + self.max_radius) / 2
            return [mid for _ in self.sizes]
        span = self.max_radius - self.min_radius
        return [self.min_radius + (s - lo) / (hi - lo) * span for s in self.sizes]

    @property
    def representation(self) -> G:
        radii = self._scaled_radii()

        g = G(
            opacity=0.8,
            transform=[*self.get_base_transform()],
            clip_path="url(#plot-clip)",
        )
        for series_idx, (y_values, y_offsets, x_values, color) in enumerate(
            zip(self.y_values, self.y_offsets, self.x_values, self.colors),
        ):
            fill = color
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = style["fill"]

            series = G(fill=fill)
            x_offset = self.x_offset

            for i, (x, y, y_offset) in enumerate(zip(x_values, y_values, y_offsets)):
                x += x_offset
                y = self._apply_stacking(y, y_offset)
                r = radii[i] if i < len(radii) else self.min_radius
                series.add_child(Circle(cx=x, cy=y, r=r))
            g.add_children(series)

        wrapper = G()
        wrapper.add_child(g)

        data_labels_g = self._render_data_labels()
        if data_labels_g:
            unclipped = G(transform=[*self.get_base_transform()])
            unclipped.add_child(data_labels_g)
            wrapper.add_child(unclipped)

        quadrant_g = self._render_quadrant_labels()
        if quadrant_g:
            unclipped_q = G(transform=[*self.get_base_transform()])
            unclipped_q.add_child(quadrant_g)
            wrapper.add_child(unclipped_q)

        return wrapper

    def to_config(self) -> dict:
        cfg = super().to_config()
        cfg["sizes"] = list(self.sizes)
        cfg["min_radius"] = self.min_radius
        cfg["max_radius"] = self.max_radius
        return cfg
