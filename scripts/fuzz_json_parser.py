#!/usr/bin/env python3
"""Fuzz testing for JSON parsing using atheris.

This script fuzzes the JSON parsing logic to find edge cases and potential bugs.
Run with: python scripts/fuzz_json_parser.py

Note: Install atheris first: pip install atheris
"""

import sys

import atheris


def TestOneInput(data: bytes) -> int:
    """Fuzz test function for JSON parsing.

    Args:
        data: Random bytes to parse as JSON

    Returns:
        0 if parsing succeeded without exceptions
    """
    # Convert bytes to string, handling encoding errors
    try:
        json_content = data.decode("utf-8", errors="replace")
    except Exception:
        return 0

    # Skip empty or very small inputs
    if len(json_content) < 2:
        return 0

    # Try to parse as JSON
    try:
        import json

        parsed = json.loads(json_content)

        # Validate that it's a dict (our expected format)
        if isinstance(parsed, dict):
            # Check for expected keys
            if "data" in parsed or "labels" in parsed:
                # This looks like valid chart data
                pass

    except json.JSONDecodeError:
        # Expected - invalid JSON
        pass
    except Exception as e:
        # Unexpected exception
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
