# Charted Library — Theming System Analysis & UX Improvement Report

**Date:** 2026-05-22  
**Repository:** [marzukia/charted](https://github.com/marzukia/charted)  
**Scope:** Theme system analysis, UX pain points, industry comparison, and improvement recommendations

---

## 1. Current State Assessment

### 1.1 Architecture Overview

Charted's theming system spans four files:

| File | Role |
|------|------|
| `charted/utils/themes.py` | Theme data structures (TypedDicts), preset definitions, `Theme.load()` |
| `charted/utils/theme_manager.py` | `ThemeManager` — bridges config file loading with theme application |
| `charted/config.py` | TOML-based `.chartedrc` config loader; defines global defaults and chart-type overrides |
| `charted/chart_config.py` | Dataclass-based `ChartConfig` hierarchy; `theme` field accepts `Theme | str | None` |

### 1.2 Theme Data Structure

The `Theme` TypedDict in `themes.py` defines these top-level keys:

```python
class Theme(TypedDict):
    colors: list[str] | None          # Color palette (5 colors by default)
    v_grid: GridConfig | None         # Vertical grid lines
    h_grid: GridConfig | None         # Horizontal grid lines
    series_style: SeriesStyleConfig | None  # Per-series defaults
    legend: LegendConfig | None       # Legend appearance
    marker: MarkerConfig | None       # Marker size default
    title: TitleConfig | None         # Title font styling
    padding: PaddingConfig | None     # Chart padding fractions
```

Each sub-config (`GridConfig`, `LegendConfig`, `MarkerConfig`, `TitleConfig`, `PaddingConfig`) is a separate TypedDict with optional fields.

### 1.3 Preset Themes

Four presets are defined, all in the same file:

| Name | Background | Colors | Use Case |
|------|-----------|--------|----------|
| `light` (DEFAULT) | White | Green/blue/red/orange/purple | Default output |
| `dark` | Dark | Teal/orange/yellow/red/dark-blue | Dark backgrounds |
| `high-contrast` | White | Black/yellow/cyan/magenta/green | Accessibility |
| `fungoid` | White | Orange/green/yellow/red/brown | Niche/custom |

### 1.4 How Themes Are Applied

1. **CLI path:** `charted/cli/create.py` instantiates a chart class → passes `theme=None` → `Chart.__init__()` calls `ThemeManager.load_theme(None, chart_type)`.
2. **Programmatic path:** User passes `theme="dark"` or a dict to any chart constructor → `Chart.__init__()` → `ThemeManager.load_theme(theme, chart_type)` → `Theme.load()` does deep merge with defaults.
3. **Config file path:** `.chartedrc.toml` can set `theme = "dark"` globally or `charts.bar.theme = { ... }` per-chart-type overrides.
4. **Per-chart:** Individual chart instances can override the global theme by passing a different `theme` argument.

### 1.5 Configuration File Structure (`.chartedrc.toml`)

```toml
# Global defaults
font = "Arial"
font_size = 12
title_font_size = 16
colors = ["#5fab9e", "#f58b51", ...]
width = 500
height = 500
theme = "dark"

# Chart-type-specific overrides
charts.bar.theme = { colors = ["#ff0000"] }
charts.line.marker_shape = "square"

# Series-style overrides
[[series_styles]]
fill = "#ff0000"
stroke = "#cc0000"
```

---

## 2. UX Pain Points

### 2.1 Critical Issues

| # | Pain Point | Severity | Detail |
|---|-----------|----------|--------|
| C1 | **No programmatic theme API** | Critical | Users cannot create themes in Python code; must use string names or raw dicts. No `Theme("mytheme", colors=[...])` constructor. |
| C2 | **TypedDict is user-facing but not documented** | Critical | `Theme` is a `TypedDict`, meaning users get poor IDE support and no autocomplete on theme properties. The dict keys are magic strings (`"colors"`, `"v_grid"`, etc.). |
| C3 | **Colors are per-theme, not global** | Critical | Each preset redefines the entire 5-color palette. There's no way to set a global color palette that all charts share. Users must copy-paste colors across charts or themes. |
| C4 | **No theme inheritance/composition** | Critical | `deep_merge()` does a single-level merge. You cannot say "start with the light theme and just change the colors." There's no `Theme.compose("light", {colors: [...]})` pattern. |
| C5 | **Config file is opaque for themes** | Critical | The TOML config has no schema validation. Users can write invalid nested structures with no error messages. The `charts.*.theme` override syntax is undocumented and inconsistent. |

### 2.2 Significant Issues

| # | Pain Point | Detail |
|---|-----------|--------|
| S1 | **No dark mode toggle** | The "dark" preset exists but requires manually setting it on every chart instance or in the config file. No `theme="auto"` for system preference detection. |
| S2 | **Limited color palette** | Only 5 colors per theme. Multi-series charts with >5 series will reuse colors with no visual distinction beyond repetition. |
| S3 | **No automatic contrast enforcement** | The library has `get_contrast_color()` in `colors.py` but it's never used during theme application. Titles, legend text, and grid lines may have poor contrast against backgrounds. |
| S4 | **Grid styling is limited** | `GridConfig` only supports `stroke` and `stroke_dasharray`. No support for `visible`, `width`, or per-axis independent styling (v_grid vs h_grid are separate keys but the naming is confusing). |
| S5 | **Legend position is hardcoded** | Only `"topright"` and `"topleft"` are supported. No option for bottom, right side, or floating positions. |
| S6 | **Per-series styles require complex dict** | `SeriesStyleConfig` requires users to construct dicts with keys like `"fill"`, `"stroke"`, `"stroke_dasharray"`. No ergonomic builder pattern. |

### 2.3 Minor Issues

| # | Detail |
|---|--------|
| M1 | `FUNGOID_THEME` is a named preset that feels out of place alongside generic themes like "light" and "dark" |
| M2 | `stroke_dasharray=None` in GridConfig means "no dash" but the type is `str | None` — confusing API |
| M3 | Padding is specified as a fraction (0.05) rather than pixels — unintuitive for users expecting pixel values |
| M4 | No programmatic way to list available themes (`list_themes()`) |
| M5 | The `Theme.load()` method accepts both a dict and a string name, but the behavior differs: strings look up presets, dicts are merged directly with no validation |

---

## 3. Industry Best Practices Comparison

### 3.1 Chart.js

| Feature | Chart.js v4 | Charted |
|---------|-------------|---------|
| Theme API | `options.scales.*`, `options.plugins.legend.*`, `options.color` — flat nested config | Nested TypedDicts with magic string keys |
| Color management | Automatic color assignment from palette, automatic color cycling for multi-series | Manual color list, fixed 5-color palette |
| Dark mode | `options.scales.x.grid.color = 'rgba(255,255,255,0.1)'` — granular per-element | Coarse: entire grid gets same stroke |
| Extensibility | Plugin system for custom behavior | No plugin system; must modify chart class directly |
| Default theme | `"auto"` uses CSS `color-scheme` for light/dark detection | No auto-detection |

### 3.2 Plotly (Python)

| Feature | Plotly | Charted |
|---------|--------|---------|
| Theme API | `Template` objects with `layout` and `data` properties; registered in `pio.templates["name"]` | Raw dicts merged with `deep_merge()` |
| Theme composition | `"plotly+dark"` — compose multiple templates with `+` | No composition support |
| Per-trace defaults | `template.data.scatter = [Scatter(marker=dict(...))]` — type-safe per-trace defaults | No per-chart-type defaults beyond basic config |
| Color palette | `colorway` property with automatic cycling | Fixed 5-color list, no cycling |
| Registration | `pio.templates["custom"] = Template(...)` — simple dict-style registration | No registration mechanism |

### 3.3 Highcharts

| Feature | Highcharts | Charted |
|---------|------------|---------|
| Theme API | Named themes with full object definitions; can extend base theme | String names only, no inheritance |
| Accessibility | Built-in `accessibility` section in themes (contrast ratios, screen reader text) | No accessibility support |
| Responsive | Themes can include responsive rules | No responsive theming |

### 3.4 Matplotlib

| Feature | Matplotlib | Charted |
|---------|------------|---------|
| Theme API | `matplotlib.style.use('seaborn-v0_8')` — named style sheets; `plt.style.context()` for temporary themes | Manual per-chart application only |
| rcParams | Global `rcParams` dictionary for defaults | Config file only, no programmatic override at runtime |
| Custom themes | `matplotlib.rcParams.update({...})` or custom `.mplstyle` files | No equivalent |

### 3.5 Key Takeaways from Industry Comparison

1. **Theme composition** (Plotly's `"plotly+dark"`) is the most valuable pattern — it lets users layer customizations on top of built-in defaults without copying entire theme definitions.
2. **Automatic color cycling** (Chart.js, Plotly) handles multi-series charts gracefully; Charted's fixed 5-color list fails for larger datasets.
3. **Type-safe theme objects** (Plotly's `Template`) provide IDE autocomplete and validation; Charted's raw dicts do not.
4. **Registration API** (`pio.templates["name"] = Template(...)`) is the simplest, most discoverable pattern for extending themes.
5. **Accessibility** (contrast checking, screen-reader text) is standard in commercial charting libraries but absent in Charted.

---

## 4. Concrete Improvement Suggestions

### Priority 1 — Core API Overhaul (P0)

#### 4.1 Introduce a `Theme` dataclass (replace TypedDict)

**Rationale:** TypedDicts provide zero runtime behavior, no validation, and poor IDE support. A dataclass gives autocomplete, type checking, and a clean constructor.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class ColorPalette:
    colors: list[str] = field(default_factory=lambda: ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"])
    
    def get_color(self, index: int) -> str:
        return self.colors[index % len(self.colors)]

@dataclass(frozen=True)
class Theme:
    """Immutable theme configuration for charted charts."""
    
    colors: list[str] = field(default_factory=list)  # Empty = use defaults
    grid_color: str = "#CCCCCC"
    grid_dasharray: Optional[str] = None
    grid_visible: bool = True
    legend_position: str = "topright"
    legend_font_size: int = 11
    title_color: str = "#444444"
    title_font_size: int = 16
    title_font_family: str = "Arial"
    background_color: str = "#FFFFFF"
    
    @classmethod
    def from_preset(cls, name: str) -> "Theme":
        """Load a built-in preset theme."""
        presets = {
            "light": cls(colors=["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"]),
            "dark": cls(colors=["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
                        background_color="#1a1a1a", grid_color="#444444"),
            "high-contrast": cls(colors=["#000000", "#FFFF00", "#00FFFF", "#FF00FF", "#00FF00"],
                                 title_color="#000000"),
        }
        if name not in presets:
            raise ValueError(f"Unknown theme: {name!r}. Available: {list(presets.keys())}")
        return presets[name]
    
    def compose(self, overrides: Optional["Theme"] = None) -> "Theme":
        """Create a new theme by merging self with overrides."""
        if overrides is None:
            return self
        # Use dataclasses.replace for immutable update
        return dataclasses.replace(self, **{
            k: v for k, v in dataclasses.asdict(overrides).items()
            if v is not None and v != []
        })
    
    def cycle_color(self, index: int) -> str:
        """Get color at index, cycling through the palette."""
        return self.colors[index % len(self.colors) if self.colors else "#5fab9e"]
```

**Benefits:**
- `Theme.from_preset("dark")` — discoverable, autocomplete-friendly
- `theme.compose(Theme(colors=["#ff0000"]))` — layered customization
- `theme.cycle_color(7)` — automatic color cycling for large datasets
- Full IDE support with autocomplete on every property

#### 4.2 Add Theme Registration API

```python
# charted/themes/__init__.py
from charted.themes.registry import register_theme, list_themes, get_default_theme

# Users can register custom themes:
register_theme("corporate", Theme(colors=["#1a365d", "#2b6cb0", "#3182ce", "#4299e1", "#63b3ed"]))

# List available themes
available = list_themes()  # ["light", "dark", "high-contrast", "fungoid", "corporate"]

# Set default theme (session-wide)
get_default_theme().set_default("dark")
```

**Rationale:** This mirrors Plotly's `pio.templates["name"] = Template(...)` pattern. It's the single most important UX improvement for theme extensibility.

### Priority 2 — Color System Improvements

#### 4.3 Automatic Color Assignment with Cyclic Palette

```python
# In chart rendering (line_renderer.py, bar_renderer.py, etc.)
class ColorManager:
    def __init__(self, theme: Theme, num_series: int):
        self.theme = theme
        self.num_series = num_series
    
    def get_color(self, index: int) -> str:
        """Get color for series at given index, cycling through palette."""
        return self.theme.cycle_color(index)
    
    def ensure_palette_size(self, min_colors: int) -> list[str]:
        """Expand palette if more series than colors available."""
        if len(self.theme.colors) >= min_colors:
            return self.theme.colors
        # Generate additional colors using HSL cycling
        base_colors = self.theme.colors
        extra = []
        for i in range(min_colors - len(base_colors)):
            hue = (i * 360 / min_colors) % 360
            extra.append(f"hsl({hue}, 70%, 50%)")
        return base_colors + extra
```

**Rationale:** Chart.js and Plotly both automatically cycle colors. Users currently hit a wall at 5 series with no way to get more distinct colors without manually specifying them.

#### 4.4 WCAG Contrast Enforcement

```python
# In theme application, validate that text colors have sufficient contrast
from charted.utils.colors import hex_to_rgb

def ensure_contrast(fg_hex: str, bg_hex: str, min_ratio: float = 4.5) -> str:
    """Ensure foreground has sufficient contrast against background."""
    # Use existing get_contrast_color() or implement full WCAG check
    # If contrast is insufficient, adjust luminance of fg color
    pass
```

**Rationale:** The library already has `get_contrast_color()` but never uses it. This is critical for accessibility compliance (WCAG 2.1 AA requires 4.5:1 contrast ratio for normal text).

### Priority 3 — Configuration & Discovery

#### 4.5 Config File Schema Validation

```toml
# .chartedrc.toml — now with proper structure
[theme]
name = "dark"           # or "light", "high-contrast", or custom theme name

[theme.colors]
palette = ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]

[theme.grid]
color = "#444444"
visible = true
dash_pattern = "2,2"    # New: explicit naming

[theme.legend]
position = "topright"   # Options: topright, topleft, bottomcenter, right
font_size = 11
```

**Rationale:** Current TOML config has no validation. Users can write anything and get silent failures or confusing behavior. A schema-aware loader with clear error messages is essential.

#### 4.6 Programmatic Theme Discovery

```python
from charted.themes import list_themes, get_theme

# Discover available themes
themes = list_themes()
# Returns: ["light", "dark", "high-contrast", "fungoid", "corporate"]

# Get theme metadata
info = get_theme("dark")
print(info.description)      # "Dark theme with teal/orange palette"
print(info.colors)           # ["#5fab9e", "#f58b51", ...]
print(info.available_keys()) # All configurable properties
```

**Rationale:** Users currently have no way to discover what themes exist or what options are available. This is a basic UX requirement present in every major library.

### Priority 4 — Chart-Type-Specific Theming

#### 4.7 Per-Chart-Type Default Overrides

```toml
# In config:
[charts.line]
marker_shape = "circle"
marker_size = 4

[charts.bar]
bar_color = "#5fab9e"

[charts.pie]
inner_radius = 0.0
label_font_size = 14
```

**Rationale:** Currently, chart-type overrides are applied via the `get_chart_theme()` function in `config.py`, but the mechanism is opaque and undocumented. Exposing this as a first-class feature with clear TOML keys makes it discoverable and reliable.

#### 4.8 Per-Series Style Builders

```python
from charted.chart_config import SeriesStyle

# Current (verbose, error-prone):
series_styles = [
    {"fill": "#ff0000", "stroke": "#cc0000"},
    {"fill": "#00ff00", "stroke": "#00cc00"},
]

# Proposed (clean, type-safe):
from charted.chart_config import BarChart, SeriesStyle

style1 = SeriesStyle(fill="#ff0000", stroke="#cc0000")
style2 = SeriesStyle.fill("#00ff00").stroke("#00cc00")  # builder pattern

chart = BarChart(
    data=[[120, 180], [210, 150]],
    series_styles=[style1, style2],
)
```

### Priority 5 — Visual Enhancements

#### 4.9 Background Color Support

```python
# Currently, the background is always white (hardcoded in Chart.container property)
# Add:
background_color: str = "#FFFFFF"  # In Theme dataclass

# In Chart.__init__:
self._background_color = self.theme.background_color
```

#### 4.10 Responsive Padding

```python
# Current: padding as fraction (0.05 = 5% of chart size)
# Better: allow pixel values too
padding: float | str = "5%"  # or 25 (pixels)
```

---

## 5. Recommended Implementation Roadmap

| Phase | Scope | Effort | Impact |
|-------|-------|--------|--------|
| **Phase 1** | Dataclass `Theme` + `from_preset()` + `compose()` + `cycle_color()` | 2-3 days | High — fixes all critical UX issues |
| **Phase 2** | Theme registration API (`register_theme`, `list_themes`) | 1-2 days | High — enables extensibility |
| **Phase 3** | Color palette auto-expansion + contrast checking | 1-2 days | Medium — handles edge cases |
| **Phase 4** | Config schema validation + docs update | 2-3 days | Medium — prevents user errors |
| **Phase 5** | Per-series style builders + chart-type defaults | 2-3 days | Low-Medium — polish |
| **Phase 6** | Background color + responsive padding | 1 day | Low |

---

## 6. Summary of Key Findings

### What We Found

1. **Charted has a functional but incomplete theming system.** The TypedDict-based approach works but provides poor developer experience (no autocomplete, no validation, magic strings).

2. **The theme system is fragmented across 4 files** with inconsistent patterns — `Theme.load()` accepts both strings and dicts, `ThemeManager` adds another layer of indirection, and the config file has undocumented override syntax.

3. **The color system is the weakest link.** A fixed 5-color palette per preset with no cycling, no auto-expansion, and no contrast checking means charts look bad with >5 series and may fail accessibility requirements.

4. **Industry standards clearly favor composable, type-safe theme objects** (Plotly's `Template`, Chart.js's flat config). Charted should adopt a dataclass-based approach with registration API.

### What We Recommend

1. **Replace TypedDict `Theme` with a frozen dataclass** — this is the single highest-impact change. It solves autocomplete, validation, and immutability in one move.

2. **Add theme registration (`register_theme`, `list_themes`)** — mirrors Plotly's pattern and enables community/theme ecosystem growth.

3. **Implement automatic color cycling** — essential for any charting library that supports multi-series charts.

4. **Add contrast validation** — use the existing `get_contrast_color()` utility to ensure readable text on all backgrounds.

5. **Document the configuration schema** with examples — the current TOML config has undocumented behavior that confuses users.

### Files That Need Modification

| File | Change |
|------|--------|
| `charted/utils/themes.py` | Replace TypedDicts with dataclass-based `Theme` |
| `charted/utils/theme_manager.py` | Simplify — delegate to new Theme API |
| `charted/config.py` | Update to work with new Theme API; add schema validation |
| `charted/chart_config.py` | Update `theme` field type from `Theme | str | None` to new dataclass |
| `charted/charts/chart.py` | Minor updates for new theme interface |
| `charted/utils/colors.py` | Add contrast validation + palette expansion utilities |
| `charted/__init__.py` | Export new theme functions (`register_theme`, `list_themes`, etc.) |
