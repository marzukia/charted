"""Font wrapper for loading and measuring text with custom fonts."""

import json
import os
from pathlib import Path
from typing import Any

from charted.utils.defaults import BASE_DEFINITIONS_DIR, DEFAULT_FONT, DEFAULT_FONT_SIZE


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

    def _load_definitions(self) -> dict[str, dict[str, Any]]:
        """Load font definitions from JSON file."""
        font_path = Path(self.definitions_dir) / f"{self.family}.json"

        if not font_path.exists():
            # Fallback to Arial if requested font not found
            if self.family != "Arial":
                import warnings

                warnings.warn(f"Font '{self.family}' not found, falling back to Arial")
                return self._load_definitions_fallback("Arial")
            return {}

        try:
            with open(font_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            import warnings

            warnings.warn(f"Failed to parse font JSON for '{self.family}': {e}")
            return {}
        except IOError as e:
            import warnings

            warnings.warn(f"Failed to load font file '{font_path}': {e}")
            return {}

    def _load_definitions_fallback(self, fallback: str) -> dict[str, dict[str, Any]]:
        """Load fallback font definitions."""
        fallback_path = Path(self.definitions_dir) / f"{fallback}.json"

        if not fallback_path.exists():
            return {}

        try:
            with open(fallback_path, "r") as f:
                return json.load(f)
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
                total_width += char_def.get("width", 5)
                max_height = max(max_height, char_def.get("height", 9))
            else:
                # Unknown character - use average width
                total_width += 5
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

        if str(char_code) in definitions:
            return definitions[str(char_code)].get("width", 5)
        return 5  # Default width for unknown chars

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
