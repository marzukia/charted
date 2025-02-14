"""CLI tests for charted - Happy Path and Sad Path testing.

This module contains tests for the CLI entry point and commands.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from charted.__main__ import main
from charted.cli.batch import _infer_chart_type, batch_command
from charted.cli.create import load_data


class TestCLIEntryHappyPath:
    """Happy path tests for CLI entry point."""

    def test_cli_help(self, capsys):
        """Test that --help shows usage information."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "charted" in captured.out.lower()
        assert "create" in captured.out.lower()
        assert "batch" in captured.out.lower()

    def test_cli_create_bar_chart(self, tmp_path):
        """Test creating a basic bar chart via CLI."""
        output_path = tmp_path / "test_bar.svg"

        # Create test data file
        data = {"data": [10, 20, 30], "labels": ["a", "b", "c"]}
        data_file = tmp_path / "test_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        main(["create", "bar", str(output_path), "--data", str(data_file)])

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        svg_content = output_path.read_text()
        assert "svg" in svg_content.lower()

    def test_cli_create_column_chart(self, tmp_path):
        """Test creating a column chart via CLI."""
        output_path = tmp_path / "test_column.svg"

        data = {"data": [15, 25, 35], "labels": ["x", "y", "z"]}
        data_file = tmp_path / "test_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        main(["create", "column", str(output_path), "--data", str(data_file)])

        assert output_path.exists()

    def test_cli_create_line_chart(self, tmp_path):
        """Test creating a line chart via CLI."""
        output_path = tmp_path / "test_line.svg"

        data = {"data": [10, 20, 30], "labels": ["a", "b", "c"]}
        data_file = tmp_path / "test_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        main(["create", "line", str(output_path), "--data", str(data_file)])

        assert output_path.exists()

    def test_cli_create_pie_chart(self, tmp_path):
        """Test creating a pie chart via CLI."""
        output_path = tmp_path / "test_pie.svg"

        data = {"data": [30, 20, 50], "labels": ["a", "b", "c"]}
        data_file = tmp_path / "test_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        main(["create", "pie", str(output_path), "--data", str(data_file)])

        assert output_path.exists()

    def test_cli_create_scatter_chart(self, tmp_path):
        """Test creating a scatter chart via CLI."""
        output_path = tmp_path / "test_scatter.svg"

        # Scatter uses x_data/y_data format
        data = {"x_data": [1, 2, 3], "y_data": [2, 4, 6]}
        data_file = tmp_path / "test_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        main(["create", "scatter", str(output_path), "--data", str(data_file)])

        assert output_path.exists()

    def test_cli_create_without_data(self, tmp_path):
        """Test creating chart without data file (uses defaults)."""
        output_path = tmp_path / "test_no_data.svg"

        # This should fail because data is required
        with pytest.raises(SystemExit):
            main(["create", "bar", str(output_path)])


class TestCLIEntrySadPath:
    """Sad path tests for CLI entry point."""

    def test_cli_no_command(self, capsys):
        """Test that running without command shows help and exits."""
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "usage" in captured.out.lower()

    def test_cli_invalid_chart_type(self, tmp_path):
        """Test that invalid chart type fails gracefully."""
        output_path = tmp_path / "test.svg"

        with pytest.raises(SystemExit) as exc_info:
            main(["create", "invalid", str(output_path)])

        assert exc_info.value.code != 0


