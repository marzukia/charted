"""MCP Server for the charted SVG chart library."""

from __future__ import annotations

import sys

__version__ = "0.1.0"

MCP_MISSING_MESSAGE = (
    'MCP support requires charted[mcp]. Install with: pip install "charted[mcp]"'
)


def main() -> None:
    """Entry point. Defers the mcp import to runtime.

    If the optional ``mcp`` dependency is not installed, exit non-zero with a
    single-line install hint instead of dumping a ModuleNotFoundError traceback.
    """
    try:
        from mcp_server.server import run
    except ModuleNotFoundError as exc:
        if _is_missing_mcp(exc):
            print(MCP_MISSING_MESSAGE, file=sys.stderr)
            raise SystemExit(1) from None
        raise

    run()


def _is_missing_mcp(exc: ModuleNotFoundError) -> bool:
    """Return True if the import failure is the missing ``mcp`` package."""
    name = exc.name or ""
    return name == "mcp" or name.startswith("mcp.")
