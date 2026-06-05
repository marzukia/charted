"""Combo (mixed) chart: bar/column and line/area on shared axes.

Composes a column representation and a line representation against one shared
coordinate system. Series can optionally be assigned to a secondary y-axis
that scales to its own range and renders tick labels on the right.
"""

from __future__ import annotations

from typing import cast

from charted.charts.axes import XAxis, YAxis, _AxisParent
from charted.charts.chart import Chart
from charted.charts.column import ColumnChart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path, Text
from charted.themes.core import Theme
from charted.utils.defaults import DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.layout_engine import LayoutEngine
from charted.utils.line_renderer import LineRenderer, _LineHost
from charted.utils.transform import translate
from charted.utils.types import ComboSeriesDict, Labels, SeriesStyleConfig, Vector2D

_BAR_TYPES = {"bar", "column"}
_LINE_TYPES = {"line", "area"}
_VALID_TYPES = _BAR_TYPES | _LINE_TYPES


class _SeriesProxy:
    """Lightweight view over a ComboChart exposing a subset of its series.

    Reuses the parent's layout, axes, padding and theme while presenting only
    the y-values/colors for the series of a given representation type. This lets
    the existing column and line renderers run unchanged against the shared
    coordinate system.
    """

    x_axis: XAxis
    y_axis: YAxis

    def __init__(self, parent: "ComboChart", indices: list[int], y_axis: YAxis) -> None:
        self._parent = parent
        self._indices = indices
        self.y_axis: YAxis = y_axis
        self.x_axis: XAxis = parent.x_axis
        self.theme: Theme = parent.theme
        self.layout: LayoutEngine = parent.layout
        self.series_styles: list[SeriesStyleConfig] | None = (
            [parent.series_styles[i] for i in indices] if parent.series_styles else None
        )

    # --- subset data ---
    @property
    def y_values(self) -> Vector2D:
        return [self._parent._reproject_series(i) for i in self._indices]

    @property
    def y_offsets(self) -> Vector2D:
        # Combo never stacks; offsets are zero.
        return [[0.0] * len(self._parent.series[i]["data"]) for i in self._indices]

    @property
    def x_values(self) -> Vector2D:
        return [self._parent.x_values[0] for _ in self._indices]

    @property
    def colors(self) -> list[str]:
        return [self._parent.colors[i] for i in self._indices]

    # --- pass-through layout/geometry ---
    @property
    def plot_width(self) -> float:
        return self._parent.plot_width

    @property
    def plot_height(self) -> float:
        return self._parent.plot_height

    @property
    def x_count(self) -> int:
        return self._parent.x_count

    @property
    def x_width(self) -> float:
        return self._parent.x_width

    @property
    def x_offset(self) -> float:
        return self._parent.x_offset

    @property
    def left_padding(self) -> float:
        return self._parent.left_padding

    @property
    def top_padding(self) -> float:
        return self._parent.top_padding

    def get_base_transform(self) -> list[str]:
        return self._parent.get_base_transform()

    def _apply_stacking(self, y: float, y_offset: float) -> float:
        return y

    # attributes the renderers probe with getattr
    y_stacked: bool = False
    markers: bool = False
    _data_labels: list[str] | list[list[str]] | None = None


class _ColumnProxy(_SeriesProxy, ColumnChart):
    """Column representation over a subset of combo series (side-by-side)."""

    def __init__(self, parent: "ComboChart", indices: list[int], y_axis: YAxis) -> None:
        _SeriesProxy.__init__(self, parent, indices, y_axis)
        self.column_gap = getattr(parent, "column_gap", 0.2)
        self.y_stacked = False
        self.series_names = None

    @property
    def representation(self) -> G:
        """Render bars centered inside each category band.

        ColumnChart.representation steps by its own gap-aware ``x_width``, but
        the proxy inherits the parent's gap-less band width (plot_width /
        x_count) via _SeriesProxy, so reusing it overflowed the plot. Instead
        position bars directly on the band centers that the line renderer uses
        (``x_values[i] + x_offset``) and size the bar group to fit within the
        band so the rightmost bar never crosses the plot edge.
        """
        g = G(opacity="0.8", transform=[*self.get_base_transform()])

        y_values = self.y_values
        num_series = len(y_values)
        if num_series == 0:
            return g

        # Band spacing is the per-category step the line vertices use; for an
        # ordinal axis this equals x_offset (x_axis.reproject(1)).
        x_values = self.x_values[0]
        if len(x_values) > 1:
            band_spacing = (x_values[-1] - x_values[0]) / (len(x_values) - 1)
        else:
            band_spacing = self.x_offset or self.x_width

        # Bar group fits inside the band: total group width leaves column_gap of
        # the band as empty margin, split evenly on both sides.
        group_width = band_spacing * (1 - self.column_gap)
        bar_width = group_width / num_series if num_series else group_width

        for series_idx, (y_values_series, color) in enumerate(
            zip(y_values, self.colors)
        ):
            fill = color
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = cast("str", style["fill"])

            paths = []
            for x_idx, y in enumerate(y_values_series):
                center = x_values[x_idx] + self.x_offset
                group_left = center - group_width / 2
                bar_x = group_left + series_idx * bar_width
                if y >= 0:
                    paths.append(Path.get_path(bar_x, 0, bar_width, y))
                else:
                    paths.append(Path.get_path(bar_x, y, bar_width, -y))
            g.add_child(Path(d=paths, fill=fill))

        return g


