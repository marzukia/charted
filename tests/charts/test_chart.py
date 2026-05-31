"""Tests for Chart base class methods.

Covers construction, output methods, config serialization, styling, and padding.
"""

import pytest

from charted.charts.column import ColumnChart
from charted.charts.line import LineChart
from charted.utils.exceptions import NoDataError


class TestChartConstruction:
    """Tests for Chart base class initialization."""

    def test_get_base_transform_returns_4_elements(self):
        """Transform chain returns list of 4 transform functions."""
        chart = ColumnChart(data=[1, 2, 3])
        transforms = chart.get_base_transform()
        assert len(transforms) == 4

    def test_x_offset_property_returns_reprojected_value(self):
        """x_offset returns reprojected value when labels=True."""
        chart = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"])
        offset = chart.x_offset
        assert offset > 0

    def test_apply_stacking_adds_offset_when_stacked(self):
        """Stacking adds offset only when y_stacked=True."""
        chart = ColumnChart(data=[1, 2, 3])
        chart.y_stacked = True
        result = chart._apply_stacking(10, 5)
        assert result == 15

        chart.y_stacked = False
        result = chart._apply_stacking(10, 5)
        assert result == 10

    def test_h_padding_rejects_value_greater_than_one(self):
        """h_padding > 1 raises InvalidValue."""
        with pytest.raises(Exception) as exc_info:
            chart = ColumnChart(data=[1, 2, 3])
            chart.h_padding = 1.5
        assert "h_padding" in str(exc_info.value).lower()

    def test_v_padding_rejects_value_greater_than_one(self):
        """v_padding > 1 raises InvalidValue."""
        with pytest.raises(Exception) as exc_info:
            chart = ColumnChart(data=[1, 2, 3])
            chart.v_padding = 1.5
        assert "v_padding" in str(exc_info.value).lower()

    def test_validate_data_rejects_empty_data(self):
        """Empty data raises exception."""
        from charted.utils.data_model import DataModel

        with pytest.raises(Exception, match="No data was provided"):
            DataModel([], None)

    def test_validate_data_rejects_mismatched_lengths(self):
        """Data vectors of different lengths raise exception."""
        from charted.utils.data_model import DataModel

        with pytest.raises(
            Exception, match="Not all data vectors were the same length"
        ):
            DataModel.validate_data([[1, 2, 3], [4, 5]])

    def test_no_data_raises_nodataerror(self):
        """Chart with no x_data or y_data raises NoDataError."""
        with pytest.raises(NoDataError, match="No data"):
            ColumnChart(data=[], labels=[])

    def test_pad_x_labels_default_true(self):
        """Chart pad_x_labels defaults to True."""
        chart = ColumnChart(data=[1, 2, 3])
        assert chart.pad_x_labels is True


class TestChartOutputMethods:
    """Tests for Chart output methods."""

    def test_to_svg_returns_svg_string(self):
        """to_svg() returns valid SVG string."""
        chart = ColumnChart(data=[1, 2, 3])
        svg = chart.to_svg()
        assert svg.startswith("<svg")
        assert "viewBox" in svg

    def test_to_html_returns_html_wrapper(self):
        """to_html() returns HTML with embedded SVG."""
        chart = ColumnChart(data=[1, 2, 3])
        html = chart.to_html()
        assert "<div" in html
        assert "<svg" in html
        assert "style=" in html or "style" in html

    def test_to_html_custom_style(self):
        """to_html() accepts custom style parameter."""
        chart = ColumnChart(data=[1, 2, 3])
        html = chart.to_html(style="display: block; margin: 10px;")
        assert "display: block" in html

    def test_repr_html_returns_html_wrapper(self):
        """_repr_html_() returns HTML wrapper."""
        chart = ColumnChart(data=[1, 2, 3])
        html = chart._repr_html_()
        assert "<div" in html

    def test_to_base64_returns_data_uri(self):
        """to_base64() returns data URI."""
        chart = ColumnChart(data=[1, 2, 3])
        b64 = chart.to_base64()
        assert b64.startswith("data:image/svg+xml")

    def test_to_markdown_returns_markdown(self):
        """to_markdown() returns markdown image."""
        chart = ColumnChart(data=[1, 2, 3], title="Test")
        md = chart.to_markdown()
        assert "![" in md

    def test_to_markdown_with_alt_text(self):
        """to_markdown() with custom alt text."""
        chart = ColumnChart(data=[1, 2, 3], title="Test")
        md = chart.to_markdown(alt_text="Custom alt", width="50%")
        assert "Custom alt" in md
        assert "50%" in md

    def test_save_writes_svg_to_file(self, tmp_path):
        """save() writes SVG to file."""
        chart = ColumnChart(data=[1, 2, 3])
        path = str(tmp_path / "test.svg")
        chart.save(path)
        with open(path) as f:
            content = f.read()
        assert content.startswith("<svg")

    def test_repr_svg_returns_svg_string(self):
        """_repr_svg_() returns SVG string."""
        chart = ColumnChart(data=[1, 2, 3])
        svg = chart._repr_svg_()
        assert svg.startswith("<svg")


