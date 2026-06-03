"""Tests for create CLI command and data loading."""

import csv
import json
import tempfile
from pathlib import Path

import pytest

from charted.cli.create import _parse_csv, create_command, load_data


def _ns(**kwargs):
    """Build an argparse.Namespace with CLI defaults filled in.

    Tests only need to set the fields they care about; everything else
    falls back to the same defaults argparse would supply.
    """
    import argparse

    defaults = {
        "chart_type": "bar",
        "output": None,
        "data": None,
        "config": None,
        "title": None,
        "width": None,
        "height": None,
        "transpose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestLoadData:
    """Test load_data function for CSV and JSON files."""

    def test_load_json_data(self):
        """Test loading data from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.json"
            data = {"labels": ["A", "B"], "data": [10, 20]}
            data_file.write_text(json.dumps(data))

            result = load_data(str(data_file))
            assert result == data

    def test_load_csv_single_series(self):
        """Test loading single series from CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            # Simple CSV with labels in first column, data in second
            data_file.write_text("label,value\nA,10\nB,20\nC,30")

            result = load_data(str(data_file))
            assert "data" in result
            assert "labels" in result
            assert result["labels"] == ["A", "B", "C"]
            assert result["data"] == [10.0, 20.0, 30.0]

    def test_load_csv_multi_series(self):
        """Test loading multi-series data from CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            # CSV with multiple data columns
            data_file.write_text("label,series1,series2\nA,10,15\nB,20,25\nC,30,35")

            result = load_data(str(data_file))
            assert "data" in result
            assert "labels" in result
            assert result["labels"] == ["A", "B", "C"]
            assert len(result["data"]) == 2  # Two series
            assert result["data"][0] == [10.0, 20.0, 30.0]
            assert result["data"][1] == [15.0, 25.0, 35.0]

    def test_load_csv_with_text_values(self):
        """Test CSV with non-numeric values (preserved as strings)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            data_file.write_text("label,value\nA,10\nB,text\nC,30")

            result = load_data(str(data_file))
            # Text values should be preserved
            assert result["data"] == [10.0, "text", 30.0]

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_data("/nonexistent/path/file.csv")

    def test_load_unsupported_format(self):
        """Test loading unsupported file format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.txt"
            data_file.write_text("some text")

            with pytest.raises(ValueError, match="Unsupported file format"):
                load_data(str(data_file))

    def test_load_empty_csv(self):
        """Test loading empty CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            data_file.write_text("")

            result = load_data(str(data_file))
            assert result == {"data": []}


class TestParseCSV:
    """Test CSV parsing function."""

    def test_parse_csv_basic(self):
        """Test basic CSV parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            data_file.write_text("label,value\nA,10\nB,20")

            result = _parse_csv(data_file)
            assert result["labels"] == ["A", "B"]
            assert result["data"] == [10.0, 20.0]

    def test_parse_csv_empty(self):
        """Test parsing empty CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            data_file.write_text("")

            result = _parse_csv(data_file)
            assert result == {"data": []}

    def test_parse_csv_single_column(self):
        """Test CSV with only label column."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.csv"
            data_file.write_text("label\nA\nB\nC")

            result = _parse_csv(data_file)
            assert result["labels"] == ["A", "B", "C"]
            assert result["data"] == []


class TestCreateCommand:
    """Test create command integration."""

    def test_create_bar_chart(self):
        """Test creating a bar chart via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"
            # Provide default data
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()
            assert output_file.stat().st_size > 0
            content = output_file.read_text()
            assert "<svg" in content

    def test_create_column_chart(self):
        """Test creating a column chart via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="column",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()
            assert "<path" in output_file.read_text().lower()

    def test_create_line_chart(self):
        """Test creating a line chart via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="line",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_pie_chart(self):
        """Test creating a pie chart via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="pie",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_scatter_chart(self):
        """Test creating a scatter chart via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"
            data_file = Path(tmpdir) / "data.json"
            # Scatter needs x_data and y_data
            data_file.write_text(json.dumps({"x_data": [1, 2], "y_data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="scatter",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_radar_chart(self):
        """Test creating a radar chart via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="radar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_with_json_data(self):
        """Test creating chart with JSON data file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "data.json"
            output_file = Path(tmpdir) / "output.svg"
            data = {"labels": ["A", "B", "C"], "data": [10, 20, 30]}
            data_file.write_text(json.dumps(data))

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_with_csv_data(self):
        """Test creating chart with CSV data file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "data.csv"
            output_file = Path(tmpdir) / "output.svg"
            data_file.write_text("label,value\nA,10\nB,20\nC,30")

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_creates_parent_directories(self):
        """Test that create command creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "nested" / "dir" / "output.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_create_unknown_chart_type(self, capsys):
        """Test create with unknown chart type exits with error."""
        import argparse

        args = argparse.Namespace(
            chart_type="invalid",
            output="/tmp/test.svg",
            data=None,
            config=None,
        )

        # Simulate the check in create_command
        from charted.cli.create import CHART_TYPES

        if "invalid" not in CHART_TYPES:
            with pytest.raises(SystemExit) as exc_info:
                create_command(args)
            assert exc_info.value.code == 1

    def test_create_invalid_data_file(self, capsys):
        """Test create with invalid data file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.svg"

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data="/nonexistent/file.json",
                config=None,
            )

            with pytest.raises(SystemExit) as exc_info:
                create_command(args)
            assert exc_info.value.code == 1

            # Check error message
            captured = capsys.readouterr()
            assert "not found" in captured.err.lower()

    def test_create_with_invalid_json(self, capsys):
        """Test create with invalid JSON data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "invalid.json"
            output_file = Path(tmpdir) / "output.svg"
            data_file.write_text("{invalid json}")

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            # Should raise JSON decode error or chart creation error
            with pytest.raises(SystemExit) as exc_info:
                create_command(args)
            assert exc_info.value.code == 1


class TestCLIIntegration:
    """End-to-end CLI integration tests."""

    def test_full_workflow_json(self):
        """Test complete workflow: create JSON data, generate chart."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create data file
            data_file = Path(tmpdir) / "sales.json"
            sales_data = {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "data": [150, 200, 175, 225],
            }
            data_file.write_text(json.dumps(sales_data))

            # Generate chart
            output_file = Path(tmpdir) / "sales.svg"

            import argparse

            args = argparse.Namespace(
                chart_type="column",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            # Verify output
            assert output_file.exists()
            content = output_file.read_text()
            assert "Q1" in content
            assert "Q2" in content
            assert "<svg" in content

    def test_full_workflow_csv_multi_series(self):
        """Test complete workflow with multi-series CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multi-series CSV - need proper format for bar chart
            data_file = Path(tmpdir) / "comparison.csv"
            with open(data_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Month", "Product A", "Product B"])
                writer.writerow(["Jan", 100, 120])
                writer.writerow(["Feb", 150, 140])
                writer.writerow(["Mar", 180, 160])

            # Generate chart
            output_file = Path(tmpdir) / "comparison.svg"

            import argparse

            args = argparse.Namespace(
                chart_type="bar",
                output=str(output_file),
                data=str(data_file),
                config=None,
            )

            create_command(args)

            assert output_file.exists()

    def test_multiple_chart_types_same_data(self):
        """Test generating multiple chart types from same data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create data file
            data_file = Path(tmpdir) / "data.json"
            data = {"labels": ["A", "B", "C"], "data": [10, 20, 30]}
            data_file.write_text(json.dumps(data))

            chart_types = ["bar", "column", "line", "pie"]

            for chart_type in chart_types:
                output_file = Path(tmpdir) / f"{chart_type}.svg"

                import argparse

                args = argparse.Namespace(
                    chart_type=chart_type,
                    output=str(output_file),
                    data=str(data_file),
                    config=None,
                )

                create_command(args)

                assert output_file.exists()


class TestTitleAndDimensions:
    """Test --title, --width, --height CLI options."""

    def test_title_sets_chart_title(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "out.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            create_command(
                _ns(output=str(output_file), data=str(data_file), title="My Report")
            )

            content = output_file.read_text()
            assert "My Report" in content

    def test_width_and_height_change_dimensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "out.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))

            create_command(
                _ns(
                    output=str(output_file),
                    data=str(data_file),
                    width=900,
                    height=400,
                )
            )

            content = output_file.read_text()
            assert 'width="900"' in content
            assert 'height="400"' in content
            assert 'viewBox="0 0 900 400"' in content

    def test_cli_title_overrides_config(self):
        """A --title flag takes precedence over a title in the config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "out.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))
            config_file = Path(tmpdir) / "cfg.json"
            config_file.write_text(json.dumps({"title": "From Config", "width": 600}))

            create_command(
                _ns(
                    output=str(output_file),
                    data=str(data_file),
                    config=str(config_file),
                    title="From CLI",
                )
            )

            content = output_file.read_text()
            assert "From CLI" in content
            assert "From Config" not in content

    def test_config_title_used_when_no_cli_flag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "out.svg"
            data_file = Path(tmpdir) / "data.json"
            data_file.write_text(json.dumps({"labels": ["A", "B"], "data": [10, 20]}))
            config_file = Path(tmpdir) / "cfg.json"
            config_file.write_text(json.dumps({"title": "From Config"}))

            create_command(
                _ns(
                    output=str(output_file),
                    data=str(data_file),
                    config=str(config_file),
                )
            )

            assert "From Config" in output_file.read_text()


class TestCSVOrientation:
    """Test CSV orientation handling and the --transpose flag."""

    def test_default_orientation_series_per_column(self):
        """Default: first column is x labels, each other column is a series."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "data.csv"
            data_file.write_text("Quarter,Revenue\nQ1,120\nQ2,180\nQ3,210")

            result = load_data(str(data_file))
            assert result["labels"] == ["Q1", "Q2", "Q3"]
            assert result["data"] == [120.0, 180.0, 210.0]

    def test_transpose_series_per_row(self):
        """With transpose=True, each data row is a series and the header row
        (minus the corner cell) supplies the x labels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "data.csv"
            # Wide layout: series live on rows, x values across the header.
            data_file.write_text(
                "Series,Q1,Q2,Q3\nRevenue,120,180,210\nExpenses,80,95,110"
            )

            result = load_data(str(data_file), transpose=True)
            assert result["labels"] == ["Q1", "Q2", "Q3"]
            assert result["data"] == [[120.0, 180.0, 210.0], [80.0, 95.0, 110.0]]
            assert result["series_names"] == ["Revenue", "Expenses"]

    def test_transpose_single_series_per_row(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "data.csv"
            data_file.write_text("Series,Q1,Q2,Q3\nRevenue,120,180,210")

            result = load_data(str(data_file), transpose=True)
            assert result["labels"] == ["Q1", "Q2", "Q3"]
            assert result["data"] == [120.0, 180.0, 210.0]
            assert result["series_names"] == ["Revenue"]

    def test_transpose_via_create_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "out.svg"
            data_file = Path(tmpdir) / "data.csv"
            data_file.write_text(
                "Series,Q1,Q2,Q3\nRevenue,120,180,210\nExpenses,80,95,110"
            )

            create_command(
                _ns(
                    chart_type="column",
                    output=str(output_file),
                    data=str(data_file),
                    transpose=True,
                )
            )

            content = output_file.read_text()
            assert "Q1" in content
            assert "Q2" in content
            assert "<svg" in content
