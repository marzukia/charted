"""DuckDB extension for charted: generate SVG charts directly from SQL queries."""

from .extension import load, register

__all__ = ["register", "load"]
