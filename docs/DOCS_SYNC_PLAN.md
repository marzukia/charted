# Documentation Sync Plan

Recommendations for keeping docs in sync with the charted codebase.

## 1. CI Check: Docs Match API

Add a CI job that verifies documentation covers all public API surface:

```yaml
# .github/workflows/docs-check.yml
name: Docs Coverage
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run python scripts/check_docs_coverage.py
```

The script (`scripts/check_docs_coverage.py`) should:
- Import `charted` and inspect `__all__` for all public symbols
- Verify each public class/function has a non-empty docstring
- Verify each chart type has a corresponding `docs/charts/<name>.rst`
- Verify documented examples are syntactically valid (compile with `ast.parse`)
- Exit non-zero with a report of missing coverage

Example implementation approach:

```python
import ast
import importlib
import inspect
import sys
from pathlib import Path

import charted

def check_docstrings():
    """Verify all public symbols have docstrings."""
    missing = []
    for name in charted.__all__:
        obj = getattr(charted, name)
        if inspect.isclass(obj) or inspect.isfunction(obj):
            if not obj.__doc__:
                missing.append(name)
    return missing

def check_chart_docs():
    """Verify each chart class has a .rst file."""
    docs_dir = Path("docs/charts")
    chart_classes = [
        name for name in charted.__all__
        if inspect.isclass(getattr(charted, name))
        and hasattr(getattr(charted, name), 'to_svg')
    ]
    # Map class names to expected .rst filenames
    name_map = {
        "BarChart": "bar", "ColumnChart": "column", "LineChart": "line",
        "ScatterChart": "scatter", "PieChart": "pie", "RadarChart": "radar",
        "AreaChart": "area", "BoxPlot": "boxplot", "Histogram": "histogram",
        "HeatmapChart": "heatmap", "GanttChart": "gantt",
    }
    missing = []
    for cls_name in chart_classes:
        rst_name = name_map.get(cls_name)
        if rst_name and not (docs_dir / f"{rst_name}.rst").exists():
            missing.append(cls_name)
    return missing
```

## 2. sphinx-autodoc for API Reference

Already partially in place (`.. autoclass::` directives in `docs/api/charts.rst`).
To make it work reliably:

- Ensure `conf.py` has `extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']`
- Add `autodoc_member_order = 'bysource'` for stable ordering
- Run `make html` in CI to catch broken references early
- Consider `sphinx.ext.intersphinx` for cross-linking to Python stdlib docs

The existing autoclass directives will pull docstrings automatically once Sphinx
is configured. No separate generation step needed.

## 3. Pre-commit Hook for Doc Coverage

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: check-docs
      name: Check documentation coverage
      entry: python scripts/check_docs_coverage.py
      language: python
      pass_filenames: false
      additional_dependencies: []
```

This runs on every commit and blocks if a new public API symbol lacks a docstring
or a new chart type lacks documentation.

## 4. AGENTS.md Generation

AGENTS.md should NOT be auto-generated from code inspection. Reasons:

- It contains architectural decisions, conventions, and workflow guidance that
  don't live in code (e.g., "use Theme dataclass, not dicts")
- Auto-generated docs would be a flat API dump without the narrative context
  AI agents need to use the library effectively
- It's maintained infrequently (only when major features land)

Instead, add a CI check that warns when `charted/__init__.py` exports change
without a corresponding AGENTS.md update:

```python
# In check_docs_coverage.py
def check_agents_md_freshness():
    """Warn if __all__ changed since last AGENTS.md update."""
    agents_md = Path("AGENTS.md")
    init_py = Path("charted/__init__.py")
    if init_py.stat().st_mtime > agents_md.stat().st_mtime:
        print("WARNING: charted/__init__.py modified more recently than AGENTS.md")
        print("Consider updating AGENTS.md if public API changed.")
```

## Summary

| Approach | Effort | Value |
|----------|--------|-------|
| CI docs coverage script | Low | High — catches drift on every PR |
| sphinx-autodoc (already started) | Low | Medium — API ref stays current |
| Pre-commit hook | Low | Medium — catches issues before PR |
| AGENTS.md auto-gen | N/A | Skip — manual is better for this |
