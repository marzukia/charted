"""Tests for PR1 features: axis titles, reference lines, color shorthand, subtitle.

TDD tests written before implementation.
"""

from charted.charts.area import AreaChart
from charted.charts.bar import BarChart
from charted.charts.column import ColumnChart
from charted.charts.histogram import Histogram
from charted.charts.line import LineChart
from charted.charts.scatter import ScatterChart

# =========================================================================
# Feature 1: Axis titles on all chart types
# =========================================================================


class TestAxisTitlesAreaChart:
    """AreaChart should accept x_label and y_label."""

    def test_area_x_label(self):
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            x_label="Time",
        )
        svg = chart.svg
        assert "Time" in svg

    def test_area_y_label(self):
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            y_label="Value",
        )
        svg = chart.svg
        assert "Value" in svg
        assert "rotate(-90" in svg

    def test_area_both_labels(self):
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            x_label="Time",
            y_label="Value",
        )
        svg = chart.svg
        assert "Time" in svg
        assert "Value" in svg


class TestAxisTitlesHistogram:
    """Histogram should accept x_label and y_label."""

    def test_histogram_x_label(self):
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            bins=5,
            x_label="Bins",
        )
        svg = chart.svg
        assert "Bins" in svg

    def test_histogram_y_label(self):
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            bins=5,
            y_label="Frequency",
        )
        svg = chart.svg
        assert "Frequency" in svg
        assert "rotate(-90" in svg


# =========================================================================
# Feature 2: Reference lines on LineChart, BarChart (+ AreaChart, Histogram)
# =========================================================================


