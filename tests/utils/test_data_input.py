"""Tests for charted.utils.data_input module.

Covers auto(), auto_size(), from_dict(), and from_dataframe().
"""

import pytest

from charted.utils.data_input import auto, auto_size, from_dataframe, from_dict


class TestAutoSize:
    """Tests for auto_size() function."""

    def test_explicit_width_height(self):
        """Explicit dimensions are returned as-is."""
        w, h = auto_size([1, 2, 3], width=800, height=600)
        assert w == 800
        assert h == 600

    def test_partial_width(self):
        """Only width provided, height auto-calculated."""
        w, h = auto_size([[1, 2, 3, 4, 5]], width=700)
        assert w == 700
        assert h >= 500

    def test_partial_height(self):
        """Only height provided, width auto-calculated."""
        w, h = auto_size([[1, 2, 3, 4, 5]], height=400)
        assert h == 400
        assert w >= 500

    def test_empty_list_returns_defaults(self):
        """Empty data list returns default dimensions."""
        w, h = auto_size([])
        assert w == 500
        assert h == 500

    def test_1d_list_single_row(self):
        """1D list: n_rows=1, n_cols=len(data)."""
        data = list(range(20))
        w, h = auto_size(data)
        assert w >= 500
        assert h >= 500

    def test_2d_list_scales_by_dimensions(self):
        """2D list scales by rows and columns."""
        data = [[float(i) for i in range(15)] for _ in range(10)]
        w, h = auto_size(data)
        assert w >= 15 * 50  # n_cols * 50
        assert h >= 10 * 50  # n_rows * 50

    def test_2d_with_empty_first_row(self):
        """First row empty: n_cols=0, uses default width."""
        data = [[], [1, 2, 3]]
        w, h = auto_size(data)
        assert w >= 500
        assert h >= 100

    def test_non_list_returns_defaults(self):
        """Non-list input returns defaults."""
        w, h = auto_size("not a list")
        assert w == 500
        assert h == 500

    def test_none_data_returns_defaults(self):
        """None data returns defaults."""
        w, h = auto_size(None)
        assert w == 500
        assert h == 500


class TestAuto:
    """Tests for auto() function."""

    def test_1d_list_small_creates_pie_chart(self):
        """1D list with <=6 items creates PieChart."""
        chart = auto([10, 20, 30], title="Pie")
        assert chart.__class__.__name__ == "PieChart"

    def test_1d_list_large_creates_bar_chart(self):
        """1D list with >6 items creates BarChart."""
        chart = auto(list(range(10)), title="Bar")
        assert chart.__class__.__name__ == "BarChart"

    def test_2d_few_rows_many_cols_creates_column_chart(self):
        """2D with <=3 rows, >3 cols creates ColumnChart."""
        chart = auto([[1, 2, 3, 4, 5]], title="Column")
        assert chart.__class__.__name__ == "ColumnChart"

    def test_2d_many_rows_few_cols_creates_line_chart(self):
        """2D with >3 rows, <=6 cols creates LineChart."""
        chart = auto(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]],
            title="Line",
        )
        assert chart.__class__.__name__ == "LineChart"

    def test_2d_squareish_creates_heatmap(self):
        """Square-ish 2D matrix creates HeatmapChart.

        n_rows > 3 and n_cols > 6 triggers the else branch -> HeatmapChart.
        """
        chart = auto(
            [
                [1, 2, 3, 4, 5, 6, 7],
                [5, 6, 7, 8, 9, 10, 11],
                [9, 10, 11, 12, 13, 14, 15],
                [13, 14, 15, 16, 17, 18, 19],
            ],
            title="Heatmap",
        )
        assert chart.__class__.__name__ == "HeatmapChart"

    def test_dict_data_uses_from_dataframe(self):
        """Dict input delegates to from_dataframe."""
        chart = auto({"x": [1, 2, 3], "y": [4, 5, 6]}, title="Dict")
        assert chart.__class__.__name__ == "BarChart"

    def test_empty_data_raises(self):
        """Empty data raises ValueError."""
        with pytest.raises(ValueError, match="Empty data"):
            auto([])

    def test_unsupported_type_raises(self):
        """Non-list/dict input raises TypeError."""
        with pytest.raises(TypeError, match="Unsupported"):
            auto("string")

    def test_auto_size_applied_when_no_dimensions(self):
        """Auto-sizing applied when width/height not in kwargs."""
        chart = auto([10, 20, 30])
        assert chart.width >= 500
        assert chart.height >= 500


