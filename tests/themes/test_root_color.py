"""Tests for theme opacity tiers with root color (Issue #25)."""

import pytest

from charted.themes.core import Theme
from charted.utils.colors import derive_color

# =========================================================================
# 1. Theme.root_color field
# =========================================================================


class TestRootColorField:
    def test_default_is_black(self):
        t = Theme()
        assert t.root_color == "#000000"

    def test_dark_preset_is_white(self):
        t = Theme.from_preset("dark")
        assert t.root_color == "#ffffff"

    def test_custom_value(self):
        t = Theme(root_color="#112233")
        assert t.root_color == "#112233"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="root_color"):
            Theme(root_color="not-a-color")


# =========================================================================
# 2. derive_color helper
# =========================================================================


class TestDeriveColor:
    def test_full_opacity(self):
        assert derive_color("#000000", 1.0) == "#000000"

    def test_half_opacity(self):
        assert derive_color("#000000", 0.5, "#ffffff") == "#7f7f7f"

    def test_twenty_percent(self):
        assert derive_color("#000000", 0.20, "#ffffff") == "#cccccc"

    def test_white_root_on_black(self):
        assert derive_color("#ffffff", 0.6, "#000000") == "#999999"

    def test_preserves_rgb_channel(self):
        result = derive_color("#ff0000", 0.5, "#ffffff")
        assert result == "#ff7f7f"
        assert len(result) == 7


# =========================================================================
# 3. Theme resolved color methods
# =========================================================================


class TestResolvedColors:
    def test_resolved_grid_color_default(self):
        """Default grid_color (#CCCCCC) should resolve to root at 20%."""
        t = Theme()
        assert t.resolved_grid_color == derive_color("#000000", 0.20, "#FFFFFF")

    def test_resolved_grid_color_explicit(self):
        """Explicit override should be returned as-is."""
        t = Theme(grid_color="#ff0000")
        assert t.resolved_grid_color == "#ff0000"

    def test_resolved_axis_border_color_default(self):
        t = Theme()
        assert t.resolved_axis_border_color == derive_color("#000000", 0.60, "#FFFFFF")

    def test_resolved_reference_line_color_default(self):
        t = Theme()
        assert t.resolved_reference_line_color == derive_color("#000000", 0.50, "#FFFFFF")

    def test_resolved_axis_title_color_default(self):
        """Default title_color (#444444) should resolve to root at 80%."""
        t = Theme()
        assert t.resolved_axis_title_color == derive_color("#000000", 0.80, "#FFFFFF")

    def test_resolved_axis_title_color_explicit(self):
        t = Theme(title_color="#ff0000")
        assert t.resolved_axis_title_color == "#ff0000"

    def test_resolved_label_color_default(self):
        t = Theme()
        assert t.resolved_label_color == derive_color("#000000", 1.0, "#FFFFFF")

    def test_resolved_quadrant_label_color_default(self):
        t = Theme()
        assert t.resolved_quadrant_label_color == derive_color("#000000", 0.18, "#FFFFFF")


# =========================================================================
# 4. Compose preserves root_color
# =========================================================================


class TestComposeRootColor:
    def test_compose_preserves_root(self):
        base = Theme(root_color="#ff0000")
        result = base.compose(Theme(grid_color="#aabbcc"))
        assert result.root_color == "#ff0000"

    def test_compose_override_root(self):
        base = Theme(root_color="#ff0000")
        result = base.compose(Theme(root_color="#00ff00"))
        assert result.root_color == "#00ff00"


# =========================================================================
# 5. Backward compatibility
# =========================================================================


class TestBackwardCompat:
    def test_light_preset_explicit_colors(self):
        t = Theme.from_preset("light")
        # Light preset sets explicit grid_color="#6b7280" which != default "#CCCCCC"
        assert t.resolved_grid_color == "#6b7280"

    def test_dark_preset_explicit_colors(self):
        t = Theme.from_preset("dark")
        # Dark preset sets explicit title_color="#ffffff" which != default "#444444"
        assert t.resolved_axis_title_color == "#ffffff"

    def test_high_contrast_preset_explicit_colors(self):
        t = Theme.from_preset("high-contrast")
        # High-contrast preset sets explicit grid_color="#000000"
        assert t.resolved_grid_color == "#000000"
