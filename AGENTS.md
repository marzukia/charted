# Charted - AI Agent & Developer Guide

This document provides guidance for AI coding assistants (Hermes, Claude Code, etc.) and human developers working on the Charted repository.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/marzukia/charted.git
cd charted

# Install with dev dependencies (includes PNG testing)
uv pip install -e '.[dev]'

# Run tests
pytest tests/ -v

# Run pre-commit hooks
pre-commit run --all-files
```

## Project Overview

**Charted** is a zero-dependency SVG chart generation library. It provides simple interfaces for creating bar charts, column charts, line charts, pie charts, scatter plots, and radar charts.

### Key Principles
- **Zero runtime dependencies** - Main package has 0 dependencies
- **Dev/test dependencies only** - PNG visual testing uses pillow, numpy, cairosvg (dev optional-dependencies)
- **Pure SVG output** - All charts render to standalone SVG files

## Architecture

```
charted/
├── charted/
│   ├── __init__.py        # Package exports
│   ├── base.py            # BaseChart abstract class
│   ├── charts/            # Chart implementations
│   │   ├── bar.py         # BarChart
│   │   ├── column.py      # ColumnChart
│   │   ├── line.py        # LineChart
│   │   ├── pie.py         # PieChart
│   │   ├── scatter.py     # ScatterChart
│   │   └── radar.py       # RadarChart
│   └── utils/             # Utility functions
├── tests/
│   ├── charts/            # Test files per chart type
│   │   ├── test_bar.py
│   │   ├── test_column.py
│   │   ├── test_line.py
│   │   ├── test_pie.py
│   │   ├── test_scatter.py
│   │   ├── test_radar.py
│   │   └── test_visual.py  # Visual regression tests (SVG + PNG)
│   ├── utils/
│   │   └── image_comparison.py  # PNG comparison utilities
│   ├── baselines/         # SVG + PNG baseline files
│   │   ├── *.svg          # SVG baselines
│   │   ├── *.png          # PNG baselines
│   │   ├── MANIFEST.sha256      # SVG integrity manifest
│   │   └── PNG_MANIFEST.sha256  # PNG integrity manifest
│   ├── diffs/             # Generated test diff images
│   └── conftest.py        # Baseline protection fixture
├── scripts/
│   └── update_baselines.py  # Regenerate all baselines
├── .pre-commit-config.yaml  # Pre-commit hooks (ruff)
└── pyproject.toml         # Project config & dependencies
```

## Development Workflow

### 1. Branch Strategy

**Always use feature branches - never push directly to `main`:**

```bash
# Start from latest main
git checkout main && git pull

# Create feature branch
git checkout -b feat/description
# or for bug fixes:
git checkout -b fix/issue-number
```

### 2. Make Changes

- Use **conventional commits**:
  - `feat:` - new feature
  - `fix:` - bug fix
  - `refactor:` - code refactoring (no behavior change)
  - `docs:` - documentation changes
  - `test:` - test additions/modifications
  - `chore:` - maintenance tasks

- **Type safety**: No `any`, `as any`, or type ignores
- **Tests**: All tests must pass before committing

### 3. Run Pre-commit Hooks

```bash
# Check all files
pre-commit run --all-files

# Auto-fix linting issues
ruff check --fix .
ruff format .
```

### 4. Update Visual Baselines (When Needed)

If you change chart rendering and tests fail:

```bash
# Regenerate all baselines
python scripts/update_baselines.py

