"""Tests for Chart.save() with PNG output via extension detection."""

from unittest.mock import patch

import pytest

from charted.charts.column import ColumnChart


@pytest.fixture
def chart():
    """Simple chart for save tests."""
    return ColumnChart(data=[10, 20, 30], labels=["A", "B", "C"])


class TestSaveSVG:
    """Regression tests: .save() still works for SVG files."""

    def test_save_svg_creates_file(self, chart, tmp_path):
        path = tmp_path / "chart.svg"
        chart.save(str(path))
        assert path.exists()
        content = path.read_text()
        assert content.startswith("<svg")

    def test_save_svg_uppercase_extension(self, chart, tmp_path):
        path = tmp_path / "chart.SVG"
        chart.save(str(path))
        assert path.exists()
        content = path.read_text()
        assert "<svg" in content

    def test_save_svg_mixed_case(self, chart, tmp_path):
        path = tmp_path / "chart.Svg"
        chart.save(str(path))
        assert path.exists()


class TestSavePNG:
    """Tests for PNG output via cairosvg."""

    def test_save_png_produces_valid_png(self, chart, tmp_path):
        pytest.importorskip("cairosvg")
        path = tmp_path / "chart.png"
        chart.save(str(path))
        assert path.exists()
        # Check PNG magic bytes
        data = path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_save_png_uppercase_extension(self, chart, tmp_path):
        pytest.importorskip("cairosvg")
        path = tmp_path / "chart.PNG"
        chart.save(str(path))
        assert path.exists()
        data = path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_save_png_raises_import_error_without_cairosvg(self, chart, tmp_path):
        path = tmp_path / "chart.png"
        with patch.dict("sys.modules", {"cairosvg": None}):
            with pytest.raises(ImportError, match="pip install cairosvg"):
                chart.save(str(path))

    def test_save_png_scale_parameter(self, chart, tmp_path):
        pytest.importorskip("cairosvg")
        path_1x = tmp_path / "chart_1x.png"
        path_3x = tmp_path / "chart_3x.png"
        chart.save(str(path_1x), scale=1)
        chart.save(str(path_3x), scale=3)
        # 3x should produce a larger file than 1x
        assert path_3x.stat().st_size > path_1x.stat().st_size

    def test_save_png_default_scale_is_2(self, chart, tmp_path):
        pytest.importorskip("cairosvg")
        path = tmp_path / "chart.png"
        with patch("cairosvg.svg2png") as mock_svg2png:
            mock_svg2png.return_value = b"\x89PNG\r\n\x1a\n"
            chart.save(str(path))
            mock_svg2png.assert_called_once()
            _, kwargs = mock_svg2png.call_args
            assert kwargs["scale"] == 2


class TestSaveExtensionDetection:
    """Tests for extension detection and unsupported formats."""

    def test_unsupported_extension_raises_value_error(self, chart, tmp_path):
        path = tmp_path / "chart.pdf"
        with pytest.raises(ValueError, match="Unsupported file extension"):
            chart.save(str(path))

    def test_unsupported_extension_jpg(self, chart, tmp_path):
        path = tmp_path / "chart.jpg"
        with pytest.raises(ValueError, match="Unsupported file extension"):
            chart.save(str(path))

    def test_no_extension_raises_value_error(self, chart, tmp_path):
        path = tmp_path / "chartfile"
        with pytest.raises(ValueError, match="Unsupported file extension"):
            chart.save(str(path))