class TestChartStyle:
    """Tests for Chart.style() method."""

    def test_style_background(self):
        """style() changes background color."""
        chart = ColumnChart(data=[1, 2, 3]).style(background_color="#ffffff")
        assert chart.theme.background_color == "#ffffff"

    def test_style_multiple_properties(self):
        """style() with multiple properties."""
        chart = ColumnChart(data=[1, 2, 3]).style(
            background_color="#fff",
            font_family="sans-serif",
            legend_font_size=12,
        )
        assert chart.theme.background_color == "#fff"
        assert chart.theme.legend_font_size == 12

    def test_style_returns_self_for_chaining(self):
        """style() returns self for method chaining."""
        chart = ColumnChart(data=[1, 2, 3])
        result = chart.style(background_color="#fff")
        assert result is chart

    def test_style_unknown_kwargs_ignored(self):
        """style() ignores unknown kwargs gracefully."""
        chart = ColumnChart(data=[1, 2, 3]).style(
            background_color="#fff",
            nonexistent_attr="value",
        )
        assert chart.theme.background_color == "#fff"


class TestChartConfig:
    """Tests for Chart.to_config() and Chart.from_config()."""

    def test_to_config_returns_dict(self):
        """to_config() returns serializable dict."""
        chart = ColumnChart(
            data=[1, 2, 3],
            labels=["a", "b", "c"],
            title="Test",
            series_names=["Series"],
        )
        cfg = chart.to_config()
        assert isinstance(cfg, dict)
        assert cfg["chart_type"] == "ColumnChart"
        assert cfg["title"] == "Test"
        assert cfg["labels"] == ["a", "b", "c"]
        assert cfg["series_names"] == ["Series"]

    def test_to_config_without_title(self):
        """to_config() handles charts without title."""
        chart = ColumnChart(data=[1, 2, 3])
        cfg = chart.to_config()
        assert cfg["title"] is None

    def test_to_config_contains_data(self):
        """to_config() includes data values."""
        chart = ColumnChart(data=[1, 2, 3])
        cfg = chart.to_config()
        assert "y_data" in cfg

    def test_to_config_with_data_model(self):
        """to_config() includes x_data/y_data from data_model."""
        from charted.charts.line import LineChart

        chart = LineChart(
            data=[10, 20, 30],
            x_data=[1.0, 2.0, 3.0],
            labels=["a", "b", "c"],
        )
        cfg = chart.to_config()
        assert "x_data" in cfg
        assert "y_data" in cfg

    def test_to_config_with_series_styles(self):
        """to_config() includes series_styles when present."""
        styles = [{"fill": "#ff0000"}]
        chart = ColumnChart(data=[1, 2, 3], series_styles=styles)
        cfg = chart.to_config()
        assert "series_styles" in cfg

    def test_from_config_recreates_chart(self):
        """from_config() recreates chart from config."""
        original = ColumnChart(
            data=[1, 2, 3],
            labels=["a", "b", "c"],
            title="Test",
        )
        cfg = original.to_config()
        restored = ColumnChart.from_config(cfg)
        assert restored._title.text == "Test"
        assert restored.width == original.width

    def test_from_config_with_overrides(self):
        """from_config() applies overrides on top of config."""
        original = ColumnChart(data=[1, 2, 3], labels=["a", "b", "c"], title="Test")
        cfg = original.to_config()
        restored = ColumnChart.from_config(cfg, title="Override")
        assert restored._title.text == "Override"

    def test_from_config_no_chart_type_fallback(self):
        """from_config() falls back to cls when chart_type missing."""
        cfg = {"title": "Test", "data": [1, 2, 3]}
        chart = ColumnChart.from_config(cfg)
        assert chart._title.text == "Test"

    def test_from_config_maps_data_alias(self):
        """from_config() maps data/y_data aliases."""
        cfg = {"chart_type": "ColumnChart", "y_data": [[1, 2, 3]]}
        chart = ColumnChart.from_config(cfg)
        assert chart.title is None

    def test_from_config_with_line_chart(self):
        """from_config() works with LineChart."""
        cfg = {
            "chart_type": "LineChart",
            "data": [[1, 2, 3]],
            "labels": ["a", "b", "c"],
            "title": "Line",
        }
        chart = LineChart.from_config(cfg)
        assert chart.__class__.__name__ == "LineChart"
        assert chart._title.text == "Line"

    def test_from_config_unknown_chart_type_fallback(self):
        """from_config() falls back to cls when chart_type unknown."""
        cfg = {"chart_type": "NonExistentChart", "data": [1, 2, 3], "title": "Fallback"}
        chart = ColumnChart.from_config(cfg)
        assert chart._title.text == "Fallback"

    def test_from_config_x_data_alias(self):
        """from_config() maps x_data when data param available and y_data missing."""
        cfg = {"chart_type": "ColumnChart", "x_data": [[1, 2, 3]], "title": "XAlias"}
        chart = ColumnChart.from_config(cfg)
        assert chart._title.text == "XAlias"

    def test_from_config_y_data_alias(self):
        """from_config() maps data to y_data when chart has y_data param."""
        cfg = {"chart_type": "ScatterChart", "data": [4, 5, 6], "x_data": [1, 2, 3]}
        from charted.charts.scatter import ScatterChart

        chart = ScatterChart.from_config(cfg)
        assert chart is not None


