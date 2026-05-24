"""Tool implementations for the charted MCP server.

Each function handles one MCP tool call and returns the result
in a format suitable for the MCP response.
"""

from __future__ import annotations

import csv
import inspect
import io
from typing import Any

import charted
from charted.themes.core import NAMED_PALETTES, Theme

CHART_TYPE_MAP = {
    "bar": "BarChart",
    "column": "ColumnChart",
    "line": "LineChart",
    "scatter": "ScatterChart",
    "pie": "PieChart",
    "radar": "RadarChart",
    "area": "AreaChart",
    "box": "BoxPlot",
    "histogram": "Histogram",
    "heatmap": "HeatmapChart",
    "gantt": "GanttChart",
}

CHART_DESCRIPTIONS = {
    "bar": "Horizontal bar chart for comparing categories",
    "column": "Vertical bar chart",
    "line": "Line chart for trends over time",
    "scatter": "XY scatter plot for correlation",
    "pie": "Pie/donut chart for part-of-whole",
    "radar": "Spider/radar chart for multivariate comparison",
    "area": "Filled line chart for volume over time",
    "box": "Box-and-whisker plot for distributions",
    "histogram": "Frequency distribution of continuous data",
    "heatmap": "Color-coded matrix for 2D data",
    "gantt": "Timeline/schedule visualization",
}


def handle_create_chart(
    chart_type: str,
    data: Any,
    labels: list[str] | None = None,
    title: str | None = None,
    series_names: list[str] | None = None,
    width: float | None = None,
    height: float | None = None,
    theme: str | dict | None = None,
    output_format: str = "svg",
    save_path: str | None = None,
) -> str:
    """Create a chart and return it in the requested format.

    Args:
        chart_type: One of the supported chart types or "auto".
        data: Chart data (1D or 2D array).
        labels: X-axis category labels.
        title: Chart title.
        series_names: Names for each data series.
        width: Chart width in pixels.
        height: Chart height in pixels.
        theme: Theme preset name or config dict.
        output_format: One of "svg", "html", "data_url".
        save_path: Optional file path to save the chart.

    Returns:
        Chart content as a string in the requested format.

    Raises:
        ValueError: If chart_type is invalid or data is empty.
    """
    # Build kwargs for the chart constructor
    kwargs: dict[str, Any] = {}
    if title is not None:
        kwargs["title"] = title
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height
    if labels is not None:
        kwargs["labels"] = labels
    if series_names is not None:
        kwargs["series_names"] = series_names
    if theme is not None:
        if isinstance(theme, str):
            kwargs["theme"] = theme
        elif isinstance(theme, dict):
            kwargs["theme"] = Theme(**theme)

    # Create chart
    if chart_type == "auto":
        chart = charted.auto(data, **kwargs)
    elif chart_type in CHART_TYPE_MAP:
        cls_name = CHART_TYPE_MAP[chart_type]
        cls = getattr(charted, cls_name)
        # Filter kwargs to valid params for this chart class
        sig = inspect.signature(cls.__init__)
        valid_params = set(sig.parameters.keys()) - {"self"}
        filtered = {}
        for k, v in kwargs.items():
            if k in valid_params:
                filtered[k] = v
        # Map 'labels' to the correct param name
        if "labels" not in valid_params and "labels" in kwargs:
            if "x_labels" in valid_params:
                filtered["x_labels"] = kwargs["labels"]
        # Handle charts that use x_data/y_data instead of data
        if "data" in valid_params:
            chart = cls(data=data, **filtered)
        elif "x_data" in valid_params and "y_data" in valid_params:
            # ScatterChart style: expects x_data and y_data
            if isinstance(data, list) and len(data) == 2 and isinstance(data[0], list):
                chart = cls(x_data=data[0], y_data=data[1], **filtered)
            else:
                # Single series: use indices as x_data
                chart = cls(
                    x_data=list(range(len(data))),
                    y_data=data,
                    **filtered,
                )
        else:
            chart = cls(data=data, **filtered)
    else:
        raise ValueError(
            f"Invalid chart_type: {chart_type!r}. "
            f"Must be one of: {list(CHART_TYPE_MAP.keys())} or 'auto'."
        )

    # Save if requested
    if save_path:
        chart.save(save_path)

    # Return in requested format
    if output_format == "html":
        return chart.to_html()
    elif output_format == "data_url":
        return chart.to_base64()
    else:
        return chart.to_svg()


