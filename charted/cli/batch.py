"""Batch command for charted CLI."""

import argparse
import sys
from pathlib import Path

from .create import CHART_TYPES, load_data


def batch_command(args: argparse.Namespace) -> None:
    """Generate multiple charts from a directory."""
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    override_chart_type = (
        args.chart_type if hasattr(args, "chart_type") and args.chart_type else None
    )

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: Not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all data files
    data_files = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.json"))

    if not data_files:
        print(f"Error: No data files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(data_files)} data files")

    success_count = 0
    error_count = 0

    for data_file in data_files:
        try:
            # Determine chart type from filename or override
            if override_chart_type:
                chart_type = override_chart_type
            else:
                stem = data_file.stem.lower()
                chart_type = _infer_chart_type(stem)

            if chart_type not in CHART_TYPES:
                print(f"  Skipping {data_file.name}: unknown chart type in filename")
                error_count += 1
                continue

            ChartClass = CHART_TYPES[chart_type]
            data = load_data(str(data_file))

            chart = ChartClass(**data)
            svg = chart.html

            output_path = output_dir / f"{data_file.stem}.svg"
            with open(output_path, "w") as f:
                f.write(svg)

            print(f"  Created: {output_path.name}")
            success_count += 1

        except (FileNotFoundError, ValueError, KeyError) as e:
            # Expected errors from data loading or chart creation
            error_msg = str(e)
            print(f"  Error with {data_file.name}: {e}", file=sys.stderr)
            if "not found" in error_msg:
                print(
                    "    Suggestion: Check that the data file exists and is readable",
                    file=sys.stderr,
                )
            elif "chart type" in error_msg.lower() or "key" in error_msg.lower():
                print(
                    "    Suggestion: Check data matches expected chart format",
                    file=sys.stderr,
                )
            else:
                print(
                    "    Suggestion: Check that your CSV/JSON is properly formatted",
                    file=sys.stderr,
                )
            error_count += 1
        except Exception as e:
            # Unexpected errors - log and re-raise for debugging
            import traceback

            print(f"  Unexpected error with {data_file.name}: {e}", file=sys.stderr)
            traceback.print_exc()
            error_count += 1

    print(f"\nCompleted: {success_count} succeeded, {error_count} failed")

    if error_count > 0:
        sys.exit(1)


def _infer_chart_type(filename: str) -> str:
    """Infer chart type from filename."""
    # Look for chart type keywords in filename
    keywords = [
        "bar",
        "column",
        "line",
        "pie",
        "scatter",
        "area",
        "boxplot",
        "histogram",
        "heatmap",
        "gantt",
    ]

    for keyword in keywords:
        if keyword in filename:
            return keyword

    # Default to bar chart
    return "bar"
