"""Configuration loader for .chartedrc files."""

import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

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
        "width": 500,
        "height": 500,
        "theme": None,
        "charts": {},
        "pie": {},
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
    except Exception:
        return defaults

    # Merge loaded config with defaults
    for key in defaults:
        if key in loaded:
            defaults[key] = loaded[key]

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


def get_font_definitions_dir() -> str:
    """Return the base font definitions directory."""
    return BASE_DEFINITIONS_DIR
