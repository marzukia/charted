"""Create command for charted CLI."""

import argparse
import json
import sys
from pathlib import Path

from ..charts import (
    AreaChart,
    BarChart,
    BoxPlot,
    ColumnChart,
    ComboChart,
    GanttChart,
    HeatmapChart,
    Histogram,
    LineChart,
    PieChart,
    RadarChart,
    ScatterChart,
)

CHART_TYPES = {
    "area": AreaChart,
    "bar": BarChart,
    "boxplot": BoxPlot,
    "column": ColumnChart,
    "combo": ComboChart,
    "gantt": GanttChart,
    "heatmap": HeatmapChart,
    "histogram": Histogram,
    "line": LineChart,
    "pie": PieChart,
    "radar": RadarChart,
    "scatter": ScatterChart,
}


def load_data(data_path: str) -> dict:
    """Load data from CSV or JSON file."""
    path = Path(data_path)

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path) as f:
            return json.load(f)
    elif suffix == ".csv":
        return _parse_csv(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .json")


def _parse_csv(path: Path) -> dict:
    """Parse CSV file into data dict."""
    import csv

    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"data": []}

    # Assume first column is labels, rest are data
    fieldnames = list(rows[0].keys())
    labels = [row[fieldnames[0]] for row in rows]
    data_values = []

    for i, field in enumerate(fieldnames[1:], 1):
        column_data = []
        for row in rows:
            try:
                column_data.append(float(row[field]))
            except ValueError:
                column_data.append(row[field])
        data_values.append(column_data)

    # Return in chart-compatible format
    if len(data_values) == 1:
        return {"data": data_values[0], "labels": labels}
    else:
        return {"data": data_values, "labels": labels}


def _build_combo_kwargs(data: dict) -> dict:
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
    if raw and not isinstance(raw[0], list):
        columns = [raw]
    else:
        columns = list(raw)

    # Drop non-numeric columns (e.g. a stray label column read as data).
    numeric_columns = [
        col for col in columns if all(isinstance(v, (int, float)) for v in col)
    ]
    if len(numeric_columns) < 2:
        raise ValueError(
            "combo charts require at least two numeric series, "
            f"got {len(numeric_columns)}"
        )

    series = []
    for i, col in enumerate(numeric_columns):
        series.append(
            {
                "data": col,
                "type": "column" if i == 0 else "line",
                "name": f"Series {i + 1}",
            }
        )

    kwargs = {"series": series}
    if labels is not None:
        kwargs["labels"] = labels
    return kwargs


def create_command(args: argparse.Namespace):
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
            data = load_data(args.data)
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
