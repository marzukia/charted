"""Tests for chart configuration objects.

These tests verify the config object pattern implementation
for Issue #76 (Design config object pattern for chart constructors).
"""

import pytest

from charted.chart_config import (
    BarChartConfig,
    ChartConfig,
    ColumnChartConfig,
    LineChartConfig,
    PieChartConfig,
    RadarChartConfig,
    ScatterChartConfig,
)


class TestChartConfig:
    """Tests for base ChartConfig class."""

    def test_default_values(self):
        """Test default values are set correctly."""
        config = ChartConfig()
        assert config.width == 500
        assert config.height == 500
        assert config.title is None
        assert config.render_axes is True
        assert config.zero_index is True

    def test_custom_values(self):
        """Test setting custom values."""
        config = ChartConfig(
            width=800,
            height=600,
            title="My Chart",
            render_axes=False
        )
        assert config.width == 800
        assert config.height == 600
        assert config.title == "My Chart"
        assert config.render_axes is False

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = ChartConfig(width=600, title="Test")
        result = config.to_dict()
        assert result["width"] == 600
        assert result["title"] == "Test"
        assert "height" in result

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {"width": 700, "title": "From Dict", "extra_field": "ignored"}
        config = ChartConfig.from_dict(data)
        assert config.width == 700
        assert config.title == "From Dict"

    def test_update(self):
        """Test update method for method chaining."""
        config = ChartConfig()
        result = config.update(width=600, title="Updated")
        assert config.width == 600
        assert config.title == "Updated"
        assert result is config  # Returns self

    def test_copy(self):
        """Test copy creates independent instance."""
        config1 = ChartConfig(width=600, title="Original")
        config2 = config1.copy()

        assert config2.width == 600
        assert config2.title == "Original"

        config2.width = 800
        assert config1.width == 600  # Original unchanged


class TestBarChartConfig:
    """Tests for BarChartConfig class."""

    def test_inherits_from_chart_config(self):
        """Test BarChartConfig inherits from ChartConfig."""
        config = BarChartConfig()
        assert isinstance(config, ChartConfig)

    def test_default_values(self):
        """Test default values."""
        config = BarChartConfig()
        assert config.bar_gap == 0.50
        assert config.x_stacked is False
        assert config.labels is None

    def test_custom_values(self):
        """Test setting custom values."""
        config = BarChartConfig(
            width=600,
            bar_gap=0.3,
            x_stacked=True,
            labels=['Q1', 'Q2', 'Q3']
        )
        assert config.width == 600
        assert config.bar_gap == 0.3
        assert config.x_stacked is True
        assert config.labels == ['Q1', 'Q2', 'Q3']


class TestColumnChartConfig:
    """Tests for ColumnChartConfig class."""

    def test_default_values(self):
        """Test default values."""
        config = ColumnChartConfig()
        assert config.column_gap == 0.20
        assert config.y_stacked is True
        assert config.labels is None

    def test_custom_values(self):
        """Test setting custom values."""
        config = ColumnChartConfig(
            column_gap=0.15,
            y_stacked=False,
            labels=['Jan', 'Feb', 'Mar']
        )
        assert config.column_gap == 0.15
        assert config.y_stacked is False
        assert config.labels == ['Jan', 'Feb', 'Mar']


class TestLineChartConfig:
    """Tests for LineChartConfig class."""

    def test_default_values(self):
        """Test default values."""
        config = LineChartConfig()
        assert config.line_style == "solid"
        assert config.marker_shape == "circle"
        assert config.marker_size == 4.0
        assert config.area_fill is False
        assert config.area_fill_opacity == 0.3

    def test_custom_values(self):
        """Test setting custom values."""
        config = LineChartConfig(
            line_style="dashed",
            marker_shape="square",
            marker_size=6.0,
            area_fill=True,
            area_fill_opacity=0.2
        )
        assert config.line_style == "dashed"
        assert config.marker_shape == "square"
        assert config.marker_size == 6.0
        assert config.area_fill is True
        assert config.area_fill_opacity == 0.2


