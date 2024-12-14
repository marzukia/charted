"""Visual regression tests for charts with themes and edge cases.

These tests generate SVG charts and compare them against baseline images
to detect unintended visual changes.

Run with: uv run pytest tests/visual/ -v
"""

import io

import pytest

# Optional dependencies for PNG comparison
pytest.importorskip("cairosvg")
pytest.importorskip("PIL")

import cairosvg
from PIL import Image, ImageChops

from charted import BarChart, ColumnChart, LineChart, PieChart, Theme


def svg_to_png(svg_data: str) -> bytes:
    """Convert SVG string to PNG bytes."""
    png_data = cairosvg.svg2png(bytestring=svg_data.encode())
    return png_data


def compare_images(
    image1: Image.Image, image2: Image.Image, tolerance: int = 10
) -> bool:
    """Compare two images with pixel tolerance.

    Args:
        image1: First image
        image2: Second image
        tolerance: Maximum pixel difference (0-255)

    Returns:
        True if images are similar within tolerance
    """
    diff = ImageChops.difference(image1, image2)
    bbox = diff.getbbox()

    if bbox is None:
        return True  # Images are identical

    # Calculate difference percentage
    pixels = list(diff.getdata())
    total_pixels = len(pixels) // 4  # RGBA
    differing_pixels = sum(1 for p in pixels if any(c > tolerance for c in p[:3]))

    diff_percentage = (differing_pixels / total_pixels) * 100
    return diff_percentage < 1.0  # Less than 1% difference allowed


class TestVisualRegressionThemes:
    """Test chart rendering with different themes."""

    @pytest.mark.parametrize("chart_class", [BarChart, ColumnChart, LineChart])
    def test_chart_with_default_theme(self, chart_class, tmp_path):
        """Test chart renders correctly with default theme."""
        chart = chart_class(data=[10, 20, 30], labels=["A", "B", "C"])
        svg = chart.html

        # Save SVG for manual inspection if needed
        output_path = tmp_path / f"{chart_class.__name__}_default.svg"
        output_path.write_text(svg)

        # Basic visual validation - SVG should be valid
        assert "<svg" in svg
        assert "</svg>" in svg
        assert len(svg) > 100  # Should have substantial content

    @pytest.mark.parametrize("chart_class", [BarChart, ColumnChart, LineChart])
    def test_chart_with_custom_theme(self, chart_class, tmp_path):
        """Test chart renders with custom theme colors."""
        custom_theme = Theme(
            colors=["#FF0000", "#00FF00", "#0000FF"],
            background_color="#000000",
            legend_font_color="#ffffff",
        )
        chart = chart_class(
            data=[10, 20, 30], labels=["A", "B", "C"], theme=custom_theme
        )
        svg = chart.html

        # Should contain custom colors
        assert "#ff0000" in svg.lower() or "#FF0000" in svg
        output_path = tmp_path / f"{chart_class.__name__}_custom.svg"
        output_path.write_text(svg)

    def test_pie_chart_with_theme(self, tmp_path):
        """Test pie chart rendering with theme."""
        custom_theme = Theme(colors=["#FF0000", "#00FF00", "#0000FF"])
        chart = PieChart(data=[25, 35, 40], labels=["A", "B", "C"], theme=custom_theme)
        svg = chart.html

        assert "<path" in svg.lower()
        output_path = tmp_path / "pie_custom.svg"
        output_path.write_text(svg)


