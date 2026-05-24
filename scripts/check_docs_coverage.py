#!/usr/bin/env python3
"""Check documentation coverage for all public symbols in charted."""

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_CHARTS_DIR = ROOT / "docs" / "charts"
AGENTS_MD = ROOT / "AGENTS.md"
INIT_FILE = ROOT / "charted" / "__init__.py"

# Chart classes that should each have a docs/charts/<name>.rst file
CHART_CLASSES = {
    "AreaChart": "area",
    "BarChart": "bar",
    "BoxPlot": "boxplot",
    "ColumnChart": "column",
    "GanttChart": "gantt",
    "HeatmapChart": "heatmap",
    "Histogram": "histogram",
    "LineChart": "line",
    "PieChart": "pie",
    "RadarChart": "radar",
    "ScatterChart": "scatter",
}


def check_docstrings() -> list[str]:
    """Verify every public symbol in __all__ has a non-empty docstring."""
    sys.path.insert(0, str(ROOT))
    import charted

    errors = []
    for name in charted.__all__:
        if name == "__version__":
            continue
        obj = getattr(charted, name, None)
        if obj is None:
            errors.append(f"  {name}: listed in __all__ but not importable")
            continue
        if inspect.isclass(obj) or inspect.isfunction(obj):
            doc = inspect.getdoc(obj)
            if not doc:
                errors.append(f"  {name}: missing docstring")
    return errors


def check_chart_rst_files() -> list[str]:
    """Verify each chart type has a corresponding docs/charts/<name>.rst."""
    errors = []
    for cls_name, rst_stem in CHART_CLASSES.items():
        rst_path = DOCS_CHARTS_DIR / f"{rst_stem}.rst"
        if not rst_path.exists():
            errors.append(f"  {cls_name}: missing docs/charts/{rst_stem}.rst")
    return errors


def check_agents_md() -> list[str]:
    """Verify AGENTS.md mentions each chart type."""
    if not AGENTS_MD.exists():
        return ["  AGENTS.md not found"]
    content = AGENTS_MD.read_text()
    errors = []
    for cls_name in CHART_CLASSES:
        if cls_name not in content:
            errors.append(f"  {cls_name}: not mentioned in AGENTS.md")
    return errors


def check_freshness() -> list[str]:
    """Warn if __init__.py is newer than AGENTS.md."""
    warnings = []
    if AGENTS_MD.exists() and INIT_FILE.exists():
        init_mtime = INIT_FILE.stat().st_mtime
        agents_mtime = AGENTS_MD.stat().st_mtime
        if init_mtime > agents_mtime:
            warnings.append(
                "  charted/__init__.py is newer than AGENTS.md — "
                "AGENTS.md may need updating"
            )
    return warnings


def main() -> int:
    failed = False
    all_errors: list[str] = []

    # 1. Docstrings
    docstring_errors = check_docstrings()
    if docstring_errors:
        all_errors.append("Missing docstrings:")
        all_errors.extend(docstring_errors)
        failed = True

    # 2. Chart RST files
    rst_errors = check_chart_rst_files()
    if rst_errors:
        all_errors.append("Missing chart documentation files:")
        all_errors.extend(rst_errors)
        failed = True

    # 3. AGENTS.md coverage
    agents_errors = check_agents_md()
    if agents_errors:
        all_errors.append("Missing from AGENTS.md:")
        all_errors.extend(agents_errors)
        failed = True

    # 4. Freshness (warning only, does not fail)
    freshness_warnings = check_freshness()
    if freshness_warnings:
        all_errors.append("Warnings:")
        all_errors.extend(freshness_warnings)

    if all_errors:
        print("Documentation coverage report:")
        print("\n".join(all_errors))

    if failed:
        print("\nFAILED: documentation coverage incomplete")
        return 1

    print("OK: all documentation coverage checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
