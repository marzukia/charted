"""Property-based tests for theme system using hypothesis.

These tests verify theme composition, immutability, and validation.
Install hypothesis: uv pip install hypothesis
Run: pytest tests/properties/ --hypothesis-seed=0
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from charted.themes.core import ColorPalette, Theme

# ============================================================
# Color Palette Properties
# ============================================================


@given(
    colors=st.lists(
        st.sampled_from(["#F00", "#0F0", "#00F", "#FF0", "#0FF", "#F0F"]),
        min_size=1,
        max_size=10,
    ),
    index=st.integers(0, 1000),
)
@settings(max_examples=100)
def test_color_cycling_is_deterministic(colors, index):
    """Color palette cycling should be deterministic."""
    palette = ColorPalette(colors=colors)

    # Multiple calls with same index should return same color
    for _ in range(5):
        assert palette.get_color(index) == colors[index % len(colors)]


@given(
    colors=st.lists(st.sampled_from(["#F00", "#0F0", "#00F"]), min_size=1, max_size=5),
    min_colors=st.integers(1, 20),
)
@settings(max_examples=100)
def test_palette_expansion_preserves_original(colors, min_colors):
    """Expanded palette should preserve original colors."""
    palette = ColorPalette(colors=colors)
    expanded = palette.expand(min_colors)

    # First N colors should match original
    for i, color in enumerate(colors):
        assert expanded.colors[i] == color


@given(
    colors=st.lists(st.sampled_from(["#F00"]), min_size=1, max_size=1),
    min_colors=st.integers(5, 20),
)
@settings(max_examples=50)
def test_palette_expansion_generates_hsl(colors, min_colors):
    """Expanded palette should generate HSL colors for additional slots."""
    palette = ColorPalette(colors=colors)
    expanded = palette.expand(min_colors)

    assert len(expanded.colors) == min_colors
    # Generated colors should be HSL format
    generated = expanded.colors[len(colors) :]
    for color in generated:
        assert color.startswith("hsl(")


@given(
    colors=st.lists(st.sampled_from(["#F00", "#0F0", "#00F"]), min_size=1, max_size=5),
)
@settings(max_examples=50)
def test_palette_expand_returns_copy(colors):
    """expand should return a copy, not modify original."""
    palette = ColorPalette(colors=colors)
    original_len = len(palette.colors)
    original_colors = palette.colors.copy()

    result = palette.expand(10)

    # Original should be unchanged
    assert len(palette.colors) == original_len
    assert palette.colors == original_colors
    # Result should be different object
    assert result is not palette


# ============================================================
# Theme Immutability Properties
# ============================================================


@given(
    colors=st.lists(st.sampled_from(["#F00", "#0F0", "#00F"]), min_size=1, max_size=5),
)
@settings(max_examples=50)
def test_theme_is_frozen(colors):
    """Theme should be immutable (frozen dataclass)."""
    theme = Theme(colors=colors)

    # Attempting to modify should raise
    with pytest.raises(Exception):  # FrozenInstanceError
        theme.title_color = "#FFF"


@given(
    base_colors=st.lists(st.sampled_from(["#F00", "#0F0"]), min_size=1, max_size=3),
    override_colors=st.lists(st.sampled_from(["#00F", "#FF0"]), min_size=1, max_size=3),
)
@settings(max_examples=50)
def test_compose_returns_new_instance(base_colors, override_colors):
    """compose() should return new Theme instance, not modify original."""
    base = Theme(colors=base_colors)
    override = Theme(colors=override_colors)

    original_base_colors = base.colors.copy()
    result = base.compose(override)

    # Base should be unchanged
    assert base.colors == original_base_colors
    # Result should be different object
    assert result is not base


# ============================================================
# Theme Composition Properties
# ============================================================


@given(
    base_colors=st.lists(st.sampled_from(["#F00", "#0F0"]), min_size=1, max_size=3),
    override_colors=st.lists(st.sampled_from(["#00F", "#FF0"]), min_size=1, max_size=3),
)
@settings(max_examples=50)
def test_compose_applies_color_override(base_colors, override_colors):
    """Composing with color override should apply the override."""
    base = Theme(colors=base_colors)
    override = Theme(colors=override_colors)

    result = base.compose(override)

    assert result.colors == override_colors


@given(
    base_background=st.sampled_from(["#FFF", "#000"]),
    override_background=st.sampled_from(
        ["#111", "#222"]
    ),  # Dark backgrounds with white text
)
@settings(max_examples=50)
def test_compose_applies_background_override(base_background, override_background):
    """Composing with background override should apply it."""
    # Use legend colors that have adequate contrast with both backgrounds
    if base_background == "#FFF":
        base_legend = "#000000"  # Black on white
    else:
        base_legend = "#FFFFFF"  # White on black

    if override_background in ["#111", "#222"]:
        override_legend = "#FFFFFF"  # White on dark
    else:
        override_legend = "#000000"  # Black on light

    base = Theme(background_color=base_background, legend_font_color=base_legend)
    override = Theme(
        background_color=override_background, legend_font_color=override_legend
    )

    result = base.compose(override)

    assert result.background_color == override_background


@given(
    base_colors=st.lists(st.sampled_from(["#F00"]), min_size=1, max_size=1),
)
@settings(max_examples=50)
def test_compose_preserves_non_overridden_fields(base_colors):
    """Composing should preserve base theme's non-overridden fields."""
    base = Theme.from_preset("light")
    override = Theme(colors=base_colors)  # Only override colors

    result = base.compose(override)

    # Non-color fields should match base, not class defaults
    assert result.background_color == base.background_color
    assert result.title_color == base.title_color
    assert result.grid_color == base.grid_color


