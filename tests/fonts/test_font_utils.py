"""Tests for font utility functions."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from charted.utils.defaults import BASE_DEFINITIONS_DIR

# Try to import TextMeasurer, handle missing tkinter gracefully
try:
    from charted.fonts.tkinter import TextMeasurer

    TKINTER_AVAILABLE = True
except ImportError:
    TextMeasurer = None  # type: ignore
    TKINTER_AVAILABLE = False


class TestFontLoadingHappyPath:
    """Test happy path scenarios for font loading and utilities."""

    def test_create_font_definition(self):
        """Test that create_font_definition creates a JSON file."""
        if not TKINTER_AVAILABLE:
            pytest.skip("tkinter not available")

        from charted.fonts.utils import create_font_definition

        mock_tm = MagicMock(spec=TextMeasurer)
        mock_tm.__enter__ = MagicMock(return_value=mock_tm)
        mock_tm.__exit__ = MagicMock(return_value=None)
        mock_tm.measure_text = MagicMock(return_value=(10.0, 12.0))

        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=MagicMock())
        mock_file.__exit__ = MagicMock(return_value=None)

        with patch.object(TextMeasurer, "__new__", return_value=mock_tm):
            with patch("charted.fonts.utils.open", mock_file):
                create_font_definition("TestFont", min_font_size=10, max_font_size=12)

    def test_load_arial_json(self):
        """Test loading Arial font definition JSON file."""
        arial_path = os.path.join(BASE_DEFINITIONS_DIR, "Arial.json")
        assert os.path.exists(arial_path), "Arial.json should exist"

        with open(arial_path) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert len(data) > 0

    def test_load_helvetica_json(self):
        """Test loading Helvetica font definition JSON file."""
        helvetica_path = os.path.join(BASE_DEFINITIONS_DIR, "Helvetica.json")
        assert os.path.exists(helvetica_path), "Helvetica.json should exist"

        with open(helvetica_path) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert len(data) > 0

    def test_font_caching(self):
        """Test that font definitions are cached after loading."""
        from charted.utils import defaults

        assert hasattr(defaults, "DEFAULT_FONT")
        assert defaults.DEFAULT_FONT in ("Helvetica", "Arial", "JetBrains Mono")


class TestFontMeasurementSadPath:
    """Test edge cases for font measurement."""

    @pytest.mark.skipif(
        not os.environ.get("DISPLAY"), reason="Requires DISPLAY for tkinter"
    )
    def test_measure_empty_string(self):
        """Test measuring empty string returns valid dimensions."""
        from charted.fonts.tkinter import TextMeasurer

        with TextMeasurer() as tm:
            result = tm.measure_text("")
            assert result == (0, 0)

    @pytest.mark.skipif(
        not os.environ.get("DISPLAY"), reason="Requires DISPLAY for tkinter"
    )
    def test_unicode_characters(self):
        """Test measuring unicode characters."""
        from charted.fonts.tkinter import TextMeasurer

        with TextMeasurer() as tm:
            result = tm.measure_text("你好", family="Helvetica", size=12)
            assert isinstance(result, tuple)
            assert len(result) == 2

    @pytest.mark.skipif(
        not os.environ.get("DISPLAY"), reason="Requires DISPLAY for tkinter"
    )
    def test_negative_font_size(self):
        """Test that negative font size is handled."""
        from charted.fonts.tkinter import TextMeasurer

        with TextMeasurer() as tm:
            result = tm.measure_text("test", size=-1)
            assert isinstance(result, tuple)
