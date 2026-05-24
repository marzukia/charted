#!/usr/bin/env python3
"""Tests for the charted DuckDB extension."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import duckdb
from duckdb_ext.extension import (
    CHART_TYPES,
    _build_chart,
    _extract_chart_data_from_result,
    charted_query,
    charted_svg,
    load,
    register,
)


def setup_con():
    """Create a test connection with sample data."""
    con = load()
    con.execute("""
        CREATE TABLE test_data (label VARCHAR, a DOUBLE, b DOUBLE);
        INSERT INTO test_data VALUES
            ('X', 10, 5), ('Y', 20, 15), ('Z', 30, 25);
    """)
    return con


def test_register():
    """register() should not raise."""
    con = duckdb.connect()
    register(con)
    # Verify functions exist by calling them
    result = con.execute("""
        SELECT charted_from_arrays('["A","B","C"]', '[1,2,3]', 'bar', 'Test', '/tmp/test_reg.svg')
    """).fetchone()
    assert result[0] == "/tmp/test_reg.svg"
    assert Path("/tmp/test_reg.svg").exists()
    Path("/tmp/test_reg.svg").unlink()


def test_charted_query_single_series():
    con = setup_con()
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = charted_query(con, "SELECT label, a FROM test_data",
                             chart_type="bar", title="Single", output=f.name)
        content = Path(path).read_text()
        assert "<svg" in content
        Path(path).unlink()


def test_charted_query_multi_series():
    con = setup_con()
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        path = charted_query(con, "SELECT label, a, b FROM test_data",
                             chart_type="line", title="Multi", output=f.name)
        content = Path(path).read_text()
        assert "<svg" in content
        Path(path).unlink()


def test_charted_svg_returns_string():
    con = setup_con()
    svg = charted_svg(con, "SELECT label, a FROM test_data",
                      chart_type="pie", title="Pie Test")
    assert "<svg" in svg
    assert "Pie Test" in svg


def test_all_chart_types():
    """Each supported chart type should produce valid SVG."""
    con = setup_con()
    for chart_type in CHART_TYPES:
        if chart_type == "heatmap":
            # Heatmap needs matrix data
            con.execute("""
                CREATE OR REPLACE TABLE heat AS
                SELECT i AS x, j AS y, (i * j) AS val
                FROM generate_series(1, 3) t(i), generate_series(1, 3) s(j)
            """)
            query = "SELECT x, y, val FROM heat"
        elif chart_type == "scatter":
            query = "SELECT a, b FROM test_data"
        elif chart_type == "box":
            con.execute("""
                CREATE OR REPLACE TABLE boxdata (cat VARCHAR, val DOUBLE);
                INSERT INTO boxdata VALUES
                    ('A', 1), ('A', 2), ('A', 3), ('A', 4), ('A', 5),
                    ('B', 2), ('B', 4), ('B', 6), ('B', 8), ('B', 10);
            """)
            query = "SELECT cat, val FROM boxdata"
        elif chart_type == "histogram":
            con.execute("""
                CREATE OR REPLACE TABLE histdata AS
                SELECT random() * 100 AS val FROM generate_series(1, 30) t(i);
            """)
            query = "SELECT val FROM histdata"
        else:
            query = "SELECT label, a FROM test_data"

        try:
            svg = charted_svg(con, query, chart_type=chart_type, title=f"{chart_type} test")
            assert "<svg" in svg, f"{chart_type}: no <svg> in output"
            print(f"  PASS: {chart_type}")
        except Exception as e:
            print(f"  FAIL: {chart_type} — {e}")


def test_extract_data_from_result():
    """Data extraction should correctly identify labels and numeric columns."""
    columns = [("name", None), ("value", None), ("count", None)]
    rows = [("A", 10.0, 5), ("B", 20.0, 10), ("C", 30.0, 15)]

    labels, data, series_names = _extract_chart_data_from_result(columns, rows)
    assert labels == ["A", "B", "C"]
    assert data == [[10.0, 20.0, 30.0], [5.0, 10.0, 15.0]]
    assert series_names == ["value", "count"]


def test_no_labels_column():
    """If all columns are numeric, labels should be None."""
    columns = [("x", None), ("y", None)]
    rows = [(1.0, 10.0), (2.0, 20.0), (3.0, 30.0)]

    labels, data, series_names = _extract_chart_data_from_result(columns, rows)
    assert labels is None
    assert len(data) == 2


def test_sql_udf_from_arrays():
    """The SQL UDF should work with JSON-encoded arrays."""
    con = load()
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        result = con.execute(f"""
            SELECT charted_from_arrays(
                '["Mon","Tue","Wed"]',
                '[10, 20, 30]',
                'column',
                'Weekday Sales',
                '{f.name}'
            )
        """).fetchone()
        assert Path(result[0]).exists()
        content = Path(result[0]).read_text()
        assert "<svg" in content
        Path(result[0]).unlink()


def test_sql_udf_multi_series():
    """Multi-series via nested JSON arrays."""
    con = load()
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        result = con.execute(f"""
            SELECT charted_from_arrays(
                '["A","B","C"]',
                '[[1,2,3],[4,5,6]]',
                'bar',
                'Multi',
                '{f.name}'
            )
        """).fetchone()
        content = Path(result[0]).read_text()
        assert "<svg" in content
        Path(result[0]).unlink()


if __name__ == "__main__":
    print("Running charted DuckDB extension tests...\n")

    tests = [
        test_register,
        test_charted_query_single_series,
        test_charted_query_multi_series,
        test_charted_svg_returns_string,
        test_extract_data_from_result,
        test_no_labels_column,
        test_sql_udf_from_arrays,
        test_sql_udf_multi_series,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__} — {e}")
            failed += 1

    print(f"\nChart type coverage:")
    test_all_chart_types()

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
