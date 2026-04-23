"""CLI entry point for charted."""

import argparse
import sys


def main(args=None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="charted",
        description="Generate SVG charts from the command line",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create subcommand
    create_parser = subparsers.add_parser("create", help="Create a new chart")
    create_parser.add_argument(
        "chart_type", choices=["bar", "column", "line", "pie", "scatter"]
    )
    create_parser.add_argument("output", help="Output SVG file path")
    create_parser.add_argument("--data", "-d", help="Data file (CSV or JSON)")
    create_parser.add_argument(
        "--data-inline", help="Inline data values (comma-separated, e.g. '10,20,30')"
    )
    create_parser.add_argument(
        "--labels", help="Labels for data points (comma-separated, e.g. 'A,B,C')"
    )
    create_parser.add_argument(
        "--x-data", help="X-coordinates for scatter plots (comma-separated)"
    )
    create_parser.add_argument(
        "--y-data", help="Y-coordinates for scatter plots (comma-separated)"
    )
    create_parser.add_argument("--title", help="Chart title")
    create_parser.add_argument("--config", "-c", help="Config file path")
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
        choices=["bar", "column", "line", "pie", "scatter"],
        help="Override chart type inferred from filename",
    )
    batch_parser.add_argument("--config", "-c", help="Config file path")
    batch_parser.set_defaults(func="batch")

    args = parser.parse_args(args)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Import here to avoid circular imports
    if args.command == "create":
        from .cli.create import create_command

        create_command(args)
    elif args.command == "batch":
        from .cli.batch import batch_command

        batch_command(args)


if __name__ == "__main__":
    main()
