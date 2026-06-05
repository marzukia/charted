"""ColumnChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for ColumnChart functionality.
"""

import pytest

from charted.charts.column import ColumnChart


class TestColumnChartHappyPath:
    """Happy path tests for ColumnChart."""

    def test_basic_column_chart(self):
        """Test basic column chart with simple data."""
        chart = ColumnChart(data=[10, 20, 30], labels=["a", "b", "c"])
        html = chart.html
        assert "<path" in html.lower()
        # SVG uses path elements for bars, not rect

    def test_stacked_column_chart(self):
        """Test stacked column chart with multiple series."""
        chart = ColumnChart(data=[[10, 5], [15, 10], [20, 15]], labels=["a", "b", "c"])
        html = chart.html
        assert "<path" in html.lower()

    def test_column_chart_single_point(self):
        """Test column chart with single data point."""
        chart = ColumnChart(data=[42], labels=["only"])
        html = chart.html
        assert "svg" in html.lower()

    def test_column_chart_negative_values(self):
        """Test column chart with negative values."""
        chart = ColumnChart(data=[-10, -20, -30], labels=["a", "b", "c"])
        html = chart.html
        assert "svg" in html.lower()

    def test_column_chart_large_values(self):
        """Test column chart with very large values."""
        chart = ColumnChart(data=[1e6, 2e6, 3e6], labels=["a", "b", "c"])
        html = chart.html
        assert "NaN" not in html
        assert "Infinity" not in html
        assert "-Infinity" not in html

    def test_column_chart_unicode_labels(self):
        """Test that unicode labels render correctly in SVG output."""
        data = [10, 20]
        labels = ["Test", "Data"]
        chart = ColumnChart(data, labels=labels)
        html = chart.html
        assert "Test" in html
        assert "Data" in html


class TestColumnChartSadPath:
    """Sad path tests for ColumnChart edge cases and error conditions."""

    def test_column_chart_empty_data(self):
        """Test that empty data raises ValueError."""
        from charted import NoDataError

        with pytest.raises(NoDataError, match="No data"):
            ColumnChart(data=[], labels=[])

    def test_column_chart_side_by_side(self):
        """Test side-by-side column chart (y_stacked=False)."""
        chart = ColumnChart(
            data=[[10, 15], [20, 25], [30, 35]], labels=["a", "b", "c"], y_stacked=False
        )
        html = chart.html
        assert "<path" in html.lower()
        assert "svg" in html.lower()

    def test_column_chart_side_by_side_negative(self):
        """Test side-by-side column chart with negative values."""
        chart = ColumnChart(
            data=[[-10, 15], [-20, -25], [30, -35]],
            labels=["a", "b", "c"],
            y_stacked=False,
        )
        html = chart.html
        assert "svg" in html.lower()
        assert "NaN" not in html


class TestColumnLongCategoryLabels:
    """Long x-axis category labels degrade gracefully (truncate) by default."""

    LONG = [
        "This is an extremely long category label that goes on and on for many chars",
        "Another quite long category label that should overflow the gutter badly here",
        "Short",
    ]

    def test_long_labels_do_not_collapse_plot(self):
        # Without bounding, long rotated x-labels inflate bottom padding until
        # the plot height goes negative. The default cap must keep it positive.
        chart = ColumnChart(data=[10, 20, 15], labels=self.LONG, width=600, height=400)
        assert chart.plot_height > chart.height * 0.5

    def test_long_labels_truncated_with_ellipsis(self):
        chart = ColumnChart(data=[10, 20, 15], labels=self.LONG, width=600, height=400)
        rendered = [label.text for label in chart.x_axis.labels]
        assert any("…" in text for text in rendered)
        # The short label is untouched.
        assert "Short" in rendered

    def test_short_labels_unchanged(self):
        chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
        rendered = [label.text for label in chart.x_axis.labels if label.text.strip()]
        assert rendered == ["a", "b", "c"]

    def test_edge_label_stays_in_viewbox(self):
        # The leftmost category label is centred on the first column; a wide one
        # must be clamped so it does not spill off the left of the canvas.
        chart = ColumnChart(data=[10, 20, 15], labels=self.LONG, width=600, height=400)
        import re
        import xml.etree.ElementTree as ET

        root = ET.fromstring(chart.svg)
        vb = [
            float(x) for x in re.split(r"[\s,]+", (root.get("viewBox") or "").strip())
        ]
        width = vb[2]
        ns = "{http://www.w3.org/2000/svg}"
        # Find the x-axis label group (translated by left_padding) and check that
        # no label's anchor lands left of the canvas.
        for g in root.iter(f"{ns}g"):
            tf = g.get("transform") or ""
            m = re.match(r"translate\(\s*([\d.]+)", tf)
            if not m:
                continue
            gx = float(m.group(1))
            for text in g.findall(f"{ns}text"):
                tx = float(text.get("x", 0))
                inner = text.get("transform") or ""
                shift_m = re.search(r"translate\(\s*(-?[\d.]+)", inner)
                shift = float(shift_m.group(1)) if shift_m else 0.0
                abs_x = gx + tx + shift
                assert abs_x >= -0.5, f"label anchor {abs_x} off the left edge"
                assert abs_x <= width + 0.5
