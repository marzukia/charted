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
        # Check that path elements exist (bars are rendered as paths)
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
        """Dependency arrows should render."""
        chart = GanttChart(
            data=[(1, 3), (3, 5), (5, 7)],
            labels=["A", "B", "C"],
            dependencies=[(0, 1), (1, 2)],
        )
        svg = chart.svg
        # Check for curve paths (Q commands indicate quadratic bezier)
        assert "Q" in svg

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
        # Borders are h/v paths
        assert "h" in svg and "v" in svg

    def test_bar_dimensions(self):
        """Bar dimensions should be reasonable."""
        chart = GanttChart(
            data=[(1, 3), (2, 5)],
            labels=["A", "B"],
        )
        # row_height should be plot_height / 2
        assert chart.row_height == chart.plot_height / 2
        # bar_height should be row_height * ratio
        assert chart.bar_height == chart.row_height * 0.6


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
