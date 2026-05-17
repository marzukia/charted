# Visual Regression Testing Baselines

This directory contains baseline files for visual regression testing to ensure chart rendering remains consistent and prevent unauthorized modifications.

## Hybrid Testing Approach

### SVG Baselines (`*.svg`)
- **Purpose**: Structural tests (e.g., "legend exists", "axes rendered")
- **Advantages**: Easy to maintain, human-readable, version-control friendly
- **Tests**: `test_*_svg()` functions in `tests/charts/test_visual.py`

### PNG Baselines (`*.png`)  
- **Purpose**: Pixel-perfect visual regression tests
- **Advantages**: Harder for AI agents to cheat, catches subtle rendering issues
- **Tests**: `test_*_png()` functions in `tests/charts/test_visual.py`
- **Tolerance**: 5 pixels (accounts for anti-aliasing differences)

## Baseline Integrity

Both SVG and PNG baselines are protected:

1. **SHA256 Hash Verification**: 
   - `MANIFEST.sha256` tracks SVG baseline integrity
   - `PNG_MANIFEST.sha256` tracks PNG baseline integrity
   
2. **Read-Only Protection**:
   - Baselines are locked read-only during test runs
   - Tests fail immediately if baselines are modified

3. **Pre-Test Validation**:
   - `conftest.py` verifies all baselines match manifests before tests run
   - Prevents unauthorized modifications or AI-generated tampering

## Updating Baselines

**Never modify baseline files manually.** Use the update script:

```bash
# Install dev dependencies first
pip install 'pillow>=10.0.0' 'numpy>=1.24.0' 'cairosvg>=2.7.0'

# Generate/update all baselines
python scripts/update_baselines.py

# Update specific chart type
python scripts/update_baselines.py bar

# Update only PNG baselines
python scripts/update_baselines.py --png-only

# Update only SVG baselines  
python scripts/update_baselines.py --svg-only
```

The script will:
1. Generate new SVG and/or PNG baselines
2. Update both MANIFEST files with SHA256 hashes
3. Commit changes automatically (if git configured)

## Troubleshooting

### Baseline Tampered Error
```
Baselines have been modified outside of the update script:
  TAMPERED: bar_basic.svg
    expected abc123...
    got      def456...
```

**Solution**: Run `python scripts/update_baselines.py` to regenerate baselines intentionally.

### Missing PNG Baselines
If tests fail with missing PNG files:
```bash
python scripts/update_baselines.py --png-only
```

### CairoSVG Installation Issues
On Linux, ensure system cairo library is installed:
```bash
# Ubuntu/Debian
sudo apt-get install libcairo2-dev

# Fedora
sudo dnf install cairo-devel

# macOS
brew install cairo
```

## Test Failure Debugging

When PNG comparison fails, diff images are generated in `tests/diffs/`:
- `{test_name}_diff.png` - Shows visual differences highlighted
- Red pixels indicate where the rendered chart differs from baseline

Use these diffs to identify:
- Rendering regressions (legitimate bugs)
- Environment differences (font, DPI, etc.)
- Actual baseline tampering

## CI/CD Integration

Visual tests run in CI with dev dependencies installed:

```yaml
# .github/workflows/test.yml
- name: Install dev dependencies
  run: pip install '.[dev]'

- name: Run visual tests
  run: pytest tests/charts/test_visual.py -v
```
