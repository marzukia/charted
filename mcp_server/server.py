"""MCP server for the charted SVG chart library.

Exposes charted's chart generation as MCP tools that any AI agent can use.
"""

from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server.tools import (
    handle_chart_from_csv,
    handle_create_chart,
    handle_list_chart_types,
    handle_list_themes,
)

app = Server("charted-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of tools exposed by this server."""
    return [
        Tool(
            name="create_chart",
            description=(
                "Create an SVG chart from data. Returns SVG string, "
                "HTML wrapper, or data URL."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": [
                            "bar", "column", "line", "scatter", "pie",
                            "radar", "area", "box", "histogram", "heatmap",
                            "gantt", "auto",
                        ],
                        "description": "Chart type. 'auto' picks the best type from data shape.",
                    },
                    "data": {
                        "type": ["array", "object"],
                        "description": "Chart data. 1D array for single series, 2D for multi-series.",
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "X-axis category labels.",
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title.",
                    },
                    "series_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names for each data series (used in legend).",
                    },
                    "width": {
                        "type": "number",
                        "default": 500,
                        "description": "Chart width in pixels.",
                    },
                    "height": {
                        "type": "number",
                        "default": 500,
                        "description": "Chart height in pixels.",
                    },
                    "theme": {
                        "type": ["string", "object"],
                        "description": "Theme preset name or config object.",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["svg", "html", "data_url"],
                        "default": "svg",
                        "description": "Output format.",
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional file path to save the chart.",
                    },
                },
                "required": ["chart_type", "data"],
            },
        ),
        Tool(
            name="list_chart_types",
            description="List all supported chart types with descriptions.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="list_themes",
            description="List available theme presets and color palettes.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="chart_from_csv",
            description="Generate a chart directly from CSV text data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_data": {
                        "type": "string",
                        "description": "Raw CSV text (with header row).",
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": [
                            "bar", "column", "line", "scatter", "pie",
                            "radar", "area", "box", "histogram", "heatmap",
                            "auto",
                        ],
                        "default": "auto",
                        "description": "Chart type.",
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column name for x-axis labels.",
                    },
                    "y_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Column names for y-axis data series.",
                    },
                    "title": {"type": "string"},
                    "theme": {"type": ["string", "object"]},
                    "output_format": {
                        "type": "string",
                        "enum": ["svg", "html", "data_url"],
                        "default": "svg",
                    },
                    "save_path": {"type": "string"},
                },
                "required": ["csv_data"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch a tool call to the appropriate handler."""
    try:
        if name == "create_chart":
            result = handle_create_chart(
                chart_type=arguments["chart_type"],
                data=arguments["data"],
                labels=arguments.get("labels"),
                title=arguments.get("title"),
                series_names=arguments.get("series_names"),
                width=arguments.get("width"),
                height=arguments.get("height"),
                theme=arguments.get("theme"),
                output_format=arguments.get("output_format", "svg"),
                save_path=arguments.get("save_path"),
            )
            return [TextContent(type="text", text=result)]

        elif name == "list_chart_types":
            result = handle_list_chart_types()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_themes":
            result = handle_list_themes()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "chart_from_csv":
            result = handle_chart_from_csv(
                csv_data=arguments["csv_data"],
                chart_type=arguments.get("chart_type", "auto"),
                x_column=arguments.get("x_column"),
                y_columns=arguments.get("y_columns"),
                title=arguments.get("title"),
                theme=arguments.get("theme"),
                output_format=arguments.get("output_format", "svg"),
                save_path=arguments.get("save_path"),
            )
            return [TextContent(type="text", text=result)]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}",
            )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def _run():
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def run():
    """Entry point for the charted-mcp server."""
    asyncio.run(_run())


main = run
