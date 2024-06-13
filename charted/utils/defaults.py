import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
EXAMPLES_DIR = os.path.join(DOCS_DIR, "examples")
DEFAULT_COLORS = ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]
BASE_DEFINITIONS_DIR = os.path.join(BASE_DIR, "charted", "fonts", "definitions")
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_TITLE_FONT_SIZE = 16

if os.name == "nt":
    DEFAULT_FONT = "Arial"