def handle_list_chart_types() -> list[dict[str, str]]:
    """Return list of available chart types with descriptions.

    Returns:
        List of dicts with 'type', 'class', and 'description' keys.
    """
    return [
        {
            "type": chart_type,
            "class": CHART_TYPE_MAP[chart_type],
            "description": CHART_DESCRIPTIONS[chart_type],
        }
        for chart_type in CHART_TYPE_MAP
    ]


def handle_list_themes() -> dict[str, Any]:
    """Return available theme presets and palettes.

    Returns:
        Dict with 'presets', 'palettes', and 'usage_hint' keys.
    """
    # Built-in presets from Theme.from_preset
    presets = ["light", "dark", "high-contrast"]
    # Add any user-registered themes
    registered = charted.list_themes()
    presets = sorted(set(presets + registered))
    palettes = sorted(NAMED_PALETTES.keys())
    return {
        "presets": presets,
        "palettes": palettes,
        "usage_hint": (
            'Pass preset name as theme param, or use palette name in a '
            'theme object: {"colors": "viridis", "background_color": "#1a1a2e"}'
        ),
    }


def handle_chart_from_csv(
    csv_data: str,
    chart_type: str = "auto",
    x_column: str | None = None,
    y_columns: list[str] | None = None,
    title: str | None = None,
    theme: str | dict | None = None,
    output_format: str = "svg",
    save_path: str | None = None,
) -> str:
    """Generate a chart from CSV text data.

    Parses the CSV, auto-detects numeric columns, and uses the first
    string column as labels.

    Args:
        csv_data: Raw CSV text with a header row.
        chart_type: Chart type or "auto".
        x_column: Column to use for x-axis labels.
        y_columns: Columns to use for y-axis data series.
        title: Chart title.
        theme: Theme preset or config dict.
        output_format: Output format.
        save_path: Optional save path.

    Returns:
        Chart content as string.

    Raises:
        ValueError: If CSV is empty or cannot be parsed.
    """
    if not csv_data or not csv_data.strip():
        raise ValueError("CSV data is empty.")

    reader = csv.DictReader(io.StringIO(csv_data.strip()))
    fieldnames = reader.fieldnames
    if not fieldnames or len(fieldnames) < 2:
        raise ValueError(
            "CSV must have a header row with at least two columns."
        )

    rows = list(reader)
    if not rows:
        raise ValueError("CSV has no data rows.")

    # Determine which columns are numeric
    numeric_cols = []
    for col in fieldnames:
        try:
            [float(row[col]) for row in rows]
            numeric_cols.append(col)
        except (ValueError, TypeError):
            pass

    # Determine x_column (labels)
    if x_column is None:
        # First non-numeric column
        non_numeric = [c for c in fieldnames if c not in numeric_cols]
        if non_numeric:
            x_column = non_numeric[0]
        else:
            x_column = None

    # Determine y_columns
    if y_columns is None:
        y_columns = [c for c in numeric_cols if c != x_column]

    if not y_columns:
        raise ValueError("No numeric columns found for chart data.")

    # Extract data
    labels = [row[x_column] for row in rows] if x_column else None
    data: list[float] | list[list[float]]
    if len(y_columns) == 1:
        data = [float(row[y_columns[0]]) for row in rows]
    else:
        data = [[float(row[col]) for row in rows] for col in y_columns]

    series_names = y_columns if len(y_columns) > 1 else None

    return handle_create_chart(
        chart_type=chart_type,
        data=data,
        labels=labels,
        title=title,
        series_names=series_names,
        theme=theme,
        output_format=output_format,
        save_path=save_path,
    )