class TestPieChartConfig:
    """Tests for PieChartConfig class."""

    def test_default_values(self):
        """Test default values."""
        config = PieChartConfig()
        assert config.inner_radius == 0.0
        assert config.explode == 0.0
        assert config.start_angle == 0.0

    def test_doughnut_chart(self):
        """Test doughnut chart configuration."""
        config = PieChartConfig(inner_radius=0.5)
        assert config.inner_radius == 0.5

    def test_explode_list(self):
        """Test explode with list of values."""
        config = PieChartConfig(explode=[10, 0, 0, 0])
        assert config.explode == [10, 0, 0, 0]

    def test_invalid_inner_radius(self):
        """Test validation of inner_radius."""
        with pytest.raises(ValueError, match="inner_radius"):
            PieChartConfig(inner_radius=1.5)

        with pytest.raises(ValueError, match="inner_radius"):
            PieChartConfig(inner_radius=-0.1)


class TestScatterChartConfig:
    """Tests for ScatterChartConfig class."""

    def test_default_values(self):
        """Test default values."""
        config = ScatterChartConfig()
        assert config.marker_shape == "circle"
        assert config.marker_size == 4.0

    def test_custom_values(self):
        """Test setting custom values."""
        config = ScatterChartConfig(
            marker_shape="diamond",
            marker_size=8.0
        )
        assert config.marker_shape == "diamond"
        assert config.marker_size == 8.0


class TestRadarChartConfig:
    """Tests for RadarChartConfig class."""

    def test_labels_required(self):
        """Test that labels are required."""
        with pytest.raises(ValueError, match="labels"):
            RadarChartConfig()

    def test_valid_config(self):
        """Test valid configuration."""
        config = RadarChartConfig(
            labels=['Speed', 'Power', 'Endurance'],
            radius=0.5,
            grid_levels=4
        )
        assert config.labels == ['Speed', 'Power', 'Endurance']
        assert config.radius == 0.5
        assert config.grid_levels == 4

    def test_invalid_radius(self):
        """Test validation of radius."""
        with pytest.raises(ValueError, match="radius"):
            RadarChartConfig(labels=['A', 'B'], radius=0)

        with pytest.raises(ValueError, match="radius"):
            RadarChartConfig(labels=['A', 'B'], radius=1.5)

    def test_invalid_grid_levels(self):
        """Test validation of grid_levels."""
        with pytest.raises(ValueError, match="grid_levels"):
            RadarChartConfig(labels=['A', 'B'], grid_levels=0)


class TestConfigInheritance:
    """Tests for config inheritance and composition."""

    def test_base_to_specific(self):
        """Test that specific configs inherit base fields."""
        config = BarChartConfig(width=600, bar_gap=0.3)
        assert config.width == 600  # From ChartConfig
        assert config.bar_gap == 0.3  # From BarChartConfig

    def test_copy_with_modifications(self):
        """Test copying and modifying configs."""
        base_config = BarChartConfig(
            width=600,
            title="Sales",
            bar_gap=0.3
        )

        modified = base_config.copy()
        modified.width = 800
        modified.title = "Revenue"

        assert base_config.width == 600
        assert base_config.title == "Sales"
        assert modified.width == 800
        assert modified.title == "Revenue"

    def test_update_chain(self):
        """Test method chaining with update."""
        config = (
            BarChartConfig()
            .update(width=600)
            .update(height=400)
            .update(title="Chained")
        )
        assert config.width == 600
        assert config.height == 400
        assert config.title == "Chained"


class TestConfigSerialization:
    """Tests for config serialization."""

    def test_round_trip(self):
        """Test serialization and deserialization."""
        original = BarChartConfig(
            width=600,
            height=400,
            title="Test",
            bar_gap=0.3,
            labels=['A', 'B', 'C']
        )

        data = original.to_dict()
        restored = BarChartConfig.from_dict(data)

        assert original.width == restored.width
        assert original.height == restored.height
        assert original.title == restored.title
        assert original.bar_gap == restored.bar_gap
        assert original.labels == restored.labels

    def test_from_dict_ignores_extra_fields(self):
        """Test that from_dict ignores unknown fields."""
        data = {
            "width": 600,
            "unknown_field": "should be ignored",
            "another_unknown": 123
        }
        config = BarChartConfig.from_dict(data)
        assert config.width == 600


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
