#!/bin/bash
# Run fuzz testing for CSV and JSON parsers
# This script runs atheris to find edge cases and potential bugs

set -e

echo "=== Fuzz Testing with atheris ==="
echo ""
echo "This will run fuzz testing on:"
echo "1. CSV parser - tests edge cases in CSV parsing"
echo "2. JSON parser - tests edge cases in JSON parsing"
echo ""
echo "Expected runtime: 5-30 minutes per fuzzer"
echo ""

# Install atheris if not already installed
if ! python -c "import atheris" 2>/dev/null; then
    echo "Installing atheris..."
    pip install atheris
fi

# Run CSV fuzzer
echo "=== Running CSV Parser Fuzzer ==="
echo "Press Ctrl+C to stop..."
python scripts/fuzz_csv_parser.py

# Run JSON fuzzer
echo ""
echo "=== Running JSON Parser Fuzzer ==="
echo "Press Ctrl+C to stop..."
python scripts/fuzz_json_parser.py

echo ""
echo "Fuzz testing complete!"
