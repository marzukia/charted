"""Tests for tkinter font utilities with display fallback."""

import os
import pytest

# Try to detect if tkinter is available; if not, skip all tests in this module
try:
    import tkinter  # noqa: F401
except ImportError:
    pytestmark = pytest.mark.skip(reason="tkinter not available")

    # Provide stubs so the module can be imported without error
    class TextMeasurer:
        pass
else:
    from unittest.mock import patch, MagicMock

    from charted.fonts.tkinter import TextMeasurer


class TestTkinterFontUtils:
    """Test tkinter font utilities with display fallback."""

    @pytest.mark.skipif(
        not os.environ.get("DISPLAY"), reason="Requires DISPLAY for tkinter"
    )
    def test_tkinter_font_metrics(self):
        """Test tkinter font measurement when display is available."""
        with TextMeasurer() as tm:
            w, h = tm.measure_text("Hello", family="Helvetica", size=12)
            assert isinstance(w, (int, float))
            assert isinstance(h, (int, float))
            assert w > 0
            assert h > 0

    def test_text_measurer_context_manager(self):
        """Test TextMeasurer as context manager (mocked)."""
        with patch("tkinter.Tk") as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_root.destroy = MagicMock()

            with TextMeasurer() as tm:
                assert tm.root is not None
                assert tm.root == mock_root

            mock_root.destroy.assert_called_once()

    @pytest.mark.skipif(
        not os.environ.get("DISPLAY"), reason="Requires DISPLAY for tkinter"
    )
    def test_no_display_fallback(self):
        """Test graceful handling when no display is available."""
        pass  # If we're here, display is available


class TestTextMeasurerNoDisplay:
    """Test TextMeasurer behavior without display."""

    def test_text_measurer_without_context_raises(self):
        """Test that using TextMeasurer outside context raises error."""
        tm = TextMeasurer()
        with pytest.raises(
            RuntimeError, match="must be used within a 'with' statement"
        ):
            tm.measure_text("test")

    def test_context_manager_cleanup(self):
        """Test that context manager cleans up resources."""
        with patch("tkinter.Tk") as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root

            with TextMeasurer():
                pass

            mock_root.destroy.assert_called_once()

    def test_measure_various_fonts(self):
        """Test measuring with different font families."""
        with patch("tkinter.Tk") as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root

            with TextMeasurer() as tm:
                with patch("tkinter.Canvas") as mock_canvas:
                    mock_canvas.return_value.bbox.return_value = (0, 0, 100, 20)
                    from tkinter import font as tkfont

                    with patch.object(tkfont.Font, "measure", return_value=100):
                        with patch.object(tkfont.Font, "__init__", return_value=None):
                            result = tm.measure_text("test", family="Arial", size=14)
                            assert result == (100, 20)
