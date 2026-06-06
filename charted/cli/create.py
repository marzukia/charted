"""Create command for charted CLI."""

import argparse
import json
import sys
from pathlib import Path
from typing import cast

from ..charts import (
    AreaChart,
    BarChart,
    BoxPlot,
    BubbleChart,
    ColumnChart,
    ComboChart,
    GanttChart,
    HeatmapChart,
    Histogram,
    LineChart,
    PieChart,
    PolarAreaChart,
    RadarChart,
    SankeyChart,
    ScatterChart,
)
from ..utils.types import ChartDataDict, ComboSeriesDict

CHART_TYPES = {
    "area": AreaChart,
    "bar": BarChart,
    "boxplot": BoxPlot,
    "bubble": BubbleChart,
    "column": ColumnChart,
    "combo": ComboChart,
    "gantt": GanttChart,
    "heatmap": HeatmapChart,
    "histogram": Histogram,
    "line": LineChart,
    "pie": PieChart,
    "polar_area": PolarAreaChart,
    "radar": RadarChart,
    "sankey": SankeyChart,
    "scatter": ScatterChart,
}


def load_data(data_path: str, transpose: bool = False) -> ChartDataDict:
    """Load data from CSV or JSON file.

    Args:
        data_path: Path to a .csv or .json file.
        transpose: Only applies to CSV. When False (default) the first column
            holds the x-axis labels and every other column is a data series.
            When True the layout is read sideways: each data row becomes a
            series and the header row (minus the corner cell) supplies the
            x-axis labels.
    """
    path = Path(data_path)

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path) as f:
            return cast("ChartDataDict", json.load(f))
    elif suffix == ".csv":
        return _parse_csv(path, transpose=transpose)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .json")


def _to_number(value: str) -> float | str:
    """Convert a CSV cell to a float, leaving non-numeric text untouched."""
    try:
        return float(value)
    except ValueError:
        return value


def _parse_csv(path: Path, transpose: bool = False) -> ChartDataDict:
    """Parse a CSV file into a chart-compatible data dict.

    Default layout (``transpose=False``): the first column is the x-axis
    labels and each remaining column is a data series.

    Wide layout (``transpose=True``): the first row is the header, where the
    corner cell is ignored and the rest are the x-axis labels. Each subsequent
    row is one series, named by its first cell.
    """
    import csv

    if transpose:
        return _parse_csv_transposed(path)

    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"data": []}

    # Assume first column is labels, rest are data
    fieldnames = list(rows[0].keys())
    labels = [row[fieldnames[0]] for row in rows]
    data_values = []

    for field in fieldnames[1:]:
        column_data = [_to_number(row[field]) for row in rows]
        data_values.append(column_data)

    # Return in chart-compatible format
    if len(data_values) == 1:
        return {"data": data_values[0], "labels": labels}
    else:
        return {"data": data_values, "labels": labels}


def _parse_csv_transposed(path: Path) -> ChartDataDict:
    """Parse a wide / series-per-row CSV (see _parse_csv for the layout)."""
    import csv

    with open(path) as f:
        rows = list(csv.reader(f))

    # Drop blank trailing rows that csv.reader can leave behind.
    rows = [row for row in rows if row]

    if not rows:
        return {"data": []}

    header = rows[0]
    labels = header[1:]
    series_names = []
    data_values = []

    for row in rows[1:]:
        series_names.append(row[0])
        data_values.append([_to_number(cell) for cell in row[1:]])

    result: ChartDataDict = {"labels": labels, "series_names": series_names}
    if len(data_values) == 1:
        result["data"] = data_values[0]
    else:
        result["data"] = data_values
    return result


