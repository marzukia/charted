"""Configuration loader for .chartedrc files."""

import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from .constants import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    PIE_LABEL_FONT_SIZE,
)
from .fonts.wrapper import Font
from .utils.defaults import (
    BASE_DEFINITIONS_DIR,
    DEFAULT_COLORS,
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_TITLE_FONT_SIZE,
)

CONFIG_FILENAMES = [".chartedrc.toml", ".chartedrc", "charted.toml"]


def find_config(start_dir: str | None = None) -> Path | None:
    """Search upward from start_dir for a config file."""
    if start_dir is None:
        start_dir = os.getcwd()

    current = Path(start_dir).resolve()
    while current != current.parent:
        for filename in CONFIG_FILENAMES:
            config_path = current / filename
            if config_path.exists():
                return config_path
        current = current.parent
    return None


def load_config(config_path: str | Path | None = None) -> dict:
    """Load config from .chartedrc file, returning defaults if not found."""
    defaults = {
        "font": DEFAULT_FONT,
        "font_size": DEFAULT_FONT_SIZE,
        "title_font_size": DEFAULT_TITLE_FONT_SIZE,
        "colors": DEFAULT_COLORS,
        "width": DEFAULT_CHART_WIDTH,
        "height": DEFAULT_CHART_HEIGHT,
        "theme": None,
        "charts": {},
        "pie": {},
        "bar": {},
        "column": {},
        "theme_section": {},  # New: parsed [theme] block
    }

    if config_path is None:
        config_path = find_config()

    if config_path is None:
        return defaults

    path = Path(config_path)
    if not path.exists():
        return defaults

    try:
        with open(path, "rb") as f:
            loaded = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return defaults

    # Merge loaded config with defaults
    for key in defaults:
        if key in loaded:
            defaults[key] = loaded[key]

    # Extract [theme] block for new theme API
    if "theme" in loaded and isinstance(loaded["theme"], dict):
        defaults["theme_section"] = loaded["theme"]

    return defaults


def get_chart_theme(config: dict, chart_type: str) -> dict | None:
    """Get chart-type-specific theme overrides.

    Args:
        config: Config dict from load_config().
        chart_type: Chart type name (e.g., "pie", "column", "bar", "line", "scatter").

    Returns:
        Chart-specific theme overrides or None.
    """
    charts_config = config.get("charts", {})
    return charts_config.get(chart_type, None)


def get_font(config: dict | None = None) -> Font:
    """Create a Font instance from config.

    Args:
        config: Config dict from load_config(). Uses defaults if None.

    Returns:
        Font instance configured from config.
    """
    if config is None:
        config = load_config()

    return Font(
        family=config.get("font", DEFAULT_FONT),
        size=config.get("font_size", DEFAULT_FONT_SIZE),
        definitions_dir=BASE_DEFINITIONS_DIR,
    )


def get_title_font(config: dict | None = None) -> Font:
    """Create a Font instance for titles from config.

    Args:
        config: Config dict from load_config(). Uses defaults if None.

    Returns:
        Font instance configured for titles.
    """
    if config is None:
        config = load_config()

    return Font(
        family=config.get("font", DEFAULT_FONT),
        size=config.get("title_font_size", DEFAULT_TITLE_FONT_SIZE),
        definitions_dir=BASE_DEFINITIONS_DIR,
    )


def get_bar_gap(config: dict | None = None) -> float:
    """Get bar gap setting from config.

    Args:
        config: Config dict from load_config(). Uses defaults if None.

    Returns:
        Bar gap value (default 0.50).
    """
    if config is None:
        config = load_config()

    return config.get("bar", {}).get("bar_gap", 0.50)


def get_column_gap(config: dict | None = None) -> float:
    """Get column gap setting from config.

    Args:
        config: Config dict from load_config(). Uses defaults if None.

    Returns:
        Column gap value (default 0.50).
    """
    if config is None:
        config = load_config()

    return config.get("column", {}).get("column_gap", 0.50)


def get_pie_label_font_size(config: dict | None = None) -> int:
    """Get pie label font size from config.

    Args:
        config: Config dict from load_config(). Uses defaults if None.

    Returns:
        Pie label font size (default 14).
    """
    if config is None:
        config = load_config()

    return config.get("pie", {}).get("label_font_size", PIE_LABEL_FONT_SIZE)


def get_font_definitions_dir() -> str:
    """Return the base font definitions directory."""
    return BASE_DEFINITIONS_DIR
