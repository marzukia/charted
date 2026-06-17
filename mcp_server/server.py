"""MCP server for the charted SVG chart library.

Exposes charted's chart generation as MCP tools that any AI agent can use.
"""

from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ImageContent, TextContent, Tool

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
                "Create a chart from data. Returns an SVG string, HTML "
                "wrapper, SVG data URL, or a PNG image (output_format='png')."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": [
                            "bar", "column", "line", "scatter", "bubble",
                            "pie", "polar_area", "radar", "area", "box",
                            "histogram", "heatmap", "gantt", "combo", "auto",
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
                        "enum": ["svg", "html", "data_url", "png"],
                        "default": "svg",
                        "description": (
                            "Output format. 'png' returns a rasterized PNG "
                            "image (needs charted[png]); use it when the "
                            "caller needs a picture rather than SVG markup."
                        ),
                    },
                    "scale": {
                        "type": "number",
                        "default": 2,
                        "description": "Resolution multiplier for 'png' output.",
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
                            "bar", "column", "line", "scatter", "bubble",
                            "pie", "polar_area", "radar", "area", "box",
                            "histogram", "heatmap", "gantt", "combo", "auto",
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
                        "enum": ["svg", "html", "data_url", "png"],
                        "default": "svg",
                    },
                    "scale": {
                        "type": "number",
                        "default": 2,
                        "description": "Resolution multiplier for 'png' output.",
                    },
                    "save_path": {"type": "string"},
                },
                "required": ["csv_data"],
            },
        ),
    ]


def _png_data_url_to_image(data_url: str) -> ImageContent:
    """Convert a 'data:image/png;base64,...' URL into an MCP ImageContent.

    Chat UIs render ImageContent inline, so a PNG request comes back as a
    picture the agent can show, not as raw markup.
    """
    prefix = "data:image/png;base64,"
    b64 = data_url[len(prefix):] if data_url.startswith(prefix) else data_url
    return ImageContent(type="image", data=b64, mimeType="image/png")


@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[TextContent | ImageContent]:
    """Dispatch a tool call to the appropriate handler."""
    try:
        if name == "create_chart":
            output_format = arguments.get("output_format", "svg")
            result = handle_create_chart(
                chart_type=arguments["chart_type"],
                data=arguments["data"],
                labels=arguments.get("labels"),
                title=arguments.get("title"),
                series_names=arguments.get("series_names"),
                width=arguments.get("width"),
                height=arguments.get("height"),
                theme=arguments.get("theme"),
                output_format=output_format,
                save_path=arguments.get("save_path"),
                scale=int(arguments.get("scale", 2)),
            )
            if output_format == "png":
                return [_png_data_url_to_image(result)]
            return [TextContent(type="text", text=result)]

        elif name == "list_chart_types":
            result = handle_list_chart_types()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_themes":
            result = handle_list_themes()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "chart_from_csv":
            output_format = arguments.get("output_format", "svg")
            result = handle_chart_from_csv(
                csv_data=arguments["csv_data"],
                chart_type=arguments.get("chart_type", "auto"),
                x_column=arguments.get("x_column"),
                y_columns=arguments.get("y_columns"),
                title=arguments.get("title"),
                theme=arguments.get("theme"),
                output_format=output_format,
                save_path=arguments.get("save_path"),
                scale=int(arguments.get("scale", 2)),
            )
            if output_format == "png":
                return [_png_data_url_to_image(result)]
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
