#!/bin/bash
# Run mutation testing with mutmut
# This script should be run quarterly to identify weak tests

set -e

echo "=== Mutation Testing with mutmut ==="
echo ""
echo "This will:"
echo "1. Run initial test suite to establish baseline"
echo "2. Generate mutants and test each one"
echo "3. Report mutation score (percentage of mutants killed)"
echo ""
echo "Expected runtime: 10-30 minutes depending on test suite size"
echo ""

# Install mutmut if not already installed
if ! uv pip show mutmut > /dev/null 2>&1; then
    echo "Installing mutmut..."
    uv pip install mutmut
fi

# Run mutation testing
echo "Running mutation testing..."
mutmut run

# Show results
echo ""
echo "=== Mutation Testing Results ==="
mutmut results

echo ""
echo "To review individual mutants, run:"
echo "  mutmut show"
