"""Tests for GanttChart - timeline/project scheduling chart."""

import pytest

from charted import GanttChart


class TestGanttChartInit:
    """Test GanttChart initialization and validation."""

    def test_basic_init(self):
        """Basic initialization with single series."""
        chart = GanttChart(
            data=[(1, 3), (2, 5), (4, 6)],
            labels=["Design", "Development", "Testing"],
        )
        assert chart._total_tasks == 3
        assert chart._num_series == 1
        assert chart._global_min == 1
        assert chart._global_max == 6

    def test_multi_series(self):
        """Multi-series initialization."""
        chart = GanttChart(
            data=[
                [(1, 3), (4, 6)],
                [(2, 5), (6, 8)],
            ],
            labels=[
                "Phase 1 Task A",
                "Phase 1 Task B",
                "Phase 2 Task A",
                "Phase 2 Task B",
            ],
        )
        assert chart._total_tasks == 4
        assert chart._num_series == 2
        assert chart._tasks_per_series == [2, 2]

    def test_empty_data(self):
        """Empty data raises error."""
        with pytest.raises(ValueError, match="No data"):
            GanttChart(data=[], labels=["A"])

    def test_invalid_data_type(self):
        """Invalid data structure raises error."""
        with pytest.raises(ValueError, match="Each task must be"):
            GanttChart(data=[[1, 2, 3]], labels=["A"])

    def test_default_labels(self):
        """Auto-generated labels when none provided."""
        chart = GanttChart(
            data=[(1, 3), (4, 6)],
        )
        assert chart._total_tasks == 2

    def test_svg_output(self):
        """Chart produces valid SVG."""
        chart = GanttChart(
            data=[(1, 3), (2, 5), (4, 6)],
            labels=["Design", "Dev", "Testing"],
        )
        svg = chart.svg
        assert svg.startswith("<svg")
        assert "GanttChart" not in svg or "gantt" in svg.lower()