class TestDataLoadingHappyPath:
    """Happy path tests for data loading."""

    def test_load_json_data(self):
        """Test loading JSON data file."""
        data = {"data": [10, 20, 30], "labels": ["a", "b", "c"]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            assert loaded["data"] == [10, 20, 30]
            assert loaded["labels"] == ["a", "b", "c"]
        finally:
            Path(temp_path).unlink()

    def test_load_csv_data(self):
        """Test loading CSV data file."""
        csv_content = """label,value1,value2
a,10,15
b,20,25
c,30,35
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            assert "data" in loaded
            assert "labels" in loaded
            assert loaded["labels"] == ["a", "b", "c"]
        finally:
            Path(temp_path).unlink()

    def test_load_csv_single_column(self):
        """Test loading CSV with single data column."""
        csv_content = """label,value
a,10
b,20
c,30
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            assert loaded["data"] == [10.0, 20.0, 30.0]
            assert loaded["labels"] == ["a", "b", "c"]
        finally:
            Path(temp_path).unlink()


class TestDataLoadingSadPath:
    """Sad path tests for data loading."""

    def test_load_file_not_found(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Data file not found"):
            load_data("/nonexistent/path/data.csv")

    def test_load_unsupported_format(self):
        """Test that unsupported file format raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("some data")
            temp_txt_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                load_data(temp_txt_path)
        finally:
            Path(temp_txt_path).unlink()

    def test_load_csv_with_non_numeric_values(self):
        """Test CSV parsing handles non-numeric values."""
        csv_content = """label,value
a,10
b,text
c,30
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            # Non-numeric value should be kept as string
            assert "text" in loaded["data"]
        finally:
            Path(temp_path).unlink()


class TestCreateCommandSadPath:
    """Sad path tests for create command."""

    def test_create_unknown_chart_type(self, tmp_path, capsys):
        """Test that unknown chart type fails gracefully."""
        output_path = tmp_path / "test.svg"

        import argparse

        args = argparse.Namespace(
            chart_type="unknown",
            output=str(output_path),
            data=None,
        )

        from charted.cli.create import create_command

        with pytest.raises(SystemExit) as exc_info:
            create_command(args)
        assert exc_info.value.code == 1

    def test_create_chart_error(self, tmp_path):
        """Test chart creation error handling."""
        output_path = tmp_path / "test.svg"

        # Create data that will cause chart creation to fail
        data = {"data": None, "labels": None}
        data_file = tmp_path / "bad_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        import argparse

        args = argparse.Namespace(
            chart_type="bar",
            output=str(output_path),
            data=str(data_file),
        )

        from charted.cli.create import create_command

        with pytest.raises(SystemExit) as exc_info:
            create_command(args)
        assert exc_info.value.code == 1

    def test_load_empty_csv(self):
        """Test loading empty CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            assert loaded == {"data": []}
        finally:
            Path(temp_path).unlink()

    def test_load_csv_with_non_numeric_values(self):
        """Test loading CSV with mixed numeric/non-numeric values."""
        csv_content = """label,value
a,10
b,invalid
c,30
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            # Non-numeric values should be kept as strings
            assert loaded["data"] == [10.0, "invalid", 30.0]
            assert loaded["labels"] == ["a", "b", "c"]
        finally:
            Path(temp_path).unlink()

    def test_load_json_with_extra_fields(self):
        """Test loading JSON with extra fields beyond data/labels."""
        data = {"data": [10, 20, 30], "labels": ["a", "b", "c"], "extra": "field"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            loaded = load_data(temp_path)
            assert loaded["data"] == [10, 20, 30]
            assert loaded["labels"] == ["a", "b", "c"]
            assert loaded["extra"] == "field"
        finally:
            Path(temp_path).unlink()


class TestChartTypeInference:
    """Tests for chart type inference from filenames."""

    def test_infer_bar_from_filename(self):
        """Test bar chart inference."""
        assert _infer_chart_type("bar_data.csv") == "bar"
        assert _infer_chart_type("my_bar_chart.json") == "bar"

    def test_infer_column_from_filename(self):
        """Test column chart inference."""
        assert _infer_chart_type("column_data.csv") == "column"
        assert _infer_chart_type("my_column_chart.json") == "column"

    def test_infer_line_from_filename(self):
        """Test line chart inference."""
        assert _infer_chart_type("line_data.csv") == "line"
        assert _infer_chart_type("my_line_chart.json") == "line"

    def test_infer_pie_from_filename(self):
        """Test pie chart inference."""
        assert _infer_chart_type("pie_data.csv") == "pie"
        assert _infer_chart_type("my_pie_chart.json") == "pie"

    def test_infer_scatter_from_filename(self):
        """Test scatter chart inference."""
        assert _infer_chart_type("scatter_data.csv") == "scatter"
        assert _infer_chart_type("my_scatter_chart.json") == "scatter"

    def test_infer_default_to_bar(self):
        """Test default to bar chart when no keyword found."""
        assert _infer_chart_type("unknown_data.csv") == "bar"
        assert _infer_chart_type("data.json") == "bar"


class TestBatchCommand:
    """Tests for batch command functionality."""

    def test_batch_command_creates_charts(self, tmp_path):
        """Test batch command processes multiple files."""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        # Create test data files
        bar_data = {"data": [10, 20, 30], "labels": ["a", "b", "c"]}
        with open(input_dir / "bar_test.json", "w") as f:
            json.dump(bar_data, f)

        column_data = {"data": [15, 25, 35], "labels": ["x", "y", "z"]}
        with open(input_dir / "column_test.json", "w") as f:
            json.dump(column_data, f)

        # Run batch command
        import argparse

        from charted.cli.batch import batch_command

        args = argparse.Namespace(
            input_dir=str(input_dir), output_dir=str(output_dir), config=None
        )

        batch_command(args)

        assert (output_dir / "bar_test.svg").exists()
        assert (output_dir / "column_test.svg").exists()

    def test_batch_command_empty_directory(self, tmp_path):
        """Test batch command with no data files."""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        import argparse

        from charted.cli.batch import batch_command

        args = argparse.Namespace(
            input_dir=str(input_dir), output_dir=str(output_dir), config=None
        )

        with pytest.raises(SystemExit) as exc_info:
            batch_command(args)

        assert exc_info.value.code != 0

    def test_batch_command_nonexistent_directory(self, tmp_path):
        """Test batch command with nonexistent input directory."""
        import argparse

        from charted.cli.batch import batch_command

        args = argparse.Namespace(
            input_dir=str(tmp_path / "nonexistent"),
            output_dir=str(tmp_path / "output"),
            config=None,
        )

        with pytest.raises(SystemExit) as exc_info:
            batch_command(args)

        assert exc_info.value.code != 0


class TestConsoleScript:
    """Tests for console script entry point."""

    def test_console_script_exists(self):
        """Test that charted console script is available via python -m."""
        result = subprocess.run(
            [sys.executable, "-m", "charted", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "charted" in result.stdout.lower()

    def test_console_script_create(self, tmp_path):
        """Test charted create via console script."""
        output_path = tmp_path / "test.svg"

        # Create test data
        data = {"data": [10, 20, 30], "labels": ["a", "b", "c"]}
        data_file = tmp_path / "test_data.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "charted",
                "create",
                "bar",
                str(output_path),
                "--data",
                str(data_file),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert output_path.exists()


def test_batch_command_no_files(tmp_path, capsys):
    """Test batch command with no data files."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    args = argparse.Namespace(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        chart_type=None,
        config=None,
    )

    with pytest.raises(SystemExit) as exc_info:
        batch_command(args)

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "no data files" in captured.err.lower()


def test_batch_command_unknown_chart_type_keyword(tmp_path, capsys):
    """Test batch command with filename that doesn't match chart type keywords."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Create a file with no chart type keyword - defaults to bar
    (input_dir / "data.csv").write_text("a,b\n1,2")

    args = argparse.Namespace(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        chart_type=None,
        config=None,
    )

    # Should succeed - defaults to bar chart
    batch_command(args)
    captured = capsys.readouterr()
    assert "created: data.svg" in captured.out.lower()


def test_create_command_no_data_file(tmp_path, capsys):
    """Test create command without data file."""
    output_path = tmp_path / "output.svg"

    args = argparse.Namespace(
        chart_type="bar",
        output=str(output_path),
        data=None,
        config=None,
    )

    from charted.cli.create import create_command

    # BarChart requires data, so this should fail
    with pytest.raises(SystemExit) as exc_info:
        create_command(args)

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "error creating chart" in captured.err.lower()


def test_create_command_with_invalid_data(tmp_path, capsys):
    """Test create command with non-existent data file."""
    output_path = tmp_path / "output.svg"

    args = argparse.Namespace(
        chart_type="bar",
        output=str(output_path),
        data="/nonexistent/data.csv",
        config=None,
    )

    from charted.cli.create import create_command

    with pytest.raises(SystemExit) as exc_info:
        create_command(args)

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "data file not found" in captured.err.lower()
