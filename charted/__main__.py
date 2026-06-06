"""CLI entry point for charted."""

import argparse
import sys
from collections.abc import Sequence


def main(args: Sequence[str] | None = None) -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="charted",
        description="Generate SVG charts from the command line",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create subcommand
    create_parser = subparsers.add_parser("create", help="Create a new chart")
    create_parser.add_argument(
        "chart_type",
        choices=[
            "bar",
            "column",
            "line",
            "pie",
            "radar",
            "scatter",
            "area",
            "boxplot",
            "histogram",
            "heatmap",
            "gantt",
            "combo",
            "sankey",
        ],
    )
    create_parser.add_argument("output", help="Output SVG file path")
    create_parser.add_argument("--data", "-d", help="Data file (CSV or JSON)")
    create_parser.add_argument("--config", "-c", help="Config file path")
    create_parser.add_argument(
        "--title", help="Chart title (overrides a title in the config file)"
    )
    create_parser.add_argument(
        "--width",
        type=int,
        help="Chart width in pixels (overrides the config file)",
    )
    create_parser.add_argument(
        "--height",
        type=int,
        help="Chart height in pixels (overrides the config file)",
    )
    create_parser.add_argument(
        "--transpose",
        action="store_true",
        help=(
            "Read the CSV in wide layout: each data row is a series and the "
            "header row supplies the x-axis labels. Default layout is the first "
            "column as x labels with each other column as a series."
        ),
    )
    create_parser.set_defaults(func="create")

    # Batch subcommand
    batch_parser = subparsers.add_parser(
        "batch", help="Generate multiple charts from a directory"
    )
    batch_parser.add_argument("input_dir", help="Input directory containing data files")
    batch_parser.add_argument("output_dir", help="Output directory for SVG files")
    batch_parser.add_argument(
        "--chart-type",
        "-t",
        choices=[
            "bar",
            "column",
            "line",
            "pie",
            "radar",
            "scatter",
            "area",
            "boxplot",
            "histogram",
            "heatmap",
            "gantt",
            "combo",
            "sankey",
        ],
        help="Override chart type inferred from filename",
    )
    batch_parser.add_argument("--config", "-c", help="Config file path")
    batch_parser.set_defaults(func="batch")

    parsed_args = parser.parse_args(args)

    if parsed_args.command is None:
        parser.print_help()
        sys.exit(1)

    # Import here to avoid circular imports
    if parsed_args.command == "create":
        from .cli.create import create_command

        create_command(parsed_args)
    elif parsed_args.command == "batch":
        from .cli.batch import batch_command

        batch_command(parsed_args)


if __name__ == "__main__":
    main()
