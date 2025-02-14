"""Tests for config loading and helpers."""

import tempfile
from pathlib import Path

from charted.config import (
    find_config,
    get_bar_gap,
    get_chart_theme,
    get_column_gap,
    get_font,
    get_font_definitions_dir,
    get_pie_label_font_size,
    get_title_font,
    load_config,
)


class TestFindConfig:
    """Test config file discovery."""

    def test_find_config_in_current_dir(self):
        """Test finding config in current directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text('[font]\nfamily = "Arial"')

            result = find_config(tmpdir)
            assert result == config_path

    def test_find_config_uploads_directory(self):
        """Test finding config by searching upward."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config in parent
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text('[font]\nfamily = "Arial"')

            # Create subdirectory
            subdir = Path(tmpdir) / "subdir" / "nested"
            subdir.mkdir(parents=True)

            result = find_config(str(subdir))
            assert result == config_path

    def test_find_config_not_found(self):
        """Test returning None when no config exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_config(tmpdir)
            assert result is None

    def test_find_config_prefers_toml(self):
        """Test that .chartedrc.toml is preferred over .chartedrc."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both files
            toml_config = Path(tmpdir) / ".chartedrc.toml"
            toml_config.write_text('[font]\nfamily = "Arial"')

            classic_config = Path(tmpdir) / ".chartedrc"
            classic_config.write_text('[font]\nfamily = "Helvetica"')

            result = find_config(tmpdir)
            # Should find .chartedrc.toml first
            assert result == toml_config


class TestLoadConfig:
    """Test config loading."""

    def test_load_config_from_file(self):
        """Test loading config from explicit file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text('[font]\nfamily = "Arial"\nsize = 16')

            config = load_config(str(config_path))
            assert config["font"]["family"] == "Arial"
            assert config["font"]["size"] == 16

    def test_load_config_nonexistent_file(self):
        """Test loading config from nonexistent file returns defaults."""
        config = load_config("/nonexistent/path/.chartedrc.toml")
        assert config["font"] is not None  # Default value

    def test_load_config_invalid_toml(self):
        """Test loading invalid TOML returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text("invalid toml {{{")

            config = load_config(str(config_path))
            # Should return defaults without raising
            assert config["font"] is not None

    def test_load_config_empty_file(self):
        """Test loading empty config file returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text("")

            config = load_config(str(config_path))
            # Should return defaults
            assert config["font"] is not None

    def test_load_config_merges_with_defaults(self):
        """Test that partial config merges with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text('[font]\nfamily = "Arial"')

            config = load_config(str(config_path))
            assert config["font"]["family"] == "Arial"
            # Other values should be defaults
            assert config["font_size"] is not None
            assert config["width"] == 500
            assert config["height"] == 500

    def test_load_config_file_exists_but_none_path(self):
        """Test that config_path=None searches cwd."""
        # This tests line 58 where config_path is None initially
        config = load_config(None)
        assert config is not None

    def test_load_config_with_charts_section(self):
        """Test loading config with chart-specific themes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text(
                '[font]\nfamily = "Arial"\n\n[charts.bar]\nbar_gap = 0.3'
            )

            config = load_config(str(config_path))
            assert config["font"]["family"] == "Arial"
            assert config["charts"]["bar"]["bar_gap"] == 0.3

    def test_load_config_not_found_returns_defaults(self):
        """Test that nonexistent config path returns defaults."""
        config = load_config("/nonexistent/.chartedrc.toml")
        assert config["font"] is not None
        assert config["width"] == 500
        assert config["height"] == 500

    def test_load_config_with_pie_section(self):
        """Test loading config with pie-specific settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".chartedrc.toml"
            config_path.write_text("[pie]\nlabel_font_size = 18")

            config = load_config(str(config_path))
            assert config["pie"]["label_font_size"] == 18


class TestGetChartTheme:
    """Test chart theme retrieval."""

    def test_get_chart_theme_exists(self):
        """Test getting existing chart theme."""
        config = {"charts": {"bar": {"bar_gap": 0.3, "colors": ["red", "blue"]}}}

        theme = get_chart_theme(config, "bar")
        assert theme == {"bar_gap": 0.3, "colors": ["red", "blue"]}

    def test_get_chart_theme_not_exists(self):
        """Test getting nonexistent chart theme returns None."""
        config = {"charts": {"bar": {"bar_gap": 0.3}}}

        theme = get_chart_theme(config, "line")
        assert theme is None

    def test_get_chart_theme_no_charts_key(self):
        """Test getting theme when charts key is missing."""
        config = {}

        theme = get_chart_theme(config, "bar")
        assert theme is None

    def test_get_chart_theme_empty_config(self):
        """Test getting theme with completely empty config."""
        config = {}

        theme = get_chart_theme(config, "bar")
        assert theme is None


class TestGetFontDefinitionsDir:
    """Test font definitions directory retrieval."""

    def test_get_font_definitions_dir(self):
        """Test getting font definitions directory."""
        from charted.utils.defaults import BASE_DEFINITIONS_DIR

        result = get_font_definitions_dir()
        assert result == BASE_DEFINITIONS_DIR
        assert result is not None


class TestGetFont:
    """Test font retrieval helpers."""

    def test_get_font_with_config(self):
        """Test getting font from config."""
        config = {"font": "Arial", "font_size": 14}

        font = get_font(config)
        assert font.family == "Arial"
        assert font.size == 14

    def test_get_font_without_config(self):
        """Test getting font with defaults."""
        font = get_font()
        assert font.family is not None
        assert font.size is not None

    def test_get_title_font_with_config(self):
        """Test getting title font from config."""
        config = {"font": "Arial", "title_font_size": 18}

        font = get_title_font(config)
        assert font.family == "Arial"
        assert font.size == 18

    def test_get_title_font_without_config(self):
        """Test getting title font with defaults."""
        font = get_title_font()
        assert font.family is not None
        assert font.size is not None


class TestGetGapSettings:
    """Test gap setting retrieval."""

    def test_get_bar_gap_with_config(self):
        """Test getting bar gap from config."""
        config = {"bar": {"bar_gap": 0.3}}

        gap = get_bar_gap(config)
        assert gap == 0.3

    def test_get_bar_gap_without_config(self):
        """Test getting bar gap with defaults."""
        gap = get_bar_gap()
        assert gap == 0.50

    def test_get_bar_gap_no_bar_key(self):
        """Test getting bar gap when bar key is missing."""
        config = {}

        gap = get_bar_gap(config)
        assert gap == 0.50

    def test_get_column_gap_with_config(self):
        """Test getting column gap from config."""
        config = {"column": {"column_gap": 0.4}}

        gap = get_column_gap(config)
        assert gap == 0.4

    def test_get_column_gap_without_config(self):
        """Test getting column gap with defaults."""
        gap = get_column_gap()
        assert gap == 0.50

    def test_get_column_gap_no_column_key(self):
        """Test getting column gap when column key is missing."""
        config = {}

        gap = get_column_gap(config)
        assert gap == 0.50


class TestGetPieLabelFontSize:
    """Test pie label font size retrieval."""

    def test_get_pie_label_font_size_with_config(self):
        """Test getting pie label font size from config."""
        config = {"pie": {"label_font_size": 18}}

        size = get_pie_label_font_size(config)
        assert size == 18

    def test_get_pie_label_font_size_without_config(self):
        """Test getting pie label font size with defaults."""
        size = get_pie_label_font_size()
        assert size == 14

    def test_get_pie_label_font_size_no_pie_key(self):
        """Test getting pie label font size when pie key is missing."""
        config = {}

        size = get_pie_label_font_size(config)
        assert size == 14
