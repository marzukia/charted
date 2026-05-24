"""Tests for the MCP server tools.

Tests the tool handler functions directly without MCP transport.
"""

import pytest

from mcp_server.tools import (
    handle_chart_from_csv,
    handle_create_chart,
    handle_list_chart_types,
    handle_list_themes,
)


class TestCreateChart:
    """Tests for the create_chart tool."""

    def test_bar_chart_svg(self):
        result = handle_create_chart(
            chart_type="bar",
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="Test Bar",
        )
        assert "<svg" in result
        assert "</svg>" in result

    def test_column_chart_svg(self):
        result = handle_create_chart(
            chart_type="column",
            data=[5, 15, 25, 35],
            labels=["Q1", "Q2", "Q3", "Q4"],
        )
        assert "<svg" in result

    def test_line_chart_svg(self):
        result = handle_create_chart(
            chart_type="line",
            data=[[1, 2, 3, 4], [4, 3, 2, 1]],
            labels=["A", "B", "C", "D"],
            series_names=["Up", "Down"],
        )
        assert "<svg" in result

    def test_pie_chart_svg(self):
        result = handle_create_chart(
            chart_type="pie",
            data=[40, 30, 20, 10],
            labels=["A", "B", "C", "D"],
        )
        assert "<svg" in result

    def test_scatter_chart_svg(self):
        result = handle_create_chart(
            chart_type="scatter",
            data=[[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]],
        )
        assert "<svg" in result

    def test_area_chart_svg(self):
        result = handle_create_chart(
            chart_type="area",
            data=[10, 20, 15, 25, 30],
            labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
        )
        assert "<svg" in result

    def test_radar_chart_svg(self):
        result = handle_create_chart(
            chart_type="radar",
            data=[80, 90, 70, 60, 85],
            labels=["Speed", "Power", "Range", "Armor", "Magic"],
        )
        assert "<svg" in result

    def test_histogram_chart_svg(self):
        result = handle_create_chart(
            chart_type="histogram",
            data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
        )
        assert "<svg" in result

    def test_heatmap_chart_svg(self):
        result = handle_create_chart(
            chart_type="heatmap",
            data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        )
        assert "<svg" in result

    def test_output_format_html(self):
        result = handle_create_chart(
            chart_type="bar",
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            output_format="html",
        )
        assert "<html" in result.lower() or "<div" in result.lower()
        assert "<svg" in result

    def test_output_format_data_url(self):
        result = handle_create_chart(
            chart_type="bar",
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            output_format="data_url",
        )
        assert result.startswith("data:image/svg+xml,")

    def test_custom_dimensions(self):
        result = handle_create_chart(
            chart_type="bar",
            data=[10, 20],
            labels=["A", "B"],
            width=800,
            height=600,
        )
        assert "<svg" in result

    def test_theme_string(self):
        result = handle_create_chart(
            chart_type="bar",
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            theme="dark",
        )
        assert "<svg" in result

    def test_auto_chart_type(self):
        result = handle_create_chart(
            chart_type="auto",
            data=[10, 20, 30, 40, 50, 60, 70],
        )
        assert "<svg" in result

    def test_auto_chart_type_2d(self):
        result = handle_create_chart(
            chart_type="auto",
            data=[[1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1]],
            labels=["A", "B", "C", "D", "E", "F"],
            series_names=["Series 1", "Series 2"],
        )
        assert "<svg" in result

    def test_save_path(self, tmp_path):
        save_file = str(tmp_path / "test_chart.svg")
        result = handle_create_chart(
            chart_type="bar",
            data=[10, 20, 30],
            labels=["A", "B", "C"],
            save_path=save_file,
        )
        assert "<svg" in result
        with open(save_file) as f:
            content = f.read()
        assert "<svg" in content

    def test_invalid_chart_type(self):
        with pytest.raises((ValueError, KeyError)):
            handle_create_chart(
                chart_type="nonexistent",
                data=[1, 2, 3],
            )

    def test_empty_data(self):
        with pytest.raises((ValueError, TypeError)):
            handle_create_chart(
                chart_type="bar",
                data=[],
            )


class TestListChartTypes:
    """Tests for the list_chart_types tool."""

    def test_returns_list(self):
        result = handle_list_chart_types()
        assert isinstance(result, list)

    def test_contains_expected_types(self):
        result = handle_list_chart_types()
        type_names = [item["type"] for item in result]
        expected = ["bar", "column", "line", "scatter", "pie", "radar", "area"]
        for t in expected:
            assert t in type_names

    def test_each_entry_has_required_keys(self):
        result = handle_list_chart_types()
        for entry in result:
            assert "type" in entry
            assert "description" in entry


class TestListThemes:
    """Tests for the list_themes tool."""

    def test_returns_dict(self):
        result = handle_list_themes()
        assert isinstance(result, dict)

    def test_has_presets(self):
        result = handle_list_themes()
        assert "presets" in result
        assert isinstance(result["presets"], list)
        assert len(result["presets"]) > 0

    def test_has_palettes(self):
        result = handle_list_themes()
        assert "palettes" in result
        assert isinstance(result["palettes"], list)
        assert "default" in result["palettes"]
        assert "viridis" in result["palettes"]


class TestChartFromCsv:
    """Tests for the chart_from_csv tool."""

    def test_simple_csv(self):
        csv_data = "Name,Value\nAlpha,10\nBeta,20\nGamma,30"
        result = handle_chart_from_csv(csv_data=csv_data, chart_type="bar")
        assert "<svg" in result

    def test_multi_series_csv(self):
        csv_data = "Month,Revenue,Costs\nJan,120,80\nFeb,340,210\nMar,560,390"
        result = handle_chart_from_csv(
            csv_data=csv_data, chart_type="line", title="Financials"
        )
        assert "<svg" in result

    def test_auto_type_csv(self):
        csv_data = "Category,Value\nA,10\nB,20\nC,30\nD,40\nE,50"
        result = handle_chart_from_csv(csv_data=csv_data)
        assert "<svg" in result

    def test_csv_with_output_format(self):
        csv_data = "X,Y\n1,10\n2,20\n3,30"
        result = handle_chart_from_csv(
            csv_data=csv_data, chart_type="column", output_format="data_url"
        )
        assert result.startswith("data:image/svg+xml,")

    def test_csv_x_column_specified(self):
        csv_data = "Month,Revenue,Costs\nJan,120,80\nFeb,340,210\nMar,560,390"
        result = handle_chart_from_csv(
            csv_data=csv_data,
            chart_type="bar",
            x_column="Month",
            y_columns=["Revenue"],
        )
        assert "<svg" in result

    def test_empty_csv_raises(self):
        with pytest.raises((ValueError, Exception)):
            handle_chart_from_csv(csv_data="", chart_type="bar")

    def test_invalid_csv_raises(self):
        with pytest.raises((ValueError, Exception)):
            handle_chart_from_csv(csv_data="no-header-single-word", chart_type="bar")
