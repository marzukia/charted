"""Tests for data loading utilities."""

import json

import pytest

from charted import load_csv, load_data, load_json


class TestLoadData:
    """Tests for the load_data function."""

    def test_load_csv_basic(self, tmp_path):
        """Test loading basic CSV data."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Quarter,Revenue\nQ1,120\nQ2,180\nQ3,210\nQ4,150\n")

        x, y, labels = load_data(csv_file, x_col="Quarter", y_col="Revenue")

        assert x == ["Q1", "Q2", "Q3", "Q4"]
        assert y == [120.0, 180.0, 210.0, 150.0]
        assert labels == ["Revenue"]

    def test_load_tsv(self, tmp_path):
        """Test loading TSV data."""
        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_text("Quarter\tRevenue\nQ1\t120\nQ2\t180\nQ3\t210\n")

        x, y, labels = load_data(tsv_file, x_col="Quarter", y_col="Revenue")

        assert x == ["Q1", "Q2", "Q3"]
        assert y == [120.0, 180.0, 210.0]
        assert labels == ["Revenue"]

    def test_load_json_array(self, tmp_path):
        """Test loading JSON array of numbers."""
        json_file = tmp_path / "data.json"
        json_file.write_text("[120, 180, 210, 150]")

        x, y, labels = load_data(json_file)

        assert x == ["0", "1", "2", "3"]
        assert y == [120.0, 180.0, 210.0, 150.0]
        assert labels == ["data"]

    def test_load_json_objects(self, tmp_path):
        """Test loading JSON array of objects."""
        json_file = tmp_path / "data.json"
        json_file.write_text(
            json.dumps(
                [
                    {"label": "Q1", "value": 120},
                    {"label": "Q2", "value": 180},
                    {"label": "Q3", "value": 210},
                ]
            )
        )

        x, y, labels = load_data(json_file)

        assert x == ["Q1", "Q2", "Q3"]
        assert y == [120.0, 180.0, 210.0]
        assert labels == ["data"]

    def test_load_json_object_with_data_and_labels(self, tmp_path):
        """Test loading JSON object with data and labels."""
        json_file = tmp_path / "data.json"
        json_file.write_text(
            json.dumps(
                {
                    "data": [120, 180, 210],
                    "labels": ["Q1", "Q2", "Q3"],
                    "title": "Sales",
                }
            )
        )

        x, y, labels = load_data(json_file)

        assert x == ["Q1", "Q2", "Q3"]
        assert y == [120.0, 180.0, 210.0]
        assert labels == ["Sales"]

    def test_load_json_dict(self, tmp_path):
        """Test loading JSON dict with string keys and numeric values."""
        json_file = tmp_path / "data.json"
        json_file.write_text(json.dumps({"Q1": 120, "Q2": 180, "Q3": 210}))

        x, y, labels = load_data(json_file)

        assert x == ["Q1", "Q2", "Q3"]
        assert y == [120.0, 180.0, 210.0]
        assert labels == ["data"]

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            load_data("/nonexistent/file.csv", x_col="x", y_col="y")

    def test_csv_missing_x_col(self, tmp_path):
        """Test error when x_col is missing."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Quarter,Revenue\nQ1,120\n")

        with pytest.raises(ValueError, match="Column 'Period' not found"):
            load_data(csv_file, x_col="Period", y_col="Revenue")

    def test_csv_missing_y_col(self, tmp_path):
        """Test error when y_col is missing."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Quarter,Revenue\nQ1,120\n")

        with pytest.raises(ValueError, match="Column 'Amount' not found"):
            load_data(csv_file, x_col="Quarter", y_col="Amount")

    def test_csv_invalid_numeric(self, tmp_path):
        """Test error when y_col contains non-numeric data."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Quarter,Revenue\nQ1,not_a_number\n")

        with pytest.raises(ValueError, match="Invalid numeric value"):
            load_data(csv_file, x_col="Quarter", y_col="Revenue")

    def test_unsupported_format(self, tmp_path):
        """Test error for unsupported file format."""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("some data")

        with pytest.raises(ValueError, match="Unsupported file format"):
            load_data(txt_file)

    def test_empty_csv(self, tmp_path):
        """Test error for empty CSV file."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("")

        with pytest.raises(ValueError, match="Empty or invalid CSV"):
            load_data(csv_file, x_col="x", y_col="y")


class TestLoadCSV:
    """Tests for the load_csv convenience function."""

    def test_load_csv_simple(self, tmp_path):
        """Test load_csv with simple CSV."""
        csv_file = tmp_path / "sales.csv"
        csv_file.write_text("Quarter,Revenue\nQ1,120\nQ2,180\n")

        x, y, labels = load_csv(csv_file, x_col="Quarter", y_col="Revenue")

        assert x == ["Q1", "Q2"]
        assert y == [120.0, 180.0]
        assert labels == ["Revenue"]

    def test_load_tsv_with_delimiter(self, tmp_path):
        """Test load_csv with TSV and explicit delimiter."""
        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_text("Quarter\tRevenue\nQ1\t120\n")

        x, y, labels = load_csv(
            tsv_file, x_col="Quarter", y_col="Revenue", delimiter="\t"
        )

        assert x == ["Q1"]
        assert y == [120.0]


class TestLoadJSON:
    """Tests for the load_json convenience function."""

    def test_load_json_simple(self, tmp_path):
        """Test load_json with simple array."""
        json_file = tmp_path / "data.json"
        json_file.write_text("[1, 2, 3]")

        x, y, labels = load_json(json_file)

        assert x == ["0", "1", "2"]
        assert y == [1.0, 2.0, 3.0]
