"""Tests for markdown utilities."""

import pytest

from charted import chart_to_data_url, chart_to_markdown, inline_svg


class TestChartToMarkdown:
    """Tests for the chart_to_markdown function."""

    def test_basic_markdown(self, tmp_path):
        """Test basic markdown generation."""
        svg_file = tmp_path / "chart.svg"
        svg_file.write_text("<svg>test</svg>")

        md = chart_to_markdown(svg_file)

        assert md == f"![Chart]({svg_file})"

    def test_markdown_with_title(self, tmp_path):
        """Test markdown with custom title."""
        svg_file = tmp_path / "chart.svg"
        svg_file.write_text("<svg>test</svg>")

        md = chart_to_markdown(svg_file, title="Sales Chart")

        assert md == f"![Sales Chart]({svg_file})"

    def test_markdown_with_width(self, tmp_path):
        """Test markdown with width specification."""
        svg_file = tmp_path / "chart.svg"
        svg_file.write_text("<svg>test</svg>")

        md = chart_to_markdown(svg_file, width="600px")

        assert md == f"![Chart]({svg_file}){{width=600px}}"

    def test_markdown_with_relative_path(self, tmp_path):
        """Test markdown with relative path."""
        svg_file = tmp_path / "docs" / "examples" / "chart.svg"
        svg_file.parent.mkdir(parents=True)
        svg_file.write_text("<svg>test</svg>")

        md = chart_to_markdown(svg_file, relative_path="docs/examples/chart.svg")

        assert md == "![Chart](docs/examples/chart.svg)"

    def test_markdown_filename_to_title(self, tmp_path):
        """Test that filename is converted to title."""
        svg_file = tmp_path / "sales_by_quarter.svg"
        svg_file.write_text("<svg>test</svg>")

        md = chart_to_markdown(svg_file)

        assert md == f"![Sales By Quarter]({svg_file})"

    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            chart_to_markdown("/nonexistent/chart.svg")


class TestInlineSvg:
    """Tests for the inline_svg function."""

    def test_inline_svg_basic(self, tmp_path):
        """Test basic SVG inline."""
        svg_file = tmp_path / "chart.svg"
        expected = "<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>"
        svg_file.write_text(expected)

        result = inline_svg(svg_file)

        assert result == expected

    def test_inline_svg_multiline(self, tmp_path):
        """Test multiline SVG inline."""
        svg_file = tmp_path / "chart.svg"
        expected = """<svg xmlns='http://www.w3.org/2000/svg'>
  <rect x='0' y='0' width='100' height='100'/>
  <circle cx='50' cy='50' r='25'/>
</svg>"""
        svg_file.write_text(expected)

        result = inline_svg(svg_file)

        assert result == expected

    def test_inline_svg_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            inline_svg("/nonexistent/chart.svg")


class TestChartToDataUrl:
    """Tests for the chart_to_data_url function."""

    def test_data_url_basic(self, tmp_path):
        """Test basic data URL generation."""
        svg_file = tmp_path / "chart.svg"
        svg_file.write_text("<svg>test</svg>")

        url = chart_to_data_url(svg_file)

        assert url.startswith("data:image/svg+xml,")
        assert "test" in url

    def test_data_url_encoded(self, tmp_path):
        """Test that special characters are encoded."""
        svg_file = tmp_path / "chart.svg"
        svg_file.write_text("<svg><text>Hello World</text></svg>")

        url = chart_to_data_url(svg_file)

        assert url.startswith("data:image/svg+xml,")
        # Space should be encoded
        assert " " not in url.split(",")[1]

    def test_data_url_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            chart_to_data_url("/nonexistent/chart.svg")