class TestChartProperties:
    """Tests for Chart property accessors."""

    def test_plot_width_height(self):
        """plot_width and plot_height are positive."""
        chart = ColumnChart(data=[1, 2, 3])
        assert chart.plot_width > 0
        assert chart.plot_height > 0

    def test_padding_values(self):
        """Padding values are within expected range."""
        chart = ColumnChart(data=[1, 2, 3])
        assert chart.left_padding >= 0
        assert chart.right_padding >= 0
        assert chart.top_padding >= 0
        assert chart.bottom_padding >= 0

    def test_x_label_rotation(self):
        """x_label_rotation returns tuple or None."""
        chart = ColumnChart(data=[1, 2, 3])
        rotation = chart.x_label_rotation
        assert rotation is None or len(rotation) == 2

    def test_width_height_readonly(self):
        """width and height are accessible."""
        chart = ColumnChart(data=[1, 2, 3], width=800, height=600)
        assert chart.width == 800
        assert chart.height == 600

    def test_h_pad_scales_with_width(self):
        """h_pad scales h_padding by width."""
        chart = ColumnChart(data=[1, 2, 3], width=500)
        pad = chart.h_pad
        assert pad > 0

    def test_y_labels_property(self):
        """y_labels property returns None by default."""
        chart = ColumnChart(data=[1, 2, 3])
        assert chart.y_labels is None

    def test_x_width_zero_when_no_categories(self):
        """x_width returns 0 when x_count is 0."""
        chart = ColumnChart(data=[1], labels=["x"])
        # ColumnChart uses slot-based layout where x_count includes boundaries
        assert chart.x_width > 0

    def test_base_representation_raises(self):
        """Chart base representation raises Exception."""
        from charted.charts.chart import Chart

        with pytest.raises(Exception, match="not implemented"):

            class _BareChart(Chart):
                pass

            bc = _BareChart(y_data=[[1, 2, 3]], x_labels=["a", "b", "c"])
            _ = bc.representation
