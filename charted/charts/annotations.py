"""Annotation primitives for charts.

Annotations are positioned in *data* coordinates and reprojected through the
chart axes at render time. They draw inside the plot-area group, sharing the
same coordinate frame as legacy reference lines (h_lines / v_lines).

Three primitives are provided:

- ``LineAnnotation`` draws a straight segment between two data points.
- ``BoxAnnotation`` shades a rectangular value range.
- ``LabelAnnotation`` places text at a data point.

Example:
    >>> from charted import ScatterChart
    >>> from charted.charts.annotations import LineAnnotation, BoxAnnotation
    >>> chart = ScatterChart(
    ...     x_data=[0, 5, 10],
    ...     y_data=[0, 50, 100],
    ...     annotations=[
    ...         LineAnnotation((0, 0), (10, 100)),
    ...         BoxAnnotation((2, 8), (20, 80)),
    ...     ],
    ... )
"""

from __future__ import annotations

import dataclasses

from charted.constants import (
    REFERENCE_LINE_WIDTH,
)
from charted.html.element import Element, Path, Rect, Text


def _project(chart, x: float, y: float) -> tuple[float, float]:
    """Reproject a data point into plot-area-local pixel coordinates.

    The y-axis is flipped (high values at the top), matching the convention
    used by ``Chart._render_reference_lines``.
    """
    px = chart.x_axis.reproject(x)
    py = chart.plot_height - chart.y_axis.reproject(y)
    return px, py


@dataclasses.dataclass
class LineAnnotation:
    """A straight line segment between two data points.

    Args:
        start: (x, y) start point in data coordinates.
        end: (x, y) end point in data coordinates.
        color: Stroke color. Defaults to the theme reference-line color.
        width: Stroke width in pixels.
        dashed: If True, draw a dashed line (the legacy reference-line style).
    """

    start: tuple[float, float]
    end: tuple[float, float]
    color: str | None = None
    width: float = REFERENCE_LINE_WIDTH
    dashed: bool = False
    # Internal: when set, emit a full-span axis-aligned reference line whose
    # markup is byte-for-byte identical to the legacy h_lines / v_lines path.
    _ref_line: str | None = None
    _ref_value: float | None = None

    @classmethod
    def _h_line(cls, value: float) -> "LineAnnotation":
        """Legacy horizontal reference line spanning the full plot width."""
        return cls((0, value), (0, value), dashed=True, _ref_line="h", _ref_value=value)

    @classmethod
    def _v_line(cls, value: float) -> "LineAnnotation":
        """Legacy vertical reference line spanning the full plot height."""
        return cls((value, 0), (value, 0), dashed=True, _ref_line="v", _ref_value=value)

    def render(self, chart) -> Element:
        color = self.color or chart.theme.resolved_reference_line_color
        if self._ref_line == "h":
            y = chart.plot_height - chart.y_axis.reproject(self._ref_value)
            return self._dashed_path(f"M0 {y} h{chart.plot_width}", color)
        if self._ref_line == "v":
            x = chart.x_axis.reproject(self._ref_value)
            return self._dashed_path(f"M{x} 0 v{chart.plot_height}", color)

        x0, y0 = _project(chart, *self.start)
        x1, y1 = _project(chart, *self.end)
        kwargs = dict(
            d=[f"M{x0} {y0} L{x1} {y1}"],
            stroke=color,
            stroke_width=self.width,
            fill="none",
        )
        if self.dashed:
            from charted.constants import REFERENCE_LINE_DASH

            kwargs["stroke_dasharray"] = REFERENCE_LINE_DASH
        return Path(**kwargs)

    @staticmethod
    def _dashed_path(d: str, color: str) -> Path:
        from charted.constants import REFERENCE_LINE_DASH

        return Path(
            d=[d],
            stroke=color,
            stroke_width=REFERENCE_LINE_WIDTH,
            stroke_dasharray=REFERENCE_LINE_DASH,
            fill="none",
        )


@dataclasses.dataclass
class BoxAnnotation:
    """A shaded rectangle spanning a value range on both axes.

    Args:
        x_range: (x_min, x_max) span in data coordinates.
        y_range: (y_min, y_max) span in data coordinates.
        color: Fill color. Defaults to the theme reference-line color.
        opacity: Fill opacity (0-1).
    """

    x_range: tuple[float, float]
    y_range: tuple[float, float]
    color: str | None = None
    opacity: float = 0.15

    def render(self, chart) -> Element:
        x0, _ = _project(chart, self.x_range[0], 0)
        x1, _ = _project(chart, self.x_range[1], 0)
        _, y0 = _project(chart, 0, self.y_range[0])
        _, y1 = _project(chart, 0, self.y_range[1])

        left = min(x0, x1)
        top = min(y0, y1)
        width = abs(x1 - x0)
        height = abs(y1 - y0)
        color = self.color or chart.theme.resolved_reference_line_color
        return Rect(
            x=left,
            y=top,
            width=width,
            height=height,
            fill=color,
            fill_opacity=self.opacity,
        )


@dataclasses.dataclass
class LabelAnnotation:
    """A text label anchored at a data point.

    Args:
        point: (x, y) anchor in data coordinates.
        text: Label text.
        color: Text color. Defaults to the theme axis-title color.
        font_size: Font size in pixels.
        text_anchor: SVG text-anchor ("start", "middle", "end").
    """

    point: tuple[float, float]
    text: str
    color: str | None = None
    font_size: float = 11.0
    text_anchor: str = "middle"

    def render(self, chart) -> Element:
        x, y = _project(chart, *self.point)
        color = self.color or chart.theme.resolved_axis_title_color
        return Text(
            text=self.text,
            x=x,
            y=y,
            fill=color,
            font_size=self.font_size,
            font_family=chart.theme.title_font_family,
            text_anchor=self.text_anchor,
        )
