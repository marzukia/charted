"""LineChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for LineChart functionality.
"""

import pytest

from charted.charts.line import LineChart


class TestLineChartHappyPath:
    """Happy path tests for LineChart."""

    def test_basic_line_chart(self):
        """Test basic line chart with simple data."""
        chart = LineChart(data=[10, 20, 30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()
        assert "<path" in html.lower()  # LineChart renders paths
        assert "<circle" not in html.lower()  # Markers off by default

    def test_multi_series_line_chart(self):
        """Test line chart with multiple series."""
        chart = LineChart(
            data=[[10, 20, 30], [15, 25, 35]],
            labels=["a", "b", "c"],
            series_names=["Series 1", "Series 2"],
        )
        html = chart.html
        assert "svg" in html.lower()

    def test_line_chart_single_point(self):
        """Test line chart with single data point."""
        chart = LineChart(data=[42], labels=["only"])
        html = chart.html
        assert "svg" in html.lower()

    def test_line_chart_negative_values(self):
        """Test line chart with negative values."""
        chart = LineChart(data=[-10, -20, -30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_line_chart_large_values(self):
        """Test line chart with very large values."""
        chart = LineChart(data=[1e6, 2e6, 3e6], labels=["a", "b", "c"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html


class TestLineChartSadPath:
    """Sad path tests for LineChart edge cases and error conditions."""

    def test_line_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        from charted import NoDataError

        with pytest.raises(NoDataError, match="No data"):
            LineChart(data=[], labels=[])


class TestLineChartMarkerRendering:
    """Tests for marker rendering logic."""

    def test_markers_with_explicit_show_true(self):
        """Test markers render when show_markers=True."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            series_styles=[
                {"marker_shape": "circle", "marker_size": 5, "show_markers": True}
            ],
        )
        html = chart.html
        # Should have markers (circles)
        assert "<circle" in html.lower()

    def test_no_markers_with_explicit_show_false(self):
        """Test markers don't render when show_markers=False."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            series_styles=[
                {"marker_shape": "circle", "marker_size": 5, "show_markers": False}
            ],
        )
        html = chart.html
        # Should NOT have markers
        assert "<circle" not in html.lower()

    def test_markers_default_behavior(self):
        """Test default marker behavior (shape and size provided)."""
        chart = LineChart(
            data=[10, 20, 30],
            labels=["a", "b", "c"],
            series_styles=[{"marker_shape": "circle", "marker_size": 5}],
        )
        html = chart.html
        # Should NOT have markers by default anymore
        assert "<circle" not in html.lower()


class TestLineChartScales:
    """Tests for log and time scales on LineChart."""

    def test_line_chart_log_y_scale(self):
        """y_scale='log' renders and tick labels are decade values."""
        chart = LineChart(
            data=[1, 10, 100, 1000],
            labels=["a", "b", "c", "d"],
            y_scale="log",
        )
        html = chart.html
        assert "svg" in html.lower()
        # Decade tick labels should be present.
        assert ">1<" in html or ">1.0<" in html
        assert ">10<" in html
        assert ">100<" in html
        assert ">1000<" in html
        # to_config round-trips the scale choice.
        assert chart.to_config()["y_scale"] == "log"
        # describe reports the scale type per axis.
        assert chart.describe()["scales"]["y"] == "log"

    def test_line_chart_log_y_scale_respects_theme(self):
        from charted import Theme
        from charted.utils.defaults import DEFAULT_FONT

        theme = Theme(root_color="#123456")
        chart = LineChart(
            data=[1, 10, 100],
            labels=["a", "b", "c"],
            y_scale="log",
            theme=theme,
        )
        html = chart.html
        # Log-scale tick labels render with the theme's resolved label color
        # and the standard axis font, same as linear axes.
        assert theme.resolved_label_color.lower() in html.lower()
        assert DEFAULT_FONT.lower() in html.lower()

    def test_line_chart_log_y_scale_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            LineChart(data=[0, 10, 100], labels=["a", "b", "c"], y_scale="log").html

    def test_line_chart_time_x_axis(self):
        """date x_data + x_scale='time' renders with formatted date labels."""
        from datetime import date

        chart = LineChart(
            data=[10, 20, 30, 40],
            x_data=[
                date(2024, 1, 1),
                date(2024, 4, 1),
                date(2024, 8, 1),
                date(2024, 12, 1),
            ],
            x_scale="time",
        )
        html = chart.html
        assert "svg" in html.lower()
        assert "2024" in html
        assert chart.to_config()["x_scale"] == "time"
        assert chart.describe()["scales"]["x"] == "time"