@given(
    colors1=st.lists(st.sampled_from(["#F00"]), min_size=1, max_size=1),
    colors2=st.lists(st.sampled_from(["#0F0"]), min_size=1, max_size=1),
)
@settings(max_examples=50)
def test_compose_none_returns_copy(colors1, colors2):
    """Composing with None should return a copy of base."""
    base = Theme(colors=colors1)

    result = base.compose(None)

    assert result.colors == base.colors
    assert result is not base  # But different object


# ============================================================
# Theme Validation Properties
# ============================================================


@given(
    color=st.sampled_from(["#FFF", "#FFFFFF", "#FFFFFFFF", "#abc", "#aBcDeF"]),
)
@settings(max_examples=50)
def test_theme_accepts_valid_hex_colors(color):
    """Theme should accept valid hex colors in all positions."""
    # Should not raise
    Theme(colors=[color], title_color=color, background_color=color, grid_color=color)


@given(
    invalid=st.text(min_size=1, max_size=20),
)
@settings(max_examples=200)
def test_theme_rejects_invalid_hex_colors(invalid):
    """Theme should reject invalid hex colors."""
    from charted.themes.core import _is_valid_hex_color

    if not _is_valid_hex_color(invalid):
        with pytest.raises(ValueError, match="Invalid color"):
            Theme(colors=[invalid])


@given(
    preset_name=st.sampled_from(["light", "dark", "high-contrast"]),
)
@settings(max_examples=30)
def test_from_preset_returns_valid_theme(preset_name):
    """from_preset() should return valid Theme with all required fields."""
    from charted.themes.core import _is_valid_hex_color

    theme = Theme.from_preset(preset_name)

    # Should have all required attributes
    assert hasattr(theme, "colors")
    assert hasattr(theme, "title_color")
    assert hasattr(theme, "background_color")
    assert hasattr(theme, "grid_color")

    # Colors should be valid hex
    for color in theme.colors:
        assert _is_valid_hex_color(color)


@given(
    invalid_preset=st.text(min_size=1, max_size=20),
)
@settings(max_examples=100)
def test_from_preset_rejects_unknown_preset(invalid_preset):
    """from_preset() should reject unknown preset names."""
    valid_presets = ["light", "dark", "high-contrast"]

    if invalid_preset not in valid_presets:
        with pytest.raises(ValueError, match="Unknown theme"):
            Theme.from_preset(invalid_preset)


# ============================================================
# Edge Cases and Stress Tests
# ============================================================


@given(
    colors=st.lists(st.sampled_from(["#F00"]), min_size=1, max_size=1),
)
@settings(max_examples=50)
def test_empty_compose_list_uses_base(colors):
    """Composing with empty color list should preserve base colors."""
    base = Theme(colors=colors)
    override = Theme(colors=[])  # Empty list

    result = base.compose(override)

    # Empty list should not override
    assert result.colors == base.colors


@given(
    index=st.integers(-100, 1000),
)
@settings(max_examples=100)
def test_cycle_color_handles_negative_indices(index):
    """cycle_color should handle negative indices via modulo."""
    theme = Theme(colors=["#F00", "#0F0", "#00F"])

    result = theme.cycle_color(index)

    # Should return a valid color from the palette
    assert result in theme.colors


@given(
    colors=st.lists(st.sampled_from(["#F00"]), min_size=1, max_size=1),
)
@settings(max_examples=50)
def test_theme_defaults_are_valid(colors):
    """Theme with only colors set should have valid defaults for other fields."""
    from charted.themes.core import _is_valid_hex_color

    theme = Theme(colors=colors)

    # All color fields should be valid hex
    assert _is_valid_hex_color(theme.title_color)
    assert _is_valid_hex_color(theme.background_color)
    assert _is_valid_hex_color(theme.grid_color)
