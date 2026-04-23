"""Create command for charted CLI."""

import argparse
import json
import sys
from pathlib import Path

from ..charts import BarChart, ColumnChart, LineChart, PieChart, ScatterChart

CHART_TYPES = {
    "bar": BarChart,
    "column": ColumnChart,
    "line": LineChart,
    "pie": PieChart,
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
    elif getattr(args, "data_inline", None):
        # Parse inline data
        data["data"] = [float(x.strip()) for x in args.data_inline.split(",")]
        if getattr(args, "labels", None):
            data["labels"] = [x.strip() for x in args.labels.split(",")]
    elif chart_type == "scatter":
        # Scatter requires x_data and y_data
        if getattr(args, "x_data", None) and getattr(args, "y_data", None):
            data["x_data"] = [float(x.strip()) for x in args.x_data.split(",")]
            data["y_data"] = [float(y.strip()) for y in args.y_data.split(",")]
        else:
            print(
                "Error: Scatter plots require --x-data and --y-data arguments",
                file=sys.stderr,
            )
            sys.exit(1)

    # Add title if provided
    if getattr(args, "title", None):
        data["title"] = args.title

    # Create chart
    try:
        chart = ChartClass(**data)
        svg = chart.html

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(svg)

        print(f"Chart saved to: {output_path}")
    except Exception as e:
        print(f"Error creating chart: {e}", file=sys.stderr)
        sys.exit(1)
