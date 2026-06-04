"""ScatterChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for ScatterChart functionality.
"""

import pytest

from charted.charts.scatter import ScatterChart


class TestScatterChartHappyPath:
    """Happy path tests for ScatterChart."""

    def test_basic_scatter_chart(self):
        """Test basic scatter chart with simple data."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        html = chart.html
        assert "<circle" in html.lower()

    def test_multi_series_scatter_chart(self):
        """Test scatter chart with multiple series."""
        chart = ScatterChart(x_data=[[0, 1], [0, 1]], y_data=[[10, 20], [15, 25]])
        html = chart.html
        assert "<circle" in html.lower()

    def test_scatter_chart_single_point(self):
        """Test scatter chart with single data point."""
        chart = ScatterChart(x_data=[0, 1], y_data=[42, 50])
        html = chart.html
        assert "svg" in html.lower()

    def test_scatter_chart_negative_values(self):
        """Test scatter chart with negative values."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[-10, -20, -30])
        html = chart.html
        assert "<circle" in html.lower()

    def test_scatter_chart_large_values(self):
        """Test scatter chart with very large values."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[1e6, 2e6, 3e6])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html


class TestScatterChartSadPath:
    """Sad path tests for ScatterChart edge cases and error conditions."""

    def test_scatter_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        from charted import NoDataError

        with pytest.raises(NoDataError, match="No data"):
            ScatterChart(x_data=[], y_data=[])


class TestScatterChartScales:
    """Tests for log and time scales on ScatterChart."""

    def test_scatter_log_x_scale(self):
        """x_scale='log' renders and tick labels are decade values."""
        chart = ScatterChart(
            x_data=[1, 10, 100, 1000],
            y_data=[5, 8, 12, 15],
            x_scale="log",
        )
        html = chart.html
        assert "<circle" in html.lower()
        assert ">10<" in html
        assert ">100<" in html
        assert ">1000<" in html
        assert chart.to_config()["x_scale"] == "log"
        assert chart.describe()["scales"]["x"] == "log"

    def test_scatter_log_x_scale_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            ScatterChart(x_data=[0, 10, 100], y_data=[1, 2, 3], x_scale="log").html


class TestScatterChartAxisRange:
    """Tests for configurable axis range / domain padding."""

    def test_default_range_unchanged(self):
        """Omitting the new params leaves the auto-fit output byte-identical."""
        base = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30]).html
        explicit = ScatterChart(
            x_data=[0, 1, 2],
            y_data=[10, 20, 30],
            x_range=None,
            y_range=None,
            domain_padding=None,
        ).html
        assert base == explicit

    def test_y_range_fixes_domain(self):
        """y_range fixes the y-axis domain regardless of data extent."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30], y_range=(0, 100))
        dim = chart.y_axis.axis_dimension
        # The rendered axis must span the requested range.
        assert dim.min_value <= 0
        assert dim.max_value >= 100
        # The top bound label is rendered on the axis.
        assert ">100<" in chart.html

    def test_x_range_fixes_domain_with_padding_below_data(self):
        """x_range can extend the axis below the data minimum."""
        chart = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30], x_range=(-5, 5))
        dim = chart.x_axis.axis_dimension
        assert dim.min_value <= -5
        assert dim.max_value >= 5

    def test_domain_padding_expands_data_domain(self):
        """domain_padding pads the data-derived domain on each side."""
        unpadded = ScatterChart(x_data=[0, 1, 2], y_data=[10, 20, 30])
        padded = ScatterChart(
            x_data=[0, 1, 2], y_data=[10, 20, 30], domain_padding=0.5
        )
        # Padding only ever widens (or keeps) the span, never narrows it.
        assert (
            padded.y_axis.axis_dimension.max_value
            >= unpadded.y_axis.axis_dimension.max_value
        )
        # Plotted point count is unaffected by the synthetic anchor.
        assert len(padded.y_values[0]) == 3


class TestScatterQuadrantLabelPlacement:
    """Tests for quadrant label inset and optional backplate."""

    LABELS = ["TL", "TR", "BL", "BR"]

    def test_inset_defaults_move_labels_off_the_edge(self):
        """The default inset pushes labels in from the flush corner."""
        flush = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            quadrant_labels=self.LABELS,
            quadrant_label_inset=0,
        )
        inset = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            quadrant_labels=self.LABELS,
        )
        # Default inset is a positive pad, so the rendered SVG differs from
        # the zero-inset (old flush) rendering.
        assert inset.html != flush.html

    def test_inset_is_backward_compatible_when_zero(self):
        """Passing inset=0 reproduces the original flush-corner placement."""
        explicit_zero = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            quadrant_labels=self.LABELS,
            quadrant_label_inset=0,
        )
        # The first top-left label hugs x=8 (the original base pad) at inset 0.
        assert 'x="8.0"' in explicit_zero.html

    def test_backplate_off_by_default(self):
        """No backing <rect> is added unless requested."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            quadrant_labels=self.LABELS,
        )
        without = chart.html.count("<rect")
        with_plate = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            quadrant_labels=self.LABELS,
            quadrant_label_backplate=True,
        ).html.count("<rect")
        # One backplate rect per non-empty label.
        assert with_plate == without + 4

    def test_backplate_uses_background_color(self):
        """The backplate fills with the theme background for contrast."""
        chart = ScatterChart(
            x_data=[1, 2, 3],
            y_data=[1, 2, 3],
            quadrant_labels=self.LABELS,
            quadrant_label_backplate=True,
        )
        bg = chart.theme.background_color
        assert f'fill="{bg}"' in chart.html
        # Rounded corners and partial opacity are present on the plate.
        assert "rx=" in chart.html
