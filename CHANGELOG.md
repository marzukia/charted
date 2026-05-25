# Changelog

All notable changes to Charted will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-05-25

### Added
- MCP server for AI-agent integration (`charted-mcp` CLI command)
- DuckDB extension for SQL-based chart generation
- Native PNG output (`chart.save_png()`)
- Plot-area clipping mask for scatter charts
- Chart describe API (`chart.describe()`) for AI-readable summaries
- Agent-friendly API surface — `to_config()`/`from_config()`, color palettes, output methods
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

