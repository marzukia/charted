# Test Plan: Font Utilities (tkinter, utils)

**Created:** 2025-01-XX  
**Priority:** MEDIUM  
**Goal:** Verify font loading, parsing, and measurement utilities

## Objectives

1. **Verify font file parsing** - JSON font definitions load correctly
2. **Verify font metrics** - Character widths, heights calculated correctly
3. **Verify font fallback** - Missing fonts handled gracefully
4. **Verify tkinter integration** - Tkinter font querying works (platform-dependent)

## Test Categories

### Happy Path Tests (60%)

| Test Case | Input | Expected Output | Verify |
|-----------|-------|-----------------|--------|
| `test_load_font_definition` | `Arial.json` | Dict with glyph data | 26+ lowercase glyphs present |
| `test_get_char_width` | `font='Arial', char='a'` | Numeric width > 0 | `assert isinstance(width, (int, float))` |
| `test_get_font_height` | `font='Arial', size=12` | Numeric height | `assert 10 < height < 15` |
| `test_measure_text` | `text='Hello', size=12` | Total width | Width ≈ sum of char widths |
| `test_load_multiple_fonts` | `['Arial', 'Helvetica']` | Both load | 2 font definitions cached |
| `test_tkinter_font_exists` | `font='Helvetica 12'` | Tkinter returns font info | `font.metrics()` returns dict |

### Sad Path Tests (40%)

| Test Case | Input | Expected Behavior | Verify |
|-----------|-------|-------------------|--------|
| `test_load_nonexistent_font` | `font='NonExistent123'` | Error or fallback | `FileNotFoundError` or default font |
| `test_measure_empty_string` | `text=''` | Width = 0 | `assert width == 0` |
| `test_measure_very_long_text` | `text='a' * 10000` | No crash, reasonable width | Width > 0, < 1e6 pixels |
| `test_tkinter_without_display` | No X11/Wayland | Graceful fallback | Exception caught, uses defaults |
| `test_invalid_json_font_file` | Corrupted JSON | Parse error | `json.JSONDecodeError` or fallback |
| `test_unicode_glyph_missing` | `char='😀'` | Fallback width or error | Graceful handling, no crash |
| `test_negative_font_size` | `size=-12` | Error or absolute value | `assert size > 0` or abs applied |

## Test File Structure

```python
# tests/fonts/test_utils.py

class TestFontLoadingHappyPath:
    def test_load_arial_font(self): ...
    def test_load_helvetica_font(self): ...
    def test_get_char_width(self): ...
    def test_measure_text_basic(self): ...

class TestFontLoadingSadPath:
    def test_load_nonexistent_font(self): ...
    def test_measure_empty_string(self): ...
    def test_unicode_glyph_fallback(self): ...

class TestFontUtilities:
    def test_get_font_height(self): ...
    def test_calculate_text_bounds(self): ...

# tests/fonts/test_tkinter.py (skip if no display)
@pytest.mark.skipif(sys.platform in ['win32'] and not DISPLAY_AVAILABLE, ...)
class TestTkinterFontUtils:
    def test_tkinter_font_metrics(self): ...
    def test_tkinter_without_x11(self): ...
```

## Acceptance Criteria

- ✅ Happy path tests pass on Linux/Mac
- ✅ Sad path tests verify error handling
- ✅ Code coverage for fonts/utils.py > 70%
- ✅ tkinter.py tests skipped gracefully on CI (no display)
- ✅ No regressions in chart label rendering

## Regression Risk

- `charted/fonts/utils.py` - 26 lines, currently untested
- `charted/fonts/tkinter.py` - 39 lines, platform-dependent
- **Low risk:** Font rendering issues would be visually obvious in chart tests

## Notes

- tkinter tests may need `xvfb-run` on CI
- Font files are large (Arial.json = 7620 lines) - use subset for tests
- Consider mocking tkinter for pure unit tests

## Timeline

- **Day 1:** Font loading and parsing tests
- **Day 2:** Text measurement tests, edge cases
- **Day 3:** tkinter integration (platform-dependent)
