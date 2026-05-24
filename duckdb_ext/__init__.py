"""DuckDB extension for charted — generate SVG charts directly from SQL queries."""

from .extension import register, load

__all__ = ["register", "load"]
