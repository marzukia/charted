from charted.utils.defaults import (
    BASE_DEFINITIONS_DIR,
    BASE_DIR,
    DEFAULT_COLORS,
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_TITLE_FONT_SIZE,
    DOCS_DIR,
    EXAMPLES_DIR,
)


class TestDefaults:
    """Tests for charted.utils.defaults module."""

    def test_base_dir_exists(self):
        """Test that BASE_DIR exists and is a valid path."""
        import os

        assert os.path.exists(BASE_DIR)
        assert os.path.isdir(BASE_DIR)

    def test_docs_dir_exists(self):
        """Test that DOCS_DIR exists and is a valid path."""
        import os

        assert os.path.exists(DOCS_DIR)
        assert os.path.isdir(DOCS_DIR)

    def test_examples_dir_exists(self):
        """Test that EXAMPLES_DIR exists and is a valid path."""
        import os

        assert os.path.exists(EXAMPLES_DIR)
        assert os.path.isdir(EXAMPLES_DIR)

    def test_base_definitions_dir_exists(self):
        """Test that BASE_DEFINITIONS_DIR exists and is a valid path."""
        import os

        assert os.path.exists(BASE_DEFINITIONS_DIR)
        assert os.path.isdir(BASE_DEFINITIONS_DIR)

    def test_default_colors_count(self):
        """Test that DEFAULT_COLORS has the expected number of colors."""
        assert len(DEFAULT_COLORS) == 5

    def test_default_colors_format(self):
        """Test that all colors are valid hex colors."""
        for color in DEFAULT_COLORS:
            assert color.startswith("#")
            assert len(color) == 7

    def test_default_font(self):
        """Test that DEFAULT_FONT is set."""
        assert DEFAULT_FONT is not None
        assert len(DEFAULT_FONT) > 0

    def test_default_font_size(self):
        """Test that DEFAULT_FONT_SIZE is a positive integer."""
        assert DEFAULT_FONT_SIZE > 0

    def test_default_title_font_size(self):
        """Test that DEFAULT_TITLE_FONT_SIZE is a positive integer."""
        assert DEFAULT_TITLE_FONT_SIZE > 0

    def test_font_directories_structure(self):
        """Test that font definition directories exist."""
        import os

        # Check that the definitions directory exists
        assert os.path.exists(BASE_DEFINITIONS_DIR)

        # Check that at least one font definition exists
        font_files = [
            f for f in os.listdir(BASE_DEFINITIONS_DIR) if f.endswith(".json")
        ]
        assert len(font_files) > 0