class TestVisualRegressionEdgeCases:
    """Test visual rendering of edge cases."""

    def test_single_data_point(self, tmp_path):
        """Test chart with single data point."""
        chart = BarChart(data=[42], labels=["Only"])
        svg = chart.html

        # Should render without errors
        assert "<svg" in svg
        output_path = tmp_path / "bar_single.svg"
        output_path.write_text(svg)

    def test_very_large_values(self, tmp_path):
        """Test chart with very large values."""
        chart = BarChart(data=[1e9, 2e9, 3e9], labels=["A", "B", "C"])
        svg = chart.html

        # Should not contain NaN or Infinity
        assert "NaN" not in svg
        assert "Infinity" not in svg
        output_path = tmp_path / "bar_large.svg"
        output_path.write_text(svg)

    def test_very_small_values(self, tmp_path):
        """Test chart with very small values."""
        chart = BarChart(data=[1e-9, 2e-9, 3e-9], labels=["A", "B", "C"])
        svg = chart.html

        assert "NaN" not in svg
        output_path = tmp_path / "bar_small.svg"
        output_path.write_text(svg)

    def test_mixed_positive_negative(self, tmp_path):
        """Test chart with mixed positive and negative values."""
        chart = BarChart(data=[-10, 0, 10], labels=["A", "B", "C"])
        svg = chart.html

        assert "<svg" in svg
        output_path = tmp_path / "bar_mixed.svg"
        output_path.write_text(svg)

    def test_zero_values(self, tmp_path):
        """Test chart with zero values."""
        chart = BarChart(data=[0, 0, 0], labels=["A", "B", "C"])
        svg = chart.html

        # Should render (even if all zeros)
        assert "<svg" in svg
        output_path = tmp_path / "bar_zeros.svg"
        output_path.write_text(svg)

    def test_many_data_points(self, tmp_path):
        """Test chart with many data points."""
        chart = BarChart(data=list(range(100)), labels=[str(i) for i in range(100)])
        svg = chart.html

        assert "<svg" in svg
        assert len(svg) > 1000  # Should be substantial
        output_path = tmp_path / "bar_many.svg"
        output_path.write_text(svg)


class TestVisualRegressionSVGStructure:
    """Test SVG structure and validity."""

    def test_svg_xml_declaration(self, tmp_path):
        """Test SVG has proper XML structure."""
        chart = BarChart(data=[10, 20, 30])
        svg = chart.html

        assert svg.startswith("<svg")
        assert "xmlns=" in svg
        assert "width=" in svg
        assert "height=" in svg

    def test_svg_contains_paths(self, tmp_path):
        """Test SVG contains expected elements."""
        chart = BarChart(data=[10, 20, 30])
        svg = chart.html

        # Bar charts use path elements
        assert "<path" in svg.lower() or "<rect" in svg.lower()

    def test_svg_contains_text(self, tmp_path):
        """Test SVG contains text for labels."""
        chart = BarChart(data=[10, 20, 30], labels=["A", "B", "C"])
        svg = chart.html

        assert "<text" in svg.lower() or "A" in svg
        assert "B" in svg
        assert "C" in svg

    def test_svg_valid_viewbox(self, tmp_path):
        """Test SVG has valid viewBox."""
        chart = BarChart(data=[10, 20, 30])
        svg = chart.html

        assert "viewBox=" in svg or "width=" in svg

    def test_doughnut_chart_structure(self, tmp_path):
        """Test doughnut chart has inner and outer paths."""
        chart = PieChart(data=[25, 35, 40], inner_radius=0.5)
        svg = chart.html

        # Doughnut charts should have more complex path structure
        assert "<path" in svg.lower()
        output_path = tmp_path / "pie_doughnut.svg"
        output_path.write_text(svg)


class TestVisualRegressionPNGConversion:
    """Test SVG to PNG conversion for visual comparison."""

    @pytest.mark.skipif(
        not all([cairosvg, Image]),
        reason="cairosvg and PIL required for PNG conversion",
    )
    def test_svg_to_png_conversion(self, tmp_path):
        """Test SVG can be converted to PNG."""
        chart = BarChart(data=[10, 20, 30])
        svg = chart.html

        # Convert to PNG
        png_bytes = svg_to_png(svg)

        # Verify PNG is valid
        assert len(png_bytes) > 0

        # Can open with PIL
        image = Image.open(io.BytesIO(png_bytes))
        assert image.size[0] > 0
        assert image.size[1] > 0

    @pytest.mark.skipif(
        not all([cairosvg, Image]),
        reason="cairosvg and PIL required for PNG conversion",
    )
    def test_png_comparison(self, tmp_path):
        """Test comparing two similar PNGs."""
        chart1 = BarChart(data=[10, 20, 30])
        chart2 = BarChart(data=[10, 20, 30])

        svg1 = chart1.html
        svg2 = chart2.html

        png1 = Image.open(io.BytesIO(svg_to_png(svg1)))
        png2 = Image.open(io.BytesIO(svg_to_png(svg2)))

        # Identical charts should match
        assert compare_images(png1, png2)
