#!/usr/bin/env python3
"""Fuzz testing for CSV parser using atheris.

This script fuzzes the CSV parsing logic to find edge cases and potential bugs.
Run with: python scripts/fuzz_csv_parser.py

Note: Install atheris first: pip install atheris
"""

import sys
from io import StringIO

import atheris


def TestOneInput(data: bytes) -> int:
    """Fuzz test function for CSV parsing.

    Args:
        data: Random bytes to parse as CSV

    Returns:
        0 if parsing succeeded without exceptions
    """
    # Convert bytes to string, handling encoding errors
    try:
        csv_content = data.decode("utf-8", errors="replace")
    except Exception:
        return 0

    # Skip empty or very small inputs
    if len(csv_content) < 2:
        return 0

    # Try to parse as CSV
    try:
        import csv

        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        # If we got here, parsing succeeded
        # Optionally validate row structure
        if rows:
            # Check that all rows have same columns
            first_keys = set(rows[0].keys())
            for row in rows[1:]:
                if set(row.keys()) != first_keys:
                    # Inconsistent columns - might be a bug
                    pass

    except (csv.Error, UnicodeDecodeError, ValueError, KeyError):
        # Expected exceptions during fuzzing
        pass
    except Exception as e:
        # Unexpected exception - might indicate a bug
        print(f"Unexpected error: {e}")
        raise

    return 0


def main():
    """Main entry point for fuzz testing."""
    atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
