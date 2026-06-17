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
                "Generate an SVG, HTML, data-URL, or rasterized PNG chart from "
                "structured data. Supports 14 chart types (bar, column, line, "
                "scatter, bubble, pie, polar_area, radar, area, box, histogram, "
                "heatmap, gantt, combo) plus 'auto' which picks the best type "
                "automatically. Use this when you have data already in memory as "
                "a list or dict; for CSV input prefer chart_from_csv instead."
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
                        "description": (
                            "The type of chart to render. 'auto' inspects the "
                            "data shape and picks the most appropriate type. "
                            "Examples: 'bar' for horizontal category comparison, "
                            "'line' for time-series trends, 'pie' for "
                            "part-of-whole proportions, 'scatter' for XY "
                            "correlation, 'heatmap' for a 2-D color matrix."
                        ),
                    },
                    "data": {
                        "type": ["array", "object"],
                        "description": (
                            "Chart data. For a single series pass a 1-D list of "
                            "numbers, e.g. [10, 20, 15]. For multiple series pass "
                            "a 2-D list where each inner list is one series, e.g. "
                            "[[10, 20], [5, 30]]. Scatter/bubble charts expect "
                            "[[x_values], [y_values]]."
                        ),
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Category labels for the x-axis, one per data point. "
                            "Example: ['Jan', 'Feb', 'Mar']. Omit for numeric or "
                            "auto-indexed axes."
                        ),
                    },
                    "title": {
                        "type": "string",
                        "description": (
                            "Optional chart title rendered above the plot area. "
                            "Example: 'Monthly Revenue 2024'."
                        ),
                    },
                    "series_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Display names for each data series, shown in the "
                            "chart legend. Must match the number of series in "
                            "data. Example: ['Revenue', 'Costs']."
                        ),
                    },
                    "width": {
                        "type": "number",
                        "default": 500,
                        "description": (
                            "Chart canvas width in pixels. Default is 500. "
                            "Increase for more detail or wider labels."
                        ),
                    },
                    "height": {
                        "type": "number",
                        "default": 500,
                        "description": (
                            "Chart canvas height in pixels. Default is 500. "
                            "Adjust to control aspect ratio."
                        ),
                    },
                    "theme": {
                        "type": ["string", "object"],
                        "description": (
                            "Visual theme. Pass a preset name ('light', 'dark', "
                            "'high-contrast') or a palette name ('viridis', "
                            "'inferno', 'ocean', etc.) as a string, or a config "
                            "object such as {'colors': 'viridis', "
                            "'background_color': '#1a1a2e'}. Use "
                            "list_themes to see all available options."
                        ),
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["svg", "html", "data_url", "png"],
                        "default": "svg",
                        "description": (
                            "Format for the returned chart. 'svg' returns raw "
                            "SVG markup (default, zero extra dependencies). "
                            "'html' wraps the SVG in a minimal HTML page. "
                            "'data_url' returns an SVG data URL suitable "
                            "for use in an img src attribute. 'png' rasterizes "
                            "the chart to a PNG image (requires charted[png]) and "
                            "returns it as inline image content visible in chat UIs."
                        ),
                    },
                    "scale": {
                        "type": "number",
                        "default": 2,
                        "description": (
                            "Resolution multiplier applied when output_format is "
                            "'png'. A value of 2 (default) doubles the pixel "
                            "dimensions for high-DPI displays. Has no effect for "
                            "SVG output."
                        ),
                    },
                    "save_path": {
                        "type": "string",
                        "description": (
                            "Optional absolute or relative file path where the "
                            "chart should also be saved on disk. The file "
                            "extension should match output_format (e.g. "
                            "'chart.svg' or 'chart.png'). The tool still "
                            "returns the chart content regardless."
                        ),
                    },
                },
                "required": ["chart_type", "data"],
            },
        ),
        Tool(
            name="list_chart_types",
            description=(
                "Return the full list of chart types supported by charted, "
                "each with its type identifier and a short description of what "
                "it is best suited for. Call this before create_chart or "
                "chart_from_csv when you are unsure which chart_type to choose."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="list_themes",
            description=(
                "Return all available theme presets and named color palettes "
                "that can be passed to the theme parameter of create_chart or "
                "chart_from_csv. Also returns a usage hint showing how to "
                "combine a palette with custom background and foreground colors."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="chart_from_csv",
            description=(
                "Parse raw CSV text and generate a chart directly from it, "
                "without requiring the caller to pre-process the data. The tool "
                "auto-detects numeric columns for the y-axis and uses the first "
                "non-numeric column as x-axis labels. Use this when the user "
                "provides CSV content directly; for data already in a Python "
                "list or dict use create_chart instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_data": {
                        "type": "string",
                        "description": (
                            "Complete CSV text including a header row. Columns "
                            "are auto-classified as labels (non-numeric) or data "
                            "series (numeric). Newlines should be literal line "
                            "breaks. Example header row: Month,Sales."
                        ),
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": [
                            "bar", "column", "line", "scatter", "bubble",
                            "pie", "polar_area", "radar", "area", "box",
                            "histogram", "heatmap", "gantt", "combo", "auto",
                        ],
                        "default": "auto",
                        "description": (
                            "The type of chart to render. Defaults to 'auto', "
                            "which picks the best type based on the data shape. "
                            "See list_chart_types for descriptions of each option."
                        ),
                    },
                    "x_column": {
                        "type": "string",
                        "description": (
                            "Name of the CSV column to use as x-axis category "
                            "labels. If omitted, the first non-numeric column is "
                            "used automatically. Example: 'Month'."
                        ),
                    },
                    "y_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Names of CSV columns to plot as data series. If "
                            "omitted, all numeric columns (except x_column) are "
                            "used. Example: ['Revenue', 'Costs']."
                        ),
                    },
                    "title": {
                        "type": "string",
                        "description": (
                            "Optional chart title rendered above the plot area. "
                            "Example: 'Q1 Sales by Region'."
                        ),
                    },
                    "theme": {
                        "type": ["string", "object"],
                        "description": (
                            "Visual theme. Pass a preset name ('light', 'dark', "
                            "'high-contrast') or a palette name ('viridis', "
                            "'inferno', etc.) as a string, or a config object. "
                            "Use list_themes to see all options."
                        ),
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["svg", "html", "data_url", "png"],
                        "default": "svg",
                        "description": (
                            "Format for the returned chart: 'svg' (default), "
                            "'html', 'data_url' (SVG data URL), or 'png' "
                            "(rasterized image, requires charted[png])."
                        ),
                    },
                    "scale": {
                        "type": "number",
                        "default": 2,
                        "description": (
                            "Resolution multiplier for 'png' output. Default 2 "
                            "gives high-DPI output. Has no effect for SVG formats."
                        ),
                    },
                    "save_path": {
                        "type": "string",
                        "description": (
                            "Optional file path to also save the chart on disk. "
                            "Extension should match output_format, e.g. "
                            "'output/chart.svg'. The tool still returns the "
                            "chart content in the response."
                        ),
                    },
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
