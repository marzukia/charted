# Test Plan: Themes and Utilities

**Created:** 2025-01-XX  
**Priority:** MEDIUM  
**Goal:** Verify theme configuration and utility functions

## Objectives

1. **Verify theme loading** - Default and custom themes load correctly
2. **Verify color schemes** - Colors are valid RGB/hex values
3. **Verify utility functions** - Helpers work correctly
4. **Verify defaults** - Reasonable defaults when config missing

## Test Categories

### Happy Path Tests (60%)

| Test Case | Input | Expected Output | Verify |
|-----------|-------|-----------------|--------|
| `test_load_default_theme` | No args | Dict with colors | `assert 'background' in theme` |
| `test_load_custom_theme` | `{'primary': '#FF0000'}` | Custom colors applied | `theme['primary'] == '#FF0000'` |
| `test_get_color_valid` | `color='#FF5733'` | RGB tuple `(255, 87, 51)` | `assert isinstance(rgb, tuple)` |
| `test_get_grid_color` | Theme with `grid_color` | Valid hex or RGB | `assert len(color) >= 3` |
| `test_merge_themes` | `base + overrides` | Merged dict | Override wins on conflict |
| `test_theme_from_preset` | `preset='dark'` | Full theme dict | All required keys present |

### Sad Path Tests (40%)

| Test Case | Input | Expected Behavior | Verify |
|-----------|-------|-------------------|--------|
| `test_load_missing_theme_file` | `theme='nonexistent'` | Fallback to default | Default colors returned |
| `test_invalid_color_hex` | `color='#GGG'` | Error or fallback | `ValueError` or default color |
| `test_empty_theme_dict` | `{}` | Default theme used | All required keys present |
| `test_theme_missing_required` | `{'background': '#FFF'}` | Partial theme with defaults | Required keys filled from defaults |
| `test_invalid_color_rgb` | `(256, 0, 0)` | Error (R > 255) | `ValueError` for out-of-range |
| `test_merge_with_none` | `merge(theme, None)` | Returns original theme | Identity behavior |

## Test File Structure

```python
# tests/utils/test_themes.py

class TestThemeLoadingHappyPath:
    def test_load_default_theme(self): ...
    def test_load_custom_theme_dict(self): ...
    def test_merge_themes(self): ...
    def test_get_required_colors(self): ...

class TestThemeLoadingSadPath:
    def test_load_nonexistent_theme(self): ...
    def test_empty_theme_dict(self): ...
    def test_partial_theme_merges_with_defaults(self): ...

class TestColorUtilities:
    def test_parse_valid_hex(self): ...
    def test_parse_invalid_hex(self): ...
    def test_validate_rgb_tuple(self): ...
```

## Acceptance Criteria

- ✅ All happy path tests pass
- ✅ All sad path tests pass (graceful degradation)
- ✅ Code coverage for themes.py > 70%
- ✅ Theme changes don't break existing chart tests

## Regression Risk

- **Low risk:** themes.py is well-isolated, only affects appearance
- **Check:** `tests/charts/test_visual.py` may have theme-dependent output

## Notes

- Color parsing may use existing `charted/utils/colors.py` (already tested)
- Default theme is critical path - prioritize those tests

## Timeline

- **Day 1:** Theme loading and merging tests
- **Day 2:** Color validation, edge cases