class TestFromDict:
    """Tests for from_dict() function."""

    def test_basic_dict(self):
        """Basic dict config creates expected chart."""
        cfg = {
            "chart_type": "LineChart",
            "data": {"x_labels": ["A", "B", "C"], "series": [[10, 20, 30]]},
            "title": "Test",
        }
        chart = from_dict(cfg)
        assert chart.__class__.__name__ == "LineChart"

    def test_no_chart_type_defaults_to_bar(self):
        """No chart_type key defaults to BarChart."""
        cfg = {"data": [10, 20, 30], "title": "Default"}
        chart = from_dict(cfg)
        assert chart.__class__.__name__ == "BarChart"

    def test_kwargs_override(self):
        """Kwargs override dict values."""
        cfg = {
            "chart_type": "LineChart",
            "data": [1, 2, 3],
            "title": "Original",
        }
        chart = from_dict(cfg, title="Override")
        assert chart._title.text == "Override"

    def test_dict_data_flattened(self):
        """Dict-style data flattens x_labels and series."""
        cfg = {
            "chart_type": "ColumnChart",
            "data": {
                "x_labels": ["A", "B"],
                "series": [[10, 20]],
            },
        }
        chart = from_dict(cfg)
        assert chart.__class__.__name__ == "ColumnChart"

    def test_invalid_chart_type_uses_default(self):
        """Unknown chart_type falls back to default (BarChart)."""
        cfg = {"chart_type": "NonExistent", "data": [1, 2, 3]}
        chart = from_dict(cfg)
        assert chart.__class__.__name__ == "BarChart"

    def test_dict_data_with_series_mapped_to_y_data(self):
        """Dict data with series mapped to y_data when data param missing."""
        cfg = {
            "chart_type": "BarChart",
            "data": {
                "x_labels": ["A", "B"],
                "series": [[10, 20]],
            },
        }
        chart = from_dict(cfg)
        assert chart.__class__.__name__ == "BarChart"


class TestFromDataFrame:
    """Tests for from_dataframe() function."""

    def test_dict_fallback(self):
        """Dict input creates chart from column data."""
        data = {"value": [10, 20, 30], "score": [5, 6, 7]}
        chart = from_dataframe(data, title="Dict DF")
        assert chart.__class__.__name__ == "BarChart"

    def test_empty_dict_raises(self):
        """Empty dict raises ValueError."""
        with pytest.raises(ValueError, match="Empty dict"):
            from_dataframe({})

    def test_dict_no_chart_type_defaults_to_bar(self):
        """Dict without chart_type defaults to BarChart."""
        data = {"col": [1, 2, 3]}
        chart = from_dataframe(data)
        assert chart.__class__.__name__ == "BarChart"

    def test_dict_with_chart_type(self):
        """Dict with explicit chart_type creates correct chart."""
        data = {"col": [1, 2, 3]}
        chart = from_dataframe(data, chart_type="ColumnChart")
        assert chart.__class__.__name__ == "ColumnChart"

    def test_invalid_chart_type_uses_default(self):
        """Unknown chart_type falls back to BarChart."""
        data = {"col": [1, 2, 3]}
        chart = from_dataframe(data, chart_type="NonExistent")
        assert chart.__class__.__name__ == "BarChart"

    def test_non_dict_non_dataframe_raises(self):
        """Non-dict, non-DataFrame input raises TypeError."""
        with pytest.raises(TypeError, match="Expected"):
            from_dataframe("not a dict")

    def test_kwargs_forwarded_to_chart(self):
        """Extra kwargs matching chart params are forwarded."""
        data = {"col": [1, 2, 3]}
        chart = from_dataframe(data, chart_type="BarChart", title="Kwargs Test")
        assert chart._title.text == "Kwargs Test"

    def test_dict_labels_param_mapping(self):
        """Dict with labels param mapped correctly."""
        data = {"col": [1, 2, 3]}
        chart = from_dataframe(data, chart_type="ColumnChart")
        assert chart.__class__.__name__ == "ColumnChart"
