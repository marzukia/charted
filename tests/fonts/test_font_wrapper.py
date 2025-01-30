"""Tests for font wrapper."""

import tempfile
from pathlib import Path

from charted.fonts.wrapper import Font


class TestFont:
    """Test Font class."""

    def test_default_font_initialization(self):
        """Test font initializes with default values."""
        font = Font()
        assert font.family is not None
        assert font.size > 0

    def test_custom_font_initialization(self):
        """Test font with custom family and size."""
        font = Font(family="Arial", size=14)
        assert font.family == "Arial"
        assert font.size == 14

    def test_measure_returns_positive_dimensions(self):
        """Test measure returns positive width and height."""
        font = Font()
        width, height = font.measure("Hello World")
        assert width > 0
        assert height > 0

    def test_measure_width_returns_single_value(self):
        """Test measure_width returns just the width."""
        font = Font()
        width = font.measure_width("Test")
        assert width > 0

    def test_measure_height_returns_positive_value(self):
        """Test measure_height returns positive value."""
        font = Font()
        height = font.measure_height()
        assert height > 0

    def test_measure_height_with_size_override(self):
        """Test measure_height with size parameter."""
        font = Font(size=12)
        font.measure_height(size=12)
        font.measure_height(size=24)

    def test_get_char_width_returns_positive_value(self):
        """Test get_char_width returns positive value."""
        font = Font()
        width = font.get_char_width("A")
        assert width > 0

    def test_unknown_character_handling(self):
        """Test handling of unknown characters."""
        font = Font()
        # Unknown chars should still return a width (default 5)
        width = font.get_char_width("\uffff")  # Rare/unlikely char
        assert width > 0

    def test_measure_with_size_override(self):
        """Test measure with size parameter."""
        font = Font(size=12)
        w1, h1 = font.measure("Test", size=12)
        w2, h2 = font.measure("Test", size=24)
        # Both should return valid dimensions
        assert w1 > 0 and h1 > 0
        assert w2 > 0 and h2 > 0

    def test_repr_format(self):
        """Test __repr__ returns expected format."""
        font = Font(family="Arial", size=14)
        repr_str = repr(font)
        assert "Font" in repr_str
        assert "Arial" in repr_str
        assert "14" in repr_str

    def test_list_available_returns_fonts(self):
        """Test list_available returns font names."""
        fonts = Font.list_available()
        assert isinstance(fonts, list)
        assert len(fonts) > 0

    def test_list_available_with_custom_dir(self):
        """Test list_available with custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake font file
            Path(tmpdir, "TestFont.json").write_text("{}")
            fonts = Font.list_available(tmpdir)
            assert "TestFont" in fonts

    def test_list_available_empty_dir(self):
        """Test list_available with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fonts = Font.list_available(tmpdir)
            assert fonts == []

    def test_list_available_nonexistent_dir(self):
        """Test list_available with nonexistent directory."""
        fonts = Font.list_available("/nonexistent/path/12345")
        assert fonts == []

    def test_fallback_font_loading(self):
        """Test that missing fonts fall back to Arial."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Try to load a non-existent font
            Font(family="NonExistentFont12345")
            # Should have a warning
            assert len(w) >= 1

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON font files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an invalid JSON file
            font_file = Path(tmpdir, "Invalid.json")
            font_file.write_text("not valid json {{{")

            import warnings

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                Font(family="Invalid", definitions_dir=tmpdir)
                # Should have a warning about JSON parsing
                assert len(w) >= 1

    def test_empty_text_measurement(self):
        """Test measuring empty string."""
        font = Font()
        width, height = font.measure("")
        assert width == 0
        # Height can be 0 for empty string
        assert height >= 0

    def test_single_character_measurement(self):
        """Test measuring single character."""
        font = Font()
        width, height = font.measure("A")
        assert width > 0
        assert height > 0

    def test_special_characters_measurement(self):
        """Test measuring text with special characters."""
        font = Font()
        width, height = font.measure("Hello! @#$%")
        assert width > 0
        assert height > 0

    def test_unicode_characters_measurement(self):
        """Test measuring unicode text."""
        font = Font()
        width, height = font.measure("Hello 世界")
        assert width > 0
        assert height > 0
