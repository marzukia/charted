"""MCP Server for the charted SVG chart library."""

__version__ = "0.1.0"


def main():
    """Entry point — defers mcp import to runtime."""
    from mcp_server.server import run

    run()
