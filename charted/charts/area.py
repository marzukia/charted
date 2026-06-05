"""Area chart: line chart with filled area underneath.

Shows one or more series as filled regions under the line.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path
from charted.themes.core import Theme
from charted.utils.curves import VALID_CURVES, curve_path
from charted.utils.types import (
    Labels,
    ReferenceLineDict,
    SeriesStyleConfig,
    Vector,
    Vector2D,
)

if TYPE_CHECKING:
    from charted.charts.chart import _Annotation


def _fmt(value: float) -> str:
    """Format a coordinate the way curve_path does (trailing .0 preserved)."""
    return f"{value:g}" if value != int(value) else f"{int(value)}"


def _clamp_path_y(path: str, lo: float, hi: float) -> str:
    """Clamp every y coordinate of an absolute SVG path string to ``[lo, hi]``.

    Handles the M/L/C/H/V commands emitted by ``curve_path``. The x values and
    command structure are left untouched. When no y exceeds the bounds the
    output is identical to the input, so in-bounds curves stay byte-for-byte
    unchanged. Returns the original string verbatim if nothing was clamped.
    """

    def clamp(y: float) -> float:
        return max(lo, min(hi, y))

    out: list[str] = []
    changed = False
    # Split into (command, args) groups; curve_path only emits M/L/C/H/V.
    for cmd, args in re.findall(r"([MLCHV])([^MLCHVZ]*)", path):
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", args)
        vals = [float(n) for n in nums]
        if cmd in ("M", "L"):
            # x y pairs
            new_vals = []
            for k in range(0, len(vals), 2):
                cy = clamp(vals[k + 1])
                changed = changed or cy != vals[k + 1]
                new_vals.extend([vals[k], cy])
            out.append(cmd + " ".join(_match_token(nums, idx, v) for idx, v in enumerate(new_vals)))
        elif cmd == "C":
            # x1 y1 x2 y2 x y (every odd index is a y)
            new_vals = []
            for idx, v in enumerate(vals):
                if idx % 2 == 1:
                    cy = clamp(v)
                    changed = changed or cy != v
                    new_vals.append(cy)
                else:
                    new_vals.append(v)
            out.append(cmd + " ".join(_match_token(nums, idx, v) for idx, v in enumerate(new_vals)))
        elif cmd == "V":
            new_vals = []
            for idx, v in enumerate(vals):
                cy = clamp(v)
                changed = changed or cy != v
                new_vals.append(cy)
            out.append(cmd + " ".join(_match_token(nums, idx, v) for idx, v in enumerate(new_vals)))
        else:  # H: x only, no y
            out.append(cmd + args.strip())
    if not changed:
        return path
    return " ".join(s for s in out)


def _match_token(originals: list[str], idx: int, value: float) -> str:
    """Render ``value`` reusing the original token text when it is unchanged.

    Keeps untouched coordinates byte-identical to ``curve_path``'s output and
    only reformats the ones the clamp actually moved.
    """
    if idx < len(originals) and float(originals[idx]) == value:
        return originals[idx]
    return _fmt(value)


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
        annotations: Optional list of annotation objects (LineAnnotation,
            BoxAnnotation, LabelAnnotation) drawn in the plot area.

    Example:
        >>> chart = AreaChart(
        ...     data=[[10, 20, 30], [15, 25, 35]],
        ...     labels=['A', 'B', 'C'],
        ... )
    """

    fill_opacity: float = 0.3
    pad_x_labels: bool = False
    curve: str = "linear"
    y_stacked: bool = True

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
        subtitle_leading: float = 8.0,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        curve: str = "linear",
        stacked: bool = True,
        x_scale: object | None = None,
        y_scale: object | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        annotations: list[_Annotation] | None = None,
        reference_lines: list[ReferenceLineDict] | None = None,
        colors: list[str] | None = None,
        domain_padding: float | None = None,
    ):
        if curve not in VALID_CURVES:
            raise ValueError(
                f"Unknown curve {curve!r}. Valid options: {', '.join(VALID_CURVES)}"
            )
        self.fill_opacity = fill_opacity
        self.curve = curve
        # Set before super().__init__ so the base Chart anchors the y-domain to
        # the stacked totals. Stacked is the sensible default for multi-series
        # area; pass stacked=False for overlapping translucent areas.
        self.y_stacked = stacked
        super().__init__(
            y_data=data,
            x_data=x_data,
            x_labels=labels,
            width=width,
            height=height,
            title=title,
            subtitle=subtitle,
            subtitle_leading=subtitle_leading,
            theme=theme,
            series_names=series_names,
            series_styles=series_styles,
            chart_type="area",
            x_scale=x_scale,
            y_scale=y_scale,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            annotations=annotations,
            reference_lines=reference_lines,
            colors=colors,
            domain_padding=domain_padding,
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

        # The filled polygon must stay within the plot box: clamp every vertex
        # to [plot_top, plot_bottom] so a value sitting at (or interpolating
        # toward) the axis minimum can't bleed below the floor into the x-label
        # row, nor exceed the top edge. The clamp is a no-op for points already
        # inside the plot, so normal charts render byte-for-byte identically.
        plot_top = pad_y
        plot_bottom = pad_y + plot_h
        for i, (y_vals, y_offs) in enumerate(zip(self.y_values, self.y_offsets)):
            color = self.colors[i]
            points = []
            for j in range(len(y_vals)):
                x = pad_x + x_positions[j]
                y = y_vals[j] + y_offs[j] if self.y_stacked else y_vals[j]
                py = pad_y + plot_h - y
                py = max(plot_top, min(plot_bottom, py))
                points.append((x, py))

            if not points:
                continue

            if self.curve == "linear":
                # Preserve the exact historical linear path output. Vertices are
                # already clamped above, so the linear boundary cannot bleed.
                top = [f"M{points[0][0]} {points[0][1]}"]
                for px, py in points[1:]:
                    top.append(f"L{px} {py}")
                top_d = " ".join(top)
            else:
                # Smooth/step the top boundary through the (clamped) points.
                # Smooth curves derive cubic control points from the vertices and
                # can still overshoot past the plot edge between them, so clamp
                # the y of every coordinate in the generated path. This stays a
                # no-op (byte-identical) when nothing overshoots.
                top_d = _clamp_path_y(curve_path(self.curve, points), plot_top, plot_bottom)

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
