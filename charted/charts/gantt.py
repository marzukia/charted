"""Gantt chart for project timeline visualization.

Displays tasks as horizontal bars along a timeline, where each bar's
position and length represent the task's start and duration. Supports
a real date/time x-axis (start/end may be dates, datetimes or ISO
strings), optional dependency arrows between tasks, and optional
task-duration labels.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import cast

from charted.charts.chart import Chart
from charted.charts.scales import TimeValue
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path, Text
from charted.themes.core import Theme
from charted.utils.types import Labels, SeriesStyleConfig, Vector2D

GanttTask = tuple[TimeValue, TimeValue]
GanttSeries = list[GanttTask]
DurationFormatter = Callable[[TimeValue, TimeValue], object]


def _is_time_value(value: object) -> bool:
    """True if a start/end value should be plotted on a date/time axis."""
    return isinstance(value, (date, datetime, str))


class GanttChart(Chart):
    """Gantt chart for scheduling and project timeline visualization.

    Displays tasks as horizontal bars along a timeline. Each task has a
    start and end value, and bars are drawn proportionally along the x-axis.
    Supports multi-series (grouped tasks) and optional dependency arrows.

    Args:
        data: Single series of (start, end) tuples, or multi-series list of lists.
        labels: Task names displayed on the y-axis (one per task in single series,
            or one per group in multi-series).
        width, height: Chart dimensions in pixels.
        title: Optional chart title.
        theme: Optional theme configuration.
        series_names: Names for each series (shown in legend).
        series_styles: Per-series style overrides.
        dependencies: List of (from_task, to_task) tuples for dependency arrows.
            Task indices are 0-based within the flattened task list.
        bar_height_ratio: Bar height as fraction of row height (default 0.6).
        show_today_line: If True, draw a dashed vertical line at a given
            x_position value (requires x_position to be set).
        x_position: Value (number or date) for the today/marker line.
        show_durations: If True, label each bar with its duration (default
            False). For numeric data the label is ``end - start``; for date
            data it is the number of whole days. A ``duration_formatter`` can
            override the rendered text.
        duration_formatter: Optional ``callable(start, end) -> str`` used to
            format each duration label.

    Dates: ``start``/``end`` may be ``date``, ``datetime`` or ISO-8601
    strings as well as plain numbers. When any value is date-like the x-axis
    automatically switches to a calendar-aware time scale; otherwise the
    historical integer axis is used unchanged.

    Example:
        >>> from charted import GanttChart
        >>> chart = GanttChart(
        ...     data=[("2024-01-01", "2024-02-15"), ("2024-02-01", "2024-04-01")],
        ...     labels=["Design", "Development"],
        ...     show_durations=True,
        ... )
        >>> chart.save('project.svg')
    """

    # Gantt stores N tasks as N (start, end) pairs, so x_data holds 2N
    # coordinate values rather than one per label. The generic label-length
    # cross-check does not apply; Gantt validates its own labels in __init__.
    _skip_label_length_validation: bool = True

    def __init__(
        self,
        data: list[GanttTask] | list[GanttSeries],
        labels: Labels | None = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        dependencies: list[tuple[int, int]] | None = None,
        bar_height_ratio: float = 0.6,
        show_today_line: bool = False,
        x_position: TimeValue | None = None,
        show_durations: bool = False,
        duration_formatter: DurationFormatter | None = None,
    ):
        if not data:
            raise ValueError("No data was provided to the GanttChart element.")

        if isinstance(data[0], tuple):
            flat_data = [list(data)]
            self._is_multi = False
        elif isinstance(data[0], list) and len(data) > 0:
            flat_data = data
            self._is_multi = True
        else:
            raise ValueError(
                "Data must be a list of (start, end) tuples or a list of series."
            )

        for series in flat_data:
            for task in series:
                if not isinstance(task, tuple) or len(task) != 2:
                    raise ValueError("Each task must be a (start, end) tuple.")

        self._raw_data = flat_data
        self._num_series = len(flat_data)
        self.dependencies = dependencies or []
        self.bar_height_ratio = bar_height_ratio
        self.show_today_line = show_today_line
        self._x_position = x_position
        self.show_durations = show_durations
        self._duration_formatter = duration_formatter

        all_starts = [s for series in flat_data for (s, e) in series]
        all_ends = [e for series in flat_data for (s, e) in series]

        # Detect a date/time axis: if any start or end is date-like, the whole
        # x-axis switches to a calendar-aware time scale. Pure-numeric data
        # keeps the original linear integer axis byte-for-byte.
        self._is_time = any(
            _is_time_value(v) for v in (*all_starts, *all_ends)
        ) or _is_time_value(x_position)

        self._global_min = min(all_starts)
        self._global_max = max(all_ends)

        self._tasks_per_series = [len(series) for series in flat_data]
        self._total_tasks = sum(self._tasks_per_series)

        if labels is None:
            labels = [f"Task {i + 1}" for i in range(self._total_tasks)]
        elif len(labels) != self._total_tasks:
            if self._is_multi and len(labels) == self._num_series:
                expanded = []
                for series_idx, count in enumerate(self._tasks_per_series):
                    if series_idx < len(labels):
                        expanded.extend([labels[series_idx]] * count)
                    else:
                        expanded.extend([f"Series {series_idx + 1}"] * count)
                labels = expanded
            else:
                labels = [f"Task {i + 1}" for i in range(self._total_tasks)]

        # Time/date values flow through the Chart x_data plumbing unchanged when
        # a time scale is active; the static type is widened only for mypy.
        x_data = cast(Vector2D, [all_starts + all_ends])
        y_data = [[float(i) for i in range(self._total_tasks)]]

        super().__init__(
            width=width,
            height=height,
            x_data=x_data,
            y_data=y_data,
            y_labels=labels,
            title=title,
            zero_index=False,
            theme=theme,
            chart_type="gantt",
            series_styles=series_styles,
            series_names=series_names,
            x_scale="time" if self._is_time else None,
        )

    @property
    def y_height(self) -> float:
        return self.plot_height / self._total_tasks if self._total_tasks else 0

    @property
    def bar_gap(self) -> float:
        return 0.0

    @property
    def row_height(self) -> float:
        return self.plot_height / self._total_tasks if self._total_tasks else 0

    @property
    def bar_height(self) -> float:
        return self.row_height * self.bar_height_ratio

    @property
    def bar_y_offset(self) -> float:
        return (self.row_height - self.bar_height) / 2

    def _task_index(self, series_idx: int, task_idx: int) -> int:
        offset = sum(self._tasks_per_series[:series_idx])
        return offset + task_idx

    @property
    def representation(self) -> G:
        result = G(
            transform=f"translate({self.left_padding}, {self.top_padding})",
        )

        bars_g = G(opacity="0.8")
        duration_g = G(
            font_family="DejaVu Sans",
            font_size=11,
            fill=self.theme.resolved_label_color,
        )
        series_offset_y = 0

        for series_idx in range(self._num_series):
            series = self._raw_data[series_idx]
            color = self.colors[series_idx] if series_idx < len(self.colors) else "#666"

            # Apply fill override from series_styles
            fill = color
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = cast(str, style["fill"])

            paths = []
            for task_idx, (start, end) in enumerate(series):
                flat_idx = series_offset_y + task_idx
                y = flat_idx * self.row_height + self.bar_y_offset
                x_start = self.x_axis.reproject(cast(float, start))
                x_end = self.x_axis.reproject(cast(float, end))
                width = abs(x_end - x_start)
                paths.append(Path.get_path(x_start, y, width, self.bar_height))

                if self.show_durations:
                    label = self._duration_label(start, end)
                    if label:
                        duration_g.add_child(
                            Text(
                                x=max(x_start, x_end) + 4,
                                y=y + self.bar_height / 2,
                                text=label,
                                dominant_baseline="central",
                            )
                        )
            bars_g.add_child(Path(d=paths, fill=fill))
            series_offset_y += self._tasks_per_series[series_idx]

        result.add_children(bars_g)
        if self.show_durations:
            result.add_children(duration_g)

        if self.dependencies:
            arrow_color = self._arrow_color()
            # Dependency arrows read as deliberate connectors, distinct from the
            # solid data bars: a dashed, lighter-weight orthogonal route ending
            # in a filled arrowhead pointing into the dependent task.
            line_g = G(
                stroke=arrow_color,
                fill="none",
                stroke_width=1.4,
                stroke_dasharray="5,3",
                stroke_linejoin="round",
            )
            head_g = G(stroke="none", fill=arrow_color)
            head = 5.0  # arrowhead half-length in px
            for from_task, to_task in self.dependencies:
                if from_task >= self._total_tasks or to_task >= self._total_tasks:
                    continue

                from_y = from_task * self.row_height + self.row_height / 2
                to_y = to_task * self.row_height + self.row_height / 2

                from_end = self._get_end_for_task(from_task)
                to_start = self._get_start_for_task(to_task)

                from_x = self.x_axis.reproject(from_end)
                to_x = self.x_axis.reproject(to_start)

                # Orthogonal elbow: out the end of the predecessor, across to
                # the successor's row, then into its start. A small stub keeps
                # the line clear of the bar edges and gives the arrowhead room.
                stub = 8.0
                elbow_x = max(from_x + stub, to_x - stub)
                tip_x = to_x - 1.0  # stop just shy so the head touches the bar
                d = (
                    f"M{from_x:.2f},{from_y:.2f} "
                    f"H{elbow_x:.2f} "
                    f"V{to_y:.2f} "
                    f"H{tip_x - head:.2f}"
                )
                line_g.add_child(Path(d=[d]))

                # Filled triangular arrowhead pointing right into the to-task.
                head_d = (
                    f"M{tip_x:.2f},{to_y:.2f} "
                    f"L{tip_x - head:.2f},{to_y - head * 0.6:.2f} "
                    f"L{tip_x - head:.2f},{to_y + head * 0.6:.2f} Z"
                )
                head_g.add_child(Path(d=[head_d]))
            result.add_children(line_g, head_g)

        if self.show_today_line and self._x_position is not None:
            x_pos = self.x_axis.reproject(cast(float, self._x_position))
            line_g = G(
                stroke=self.theme.grid_color,
                stroke_dasharray="4,4",
                stroke_width=1.5,
            )
            line_g.add_child(
                Path(
                    d=[f"M{x_pos},0 v{self.plot_height}"],
                )
            )
            result.add_children(line_g)

        # Plot borders: all four sides.
        grid_color = self.theme.grid_color
        borders = [
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 {self.plot_height} h{self.plot_width}"],
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 h{self.plot_width}"],
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M0 0 v{self.plot_height}"],
            ),
            Path(
                stroke=grid_color,
                stroke_dasharray="None",
                d=[f"M{self.plot_width} 0 v{self.plot_height}"],
            ),
        ]
        result.add_children(*borders)

        return result

    def _get_start_for_task(self, flat_idx: int) -> float:
        offset = 0
        for series in self._raw_data:
            if flat_idx < offset + len(series):
                return cast(float, series[flat_idx - offset][0])
            offset += len(series)
        return 0.0

    def _get_end_for_task(self, flat_idx: int) -> float:
        offset = 0
        for series in self._raw_data:
            if flat_idx < offset + len(series):
                return cast(float, series[flat_idx - offset][1])
            offset += len(series)
        return 0.0

    def _arrow_color(self) -> str:
        """Theme arrow colour, nudged to meet a minimum contrast ratio.

        Dependency arrows must stay legible against the plot background. The
        themed ``arrow_color`` is used as-is when it clears WCAG ~3:1 against
        the background; otherwise it falls back to a guaranteed black/white so
        the connectors never wash out (notably on the dark preset).
        """
        from charted.utils.colors import (
            calculate_contrast_ratio,
            get_contrast_color,
        )

        color = self.theme.arrow_color
        background = self.theme.background_color
        try:
            ratio = calculate_contrast_ratio(color, background)
        except Exception:
            return color
        if ratio >= 3.0:
            return color
        return get_contrast_color(background)

    def _duration_label(self, start: TimeValue, end: TimeValue) -> str:
        """Render a task's duration as text.

        A caller-supplied ``duration_formatter`` wins. Otherwise date tasks are
        labelled in whole days (``"45d"``) and numeric tasks show the raw span.
        """
        if self._duration_formatter is not None:
            return str(self._duration_formatter(start, end))
        if self._is_time:
            from charted.charts.scales import _to_epoch

            days = (_to_epoch(end) - _to_epoch(start)) / 86400.0
            return f"{round(days)}d"
        span = cast(float, end) - cast(float, start)
        if isinstance(span, float) and span.is_integer():
            span = int(span)
        return str(span)
