"""Core DuckDB extension for charted.

Registers Python UDFs that let users generate SVG charts directly from SQL.

Two usage patterns:

1. Python-driven (recommended): Use charted_query() helper which handles
   query execution and chart generation in one call.

2. SQL-driven: Use charted_from_columns() UDF which takes pre-extracted
   column data as arrays.

Usage:
    import duckdb
    from charted.duckdb_ext import load

    con = load()

    # Python helper — runs the query, generates the chart
    from charted.duckdb_ext.extension import charted_query
    charted_query(con, 'SELECT quarter, revenue FROM sales',
                  chart_type='bar', title='Sales', output='/tmp/chart.svg')

    # Or from SQL using array aggregation:
    SELECT charted_from_arrays(
        list(quarter), list(revenue), 'bar', 'Sales', '/tmp/chart.svg'
    ) FROM sales;
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Optional

import duckdb

import charted

# Map short names to chart classes
CHART_TYPES = {
    "bar": charted.BarChart,
    "column": charted.ColumnChart,
    "line": charted.LineChart,
    "scatter": charted.ScatterChart,
    "pie": charted.PieChart,
    "radar": charted.RadarChart,
    "area": charted.AreaChart,
    "box": charted.BoxPlot,
    "histogram": charted.Histogram,
    "heatmap": charted.HeatmapChart,
}


def _extract_chart_data_from_result(columns, rows):
    """Extract labels, data series, and series names from query results.

    Heuristic:
    - First string/date/timestamp column becomes labels
    - All numeric columns become data series
    - Column names of numeric columns become series_names
    """
    if not rows:
        raise ValueError("Query returned no rows")

    label_col_idx = None
    numeric_col_indices = []

    for i, col in enumerate(columns):
        sample = rows[0][i]
        if isinstance(sample, (int, float)) and not isinstance(sample, bool):
            numeric_col_indices.append(i)
        elif label_col_idx is None:
            label_col_idx = i

    if not numeric_col_indices:
        raise ValueError(
            "Query must return at least one numeric column. "
            f"Got columns: {[c[0] for c in columns]}"
        )

    labels = None
    if label_col_idx is not None:
        labels = [str(row[label_col_idx]) for row in rows]

    data = []
    series_names = []
    for idx in numeric_col_indices:
        series = [float(row[idx]) if row[idx] is not None else 0.0 for row in rows]
        data.append(series)
        series_names.append(columns[idx][0])

    return labels, data, series_names


def _build_chart(
    chart_type: str,
    labels,
    data,
    series_names,
    title: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    theme: Optional[str] = None,
):
    """Construct a chart instance from extracted data."""
    cls = CHART_TYPES.get(chart_type.lower())
    if cls is None:
        available = ", ".join(sorted(CHART_TYPES.keys()))
        raise ValueError(f"Unknown chart type '{chart_type}'. Available: {available}")

    # Special handling for chart types with different data expectations
    chart_type_lower = chart_type.lower()

    # Histogram expects a flat list of raw values
    if chart_type_lower == "histogram":
        # Concatenate all numeric series into one flat list
        chart_data = []
        for series in data:
            chart_data.extend(series)
        series_names_arg = None
    # BoxPlot expects Vector2D — each inner list is one distribution
    elif chart_type_lower == "box":
        # If we have labels, group by label; otherwise each series is a group
        if labels and len(data) == 1:
            # Group values by label
            from collections import defaultdict
            groups = defaultdict(list)
            for i, val in enumerate(data[0]):
                groups[labels[i]].append(val)
            unique_labels = list(dict.fromkeys(labels))
            chart_data = [groups[lbl] for lbl in unique_labels]
            labels = unique_labels
        else:
            chart_data = data
        series_names_arg = None
    elif len(data) == 1:
        chart_data = data[0]
        series_names_arg = None
    else:
        chart_data = data
        series_names_arg = series_names

    sig = inspect.signature(cls.__init__)
    valid_params = set(sig.parameters.keys()) - {"self"}

    kwargs = {}

    # ScatterChart needs x_data and y_data separately
    if "x_data" in valid_params and "data" not in valid_params:
        # For scatter: first series is x, second is y
        if len(data) >= 2:
            kwargs["x_data"] = data[0]
            kwargs["y_data"] = data[1]
            series_names_arg = None  # x/y don't need names the same way
        else:
            # Single series: use index as x
            kwargs["x_data"] = list(range(len(data[0])))
            kwargs["y_data"] = data[0]
    elif "data" in valid_params:
        kwargs["data"] = chart_data
    elif "y_data" in valid_params:
        kwargs["y_data"] = chart_data

    if labels is not None:
        if "labels" in valid_params:
            kwargs["labels"] = labels
        elif "x_labels" in valid_params:
            kwargs["x_labels"] = labels

    if series_names_arg and "series_names" in valid_params:
        kwargs["series_names"] = series_names_arg

    if title and "title" in valid_params:
        kwargs["title"] = title

    if width and "width" in valid_params:
        kwargs["width"] = width
    if height and "height" in valid_params:
        kwargs["height"] = height

    if theme and "theme" in valid_params:
        try:
            kwargs["theme"] = charted.get_theme(theme)
        except Exception:
            pass

    return cls(**kwargs)


# =============================================================================
# Python API — the primary interface
# =============================================================================


def charted_query(
    con: duckdb.DuckDBPyConnection,
    query: str,
    chart_type: str = "bar",
    title: str = None,
    output: str = "/tmp/chart.svg",
    width: float = None,
    height: float = None,
    theme: str = None,
) -> str:
    """Generate a chart from a SQL query and save to SVG.

    This is the main Python-level function. It executes the query on the
    given connection, extracts data, builds the chart, and saves it.

    Args:
        con: DuckDB connection with the data.
        query: SQL query that returns labels + numeric columns.
        chart_type: One of: bar, column, line, scatter, pie, radar, area, box, histogram, heatmap.
        title: Chart title.
        output: SVG file path to write.
        width: Chart width in pixels.
        height: Chart height in pixels.
        theme: Theme name.

    Returns:
        The output file path.

    Example:
        >>> con = duckdb.connect()
        >>> # ... create tables ...
        >>> charted_query(con, 'SELECT name, value FROM data', title='My Chart')
        '/tmp/chart.svg'
    """
    result = con.execute(query)
    columns = result.description
    rows = result.fetchall()

    labels, data, series_names = _extract_chart_data_from_result(columns, rows)
    chart = _build_chart(chart_type, labels, data, series_names, title, width, height, theme)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    chart.save(output)
    return output


def charted_svg(
    con: duckdb.DuckDBPyConnection,
    query: str,
    chart_type: str = "bar",
    title: str = None,
    width: float = None,
    height: float = None,
    theme: str = None,
) -> str:
    """Generate a chart from a SQL query and return SVG string.

    Same as charted_query but returns the SVG content instead of saving to disk.
    """
    result = con.execute(query)
    columns = result.description
    rows = result.fetchall()

    labels, data, series_names = _extract_chart_data_from_result(columns, rows)
    chart = _build_chart(chart_type, labels, data, series_names, title, width, height, theme)
    return chart.to_svg()


# =============================================================================
# SQL UDFs — work with pre-aggregated array data passed from SQL
# =============================================================================


def _charted_from_arrays_impl(labels_json: str, data_json: str, chart_type: str, title: str, output: str) -> str:
    """UDF implementation: takes JSON-encoded labels and data arrays."""
    labels = json.loads(labels_json) if labels_json else None
    data_raw = json.loads(data_json)

    # data_raw is either a single list or list-of-lists
    if data_raw and isinstance(data_raw[0], list):
        data = data_raw
        series_names = [f"series_{i+1}" for i in range(len(data))]
    else:
        data = [data_raw]
        series_names = ["value"]

    ct = chart_type if chart_type else "bar"
    t = title if title else None
    o = output if output else "/tmp/chart.svg"

    chart = _build_chart(ct, labels, data, series_names, t)
    Path(o).parent.mkdir(parents=True, exist_ok=True)
    chart.save(o)
    return o


def _charted_svg_from_arrays_impl(labels_json: str, data_json: str, chart_type: str, title: str) -> str:
    """UDF implementation: returns SVG string from JSON-encoded arrays."""
    labels = json.loads(labels_json) if labels_json else None
    data_raw = json.loads(data_json)

    if data_raw and isinstance(data_raw[0], list):
        data = data_raw
        series_names = [f"series_{i+1}" for i in range(len(data))]
    else:
        data = [data_raw]
        series_names = ["value"]

    ct = chart_type if chart_type else "bar"
    t = title if title else None

    chart = _build_chart(ct, labels, data, series_names, t)
    return chart.to_svg()


def register(con: duckdb.DuckDBPyConnection) -> None:
    """Register all charted SQL functions with a DuckDB connection.

    Registers:
    - charted_from_arrays(labels_json, data_json, chart_type, title, output) → path
    - charted_svg_from_arrays(labels_json, data_json, chart_type, title) → SVG string

    These accept JSON-encoded arrays which can be built in SQL using
    to_json(list(...)) or cast(list_value(...) as json).

    For the simpler query-based workflow, use the Python functions:
    charted_query() and charted_svg() directly.
    """
    VARCHAR = duckdb.sqltype("VARCHAR")

    con.create_function(
        "charted_from_arrays",
        _charted_from_arrays_impl,
        [VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR],
        VARCHAR,
        side_effects=True,
    )

    con.create_function(
        "charted_svg_from_arrays",
        _charted_svg_from_arrays_impl,
        [VARCHAR, VARCHAR, VARCHAR, VARCHAR],
        VARCHAR,
        side_effects=True,
    )


def load(db_path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection with charted functions pre-registered.

    Args:
        db_path: Path to DuckDB database file, or ':memory:' for in-memory.

    Returns:
        DuckDB connection with all charted functions available.

    Example:
        >>> from charted.duckdb_ext import load
        >>> con = load()
        >>> # Use Python API:
        >>> from charted.duckdb_ext.extension import charted_query
        >>> charted_query(con, 'SELECT x, y FROM data', chart_type='line')
    """
    con = duckdb.connect(db_path)
    register(con)
    return con
