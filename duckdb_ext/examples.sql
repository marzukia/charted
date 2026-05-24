-- DuckDB + Charted Extension: SQL UDF Examples
--
-- These examples use charted_from_arrays() and charted_svg_from_arrays()
-- which are registered as SQL UDFs. They accept JSON-encoded arrays.
--
-- For the simpler query-based workflow, use the Python API directly:
--   from charted.duckdb_ext.extension import charted_query
--   charted_query(con, 'SELECT ...', chart_type='bar', output='/tmp/out.svg')

-- Create sample data
CREATE OR REPLACE TABLE sales (
    quarter VARCHAR, revenue DOUBLE, costs DOUBLE, profit DOUBLE
);
INSERT INTO sales VALUES
    ('Q1 2024', 150000, 90000, 60000),
    ('Q2 2024', 180000, 95000, 85000),
    ('Q3 2024', 210000, 100000, 110000),
    ('Q4 2024', 250000, 120000, 130000),
    ('Q1 2025', 230000, 110000, 120000),
    ('Q2 2025', 270000, 125000, 145000);

-- Single-series bar chart from SQL
SELECT charted_from_arrays(
    (SELECT to_json(list(quarter)) FROM sales),
    (SELECT to_json(list(revenue)) FROM sales),
    'bar',
    'Revenue by Quarter',
    '/tmp/sql_bar.svg'
);

-- Multi-series column chart
SELECT charted_from_arrays(
    (SELECT to_json(list(quarter)) FROM sales),
    (SELECT to_json([list(revenue), list(costs), list(profit)]) FROM sales),
    'column',
    'Financial Overview',
    '/tmp/sql_column_multi.svg'
);

-- Get SVG as string (for embedding in reports)
SELECT charted_svg_from_arrays(
    (SELECT to_json(list(quarter)) FROM sales),
    (SELECT to_json(list(profit)) FROM sales),
    'line',
    'Profit Trend'
) AS svg_content;

-- Pie chart from aggregated subquery
SELECT charted_from_arrays(
    (SELECT to_json(list(quarter)) FROM sales WHERE quarter LIKE '%2024%'),
    (SELECT to_json(list(profit)) FROM sales WHERE quarter LIKE '%2024%'),
    'pie',
    '2024 Profit Distribution',
    '/tmp/sql_pie.svg'
);
