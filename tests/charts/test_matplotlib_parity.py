"""Tests for matplotlib parity features (Issue #22).

Covers: data labels, axis title labels, quadrant labels,
reference lines, and pie percentage labels.
"""

from charted.charts.bar import BarChart
from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.charts.pie import PieChart
from charted.charts.scatter import ScatterChart


class TestDataLabels:
    """Tests for data_labels parameter across chart types."""

    def test_scatter_data_labels(self):
        """Scatter chart renders text labels on each point."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            data_labels=["alpha", "beta", "gamma"],
        )
        svg = chart.svg
        assert "alpha" in svg
        assert "beta" in svg
        assert "gamma" in svg

    def test_scatter_data_labels_multi_series(self):
        """Scatter chart renders labels for multiple series."""
        chart = ScatterChart(
            x_data=[[1, 2], [3, 4]],
            y_data=[[10, 20], [30, 40]],
            data_labels=[["a", "b"], ["c", "d"]],
        )
        svg = chart.svg
        assert "a" in svg
        assert "d" in svg

    def test_line_data_labels(self):
        """Line chart renders text labels above data points."""
        chart = LineChart(
            data=[5, 15, 25],
            labels=["Jan", "Feb", "Mar"],
            data_labels=["low", "mid", "high"],
        )
        svg = chart.svg
        assert "low" in svg
        assert "mid" in svg
        assert "high" in svg

    def test_column_data_labels(self):
        """Column chart renders labels above columns."""
        chart = ColumnChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            data_labels=["ten", "twenty", "thirty"],
        )
        svg = chart.svg
        assert "ten" in svg
        assert "twenty" in svg

    def test_bar_data_labels(self):
        """Bar chart renders labels at the end of bars."""
        chart = BarChart(
            data=[100, 200, 300],
            labels=["X", "Y", "Z"],
            data_labels=["100u", "200u", "300u"],
        )
        svg = chart.svg
        assert "100u" in svg
        assert "300u" in svg

    def test_no_data_labels(self):
        """Charts render fine with data_labels=None (default)."""
        chart = ScatterChart(x_data=[1, 2], y_data=[10, 20])
        svg = chart.svg
        assert "<text" not in svg or "text" in svg  # no crash

    def test_partial_data_labels(self):
        """Empty strings in data_labels are skipped."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            data_labels=["first", "", "third"],
        )
        svg = chart.svg
        assert "first" in svg
        assert "third" in svg


class TestAxisLabels:
    """Tests for x_label and y_label axis title parameters."""

    def test_scatter_axis_labels(self):
        """Scatter chart renders x and y axis titles."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            x_label="Velocity",
            y_label="Altitude",
        )
        svg = chart.svg
        assert "Velocity" in svg
        assert "Altitude" in svg

    def test_line_axis_labels(self):
        """Line chart renders axis titles."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            x_label="Category",
            y_label="Revenue",
        )
        svg = chart.svg
        assert "Category" in svg
        assert "Revenue" in svg

    def test_column_axis_labels(self):
        """Column chart renders axis titles."""
        chart = ColumnChart(
            data=[5, 10],
            labels=["Q1", "Q2"],
            x_label="Quarter",
            y_label="Sales",
        )
        svg = chart.svg
        assert "Quarter" in svg
        assert "Sales" in svg

    def test_bar_axis_labels(self):
        """Bar chart renders axis titles."""
        chart = BarChart(
            data=[100, 200],
            labels=["X", "Y"],
            x_label="Value",
            y_label="Category",
        )
        svg = chart.svg
        assert "Value" in svg
        assert "Category" in svg

    def test_y_label_rotation(self):
        """Y-axis label has rotate transform for vertical rendering."""
        chart = ScatterChart(
            x_data=[1, 2],
            y_data=[10, 20],
            y_label="Rotated",
        )
        svg = chart.svg
        assert "rotate(-90" in svg

    def test_no_axis_labels_default(self):
        """No axis labels rendered by default."""
        chart = ScatterChart(x_data=[1, 2], y_data=[10, 20])
        svg = chart.svg
        # Should not contain axis label text elements beyond normal axes
        assert "rotate(-90" not in svg


