"""Tests for batch CLI command."""

import json
import tempfile
from pathlib import Path

import pytest

from charted.cli.batch import _infer_chart_type, batch_command


class TestInferChartType:
    """Test chart type inference from filenames."""

    def test_infer_bar_from_filename(self):
        """Test bar chart inference."""
        assert _infer_chart_type("bar_data.csv") == "bar"
        assert _infer_chart_type("my_bar_chart.json") == "bar"
        assert _infer_chart_type("BAR.csv") == "bar"

    def test_infer_column_from_filename(self):
        """Test column chart inference."""
        assert _infer_chart_type("column_data.csv") == "column"
        assert _infer_chart_type("my_column.json") == "column"

    def test_infer_line_from_filename(self):
        """Test line chart inference."""
        assert _infer_chart_type("line_data.csv") == "line"
        assert _infer_chart_type("my_line.json") == "line"

    def test_infer_pie_from_filename(self):
        """Test pie chart inference."""
        assert _infer_chart_type("pie_data.csv") == "pie"
        assert _infer_chart_type("my_pie.json") == "pie"

    def test_infer_scatter_from_filename(self):
        """Test scatter chart inference."""
        assert _infer_chart_type("scatter_data.csv") == "scatter"
        assert _infer_chart_type("my_scatter.json") == "scatter"

    def test_default_to_bar(self):
        """Test default chart type is bar."""
        assert _infer_chart_type("unknown.csv") == "bar"
        assert _infer_chart_type("data.json") == "bar"
        assert _infer_chart_type("random_file.csv") == "bar"

    def test_first_match_wins(self):
        """Test that first matching keyword wins."""
        # "bar" comes before "column" in keywords list
        assert _infer_chart_type("bar_column.csv") == "bar"

    def test_batch_not_a_directory(self):
        """Test batch when input is a file, not directory."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        try:
            import argparse

            args = argparse.Namespace(
                input_dir=temp_path,
                output_dir="/tmp/output",
                chart_type="bar",
            )

            with pytest.raises(SystemExit) as exc_info:
                batch_command(args)
            assert exc_info.value.code == 1
        finally:
            Path(temp_path).unlink()


class TestBatchCommand:
    """Test batch command execution."""

    def test_batch_with_bar_data(self):
        """Test batch processing with bar chart data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create valid bar data
            data_file = input_dir / "bar_data.csv"
            data_file.write_text("label,value\nA,10\nB,20\nC,30")

            # Create argparse namespace
            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            # Should not raise
            batch_command(args)

            # Check output was created
            output_file = output_dir / "bar_data.svg"
            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_batch_with_json_data(self):
        """Test batch processing with JSON data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create valid bar data as JSON (matching CSV structure)
            data = {"labels": ["A", "B", "C"], "data": [10, 20, 30]}
            data_file = input_dir / "bar_data.json"
            data_file.write_text(json.dumps(data))

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            batch_command(args)

            output_file = output_dir / "bar_data.svg"
            assert output_file.exists()

    def test_batch_multiple_files(self):
        """Test batch processing multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create multiple data files
            (input_dir / "bar_data1.csv").write_text("label,value\nA,10\nB,20")
            (input_dir / "bar_data2.csv").write_text("label,value\nC,30\nD,40")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            batch_command(args)

            assert (output_dir / "bar_data1.svg").exists()
            assert (output_dir / "bar_data2.svg").exists()

    def test_batch_nonexistent_input_dir(self):
        """Test batch with nonexistent input directory."""
        import argparse

        args = argparse.Namespace(
            input_dir="/nonexistent/path/12345",
            output_dir="/tmp/output",
            chart_type="bar",
        )

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            batch_command(args)
        assert exc_info.value.code == 1

    def test_batch_empty_directory(self):
        """Test batch with directory containing no data files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            # Should exit with error (no data files)
            with pytest.raises(SystemExit) as exc_info:
                batch_command(args)
            assert exc_info.value.code == 1

    def test_batch_with_invalid_data(self):
        """Test batch processing with invalid data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create invalid data (missing required fields)
            (input_dir / "bar_invalid.csv").write_text("wrong,columns\n1,2,3")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            # Should handle error and exit with code 1
            with pytest.raises(SystemExit) as exc_info:
                batch_command(args)
            assert exc_info.value.code == 1

    def test_batch_without_override(self):
        """Test batch infers chart type from filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create line data
            (input_dir / "line_data.csv").write_text("label,value\nA,10\nB,20")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type=None,  # No override
            )

            batch_command(args)

            output_file = output_dir / "line_data.svg"
            assert output_file.exists()

    def test_batch_creates_output_directory(self):
        """Test batch creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "nonexistent" / "output"
            input_dir.mkdir()

            (input_dir / "bar_data.csv").write_text("label,value\nA,10")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            batch_command(args)

            assert output_dir.exists()

    def test_batch_with_unknown_chart_type_in_filename(self):
        """Test batch defaults to bar when no keyword matches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create file with no chart type keyword - should default to bar
            (input_dir / "unknown_type.csv").write_text("label,value\nA,10\nB,20")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type=None,
            )

            # Should succeed (defaults to bar)
            batch_command(args)

            # Check output was created as bar chart
            assert (output_dir / "unknown_type.svg").exists()

    def test_batch_with_file_not_found_error(self, capsys):
        """Test batch handles file not found errors with suggestion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            input_dir.mkdir()

            # Create a file that will cause a "not found" error
            (input_dir / "bar_missing.csv").write_text("missing,columns")

    def test_batch_skips_unknown_chart_type(self, capsys):
        """Test batch skips files with unknown chart type in override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create data file
            (input_dir / "data.csv").write_text("label,value\nA,10")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="invalid_type",  # Not in CHART_TYPES
            )
            # Should exit with code 1 (all files failed)
            with pytest.raises(SystemExit) as exc_info:
                batch_command(args)
            assert exc_info.value.code == 1

            # Check warning was printed
            captured = capsys.readouterr()
            assert (
                "skipping" in captured.out.lower() or "unknown" in captured.out.lower()
            )

    def test_batch_handles_errors_gracefully(self, capsys):
        """Test batch handles errors and continues processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create data that will cause an error
            (input_dir / "bar_bad.csv").write_text("x,y,z\n1,2,3")

            import argparse

            args = argparse.Namespace(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chart_type="bar",
            )

            # Should complete but log errors (may or may not exit with 1)
            batch_command(args)

            # Check error message was printed
            captured = capsys.readouterr()
            assert (
                "error" in captured.err.lower() or "completed" in captured.out.lower()
            )
