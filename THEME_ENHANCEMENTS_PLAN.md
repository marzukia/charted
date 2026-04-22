# Theme System Enhancements - Execution Plan

## Overview
This branch implements the theme system enhancements outlined in GitHub issues #32-#36.

## Execution Order & Dependencies

### Phase 1: Font System (#32)
**Dependency:** Foundation for typography support in #36
**Status:** Font wrapper implemented, needs integration

**Tasks:**
- [ ] Wire `Font` class into `Chart` class for actual text rendering
- [ ] Add more font definitions (Times New Roman, Courier, etc.)
- [ ] Support custom font files (.ttf, .otf) via PIL
- [ ] Implement font styling (bold, italic, weight variations)
- [ ] Add dynamic font size scaling (on-demand generation or interpolation)

**Files to modify:**
- `charted/charts/chart.py` - integrate Font wrapper
- `charted/fonts/definitions/` - add more font JSON definitions
- `charted/fonts/wrapper.py` - add styling support
- `charted/config.py` - update font configuration

---

### Phase 2: Preset Theme Packs (#34)
**Dependency:** Foundation for #35 and #36
**Status:** Basic theme dict support exists

**Tasks:**
- [ ] Add 3 preset themes to `charted/utils/themes.py`:
  - `dark`: dark background, light grid lines, high-contrast colors
  - `light`: white/light gray background, subtle grid lines
  - `high-contrast`: accessibility-optimized, bold colors, thick grid lines
- [ ] Update `Theme.load()` to support preset selection via name
- [ ] Add docs/examples for each preset
- [ ] Update README with theme previews
- [ ] Add tests for preset theme loading

**Files to modify:**
- `charted/utils/themes.py` - add preset definitions
- `charted/config.py` - update theme loading logic
- `docs/config.md` - document presets
- `tests/utils/test_themes.py` - add preset tests

---

### Phase 3: Per-Chart-Type Theme Overrides (#35)
**Dependency:** Builds on #34 (preset themes)
**Status:** Single base theme exists

**Tasks:**
- [ ] Update `Theme.load()` to accept chart-type-specific overrides
- [ ] Add config sections: `[charts.pie]`, `[charts.column]`, etc.
- [ ] Modify `Chart` class to merge base + chart-specific themes
- [ ] Add tests for theme inheritance chain
- [ ] Document config syntax

**Files to modify:**
- `charted/config.py` - update config parsing
- `charted/charts/chart.py` - implement theme merging
- `tests/charts/test_chart.py` - add inheritance tests
- `docs/config.md` - document override syntax

---

### Phase 4: Advanced Styling (#36)
**Dependency:** Requires #32 (typography) and #34 (theme system)
**Status:** Basic colors/grid lines only

**Tasks:**
- [ ] Expand `Theme` TypedDict with new sections:
  - `FillConfig` - solid colors, gradients, patterns, opacity
  - `StrokeConfig` - line width, dash patterns, opacity
  - `TypographyConfig` - per-element font sizes, weights, colors
- [ ] Update rendering code to apply fill/stroke/typography styles
- [ ] Add defaults maintaining current appearance
- [ ] Ensure backwards compatibility with existing themes
- [ ] Add documentation with examples

**Files to modify:**
- `charted/utils/types.py` - add new config types
- `charted/utils/themes.py` - expand Theme schema
- `charted/charts/*.py` - apply advanced styles in rendering
- `docs/config.md` - document advanced styling

---

### Phase 5: Theme System Enhancement Umbrella (#33)
**Dependency:** All above phases
**Status:** Coordination issue

**Tasks:**
- [ ] Verify theme inheritance/composition works end-to-end
- [ ] Consolidate documentation
- [ ] Add comprehensive examples
- [ ] Run full test suite
- [ ] Update README with complete theme system overview

---

## Technical Notes

### Backwards Compatibility
- All new theme fields must have sensible defaults
- Existing `.chartedrc.toml` configs must continue working
- Migration path should be seamless

### Testing Strategy
- Unit tests for each theme component
- Integration tests for theme merging
- Visual regression tests for preset themes
- Backwards compatibility tests

### Documentation Requirements
- Config examples for each feature
- Visual previews of preset themes
- Migration guide (if needed)
- API docs for new types

---

## Related Issues
- #32 - Revisit: Font system expansion
- #33 - Theme System Enhancement
- #34 - Add preset theme packs (dark, light, high-contrast)
- #35 - Per-chart-type theme overrides
- #36 - Advanced styling: fills, strokes, markers, typography
