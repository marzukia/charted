"""Tests for Histogram chart type.

Covers construction, bin computation, rendering, and edge cases.
"""

from charted.charts.histogram import Histogram, _auto_bins, _compute_bins


class TestAutoBins:
    """Tests for _auto_bins() helper."""

    def test_small_dataset(self):
        """Small dataset returns at least 5 bins."""
        bins = _auto_bins([1, 2, 3])
        assert bins >= 5

    def test_large_dataset(self):
        """Large dataset uses Sturges' rule, capped at 50."""
        bins = _auto_bins(list(range(1000)))
        assert bins <= 50

    def test_empty_data_returns_10(self):
        """Empty data returns default 10 bins."""
        bins = _auto_bins([])
        assert bins == 10

    def test_log_scale(self):
        """Bins follow Sturges' rule: log2(n) + 1."""
        bins = _auto_bins(list(range(100)))
        import math

        assert bins == max(5, min(50, int(math.log2(100) + 1)))


class TestComputeBins:
    """Tests for _compute_bins() helper."""

    def test_basic_binning(self):
        """Basic binning returns counts and labels."""
        counts, labels = _compute_bins([1, 2, 2, 3, 3, 3, 4, 4, 5], 5)
        assert len(counts) == 5
        assert len(labels) == 6  # n_bins + 1
        assert sum(counts) == 9  # all data points accounted for

    def test_empty_data(self):
        """Empty data returns zero counts."""
        counts, labels = _compute_bins([], 5)
        assert len(counts) == 5
        assert all(c == 0.0 for c in counts)

    def test_single_value(self):
        """Single value bins into first bin."""
        counts, labels = _compute_bins([5], 3)
        assert len(counts) == 3
        assert counts[0] == 1.0

    def test_negative_values(self):
        """Negative values handled correctly."""
        counts, labels = _compute_bins([-5, -3, 0, 2, 4], 5)
        assert len(counts) == 5
        assert sum(counts) == 5

    def test_labels_format(self):
        """Labels are formatted as floats with one decimal."""
        counts, labels = _compute_bins([0, 1, 2, 3, 4, 5], 5)
        for label in labels:
            assert "." in label  # formatted as float


class TestHistogramConstruction:
    """Tests for Histogram initialization."""

    def test_basic_construction(self):
        """Basic Histogram with auto-calculated bins."""
        import random

        random.seed(42)
        data = [random.gauss(50, 15) for _ in range(200)]
        chart = Histogram(data=data)
        assert chart.title is None

    def test_with_title(self):
        """Histogram with title."""
        chart = Histogram(data=[1, 2, 3, 4, 5], title="Test Histogram")
        assert chart._title.text == "Test Histogram"

    def test_with_explicit_bins(self):
        """Histogram with explicit bin count."""
        chart = Histogram(data=[1, 2, 3, 4, 5], bins=10)
        assert len(chart.y_data[0]) == 10

    def test_with_labels(self):
        """Histogram with custom labels matching bin count."""
        chart = Histogram(
            data=[1, 2, 3, 4, 5],
            labels=["0-1", "1-2", "2-3", "3-4", "4-5", "5-6"],
            bins=5,
        )
        assert chart.x_labels is not None

    def test_with_custom_theme(self):
        """Histogram with custom theme."""
        from charted.themes.core import Theme

        theme = Theme(colors=["#ff0000"])
        chart = Histogram(data=[1, 2, 3, 4, 5], theme=theme)
        assert chart.colors[0] == "#ff0000"

    def test_empty_data_renders_zeros(self):
        """Empty data renders as zero bins."""
        chart = Histogram(data=[], bins=5)
        svg = chart.to_svg()
        assert svg.startswith("<svg")


class TestHistogramRendering:
    """Tests for Histogram rendering."""

    def test_svg_output(self):
        """Histogram produces SVG output."""
        import random

        random.seed(42)
        data = [random.gauss(50, 15) for _ in range(200)]
        chart = Histogram(data=data)
        svg = chart.to_svg()
        assert svg.startswith("<svg")
        assert "viewBox" in svg

    def test_to_html(self):
        """Histogram to_html works."""
        chart = Histogram(data=[1, 2, 3, 4, 5], bins=5)
        html = chart.to_html()
        assert "<div" in html
        assert "<svg" in html

    def test_to_base64(self):
        """Histogram to_base64 works."""
        chart = Histogram(data=[1, 2, 3, 4, 5], bins=5)
        b64 = chart.to_base64()
        assert b64.startswith("data:image/svg+xml")

    def test_representation_returns_g(self):
        """Representation returns a G element."""
        chart = Histogram(data=[1, 2, 3, 4, 5], bins=5)
        from charted.html.element import G

        assert isinstance(chart.representation, G)
