# CLI Guide

Create charts from the command line without writing Python code.

## Installation

```bash
pip install charted
```

## Basic Usage

### Create a Single Chart

```bash
# Bar chart from CSV
python -m charted create bar sales.svg --data sales.csv

# Column chart from JSON
python -m charted create column data.svg --data data.json

# Line chart with custom title
python -m charted create line trend.svg -d trend.csv --title "Sales Trend"
```

### Batch Process

Process an entire directory of data files:

```bash
# Infer chart type from filename
python -m charted batch ./data ./output

# Force specific chart type
python -m charted batch ./data ./output --chart-type line

# Use custom config
python -m charted batch ./data ./output --config .chartedrc.toml
```

## Data Formats

### CSV Format

First column is labels, remaining columns are data series:

```csv
Quarter,Q1,Q2,Q3,Q4
Sales,120,180,210,150
Profit,80,120,140,100
```

### JSON Formats

**Simple array:**
```json
[120, 180, 210, 150]
```

**Array of objects:**
```json
[
  {"label": "Q1", "value": 120},
  {"label": "Q2", "value": 180}
]
```

**Structured object:**
```json
{
  "data": [120, 180, 210, 150],
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "title": "Sales by Quarter"
}
```

## Available Chart Types

| Type | Command | Description |
|------|---------|-------------|
| Bar | `bar` | Horizontal bars |
| Column | `column` | Vertical bars |
| Line | `line` | Line graphs |
| Scatter | `scatter` | Scatter plots |
| Pie | `pie` | Pie/doughnut charts |
| Radar | `radar` | Radar charts |
| Area | `area` | Area charts |
| Bubble | `bubble` | Bubble charts |
| Combo | `combo` | Mixed charts |
| Heatmap | `heatmap` | Heat maps |
| Gantt | `gantt` | Gantt charts |
| Histogram | `histogram` | Histograms |
| Polar Area | `polar_area` | Polar area charts |
| Box Plot | `boxplot` | Box plots |

## CLI Options

```bash
python -m charted create <chart-type> <output.svg> [options]

Options:
  -d, --data FILE       Input data file (CSV or JSON)
  -t, --title TEXT      Chart title
  --theme THEME         Theme name (light, dark, high-contrast)
  --width WIDTH         Chart width in pixels
  --height HEIGHT       Chart height in pixels
  --config FILE         Config file path
  --help                Show help message
```

## Examples

### Sales Report

```bash
# Create column chart from sales data
python -m charted create column sales.svg \
  --data sales.csv \
  --title "2024 Sales by Quarter" \
  --theme dark \
  --width 800 \
  --height 600
```

### Comparison Chart

```bash
# Create grouped column chart
python -m charted create column comparison.svg \
  --data comparison.csv \
  --title "Year-over-Year Comparison"
```

### Batch Report Generation

```bash
# Generate charts for all data files
python -m charted batch ./reports/data ./reports/charts

# Output:
#   ✓ sales.svg
#   ✓ trend.svg
#   ✓ comparison.svg
```

## Integration with Build Tools

### Makefile

```makefile
charts:
	python -m charted batch ./data ./output
	cp ./output/*.svg docs/images/
```

### GitHub Actions

```yaml
- name: Generate Charts
  run: |
    pip install charted
    python -m charted batch ./data ./docs/images
```
