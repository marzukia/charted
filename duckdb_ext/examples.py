#!/usr/bin/env python3
"""Example usage of the charted DuckDB extension.

Demonstrates both the Python API (charted_query) and the SQL UDF approach.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from duckdb_ext.extension import load, charted_query, charted_svg


def main():
    output_dir = Path("/tmp/charted_duckdb_examples")
    output_dir.mkdir(parents=True, exist_ok=True)

    con = load()

    # --- Create sample tables ---
    con.execute("""
        CREATE TABLE sales (
            quarter VARCHAR,
            revenue DOUBLE,
            costs DOUBLE,
            profit DOUBLE
        );
        INSERT INTO sales VALUES
            ('Q1 2024', 150000, 90000, 60000),
            ('Q2 2024', 180000, 95000, 85000),
            ('Q3 2024', 210000, 100000, 110000),
            ('Q4 2024', 250000, 120000, 130000),
            ('Q1 2025', 230000, 110000, 120000),
            ('Q2 2025', 270000, 125000, 145000);
    """)

    con.execute("""
        CREATE TABLE monthly_temps (
            month VARCHAR,
            new_york DOUBLE,
            london DOUBLE,
            tokyo DOUBLE
        );
        INSERT INTO monthly_temps VALUES
            ('Jan', -1, 5, 6), ('Feb', 0, 6, 7), ('Mar', 5, 9, 10),
            ('Apr', 11, 12, 15), ('May', 17, 15, 20), ('Jun', 22, 18, 23),
            ('Jul', 25, 21, 27), ('Aug', 24, 20, 28), ('Sep', 20, 17, 24),
            ('Oct', 14, 13, 18), ('Nov', 8, 9, 12), ('Dec', 2, 6, 8);
    """)

    con.execute("""
        CREATE TABLE market_share (
            company VARCHAR,
            share DOUBLE
        );
        INSERT INTO market_share VALUES
            ('Apple', 28.5), ('Samsung', 19.2), ('Xiaomi', 12.8),
            ('Oppo', 8.6), ('Others', 30.9);
    """)

    con.execute("""
        CREATE TABLE sensor_data AS
        SELECT i AS reading_id,
               20 + (random() * 15) AS temperature,
               40 + (random() * 40) AS humidity
        FROM generate_series(1, 50) t(i);
    """)

    print("=== Python API: charted_query() ===\n")

    # 1. Bar chart — single series
    path = charted_query(con, 'SELECT quarter, revenue FROM sales',
                         chart_type='bar', title='Quarterly Revenue',
                         output=f'{output_dir}/bar_revenue.svg')
    print(f"  Bar (single):    {path}")

    # 2. Bar chart — multi-series
    path = charted_query(con, 'SELECT quarter, revenue, costs, profit FROM sales',
                         chart_type='bar', title='Revenue vs Costs vs Profit',
                         output=f'{output_dir}/bar_multi.svg')
    print(f"  Bar (multi):     {path}")

    # 3. Line chart
    path = charted_query(con, 'SELECT month, new_york, london, tokyo FROM monthly_temps',
                         chart_type='line', title='Monthly Temperatures (C)',
                         output=f'{output_dir}/line_temps.svg')
    print(f"  Line:            {path}")

    # 4. Pie chart
    path = charted_query(con, 'SELECT company, share FROM market_share',
                         chart_type='pie', title='Smartphone Market Share',
                         output=f'{output_dir}/pie_market.svg')
    print(f"  Pie:             {path}")

    # 5. Column chart
    path = charted_query(con, 'SELECT quarter, profit FROM sales',
                         chart_type='column', title='Quarterly Profit',
                         output=f'{output_dir}/column_profit.svg')
    print(f"  Column:          {path}")

    # 6. Area chart
    path = charted_query(con, 'SELECT month, new_york, london FROM monthly_temps',
                         chart_type='area', title='NY vs London Temps',
                         output=f'{output_dir}/area_temps.svg')
    print(f"  Area:            {path}")

    # 7. Scatter chart
    path = charted_query(con, 'SELECT temperature, humidity FROM sensor_data',
                         chart_type='scatter', title='Temp vs Humidity',
                         output=f'{output_dir}/scatter_sensor.svg')
    print(f"  Scatter:         {path}")

    # 8. Histogram
    path = charted_query(con, 'SELECT temperature FROM sensor_data',
                         chart_type='histogram', title='Temperature Distribution',
                         output=f'{output_dir}/histogram_temp.svg')
    print(f"  Histogram:       {path}")

    # 9. SVG string (no file)
    svg = charted_svg(con, 'SELECT company, share FROM market_share',
                      chart_type='pie', title='Market Share')
    print(f"  SVG string:      {len(svg)} bytes")

    # 10. Complex query with CTE
    path = charted_query(con,
        """WITH ranked AS (
            SELECT quarter, profit,
                   ROW_NUMBER() OVER (ORDER BY profit DESC) as rank
            FROM sales
        )
        SELECT quarter, profit FROM ranked WHERE rank <= 4""",
        chart_type='bar', title='Top 4 Quarters by Profit',
        output=f'{output_dir}/bar_top_quarters.svg')
    print(f"  Bar (CTE):       {path}")

    print("\n=== SQL UDF: charted_from_arrays() ===\n")

    # Using the SQL UDF with JSON-encoded arrays
    result = con.execute(f"""
        SELECT charted_from_arrays(
            (SELECT to_json(list(quarter)) FROM sales),
            (SELECT to_json(list(revenue)) FROM sales),
            'bar',
            'Revenue (SQL UDF)',
            '{output_dir}/sql_udf_bar.svg'
        )
    """).fetchone()
    print(f"  SQL UDF bar:     {result[0]}")

    # Multi-series via SQL
    result = con.execute(f"""
        SELECT charted_from_arrays(
            (SELECT to_json(list(quarter)) FROM sales),
            (SELECT to_json([list(revenue), list(costs)]) FROM sales),
            'column',
            'Revenue & Costs (SQL UDF)',
            '{output_dir}/sql_udf_column.svg'
        )
    """).fetchone()
    print(f"  SQL UDF column:  {result[0]}")

    # SVG from SQL
    result = con.execute("""
        SELECT charted_svg_from_arrays(
            (SELECT to_json(list(company)) FROM market_share),
            (SELECT to_json(list(share)) FROM market_share),
            'pie',
            'Market Share (SQL)'
        )
    """).fetchone()
    print(f"  SQL UDF SVG:     {len(result[0])} bytes")

    # --- Validate outputs ---
    print("\n=== Validation ===\n")
    svg_files = sorted(output_dir.glob("*.svg"))
    all_ok = True
    for svg_file in svg_files:
        content = svg_file.read_text()
        if "<svg" in content:
            print(f"  OK   {svg_file.name} ({len(content):,} bytes)")
        else:
            print(f"  FAIL {svg_file.name}")
            all_ok = False

    print(f"\n{'All' if all_ok else 'Some'} {len(svg_files)} charts validated in {output_dir}/")


if __name__ == "__main__":
    main()