# Or regenerate specific baseline
python scripts/update_baselines.py column_basic
```

**Important:** The script generates both SVG and PNG baselines with matching dimensions (500x500).

### 5. Open Pull Request

```bash
git push origin feat/your-feature-name
# Open PR on GitHub against main
```

**CI must pass** before merge. Use squash merge to keep history clean.

## Visual Testing System

Charted uses a **hybrid visual testing approach** with both SVG and PNG baselines:

### SVG Baselines (`tests/baselines/*.svg`)
- **Structural testing** - Verify chart elements exist (axes, labels, legend)
- **Fast comparison** - Text-based diffing
- **Human readable** - Can inspect in browser

### PNG Baselines (`tests/baselines/*.png`)
- **Pixel-perfect verification** - Detects rendering differences
- **Prevents AI cheating** - Visual pixel checks catch subtle mutations
- **Diff generation** - On failure, creates `_diff.png` showing changes

### Baseline Integrity Protection

**⚠️ CRITICAL: BASELINES ARE SACRED AND NON-NEGOTIABLE ⚠️**

The baselines in `tests/baselines/` represent the **AUTHORITATIVE SOURCE OF TRUTH** for correct chart rendering. They define what the OUTPUT MUST BE after any code changes.

**THE GOLDEN RULE: NEVER EVER MODIFY BASELINES TO MATCH BUGGY CODE**

This is an absolute prohibition with ZERO exceptions:
- ❌ **NEVER** update baselines because "tests are failing"
- ❌ **NEVER** update baselines to make broken code pass tests  
- ❌ **NEVER** assume a baseline change is "fine" or "minor"
- ❌ **NEVER** update baselines without explicit user approval

**THE CORRECT APPROACH (Always):**
- ✅ **ALWAYS** investigate WHY tests are failing first
- ✅ **ALWAYS** fix the CODE to match the baseline output
- ✅ **ALWAYS** treat baseline failures as bugs in your implementation
- ✅ **ALWAYS** assume the baseline is correct and your code is wrong

**When baselines MAY be updated (ALL conditions must be met):**
1. User explicitly requests a rendering change with clear justification
2. Adding NEW chart types (no existing baseline exists)
3. Fixing a bug where the baseline itself was demonstrably wrong (document extensively)
4. You have explicit approval BEFORE making any changes

**Consequences of violating this rule:**
- Updates that circumvent this rule will be **REJECTED IMMEDIATELY**
- This is considered a critical violation of testing principles
- AI agents that update baselines without justification **defeat the entire purpose** of visual regression testing
- The baseline protection system exists specifically to prevent "cheating" by matching broken code

Both baselines are protected by SHA256 manifests:
- `MANIFEST.sha256` - Tracks SVG files
- `PNG_MANIFEST.sha256` - Tracks PNG files

**How it works:**
1. `conftest.py` loads manifests at test start
2. Computes SHA256 of each baseline file
3. Compares against committed hashes
4. **Fails immediately** if baselines were mutated outside update script

### Test Execution Flow

```
pytest tests/charts/test_visual.py
  ↓
conftest.py: pytest_sessionstart()
  ↓
[1] Load MANIFEST.sha256
[2] Load PNG_MANIFEST.sha256  
[3] Hash all baseline files
[4] Verify hashes match manifests
  ↓
If verification fails → pytest.exit() with error message
  ↓
Run individual tests:
  - test_column_chart_basic (SVG)
  - test_column_chart_basic_png (PNG)
  ↓
On PNG failure:
  - Generate diff image to tests/diffs/
  - Report failure with diff path
```

### Adding New Charts

1. Create chart implementation in `charted/charts/newchart.py`
2. Add unit tests in `tests/charts/test_newchart.py`
3. Add visual test in `tests/charts/test_visual.py`:
   ```python
   def test_newchart_basic():
       chart = NewChart(data=[1, 2, 3], labels=["a", "b", "c"])
       compare_svg_baseline(chart, "newchart_basic")
       compare_png_baseline(chart, "newchart_basic")
   ```
4. Add to baseline script in `scripts/update_baselines.py`:
   ```python
   CHARTS = {
       # ... existing charts ...
       "newchart_basic": NewChart(data=[1, 2, 3], labels=["a", "b", "c"]),
   }
   ```
5. Run: `python scripts/update_baselines.py newchart_basic`

## Common Tasks

### Fixing Linting Errors

```bash
# Auto-fix all fixable issues
ruff check --fix .

# Format code
ruff format .

# Check specific file
ruff check path/to/file.py
```

### Running Specific Tests

```bash
# Single test
pytest tests/charts/test_visual.py::test_column_chart_basic -v

# All PNG tests
pytest tests/charts/test_visual.py -k png -v

# All SVG tests
pytest tests/charts/test_visual.py -k svg -v
```

### Debugging Failed Visual Tests

1. Run test to generate diff:
   ```bash
   pytest tests/charts/test_visual.py::test_column_chart_basic_png -v
   ```

2. Compare images:
   ```bash
   # Baseline
   cat tests/baselines/column_basic.png
   
   # Actual (generated during test)
   cat tests/diffs/column_basic_actual.png
   
   # Diff (if mismatch)
   cat tests/diffs/column_basic_diff.png
   ```

3. If change is intentional, update baseline:
   ```bash
   python scripts/update_baselines.py column_basic
   ```

### Adding Dev Dependencies

PNG testing requires these optional dependencies (never main runtime):

```toml
# In pyproject.toml [project.optional-dependencies].dev
"pillow>=10.0.0",      # PNG image handling
"numpy>=1.24.0",       # Array operations for comparison
"cairosvg>=2.7.0",     # SVG to PNG conversion
```

Install with:
```bash
uv pip install -e '.[dev]'
```

## Code Quality Standards

### Type Safety
- Use explicit type annotations
- No `any` or untyped imports
- Use `Optional[T]` for nullable values
- Runtime type guards when needed

### Testing
- All tests must pass before committing
- Tests should gracefully skip when optional deps unavailable
- Use lazy imports in test utilities to avoid runtime dependencies

### File Organization
- Chart implementations: `charted/charts/*.py`
- Tests per chart: `tests/charts/test_*.py`
- Visual tests: `tests/charts/test_visual.py`
- Utilities: `tests/utils/*.py`
- Scripts: `scripts/*.py`

## Git Conventions

### Branch Naming
- `feat/feature-name` - new features
- `fix/issue-number` or `fix/description` - bug fixes
- `refactor/description` - refactoring
- `docs/description` - documentation

### Commit Messages
- Present tense: "add feature" not "added feature"
- Imperative mood: "fix bug" not "fixes bug"
- First line under 72 chars
- Body explains WHY, not WHAT (code shows what)

## Troubleshooting

### Test fails with "Baseline integrity check failed"

Baselines were modified outside the update script:

```bash
# If change is intentional:
python scripts/update_baselines.py <chart-name>

# If unintentional, restore from git:
git checkout tests/baselines/
```

### PNG tests skip with "dependencies not installed"

Install dev dependencies:
```bash
uv pip install -e '.[dev]'
```

### Pre-commit hooks fail

```bash
# Check what failed
pre-commit run --all-files

# Auto-fix if possible
ruff check --fix .
ruff format .

# Commit again
git add -A && git commit -m "fix: resolve linting issues"
```

### Missing PNG baseline manifest

```bash
# Generate manifest from existing PNG files
python scripts/update_baselines.py
```

## Security & Best Practices

- **Never expose secrets** in code or logs
- **Baseline protection** prevents silent test mutations
- **Lazy imports** keep runtime dependency-free
- **Pre-commit hooks** enforce code quality before commit

---

*Last updated: May 2026*
*For questions, see CONTRIBUTING.md or open an issue*
