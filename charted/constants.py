"""Constants for charted - replaces magic numbers with named constants."""

# Chart dimensions
DEFAULT_CHART_WIDTH = 500
DEFAULT_CHART_HEIGHT = 500

# Pie chart specific (wider aspect ratio for dual-column legend)
PIE_CHART_WIDTH = 700
PIE_CHART_HEIGHT = 500

# Typography
DEFAULT_FONT_SIZE = 12
DEFAULT_TITLE_FONT_SIZE = 16
PIE_LABEL_FONT_SIZE = 14
AXIS_LABEL_FONT_SIZE = 12

# Angles (in degrees)
FULL_CIRCLE = 360
RIGHT_ANGLE = 90
STRAIGHT_ANGLE = 180

# Spacing and layout
DEFAULT_PADDING = 18
AXIS_LABEL_ROTATION = 18
MAX_RADIAL_RADIUS_FACTOR = 0.4  # 40% of chart size

# Bar/Column charts
DEFAULT_BAR_GAP = 0.50
DEFAULT_COLUMN_GAP = 0.50

# Axis and reference line styling
AXIS_BORDER_COLOR = "#999"
AXIS_BORDER_WIDTH = 1.5
REFERENCE_LINE_COLOR = "#666"
REFERENCE_LINE_WIDTH = 1.5
REFERENCE_LINE_DASH = "6 3"

# Quadrant label layout
QUADRANT_LABEL_LINE_GAP = 2
QUADRANT_BOTTOM_MARGIN_FACTOR = 0.5

# Auto chart detection
AUTO_PIE_MAX_ITEMS = 6  # Threshold for PieChart vs BarChart

# Font sizing
MIN_FONT_SIZE = 8
FONT_SIZE_DELTA = 4  # title_font_size - 4 for labels

# Legend layout
LEGEND_ROW_GAP = 4
LEGEND_ICON_GAP = 2
LEGEND_PADDING = 0.15
LEGEND_INSET = 4

# Text positioning
TEXT_OFFSET_FACTOR = 0.75  # y = height * 0.75 for text baseline
LABEL_OFFSET = 4  # Space between data mark and label
GRID_MARGIN_FACTOR = 0.6  # font_size * 0.6 for grid line avoidance

# Theme defaults
H_PADDING_DEFAULT = 0.05
V_PADDING_DEFAULT = 0.05
