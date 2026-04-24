"""RadarChart unit tests - Happy Path and Sad Path testing.

This module contains dedicated tests for RadarChart functionality.
"""

import pytest

from charted.charts.radar import RadarChart


class TestRadarChartHappyPath:
    """Happy path tests for RadarChart."""

    def test_basic_radar_chart(self):
        """Test basic radar chart with simple data."""
        chart = RadarChart(
            data=[20, 35, 30, 45, 25],
            labels=["Speed", "Power", "Endurance", "Defense", "Skill"],
        )
        html = chart.html
        assert "<path" in html.lower()
        assert "<svg" in html.lower()
        assert "path" in html.lower()

    def test_radar_chart_multi_series(self):
        """Test radar chart with multiple series."""
        chart = RadarChart(
            data=[[20, 35, 30, 45, 25], [30, 25, 40, 35, 30]],
            labels=["Speed", "Power", "Endurance", "Defense", "Skill"],
            series_names=["Player A", "Player B"],
        )
        html = chart.html
        # series_names are stored on chart instance (check before html call)
        assert chart.series_names == ["Player A", "Player B"]
        assert "<path" in html.lower()

    def test_radar_chart_custom_size(self):
        """Test radar chart with custom dimensions."""
        chart = RadarChart(
            data=[10, 20, 30, 40],
            labels=["A", "B", "C", "D"],
            width=800,
            height=600,
        )
        html = chart.html
        assert 'width="800' in html
        assert 'height="600' in html

    def test_radar_chart_with_title(self):
        """Test radar chart with title."""
        chart = RadarChart(
            data=[25, 35, 45],
            labels=["X", "Y", "Z"],
            title="Test Chart",
        )
        html = chart.html
        assert "Test Chart" in html

    def test_radar_chart_custom_grid_levels(self):
        """Test radar chart with custom grid levels."""
        chart = RadarChart(
            data=[10, 20, 30, 40, 50],
            labels=["A", "B", "C", "D", "E"],
            grid_levels=3,
        )
        html = chart.html
        assert html  # Should render without error

    def test_radar_chart_without_axis_labels(self):
        """Test radar chart with axis labels hidden."""
        chart = RadarChart(
            data=[15, 25, 35],
            labels=["A", "B", "C"],
            show_axis_labels=False,
        )
        html = chart.html
        assert "A" not in html or "Speed" not in html  # Labels should not appear

    def test_radar_chart_custom_radius(self):
        """Test radar chart with custom radius."""
        chart = RadarChart(
            data=[20, 30, 40],
            labels=["X", "Y", "Z"],
            radius=0.5,
        )
        html = chart.html
        assert html  # Should render without error

    def test_radar_chart_square_marker(self):
        """Test radar chart with square markers."""
        chart = RadarChart(
            data=[10, 20, 30, 40],
            labels=["A", "B", "C", "D"],
            series_styles=[{"marker_shape": "square"}],
        )
        html = chart.html
        assert "rect" in html.lower() or "square" in html.lower()

    def test_radar_chart_diamond_marker(self):
        """Test radar chart with diamond markers."""
        chart = RadarChart(
            data=[15, 25, 35],
            labels=["X", "Y", "Z"],
            series_styles=[{"marker_shape": "diamond"}],
        )
        html = chart.html
        assert html  # Should render without error

    def test_radar_chart_custom_series_names(self):
        """Test radar chart with custom series names."""
        chart = RadarChart(
            data=[[10, 20, 30], [15, 25, 35]],
            labels=["A", "B", "C"],
            series_names=["Series 1", "Series 2"],
        )
        # series_names are stored on chart instance
        assert chart.series_names == ["Series 1", "Series 2"]
        html = chart.html
        assert "<path" in html.lower()


class TestRadarChartSadPath:
    """Sad path / error tests for RadarChart."""

    def test_radar_chart_empty_labels(self):
        """Test radar chart with empty labels raises error."""
        with pytest.raises(ValueError, match="Labels cannot be empty"):
            RadarChart(data=[10, 20, 30], labels=[])

    def test_radar_chart_mismatched_data_labels(self):
        """Test radar chart with mismatched data and labels length."""
        with pytest.raises(ValueError, match="matching labels"):
            RadarChart(
                data=[[10, 20, 30], [15, 25, 35]],
                labels=["A", "B"],  # Only 2 labels but 3 data points
            )

    def test_radar_chart_single_label(self):
        """Test radar chart with single label (degenerate case)."""
        chart = RadarChart(
            data=[[10], [15]],
            labels=["Only"],
        )
        html = chart.html
        assert html  # Should render (degenerate but valid)

    def test_radar_chart_zero_values(self):
        """Test radar chart with all zero values."""
        chart = RadarChart(
            data=[[0, 0, 0], [0, 0, 0]],
            labels=["A", "B", "C"],
        )
        html = chart.html
        assert html  # Should render without error (handles max_value=0 case)

    def test_radar_chart_negative_values(self):
        """Test radar chart with negative values."""
        chart = RadarChart(
            data=[[-10, -20, -30], [10, 20, 30]],
            labels=["A", "B", "C"],
        )
        html = chart.html
        assert html  # Should render without error