class ComboChart(Chart):
    """Mixed bar/line chart on shared axes with optional secondary y-axis.

    Args:
        series: List of series dicts. Each dict has:
            - ``data``: list of y-values
            - ``type``: one of "bar", "column", "line", "area"
            - ``axis`` (optional): "primary" (default) or "secondary"
            - ``name`` (optional): legend label
        labels: Category labels for the shared x-axis.
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        x_label, y_label: Optional axis titles.

    Example:
        >>> chart = ComboChart(
        ...     series=[
        ...         {"data": [10, 20, 30], "type": "bar", "name": "Revenue"},
        ...         {"data": [3, 6, 9], "type": "line", "name": "Margin"},
        ...     ],
        ...     labels=["Q1", "Q2", "Q3"],
        ... )
    """

    y_stacked: bool = False

    def __init__(
        self,
        series: list[ComboSeriesDict],
        labels: Labels | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        zero_index: bool = True,
        title: str | None = None,
        theme: Theme | None = None,
        column_gap: float = 0.2,
        series_styles: list[SeriesStyleConfig] | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        h_lines: list[float] | None = None,
        v_lines: list[float] | None = None,
        legend: str = "none",
    ):
        if not series or len(series) < 2:
            raise ValueError("ComboChart requires at least two series.")

        normalized: list[ComboSeriesDict] = []
        for s in series:
            stype = s.get("type", "line")
            if stype not in _VALID_TYPES:
                raise ValueError(
                    f"Invalid series type {stype!r}. "
                    f"Must be one of {sorted(_VALID_TYPES)}."
                )
            normalized.append(
                {
                    "data": list(s["data"]),
                    "type": stype,
                    "axis": s.get("axis", "primary"),
                    "name": s.get("name"),
                }
            )
        self.series = normalized
        self.column_gap = column_gap

        # Partition series indices by target axis.
        self._primary_indices = [
            i for i, s in enumerate(self.series) if s["axis"] != "secondary"
        ]
        self._secondary_indices = [
            i for i, s in enumerate(self.series) if s["axis"] == "secondary"
        ]

        # Base chart scales the primary y-axis to the primary series only.
        primary_data = [self.series[i]["data"] for i in self._primary_indices]
        if not primary_data:
            # All series on secondary; promote them so the layout has data.
            primary_data = [self.series[i]["data"] for i in self._secondary_indices]
            self._primary_indices = list(self._secondary_indices)
            self._secondary_indices = []

        series_names_list = [s["name"] for s in self.series]
        # Series names may individually be ``None``; the base chart's
        # ``series_names`` contract is ``list[str]`` but tolerates the optional
        # entries at runtime (the legend skips unnamed series).
        names = cast("list[str] | None", series_names_list)
        if all(n is None for n in series_names_list):
            names = None

        super().__init__(
            width=width,
            height=height,
            y_data=primary_data,
            x_labels=labels,
            title=title,
            zero_index=zero_index,
            theme=theme,
            series_names=names,
            chart_type="column",
            series_styles=series_styles,
            x_label=x_label,
            y_label=y_label,
            h_lines=h_lines,
            v_lines=v_lines,
            legend=legend,
        )

        # Override series_names so legend lists ALL series in original order.
        self.series_names = names

    @property
    def secondary_y_axis(self) -> YAxis | None:
        """Secondary y-axis, built lazily from secondary series only.

        Built on first access (which happens during the base __init__ when it
        computes ``representation``) so the axis can use the resolved plot
        dimensions and theme.
        """
        if not self._secondary_indices:
            return None
        cached = self.__dict__.get("_secondary_y_axis")
        if cached is None:
            secondary_data = [self.series[i]["data"] for i in self._secondary_indices]
            cached = YAxis(
                parent=cast("_AxisParent", self),
                data=secondary_data,
                labels=None,
                stacked=False,
                zero_index=self.zero_index,
                config=self.theme.resolved_grid_color,
            )
            self.__dict__["_secondary_y_axis"] = cached
        return cached

    @property
    def has_secondary_axis(self) -> bool:
        return bool(self._secondary_indices)

    @property
    def colors(self) -> list[str]:
        """One color per series, in original order."""
        return self._color_manager.ensure_palette_size(len(self.series))

    def _axis_for(self, index: int) -> YAxis:
        if self.series[index]["axis"] == "secondary" and self.secondary_y_axis:
            return self.secondary_y_axis
        return self.y_axis

    def _reproject_series(self, index: int) -> list[float]:
        """Reproject a series' raw data through its assigned y-axis."""
        axis = self._axis_for(index)
        return [axis.reproject(v) for v in self.series[index]["data"]]

    @property
    def representation(self) -> G:
        g = G()

        bar_indices = [i for i, s in enumerate(self.series) if s["type"] in _BAR_TYPES]
        line_indices = [
            i for i, s in enumerate(self.series) if s["type"] in _LINE_TYPES
        ]

        # Bars/columns: group by axis so each subset scales correctly, then
        # render side-by-side using the existing column representation.
        if bar_indices:
            for axis_kind in ("primary", "secondary"):
                subset = [
                    i
                    for i in bar_indices
                    if (self.series[i]["axis"] == "secondary")
                    == (axis_kind == "secondary")
                ]
                if not subset:
                    continue
                axis = self._axis_for(subset[0])
                proxy = _ColumnProxy(self, subset, axis)
                g.add_child(proxy.representation)

        # Lines/areas reuse the line renderer over their subset.
        if line_indices:
            line_proxy = _SeriesProxy(
                self, line_indices, self._axis_for(line_indices[0])
            )
            renderer = LineRenderer(cast("_LineHost", line_proxy))
            g.add_child(renderer.render())

        # Secondary y-axis tick labels, rendered into the normal element tree so
        # .html and .svg agree (the CLI and visual tests render .html).
        if self.has_secondary_axis:
            g.add_child(self._render_secondary_axis())

        return g

    def _render_secondary_axis(self) -> G:
        """Render secondary y-axis tick labels anchored on the right side."""
        axis = cast("YAxis", self.secondary_y_axis)
        right_x = self.left_padding + self.plot_width
        group = G(
            font_size=DEFAULT_FONT_SIZE,
            font_family=DEFAULT_FONT,
            fill=(
                self.theme.resolved_label_color
                if hasattr(self.theme, "resolved_label_color")
                else "#444444"
            ),
            transform=translate(x=right_x + 6, y=self.top_padding),
        )
        for y, label in zip(axis.coordinates, axis.labels):
            group.add_child(
                Text(
                    x=0,
                    y=y,
                    text=label.text,
                    transform=translate(x=0, y=label.height / 4),
                )
            )
        return group

    def describe(self) -> dict[str, object]:
        meta = super().describe()
        meta["chart_type"] = "ComboChart"
        meta["series_count"] = len(self.series)
        series_info = []
        for i, s in enumerate(self.series):
            data = s["data"]
            count = len(data)
            series_info.append(
                {
                    "name": s["name"],
                    "type": s["type"],
                    "axis": s["axis"],
                    "count": count,
                    "min": float(min(data)),
                    "max": float(max(data)),
                    "mean": float(sum(data)) / count if count else 0.0,
                    "sum": float(sum(data)),
                }
            )
        meta["series"] = series_info
        return meta

    def to_config(self) -> dict[str, object]:
        cfg = super().to_config()
        cfg["chart_type"] = "ComboChart"
        cfg["series"] = [dict(s) for s in self.series]
        cfg["column_gap"] = self.column_gap
        # Drop base-chart data keys that don't apply to the series-based API.
        for key in ("x_data", "y_data", "series_names", "labels"):
            cfg.pop(key, None)
        cfg["labels"] = [
            label.text if hasattr(label, "text") else str(label)
            for label in (self.x_labels or [])
        ]
        return cfg
