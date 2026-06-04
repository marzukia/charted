# Changelog

All notable changes to Charted will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-04

### Added
- `png` optional extra: `pip install charted[png]` installs cairosvg for PNG
  export. The base library stays zero-dependency.
- PEP 561 `py.typed` marker so the inline type hints are visible to downstream
  type checkers.
- Bubble, Combo, and Polar Area chart types are now documented as first-class
  (14 chart types total).
- `charted create` accepts `--title`, `--width`, and `--height`, which set the
  chart title and dimensions from the command line and override the matching
  values in a `--config` file.
- `charted create --transpose` reads a wide / series-per-row CSV, where each
  data row is a series and the header row supplies the x-axis labels.

### Changed
- Input validation is stricter: infinite values, and a label count that does
  not match the data, now raise an actionable error instead of rendering a
  broken chart silently. Gantt is exempt from the label-length check because it
  stores tasks as coordinate pairs.
- `__version__` is read from the installed package metadata.
- Pie charts label small slices with leader lines, and the bubble size legend
  draws hollow outline circles so it reads as a scale key rather than data.

### Fixed
- Bottom and top legends no longer overlap the axis category labels.
- A right-side legend no longer shifts data marks out of the plot area (the
  data-flip transform now accounts for the full right padding).
- Percent value labels on already-percentage data no longer multiply by 100,
  and stacked-bar value labels sit centered in their segment.
- Dark-theme radial axis labels on radar and polar-area charts are readable and
  centered in their badges; radar spoke labels render without garbling.
- Malformed colour strings are rejected by the contrast-ratio path.

## [1.0.5] - 2026-05-30

### Changed
- Widen pie charts to 700×500 (1.4:1 aspect ratio)
- Add dual-column legend for overflow labels

### Added
- `PIE_CHART_WIDTH`, `PIE_CHART_HEIGHT` constants
- `create_pie_legend()` function for dual-column legend layout
- `show_percentages` parameter to PieChart

## [1.0.4] - 2026-05-29

### Changed
- Add 4px vertical gap between legend entries
- Rotate radar chart axis labels to align with spokes

### Fixed
- Even top/bottom padding in legend background

## [1.0.3] - 2026-05-25

### Added
- MCP server for AI-agent integration (`charted-mcp` CLI command)
- DuckDB extension for SQL-based chart generation
- Native PNG output (`chart.save_png()`)
- Plot-area clipping mask for scatter charts
- Chart describe API (`chart.describe()`) for AI-readable summaries
- Agent-friendly API surface: `to_config()`/`from_config()`, color palettes, output methods
- Heatmap chart type with color bar and customizable cell dimensions
- Gantt chart type with dependency arrows and multi-series timelines
- Area chart type with fill support
- Box plot chart type with quartile and outlier rendering
- Histogram chart type with automatic binning
- Legend positioning options (top, bottom, left, right)
- Dark-mode legend contrast fixes
- Bar chart y-label alignment improvements
- Python 3.13 CI coverage
- Theme opacity tiers with `root_color` derivation

### Changed
- Comprehensive AGENTS.md rewrite for AI agent guidance
- Line markers off by default (cleaner output)
- Removed padding labels for line/area continuous-data chart types
- Validation errors now use typed exceptions (DataShapeError, NoDataError)
- CLI now supports all 11 chart types (area, boxplot, histogram, heatmap, gantt added)
- Bumped radar chart default radius from 0.45 to 0.75 (reduces whitespace)

### Fixed
- Heatmap right-padding clipping with color bar
- GanttChart y-axis label alignment
- Quartile calculation edge cases in BoxPlot
- Histogram binning edge cases
- `from_dict`/`auto` parameter mismatches
- Theme config flattening (padding keys moved to top level)
- Legend HSL color validation and contrast
- Zero line positioning with negative values
- SVG coordinate rounding to 1 decimal place
- Data coordinate padding offsets in AreaChart, BoxPlot, Histogram
- Merge conflict markers in baseline files
- Property-based test for hex_to_rgb validation

### Removed
- Orphan SVG baselines (bar, column, line, scatter, xy_line single-file variants)
- Stale inline comments from heatmap.py, gantt.py

### Security
- None

## [0.1.0] - 2026-04-22

### Added
- Initial release
- All chart types and core functionality