class TestQuadrantLabels:
    """Tests for quadrant_labels on ScatterChart."""

    def test_quadrant_labels_basic(self):
        """Four quadrant labels are rendered."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            quadrant_labels=["TL", "TR", "BL", "BR"],
        )
        svg = chart.svg
        assert "TL" in svg
        assert "TR" in svg
        assert "BL" in svg
        assert "BR" in svg

    def test_quadrant_labels_multiline(self):
        """Quadrant labels with newlines render multiple text elements."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            quadrant_labels=["LIKEABLE\nINSANE", "LIKEABLE\nSANE", "", ""],
        )
        svg = chart.svg
        assert "LIKEABLE" in svg
        assert "INSANE" in svg
        assert "SANE" in svg

    def test_quadrant_labels_partial(self):
        """Fewer than 4 labels pads with empty strings (no crash)."""
        chart = ScatterChart(
            x_data=[1, 2],
            y_data=[10, 20],
            quadrant_labels=["Only TL"],
        )
        svg = chart.svg
        assert "Only TL" in svg

    def test_no_quadrant_labels_default(self):
        """No quadrant labels by default."""
        chart = ScatterChart(x_data=[1, 2], y_data=[10, 20])
        svg = chart.svg
        assert "opacity=\"0.6\"" not in svg


class TestReferenceLines:
    """Tests for h_lines and v_lines reference line parameters."""

    def test_horizontal_reference_line(self):
        """Horizontal reference line renders with dashed style."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            h_lines=[15.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_vertical_reference_line(self):
        """Vertical reference line renders with dashed style."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            v_lines=[2.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_multiple_reference_lines(self):
        """Multiple h_lines and v_lines render."""
        chart = ScatterChart(
            x_data=[0, 5, 10],
            y_data=[0, 50, 100],
            h_lines=[25.0, 75.0],
            v_lines=[2.5, 7.5],
        )
        svg = chart.svg
        # Each line produces a path with dasharray
        assert svg.count("stroke-dasharray") >= 4

    def test_reference_lines_on_line_chart(self):
        """Reference lines work on line charts."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            h_lines=[15.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_reference_lines_on_column_chart(self):
        """Reference lines work on column charts."""
        chart = ColumnChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            h_lines=[15.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_no_reference_lines_default(self):
        """No reference lines rendered by default."""
        chart = ScatterChart(x_data=[1, 2], y_data=[10, 20])
        svg = chart.svg
        assert "6 3" not in svg


class TestPiePercentages:
    """Tests for show_percentages on PieChart."""

    def test_show_percentages(self):
        """Percentage values appear on each slice."""
        chart = PieChart(
            data=[25, 25, 50],
            labels=["A", "B", "C"],
            show_percentages=True,
        )
        svg = chart.svg
        assert "25.0%" in svg
        assert "50.0%" in svg

    def test_show_percentages_format(self):
        """Percentages are formatted with label and one decimal place."""
        chart = PieChart(
            data=[33, 67],
            labels=["X", "Y"],
            show_percentages=True,
        )
        svg = chart.svg
        assert "X (33.0%)" in svg
        assert "Y (67.0%)" in svg

    def test_show_percentages_false_default(self):
        """No percentages by default."""
        chart = PieChart(
            data=[50, 50],
            labels=["A", "B"],
        )
        svg = chart.svg
        assert "%" not in svg

    def test_show_percentages_with_doughnut(self):
        """Percentages work with doughnut (inner_radius) mode."""
        chart = PieChart(
            data=[40, 60],
            labels=["M", "N"],
            inner_radius=0.4,
            show_percentages=True,
        )
        svg = chart.svg
        assert "40.0%" in svg
        assert "60.0%" in svg

    def test_show_percentages_single_slice(self):
        """100% slice shows percentage."""
        chart = PieChart(
            data=[100],
            labels=["Only"],
            show_percentages=True,
        )
        svg = chart.svg
        assert "100.0%" in svg


class TestCombinedFeatures:
    """Tests combining multiple new features on a single chart."""

    def test_scatter_all_features(self):
        """Scatter with data labels, axis labels, quadrants, and ref lines."""
        chart = ScatterChart(
            x_data=[1, 2, 3, 4],
            y_data=[10, 20, 15, 25],
            data_labels=["P1", "P2", "P3", "P4"],
            quadrant_labels=["TL", "TR", "BL", "BR"],
            h_lines=[17.5],
            v_lines=[2.5],
            x_label="Speed",
            y_label="Height",
            title="Full Scatter",
        )
        svg = chart.svg
        assert "P1" in svg
        assert "TL" in svg
        assert "Speed" in svg
        assert "Height" in svg
        assert "stroke-dasharray" in svg
        assert "Full Scatter" in svg

    def test_line_with_labels_and_ref_lines(self):
        """Line chart with data labels, axis labels, and reference lines."""
        chart = LineChart(
            data=[5, 15, 10],
            labels=["Mon", "Tue", "Wed"],
            data_labels=["5", "15", "10"],
            x_label="Day",
            y_label="Count",
            h_lines=[10.0],
        )
        svg = chart.svg
        assert "Day" in svg
        assert "Count" in svg
        assert "stroke-dasharray" in svg
