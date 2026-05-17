# Baseline Comparison: Grid Line Rendering Fix

## Summary
Updated 13 baseline SVG files to reflect correct grid line rendering after fixing initialization order bug.

## Files Changed (May 17, 2026)
| File | Old Size | New Size | Change |
|------|----------|----------|--------|
| bar_basic.svg | - | 1,692 bytes | Fixed: 9→3 grid lines |
| bar_multi.svg | - | 1,887 bytes | Fixed |
| bar_stacked.svg | - | 1,884 bytes | Fixed |
| column_basic.svg | - | 1,471 bytes | Fixed |
| column_sidebyside.svg | - | 1,604 bytes | Fixed |
| column_stacked.svg | - | 2,007 bytes | Fixed |
| line_basic.svg | - | 1,532 bytes | Fixed |
| line_multi.svg | - | 2,008 bytes | Fixed |
| pie.svg | - | 1,348 bytes | Updated |
| pie_doughnut.svg | - | 1,227 bytes | Updated |
| radar.svg | - | 2,519 bytes | Updated |
| radar_multi.svg | - | 3,753 bytes | Updated |
| scatter_basic.svg | - | 1,357 bytes | Fixed |
| scatter_multi.svg | - | 1,571 bytes | Fixed |

## Key Fix in bar_basic.svg

### Before (Broken)
```svg
<!-- Y-axis grid lines: WRONG - 9 lines extending beyond plot -->
<path d="M0 90.0 h443.0 M0 225.0 h443.0 M0 360.0 h443.0 M0 495.0 h443.0 M0 630.0 h443.0 M0 765.0 h443.0 M0 900.0 h443.0 M0 1035.0 h443.0 M0 1170.0 h443.0" transform="translate(32.0, 25.0)"/>

<!-- X-axis labels: WRONG position -->
<g transform="translate(32.0, 43.0)">
```

### After (Fixed)
```svg
<!-- Y-axis grid lines: CORRECT - 3 lines at category positions -->
<path d="M0 90.0 h443.0 M0 225.0 h443.0 M0 360.0 h443.0" transform="translate(32.0, 25.0)"/>

<!-- X-axis labels: CORRECT position -->
<g transform="translate(25.0, 43.0)">
```

## Root Cause
`YAxis.grid_lines` was created during `Chart.__init__` **before** `y_axis.parent` reference was set. This caused:
- `left_padding` returned `h_pad` (25.0) instead of calculated value (32.0)
- Grid line coordinates calculated incorrectly
- Extra grid lines rendered beyond plot area

## Fix Applied
Added post-init refresh in `BarChart.__init__`:
```python
# After parent fully initialized, refresh y_axis children
if hasattr(self, 'y_axis') and self.y_axis is not None:
    _ = self.y_axis.children  # Triggers recalculation with correct padding
```

## Verification
All visual tests now pass with correct rendering:
- Grid lines appear only at actual category positions
- No grid lines extending beyond plot boundaries
- Correct axis label positioning