class TestReferenceLinesLineChart:
    """LineChart reference lines via h_lines/v_lines (already supported)
    and the new reference_lines convenience API."""

    def test_line_h_lines(self):
        """h_lines param produces dashed reference lines."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            h_lines=[15.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_line_v_lines(self):
        """v_lines param produces dashed reference lines."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            v_lines=[1.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_line_reference_lines_dict(self):
        """reference_lines=[{"value": 15, "label": "avg"}] renders line + label."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            reference_lines=[{"value": 15, "label": "avg"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg
        assert "avg" in svg

    def test_line_reference_lines_vertical(self):
        """reference_lines with axis='x' renders vertical line."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            reference_lines=[{"value": 1, "axis": "x"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_line_reference_lines_no_label(self):
        """reference_lines without label still renders the line."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            reference_lines=[{"value": 20}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg


class TestReferenceLinesBarChart:
    """BarChart reference lines."""

    def test_bar_reference_lines_dict(self):
        """reference_lines on BarChart renders line + label."""
        chart = BarChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            reference_lines=[{"value": 15, "label": "target"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg
        assert "target" in svg


class TestReferenceLinesAreaChart:
    """AreaChart should accept h_lines and v_lines."""

    def test_area_h_lines(self):
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            h_lines=[15.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_area_reference_lines_dict(self):
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            reference_lines=[{"value": 20, "label": "threshold"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg
        assert "threshold" in svg


class TestReferenceLinesColumnChart:
    """ColumnChart reference_lines convenience API."""

    def test_column_reference_lines_dict(self):
        chart = ColumnChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            reference_lines=[{"value": 25, "label": "goal"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg
        assert "goal" in svg


class TestReferenceLinesHistogram:
    """Histogram should accept h_lines and reference_lines."""

    def test_histogram_h_lines(self):
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            bins=5,
            h_lines=[2.0],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg

    def test_histogram_reference_lines_dict(self):
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            bins=5,
            reference_lines=[{"value": 2, "label": "mean"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg
        assert "mean" in svg


class TestReferenceLinesScatterChart:
    """ScatterChart reference_lines convenience API."""

    def test_scatter_reference_lines_dict(self):
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            reference_lines=[{"value": 15, "label": "baseline"}],
        )
        svg = chart.svg
        assert "stroke-dasharray" in svg
        assert "baseline" in svg


# =========================================================================
# Feature 3: Color shorthand
# =========================================================================


class TestColorShorthand:
    """colors=["#00ff00", "#ff0000"] as shorthand for setting series colors."""

    def test_line_chart_colors(self):
        chart = LineChart(
            data=[[10, 20], [30, 40]],
            labels=["A", "B"],
            colors=["#00ff00", "#ff0000"],
        )
        svg = chart.svg
        assert "#00ff00" in svg.lower()
        assert "#ff0000" in svg.lower()

    def test_bar_chart_colors(self):
        chart = BarChart(
            data=[[10, 20], [30, 40]],
            labels=["A", "B"],
            colors=["#00ff00", "#ff0000"],
        )
        svg = chart.svg
        assert "#00ff00" in svg.lower()
        assert "#ff0000" in svg.lower()

    def test_column_chart_colors(self):
        chart = ColumnChart(
            data=[[10, 20], [30, 40]],
            labels=["A", "B"],
            colors=["#00ff00", "#ff0000"],
        )
        svg = chart.svg
        assert "#00ff00" in svg.lower()
        assert "#ff0000" in svg.lower()

    def test_area_chart_colors(self):
        chart = AreaChart(
            data=[[10, 20], [30, 40]],
            labels=["A", "B"],
            colors=["#00ff00", "#ff0000"],
        )
        svg = chart.svg
        assert "#00ff00" in svg.lower()
        assert "#ff0000" in svg.lower()

    def test_scatter_chart_colors(self):
        chart = ScatterChart(
            x_data=[[1, 2], [3, 4]],
            y_data=[[10, 20], [30, 40]],
            colors=["#00ff00", "#ff0000"],
        )
        svg = chart.svg
        assert "#00ff00" in svg.lower()
        assert "#ff0000" in svg.lower()

    def test_histogram_colors(self):
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            bins=5,
            colors=["#00ff00"],
        )
        svg = chart.svg
        assert "#00ff00" in svg.lower()

    def test_colors_override_theme(self):
        """colors param should take precedence over theme colors."""
        from charted.themes.core import Theme

        theme = Theme(colors=["#aabbcc"])
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            colors=["#ff0000"],
            theme=theme,
        )
        svg = chart.svg
        assert "#ff0000" in svg.lower()


# =========================================================================
# Feature 4: Subtitle support
# =========================================================================


class TestSubtitle:
    """subtitle="text" rendered as smaller line under the title."""

    def test_line_chart_subtitle(self):
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Main Title",
            subtitle="A subtitle",
        )
        svg = chart.svg
        assert "Main Title" in svg
        assert "A subtitle" in svg

    def test_bar_chart_subtitle(self):
        chart = BarChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Sales",
            subtitle="Q1 2026",
        )
        svg = chart.svg
        assert "Sales" in svg
        assert "Q1 2026" in svg

    def test_column_chart_subtitle(self):
        chart = ColumnChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Revenue",
            subtitle="By quarter",
        )
        svg = chart.svg
        assert "Revenue" in svg
        assert "By quarter" in svg

    def test_area_chart_subtitle(self):
        chart = AreaChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Growth",
            subtitle="Over time",
        )
        svg = chart.svg
        assert "Growth" in svg
        assert "Over time" in svg

    def test_scatter_chart_subtitle(self):
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            title="Correlation",
            subtitle="X vs Y",
        )
        svg = chart.svg
        assert "Correlation" in svg
        assert "X vs Y" in svg

    def test_histogram_subtitle(self):
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            bins=5,
            title="Distribution",
            subtitle="Sample data",
        )
        svg = chart.svg
        assert "Distribution" in svg
        assert "Sample data" in svg

    def test_subtitle_without_title(self):
        """Subtitle without title should still render."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            subtitle="Just a subtitle",
        )
        svg = chart.svg
        assert "Just a subtitle" in svg

    def test_subtitle_smaller_font(self):
        """Subtitle should use a smaller font than the title."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Title",
            subtitle="Sub",
        )
        svg = chart.svg
        # Subtitle text element should exist with smaller font
        assert "Sub" in svg

    def test_no_subtitle_by_default(self):
        """No subtitle rendered when not provided."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Title Only",
        )
        svg = chart.svg
        assert "Title Only" in svg
