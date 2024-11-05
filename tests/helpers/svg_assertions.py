"""SVG assertion helpers for visual testing."""

import re
from typing import Optional


def assert_svg_valid(svg_content: str) -> None:
    """Assert that SVG content is valid XML structure.

    Args:
        svg_content: SVG string to validate

    Raises:
        AssertionError: If SVG is invalid
    """
    assert svg_content.startswith("<svg"), "SVG must start with <svg> tag"
    assert "</svg>" in svg_content, "SVG must have closing </svg> tag"
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content, (
        "SVG must have proper XML namespace"
    )


def assert_svg_has_element(svg_content: str, element: str) -> None:
    """Assert that SVG contains a specific element.

    Args:
        svg_content: SVG string to check
        element: Element name (e.g., 'path', 'text', 'circle')

    Raises:
        AssertionError: If element not found
    """
    pattern = rf"<{element}"
    assert re.search(pattern, svg_content, re.IGNORECASE), (
        f"SVG must contain <{element}> element"
    )


def assert_svg_has_attribute(
    svg_content: str, attr: str, value: Optional[str] = None
) -> None:
    """Assert that SVG contains a specific attribute.

    Args:
        svg_content: SVG string to check
        attr: Attribute name (e.g., 'fill', 'stroke')
        value: Expected value (optional)

    Raises:
        AssertionError: If attribute not found or value doesn't match
    """
    if value:
        pattern = rf'{attr}=["\']?{re.escape(value)}["\']?'
        assert re.search(pattern, svg_content, re.IGNORECASE), (
            f"SVG must have {attr}='{value}'"
        )
    else:
        pattern = rf"{attr}="
        assert re.search(pattern, svg_content, re.IGNORECASE), (
            f"SVG must have {attr} attribute"
        )


def assert_svg_has_text(svg_content: str, text: str) -> None:
    """Assert that SVG contains specific text content.

    Args:
        svg_content: SVG string to check
        text: Text to find

    Raises:
        AssertionError: If text not found
    """
    assert text in svg_content, f"SVG must contain text '{text}'"


def assert_svg_dimensions(
    svg_content: str, min_width: int = 100, min_height: int = 100
) -> None:
    """Assert that SVG has reasonable dimensions.

    Args:
        svg_content: SVG string to check
        min_width: Minimum expected width
        min_height: Minimum expected height

    Raises:
        AssertionError: If dimensions are too small
    """
    width_match = re.search(r'width=["\']?(\d+)["\']?', svg_content)
    height_match = re.search(r'height=["\']?(\d+)["\']?', svg_content)

    if width_match:
        width = int(width_match.group(1))
        assert width >= min_width, f"SVG width {width} < {min_width}"

    if height_match:
        height = int(height_match.group(1))
        assert height >= min_height, f"SVG height {height} < {min_height}"


def assert_svg_no_errors(svg_content: str) -> None:
    """Assert that SVG doesn't contain error indicators.

    Args:
        svg_content: SVG string to check

    Raises:
        AssertionError: If errors found
    """
    error_patterns = ["NaN", "Infinity", "-Infinity", "error"]
    for pattern in error_patterns:
        assert pattern not in svg_content, f"SVG contains '{pattern}'"


def count_svg_elements(svg_content: str, element: str) -> int:
    """Count occurrences of an SVG element.

    Args:
        svg_content: SVG string to analyze
        element: Element name to count

    Returns:
        Number of occurrences
    """
    pattern = rf"<{element}"
    return len(re.findall(pattern, svg_content, re.IGNORECASE))


def extract_svg_colors(svg_content: str) -> list[str]:
    """Extract all color values from SVG.

    Args:
        svg_content: SVG string to analyze

    Returns:
        List of hex color values
    """
    colors = []

    # Match fill and stroke attributes
    patterns = [
        r'fill=["\']#([0-9A-Fa-f]+)["\']',
        r'stroke=["\']#([0-9A-Fa-f]+)["\']',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, svg_content)
        colors.extend([f"#{m}" for m in matches])

    return list(set(colors))  # Return unique colors
