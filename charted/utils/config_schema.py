"""Configuration schema validation for charted theming system.

This module provides JSON schema definitions and validation logic
for .chartedrc.toml configuration files with theme support.
"""

from collections.abc import Mapping

from .types import JSONSchema

# Theme property schema definition
THEME_SCHEMA: JSONSchema = {
    "type": "object",
    "properties": {
        "colors": {
            "type": "array",
            "items": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
            "minItems": 1,
            "description": "Color palette (hex colors)",
        },
        "grid_color": {
            "type": "string",
            "pattern": "^#[0-9A-Fa-f]{6}$",
            "default": "#CCCCCC",
            "description": "Grid line color",
        },
        "grid_dasharray": {
            "type": ["string", "null"],
            "pattern": "^[\\d.,\\s]+$",
            "description": "Dash pattern for grid lines (e.g., '2,2')",
        },
        "grid_visible": {
            "type": "boolean",
            "default": True,
            "description": "Whether grid lines are visible",
        },
        "legend_position": {
            "type": "string",
            "enum": ["topright", "topleft", "bottomright", "bottomleft"],
            "default": "topright",
            "description": "Legend position",
        },
        "legend_font_size": {
            "type": "integer",
            "minimum": 8,
            "maximum": 72,
            "default": 11,
            "description": "Font size for legend text",
        },
        "title_color": {
            "type": "string",
            "pattern": "^#[0-9A-Fa-f]{6}$",
            "default": "#444444",
            "description": "Chart title color",
        },
        "title_font_size": {
            "type": "integer",
            "minimum": 8,
            "maximum": 72,
            "default": 16,
            "description": "Font size for title",
        },
        "title_font_family": {
            "type": "string",
            "default": "DejaVu Sans",
            "description": "Font family for title",
        },
        "background_color": {
            "type": "string",
            "pattern": "^#[0-9A-Fa-f]{6}$",
            "default": "#FFFFFF",
            "description": "Background color for chart area",
        },
        "h_padding": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 0.5,
            "default": 0.05,
            "description": "Horizontal padding as fraction of width",
        },
        "v_padding": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 0.5,
            "default": 0.05,
            "description": "Vertical padding as fraction of height",
        },
        "marker_size": {
            "type": "number",
            "minimum": 1.0,
            "maximum": 20.0,
            "default": 3.0,
            "description": "Default marker size for line/scatter charts",
        },
    },
    "additionalProperties": False,
}

# Chart-type specific theme override schema
CHART_THEME_OVERRIDES: JSONSchema = {
    "type": "object",
    "properties": {
        "theme": THEME_SCHEMA,
    },
    "additionalProperties": True,
}


def validate_theme_dict(theme_dict: Mapping[str, object]) -> tuple[bool, list[str]]:
    """Validate a theme dictionary against the schema.

    Args:
        theme_dict: Dictionary with theme properties to validate.

    Returns:
        Tuple of (is_valid, errors) where errors is a list of error messages.
    """
    errors = []

    # Required field validation
    if "colors" in theme_dict:
        colors = theme_dict["colors"]
        if not isinstance(colors, list) or len(colors) == 0:
            errors.append("colors must be a non-empty array")
        elif not all(isinstance(c, str) and c.startswith("#") for c in colors):
            errors.append("colors must contain only hex color strings")

    # Optional field validation
    optional_fields = {
        "grid_color": ("string", "#CCCCCC"),
        "title_color": ("string", "#444444"),
        "background_color": ("string", "#FFFFFF"),
        "title_font_family": ("string", "DejaVu Sans"),
        "legend_position": ("string", "topright"),
    }

    for field, (expected_type, default) in optional_fields.items():
        if field in theme_dict:
            value = theme_dict[field]
            if not isinstance(value, str):
                errors.append(f"{field} must be a string")

    # Numeric field validation
    numeric_fields: dict[str, tuple[float, float, float]] = {
        "legend_font_size": (8, 72, 11),
        "title_font_size": (8, 72, 16),
        "h_padding": (0.0, 0.5, 0.05),
        "v_padding": (0.0, 0.5, 0.05),
        "marker_size": (1.0, 20.0, 3.0),
    }

    for field, (min_val, max_val, _default) in numeric_fields.items():
        if field in theme_dict:
            value = theme_dict[field]
            if not isinstance(value, (int, float)):
                errors.append(f"{field} must be a number")
            elif not (min_val <= value <= max_val):
                errors.append(f"{field} must be between {min_val} and {max_val}")

    # Enum field validation
    enum_fields = {
        "legend_position": ["topright", "topleft", "bottomright", "bottomleft"],
    }

    for field, allowed_values in enum_fields.items():
        if field in theme_dict:
            value = theme_dict[field]
            if value not in allowed_values:
                errors.append(f"{field} must be one of {allowed_values}")

    return len(errors) == 0, errors


def validate_config(config: Mapping[str, object]) -> tuple[bool, list[str]]:
    """Validate entire config dictionary.

    Args:
        config: Full configuration dictionary from load_config().

    Returns:
        Tuple of (is_valid, errors).
    """
    errors = []

    # Validate theme section if present
    theme_section = config.get("theme_section")
    if isinstance(theme_section, dict):
        is_valid, theme_errors = validate_theme_dict(theme_section)
        if not is_valid:
            errors.extend([f"[theme] {e}" for e in theme_errors])

    # Validate chart-specific themes
    chart_types = ["bar", "column", "line", "pie", "scatter", "radar"]
    for chart_type in chart_types:
        chart_config = config.get(chart_type)
        if isinstance(chart_config, dict):
            theme = chart_config.get("theme")
            if isinstance(theme, dict):
                is_valid, theme_errors = validate_theme_dict(theme)
                if not is_valid:
                    errors.extend([f"[{chart_type}.theme] {e}" for e in theme_errors])

    return len(errors) == 0, errors
