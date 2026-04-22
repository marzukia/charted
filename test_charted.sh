#!/usr/bin/env bash
# test_charted.sh - verify charted installation works

echo "🧪 testing charted installation..."

# test 1: check if charted command exists
if ! command -v charted &> /dev/null; then
    echo "❌ charted command not found"
    exit 1
fi

echo "✅ charted command found"

# test 2: generate a simple bar chart
cat > /tmp/test_chart.py << 'EOF'
from charted import BarChart

# quick test
data = [10, 20, 15, 30, 25]
labels = ['A', 'B', 'C', 'D', 'E']
chart = BarChart(data, labels, title="Test Chart")
chart.save("/tmp/test_output.svg")
print("✅ chart generated: /tmp/test_output.svg")
EOF

python3 /tmp/test_chart.py
if [ $? -eq 0 ]; then
    echo "✅ chart generation successful"
else
    echo "❌ chart generation failed"
    exit 1
fi

# test 3: verify svg file exists and has content
if [ -s /tmp/test_output.svg ]; then
    echo "✅ svg file created with content ($(wc -c < /tmp/test_output.svg) bytes)"
else
    echo "❌ svg file is empty or missing"
    exit 1
fi

echo ""
echo "🎉 all tests passed! charted is working correctly."
echo ""
echo "next steps:"
echo "  - try the cli: charted --help"
echo "  - check docs: https://charted.readthedocs.io"
echo "  - report issues: https://github.com/marzukia/charted/issues"
