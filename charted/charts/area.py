"""Area chart — line chart with filled area underneath.

Shows one or more series as filled regions under the line.
"""

from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path
from charted.themes.core import Theme
from charted.utils.curves import VALID_CURVES, curve_path
from charted.utils.series_style import SeriesStyleConfig
from charted.utils.types import Labels, Vector, Vector2D


class AreaChart(Chart):
    """Area chart showing filled regions under lines.

    Args:
        data: Single series (list of values) or multi-series (list of lists).
        x_data: Optional x-axis values.
        labels: Optional x-axis labels.
        width, height: Chart dimensions in pixels.
        fill_opacity: Opacity of the area fill (default 0.3).
        title: Optional chart title.
        theme: Optional theme configuration.
        series_names: Names for each series (shown in legend).
        series_styles: Per-series style overrides.

    Example:
        >>> chart = AreaChart(
        ...     data=[[10, 20, 30], [15, 25, 35]],
        ...     labels=['A', 'B', 'C'],
        ... )
    """

    fill_opacity: float = 0.3
    pad_x_labels: bool = False
    curve: str = "linear"

    def __init__(
        self,
        data: Vector | Vector2D,
        x_data: Vector | Vector2D | None = None,
        labels: Labels | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        fill_opacity: float = 0.3,
        title: str | None = None,
        subtitle: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        curve: str = "linear",
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        reference_lines: list[dict] | None = None,
        colors: list[str] | None = None,
    ):
        if curve not in VALID_CURVES:
            raise ValueError(
                f"Unknown curve {curve!r}. Valid options: {', '.join(VALID_CURVES)}"
            )
        self.fill_opacity = fill_opacity
        self.curve = curve
        super().__init__(
            y_data=data,
            x_data=x_data,
            x_labels=labels,
            width=width,
            height=height,
            title=title,
            subtitle=subtitle,
            theme=theme,
            series_names=series_names,
            series_styles=series_styles,
            chart_type="area",
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            reference_lines=reference_lines,
            colors=colors,
        )

    @property
    def x_offset(self) -> float:
        """Area charts use direct x positions, no label-padding offset."""
        return 0.0

    @property
    def representation(self) -> G:
        """Render area chart series as filled paths."""
        g = G()
        plot_h = self.plot_height
        plot_w = self.plot_width
        n = self.x_count
        pad_y = self.top_padding
        pad_x = self.left_padding

        # Compute x positions spanning the full plot area
        # Labels sit at i/(n-1) * plot_w, from 0 to plot_w
        if n > 1:
            x_positions = [i / (n - 1) * plot_w for i in range(n)]
        else:
            x_positions = [plot_w / 2]

        for i, (y_vals, y_offs) in enumerate(zip(self.y_values, self.y_offsets)):
            color = self.colors[i]
            points = []
            for j in range(len(y_vals)):
                x = pad_x + x_positions[j]
                y = y_vals[j] + y_offs[j] if self.y_stacked else y_vals[j]
                points.append((x, pad_y + plot_h - y))

            if not points:
                continue

            if self.curve == "linear":
                # Preserve the exact historical linear path output.
                top = [f"M{points[0][0]} {points[0][1]}"]
                for px, py in points[1:]:
                    top.append(f"L{px} {py}")
                top_d = " ".join(top)
            else:
                # Smooth/step the top boundary through the same points.
                top_d = curve_path(self.curve, points)

            baseline = pad_y + plot_h
            d = " ".join(
                [
                    top_d,
                    f"L{points[-1][0]} {baseline}",
                    f"L{points[0][0]} {baseline}z",
                ]
            )

            g.add_child(
                Path(
                    d=d,
                    fill=color,
                    fill_opacity=self.fill_opacity,
                    stroke=color,
                    stroke_width=1.5,
                )
            )

        return g