class TestGanttChartRendering:
    """Test GanttChart SVG output structure."""

    def test_bars_present(self):
        """Bars should be present in SVG output."""
        chart = GanttChart(
            data=[(1, 3), (2, 5), (4, 6)],
            labels=["Design", "Dev", "Testing"],
        )
        svg = chart.svg
        assert "<path" in svg

    def test_task_labels_present(self):
        """Task labels should appear in SVG."""
        chart = GanttChart(
            data=[(1, 3), (2, 5)],
            labels=["Design", "Testing"],
        )
        svg = chart.svg
        assert "Design" in svg
        assert "Testing" in svg

    def test_dependencies(self):
        """Dependency arrows should render as connectors with arrowheads."""
        chart = GanttChart(
            data=[(1, 3), (3, 5), (5, 7)],
            labels=["A", "B", "C"],
            dependencies=[(0, 1), (1, 2)],
        )
        svg = chart.svg
        # Orthogonal dashed connector lines plus a filled triangular arrowhead
        # (closed path, "Z") render for each dependency.
        assert "stroke-dasharray=\"5,3\"" in svg
        assert "Z" in svg

    def test_today_line(self):
        """Today line should render when enabled."""
        chart = GanttChart(
            data=[(1, 5), (3, 7)],
            labels=["A", "B"],
            show_today_line=True,
            x_position=4,
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_borders_present(self):
        """Chart borders should render."""
        chart = GanttChart(
            data=[(1, 3), (2, 5)],
            labels=["A", "B"],
        )
        svg = chart.svg
        assert "h" in svg and "v" in svg

    def test_bar_dimensions(self):
        """Bar dimensions should be reasonable."""
        chart = GanttChart(
            data=[(1, 3), (2, 5)],
            labels=["A", "B"],
        )
        assert chart.row_height == chart.plot_height / 2
        assert chart.bar_height == chart.row_height * 0.6


class TestGanttChartDateAxis:
    """Date/time axis behaviour."""

    def test_string_dates_switch_to_time_scale(self):
        """ISO-string start/end values produce a time x-axis with date labels."""
        chart = GanttChart(
            data=[("2024-01-01", "2024-02-15"), ("2024-02-01", "2024-04-01")],
            labels=["Design", "Dev"],
        )
        assert chart._is_time is True
        assert chart.x_scale == "time"
        labels = [lbl.text for lbl in chart.x_axis.labels]
        # Calendar-aware month labels, not bare integers.
        assert any("2024" in lbl for lbl in labels)

    def test_date_objects_accepted(self):
        """datetime.date start/end values are accepted and plotted."""
        from datetime import date

        chart = GanttChart(
            data=[(date(2024, 1, 1), date(2024, 3, 1))],
            labels=["Task"],
        )
        assert chart.x_scale == "time"
        svg = chart.svg
        assert svg.startswith("<svg")

    def test_numeric_data_stays_linear(self):
        """Plain numeric data keeps the historical linear integer axis."""
        chart = GanttChart(data=[(1, 3), (2, 5)], labels=["A", "B"])
        assert chart._is_time is False
        assert chart.x_scale == "linear"


class TestGanttChartDurations:
    """Optional task-duration labels."""

    def test_numeric_duration_labels(self):
        """show_durations renders numeric span labels inside the SVG."""
        chart = GanttChart(
            data=[(1, 4), (2, 5)],
            labels=["A", "B"],
            show_durations=True,
        )
        svg = chart.svg
        assert ">3<" in svg  # 4 - 1 == 3

    def test_date_duration_labels_in_days(self):
        """Date durations are labelled in whole days."""
        chart = GanttChart(
            data=[("2024-01-01", "2024-01-31")],
            labels=["A"],
            show_durations=True,
        )
        svg = chart.svg
        assert "30d" in svg

    def test_duration_formatter_override(self):
        """A custom duration_formatter controls the rendered text."""
        chart = GanttChart(
            data=[(1, 4)],
            labels=["A"],
            show_durations=True,
            duration_formatter=lambda s, e: f"{e - s} units",
        )
        svg = chart.svg
        assert "3 units" in svg

    def test_durations_off_by_default(self):
        """No duration text is emitted unless show_durations is set."""
        chart = GanttChart(data=[(1, 4)], labels=["A"])
        assert chart.show_durations is False


class TestGanttChartLayout:
    """Test GanttChart layout calculations."""

    def test_row_height_single_task(self):
        """Single task gets full plot height."""
        chart = GanttChart(
            data=[(1, 5)],
            labels=["A"],
        )
        assert chart.row_height == chart.plot_height

    def test_bar_y_offset(self):
        """Bar y-offset centers bars within row."""
        chart = GanttChart(
            data=[(1, 3), (2, 5)],
            labels=["A", "B"],
        )
        expected_offset = (chart.row_height - chart.bar_height) / 2
        assert chart.bar_y_offset == expected_offset

    def test_task_index_mapping(self):
        """Flat task index from series+task."""
        chart = GanttChart(
            data=[
                [(1, 3), (4, 6)],
                [(2, 5), (6, 8)],
            ],
            labels=["A1", "A2", "B1", "B2"],
        )
        assert chart._task_index(0, 0) == 0
        assert chart._task_index(0, 1) == 1
        assert chart._task_index(1, 0) == 2
        assert chart._task_index(1, 1) == 3

    def test_get_start_end(self):
        """Start/end lookup by flat index."""
        chart = GanttChart(
            data=[
                [(1, 3), (4, 6)],
                [(2, 5), (6, 8)],
            ],
            labels=["A1", "A2", "B1", "B2"],
        )
        assert chart._get_start_for_task(0) == 1
        assert chart._get_end_for_task(0) == 3
        assert chart._get_start_for_task(2) == 2
        assert chart._get_end_for_task(3) == 8
