"""Gantt chart for project timeline visualization.

Displays tasks as horizontal bars along a timeline, where each bar's
position and length represent the task's start and duration. Supports
optional dependency arrows between tasks.
"""

from __future__ import annotations

from charted.charts.chart import Chart
from charted.constants import DEFAULT_CHART_HEIGHT, DEFAULT_CHART_WIDTH
from charted.html.element import G, Path
from charted.themes.core import Theme
from charted.utils.types import Labels, SeriesStyleConfig


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

    Example:
        >>> from charted import GanttChart
        >>> chart = GanttChart(
        ...     data=[(1, 3), (2, 5), (4, 6)],
        ...     labels=["Design", "Development", "Testing"],
        ... )
        >>> chart.save('project.svg')
    """

    def __init__(
        self,
        data: list,
        labels: Labels = None,
        width: float = DEFAULT_CHART_WIDTH,
        height: float = DEFAULT_CHART_HEIGHT,
        title: str | None = None,
        theme: Theme | None = None,
        series_names: list[str] | None = None,
        series_styles: list[SeriesStyleConfig] | None = None,
        dependencies: list[tuple[int, int]] | None = None,
        bar_height_ratio: float = 0.6,
        show_today_line: bool = False,
        x_position: float | None = None,
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

        all_starts = [s for series in flat_data for (s, e) in series]
        all_ends = [e for series in flat_data for (s, e) in series]
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

        x_data = [all_starts + all_ends]
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
        series_offset_y = 0

        for series_idx in range(self._num_series):
            series = self._raw_data[series_idx]
            color = self.colors[series_idx] if series_idx < len(self.colors) else "#666"

            # Apply fill override from series_styles
            fill = color
            if self.series_styles and series_idx < len(self.series_styles):
                style = self.series_styles[series_idx] or {}
                if style.get("fill"):
                    fill = style["fill"]

            paths = []
            for task_idx, (start, end) in enumerate(series):
                flat_idx = series_offset_y + task_idx
                y = flat_idx * self.row_height + self.bar_y_offset
                x_start = self.x_axis.reproject(start)
                x_end = self.x_axis.reproject(end)
                width = abs(x_end - x_start)
                paths.append(Path.get_path(x_start, y, width, self.bar_height))
            bars_g.add_child(Path(d=paths, fill=fill))
            series_offset_y += self._tasks_per_series[series_idx]

        result.add_children(bars_g)

        if self.dependencies:
            arrow_g = G(stroke=self.theme.arrow_color, fill="none")
            for from_task, to_task in self.dependencies:
                if from_task >= self._total_tasks or to_task >= self._total_tasks:
                    continue

                from_y = from_task * self.row_height + self.row_height / 2
                to_y = to_task * self.row_height + self.row_height / 2

                from_end = self._get_end_for_task(from_task)
                to_start = self._get_start_for_task(to_task)

                from_x = self.x_axis.reproject(from_end)
                to_x = self.x_axis.reproject(to_start)

                # Quadratic bezier connecting from-end to to-start
                mid_x = (from_x + to_x) / 2
                d = (
                    f"M{from_x},{from_y} "
                    f"Q{mid_x},{from_y} {mid_x},{to_y} "
                    f"Q{to_x},{to_y} {to_x},{to_y}"
                )
                arrow_g.add_child(Path(d=[d]))
            result.add_children(arrow_g)

        if self.show_today_line and self._x_position is not None:
            x_pos = self.x_axis.reproject(self._x_position)
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

        # Plot borders — all four sides.
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
                return series[flat_idx - offset][0]
            offset += len(series)
        return 0.0

    def _get_end_for_task(self, flat_idx: int) -> float:
        offset = 0
        for series in self._raw_data:
            if flat_idx < offset + len(series):
                return series[flat_idx - offset][1]
            offset += len(series)
        return 0.0
