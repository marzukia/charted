"""Font wrapper for loading and measuring text with custom fonts."""

import json
import os
from pathlib import Path
from typing import cast

from charted.utils.defaults import BASE_DEFINITIONS_DIR, DEFAULT_FONT, DEFAULT_FONT_SIZE
from charted.utils.types import FontDefinition

# Width used for an unknown narrow glyph (Latin punctuation, accented letters,
# symbols not in the font definition). Roughly the average advance of the
# definition fonts at their reference size.
_NARROW_FALLBACK_WIDTH = 5


def _is_wide_glyph(char_code: int) -> bool:
    """True when a codepoint is drawn roughly full-width (~1em).

    CJK ideographs, kana, Hangul, full-width forms and most emoji occupy about
    a whole em box. The font definitions only cover Latin, so these glyphs miss
    and fall back to the narrow width, which under-measures a kanji label by
    ~3x and lets it overflow into the plot. Reserving a near-em width per wide
    glyph keeps the gutter/padding honest.
    """
    return (
        0x1100 <= char_code <= 0x115F  # Hangul Jamo
        or 0x2E80 <= char_code <= 0x303E  # CJK radicals, Kangxi, punctuation
        or 0x3041 <= char_code <= 0x33FF  # Hiragana, Katakana, CJK symbols
        or 0x3400 <= char_code <= 0x4DBF  # CJK Ext A
        or 0x4E00 <= char_code <= 0x9FFF  # CJK Unified Ideographs
        or 0xA000 <= char_code <= 0xA4CF  # Yi
        or 0xAC00 <= char_code <= 0xD7A3  # Hangul syllables
        or 0xF900 <= char_code <= 0xFAFF  # CJK compatibility ideographs
        or 0xFE30 <= char_code <= 0xFE4F  # CJK compatibility forms
        or 0xFF00 <= char_code <= 0xFF60  # full-width forms
        or 0xFFE0 <= char_code <= 0xFFE6  # full-width signs
        or 0x1F000 <= char_code <= 0x1FAFF  # emoji & pictographs
        or 0x20000 <= char_code <= 0x3FFFD  # CJK Ext B and beyond
    )


class Font:
    """Font wrapper that loads definitions from JSON and measures text."""

    def __init__(
        self,
        family: str | None = None,
        size: int | None = None,
        definitions_dir: str | None = None,
    ):
        """Initialize font with family name and size.

        Args:
            family: Font family name (e.g., "Helvetica"). Loads from definitions_dir.
            size: Font size in points. Defaults to DEFAULT_FONT_SIZE.
            definitions_dir: Directory containing font JSON definitions.
        """
        self.family = family or DEFAULT_FONT
        self.size = size or DEFAULT_FONT_SIZE
        self.definitions_dir = definitions_dir or BASE_DEFINITIONS_DIR

        # Load font definition file
        self.definitions = self._load_definitions()

    def _load_definitions(self) -> FontDefinition:
        """Load font definitions from JSON file."""
        font_path = Path(self.definitions_dir) / f"{self.family}.json"

        if not font_path.exists():
            # Fallback to Arial if requested font not found
            if self.family != "DejaVu Sans":
                import warnings

                warnings.warn(f"Font '{self.family}' not found, falling back to Arial")
                return self._load_definitions_fallback("DejaVu Sans")
            return {}

        try:
            with open(font_path, "r") as f:
                return cast("FontDefinition", json.load(f))
        except json.JSONDecodeError as e:
            import warnings

            warnings.warn(f"Failed to parse font JSON for '{self.family}': {e}")
            return {}
        except IOError as e:
            import warnings

            warnings.warn(f"Failed to load font file '{font_path}': {e}")
            return {}

    def _load_definitions_fallback(self, fallback: str) -> FontDefinition:
        """Load fallback font definitions."""
        fallback_path = Path(self.definitions_dir) / f"{fallback}.json"

        if not fallback_path.exists():
            return {}

        try:
            with open(fallback_path, "r") as f:
                return cast("FontDefinition", json.load(f))
        except (json.JSONDecodeError, IOError):
            return {}

    def measure(self, text: str, size: int | None = None) -> tuple[float, float]:
        """Measure text dimensions at given size.

        Args:
            text: Text to measure.
            size: Font size override (uses self.size if None).

        Returns:
            Tuple of (width, height) in points.
        """
        measure_size = size if size is not None else self.size
        definitions = self.definitions.get(str(measure_size), {})

        total_width = 0
        max_height = 0

        for char in text:
            char_code = ord(char)
            if str(char_code) in definitions:
                char_def = definitions[str(char_code)]
                total_width += char_def.get("width", _NARROW_FALLBACK_WIDTH)
                max_height = max(max_height, char_def.get("height", 9))
            else:
                # Unknown glyph: full-width scripts (CJK/kana/Hangul/emoji)
                # advance ~1em, so the narrow fallback would badly
                # under-measure them and let labels overflow. Reserve a
                # near-em width for those; keep the small width for genuinely
                # narrow unknowns.
                if _is_wide_glyph(char_code):
                    total_width += round(measure_size * 0.95)
                    max_height = max(max_height, measure_size)
                else:
                    total_width += _NARROW_FALLBACK_WIDTH
                    max_height = max(max_height, 9)

        return (total_width, max_height)

    def measure_width(self, text: str, size: int | None = None) -> float:
        """Measure text width only."""
        width, _ = self.measure(text, size)
        return width

    def measure_height(self, size: int | None = None) -> float:
        """Get font height at given size."""
        definitions = self.definitions.get(
            str(size if size is not None else self.size), {}
        )
        if not definitions:
            return float(size if size is not None else self.size)

        # Get max height from any character
        heights = [defn.get("height", 9) for defn in definitions.values()]
        return (
            max(heights) if heights else float(size if size is not None else self.size)
        )

    def get_char_width(self, char: str, size: int | None = None) -> float:
        """Get width of single character."""
        definitions = self.definitions.get(
            str(size if size is not None else self.size), {}
        )
        char_code = ord(char)

        resolved_size = size if size is not None else self.size
        if str(char_code) in definitions:
            return definitions[str(char_code)].get("width", _NARROW_FALLBACK_WIDTH)
        if _is_wide_glyph(char_code):
            return round(resolved_size * 0.95)
        return _NARROW_FALLBACK_WIDTH  # Default width for unknown narrow chars

    @classmethod
    def list_available(cls, definitions_dir: str | None = None) -> list[str]:
        """List all available font definitions."""
        directory = definitions_dir or BASE_DEFINITIONS_DIR

        if not os.path.exists(directory):
            return []

        fonts = []
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                fonts.append(filename[:-5])  # Remove .json extension

        return sorted(fonts)

    def __repr__(self) -> str:
        return f"Font(family='{self.family}', size={self.size})"