def _build_combo_kwargs(data: ChartDataDict) -> ChartDataDict:
    """Map loaded data into ComboChart's series-based keyword arguments.

    Accepts either a dict that already carries a ``series`` list (passed
    through untouched) or the generic ``{"data": ..., "labels": ...}`` shape
    produced by the CSV/JSON loaders. Multi-column data becomes one series per
    column; the first column renders as bars and the rest as lines.

    Raises ValueError with a human-readable message for shapes that cannot
    produce a valid combo chart (no data, or fewer than two series).
    """
    # Already in series form (e.g. a hand-written JSON config).
    if "series" in data:
        return data

    raw = data.get("data")
    labels = data.get("labels")

    if not raw:
        raise ValueError("no data provided for combo chart")

    # Normalise to a list of series (list of lists).
    columns: list[object]
    if isinstance(raw, list) and raw and not isinstance(raw[0], list):
        columns = [raw]
    else:
        columns = list(raw) if isinstance(raw, list) else []

    # Drop non-numeric columns (e.g. a stray label column read as data).
    numeric_columns = [
        col
        for col in columns
        if isinstance(col, list) and all(isinstance(v, (int, float)) for v in col)
    ]
    if len(numeric_columns) < 2:
        raise ValueError(
            "combo charts require at least two numeric series, "
            f"got {len(numeric_columns)}"
        )

    series: list[ComboSeriesDict] = []
    for i, col in enumerate(numeric_columns):
        series.append(
            {
                "data": col,
                "type": "column" if i == 0 else "line",
                "name": f"Series {i + 1}",
            }
        )

    kwargs: ChartDataDict = {"series": series}
    if labels is not None:
        kwargs["labels"] = labels
    return kwargs


def create_command(args: argparse.Namespace) -> None:
    """Create a new chart."""
    chart_type = args.chart_type
    output_path = Path(args.output)

    if chart_type not in CHART_TYPES:
        print(f"Error: Unknown chart type: {chart_type}", file=sys.stderr)
        sys.exit(1)

    ChartClass = CHART_TYPES[chart_type]

    # Load data if provided
    data = {}
    if args.data:
        try:
            data = load_data(args.data, transpose=getattr(args, "transpose", False))
        except (FileNotFoundError, ValueError) as e:
            error_msg = str(e)
            if "not found" in error_msg:
                print(f"Error: Data file not found: {args.data}", file=sys.stderr)
                print(
                    "  Suggestion: Check the file path and ensure it exists",
                    file=sys.stderr,
                )
            elif "Unsupported file format" in error_msg:
                print("Error: Unsupported file format", file=sys.stderr)
                print("  Suggestion: Use .csv or .json files only", file=sys.stderr)
            else:
                print(f"Error loading data: {e}", file=sys.stderr)
                print(
                    "  Suggestion: Check that your CSV/JSON is properly formatted",
                    file=sys.stderr,
                )
            sys.exit(1)

    # ComboChart uses a series-based API rather than data=/labels=, so map the
    # loaded data into that shape (or fail with a clear message).
    if chart_type == "combo":
        try:
            data = _build_combo_kwargs(data)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            print(
                "  Suggestion: combo charts need at least two numeric series. "
                "Provide a JSON file with a 'series' list, or a CSV/JSON with two "
                "or more numeric data columns.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Merge in a config file, then let explicit CLI flags win over it. Config
    # values seed the chart kwargs; --title / --width / --height override the
    # matching config entry when supplied (and override loaded data too).
    if getattr(args, "config", None):
        try:
            with open(args.config) as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"Error: Config file not found: {args.config}", file=sys.stderr)
            print(
                "  Suggestion: Check the file path and ensure it exists",
                file=sys.stderr,
            )
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error reading config file: {e}", file=sys.stderr)
            print(
                "  Suggestion: Check that the config file is valid JSON",
                file=sys.stderr,
            )
            sys.exit(1)
        # config file is the base layer, data file overrides it.
        merged = dict(config)
        merged.update(data)
        data = merged

    # CLI flags take precedence over both the config file and the data file.
    if getattr(args, "title", None) is not None:
        data["title"] = args.title
    if getattr(args, "width", None) is not None:
        data["width"] = args.width
    if getattr(args, "height", None) is not None:
        data["height"] = args.height

    # Create chart
    try:
        chart = ChartClass(**data)
        svg = chart.html

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(svg)

        print(f"Chart saved to: {output_path}")
    except (ValueError, FileNotFoundError) as e:
        # Expected errors from chart creation
        print(f"Error creating chart: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Unexpected errors - log for debugging
        import traceback

        print(f"Unexpected error creating chart: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
