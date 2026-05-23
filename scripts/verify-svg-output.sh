#!/usr/bin/env bash
set -euo pipefail
CURRENT=$(git branch --show-current)
BASELINE="${1:-main}"
echo "=== SVG output comparison: $CURRENT vs $BASELINE ==="

compare_chart() {
    local name="$1" code="$2"
    git checkout "$BASELINE" 2>/dev/null
    python -c "$code" > /tmp/svg_base.svg
    git checkout "$CURRENT" 2>/dev/null
    python -c "$code" > /tmp/svg_cur.svg
    if diff /tmp/svg_base.svg /tmp/svg_cur.svg > /dev/null 2>&1; then
        echo "  $name: identical"
    else
        echo "  $name: DIFFERENT"
        diff /tmp/svg_base.svg /tmp/svg_cur.svg
        return 1
    fi
}

compare_chart bar          "from charted import BarChart; print(BarChart(data=[10,20,30],labels=['a','b','c']).html)"
compare_chart bar_multi    "from charted import BarChart; print(BarChart(data=[[10,20,30],[20,30,10]],labels=['a','b','c']).html)"
compare_chart column       "from charted import ColumnChart; print(ColumnChart(data=[10,20,30],labels=['a','b','c']).html)"
compare_chart column_side  "from charted import ColumnChart; print(ColumnChart(data=[[10,20,30],[20,30,10]],labels=['a','b','c'],y_stacked=False).html)"
compare_chart line         "from charted import LineChart; print(LineChart(data=[10,20,30],labels=['a','b','c']).html)"
compare_chart line_multi   "from charted import LineChart; print(LineChart(data=[[10,20,30],[20,30,10]],labels=['a','b','c']).html)"
compare_chart pie          "from charted import PieChart; print(PieChart(data=[10,20,30],labels=['a','b','c']).html)"
compare_chart pie_exploded "from charted import PieChart; print(PieChart(data=[10,20,30],labels=['a','b','c'],explode=[5,0,0]).html)"
compare_chart scatter      "from charted import ScatterChart; print(ScatterChart(x_data=[10,20,30],y_data=[10,20,30]).html)"
compare_chart radar        "from charted import RadarChart; print(RadarChart(data=[[10,20,30],[20,30,10]],labels=['a','b','c']).html)"

rm -f /tmp/svg_base.svg /tmp/svg_cur.svg
echo "Done"
