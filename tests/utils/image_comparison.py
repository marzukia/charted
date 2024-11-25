"""
Image comparison utilities for visual regression testing with PNG baselines.

This module provides pixel-perfect visual regression testing capabilities using PNG images
to prevent AI agents from easily mutating test results. It includes:

1. PNG baseline comparison with configurable tolerance
2. Diff image generation on test failures
3. Hash-based integrity checking for baselines

Dependencies:
    - PIL/Pillow (dev/test only, not required for runtime)
    - numpy (dev/test only)

Usage:
    from tests.utils.image_comparison import compare_images, generate_diff

    # Compare current render with baseline
    is_match, diff_image = compare_images(
        actual_path="tests/output/chart.png",
        baseline_path="tests/baselines/chart.png",
        tolerance=5  # Max pixel difference (0-255)
    )

    if not is_match:
        # Save diff for debugging
        diff_image.save("tests/diffs/chart_diff.png")
"""

from pathlib import Path


# Lazy imports - only imported when functions are called (dev/test dependency)
def _import_pil():
    """Import PIL with helpful error message if not installed."""
    try:
        from PIL import Image

        return Image
    except ImportError:
        raise ImportError(
            "Pillow is required for PNG visual testing. Install with: "
            "pip install 'pillow>=10.0.0' (dev dependency)"
        )


def _import_numpy():
    """Import numpy with helpful error message if not installed."""
    try:
        import numpy as np

        return np
    except ImportError:
        raise ImportError(
            "numpy is required for PNG visual testing. Install with: "
            "pip install 'numpy>=1.24.0' (dev dependency)"
        )


def load_image(path: Path):
    """Load an image from file path."""
    Image = _import_pil()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return Image.open(path).convert("RGB")


def images_to_arrays(image1, image2):
    """Convert PIL images to numpy arrays for comparison."""
    np = _import_numpy()
    arr1 = np.array(image1)
    arr2 = np.array(image2)

    # Ensure same dimensions
    if arr1.shape != arr2.shape:
        raise ValueError(
            f"Image dimensions don't match: {image1.size} vs {image2.size}"
        )

    return arr1, arr2


def compare_images(actual_path: Path, baseline_path: Path, tolerance: int = 5):
    """
    Compare two PNG images pixel-by-pixel with configurable tolerance.

    Args:
        actual_path: Path to the actual/generated image
        baseline_path: Path to the baseline reference image
        tolerance: Maximum allowed pixel difference per channel (0-255).
                  0 = pixel-perfect match required
                  5 = allows minor anti-aliasing/font rendering differences
                  10+ = allows more variation

    Returns:
        Tuple of (is_match, diff_image):
        - is_match: True if images match within tolerance
        - diff_image: Diff visualization if mismatch, None if match

    Raises:
        FileNotFoundError: If baseline image doesn't exist
        ImportError: If Pillow/numpy not installed
    """
    Image = _import_pil()
    np = _import_numpy()

    # Load images
    actual = load_image(actual_path)
    baseline = load_image(baseline_path)

    # Convert to arrays
    arr_actual, arr_baseline = images_to_arrays(actual, baseline)

    # Calculate pixel differences
    diff = np.abs(arr_actual.astype(np.int16) - arr_baseline.astype(np.int16))
    max_diff = np.max(diff)

    if max_diff <= tolerance:
        return True, None

    # Generate diff image showing where they differ
    diff_mask = np.any(diff > tolerance, axis=2)

    # Create colored diff visualization
    diff_vis = Image.new("RGB", actual.size)
    pixels_vis = diff_vis.load()
    pixels_actual = actual.load()

    for y in range(actual.size[1]):
        for x in range(actual.size[0]):
            if diff_mask[y, x]:
                # Highlight differences in red
                pixels_vis[x, y] = (255, 0, 0)
            else:
                # Show actual image for matching areas
                pixels_vis[x, y] = pixels_actual[x, y]

    return False, diff_vis


def calculate_image_hash(path: Path) -> str:
    """
    Calculate SHA256 hash of image file for integrity checking.

    Args:
        path: Path to image file

    Returns:
        Hex-encoded SHA256 hash
    """
    import hashlib

    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def generate_diff_image(
    actual_path: Path, baseline_path: Path, output_path: Path, tolerance: int = 5
) -> bool:
    """
    Generate and save a diff visualization between two images.

    Args:
        actual_path: Path to actual/generated image
        baseline_path: Path to baseline reference image
        output_path: Path where diff image will be saved
        tolerance: Pixel difference tolerance

    Returns:
        True if images differ (diff was generated), False if they match

    Raises:
        FileNotFoundError: If images don't exist
        ImportError: If Pillow/numpy not installed
    """
    is_match, diff_image = compare_images(actual_path, baseline_path, tolerance)

    if diff_image is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        diff_image.save(output_path)
        return True  # Images differ

    return False  # Images match


def render_chart_to_png(chart, width: int = 500, height: int = 500):
    """
    Render a chart object to PNG image.

    Args:
        chart: Chart object with .html or .svg attribute containing SVG data
        width: Output image width in pixels
        height: Output image height in pixels

    Returns:
        PIL Image object

    Note:
        Requires cairosvg for SVG to PNG conversion (dev dependency)
    """
    Image = _import_pil()

    # Try to get SVG string from chart
    if hasattr(chart, "html"):
        svg_data = chart.html
    elif hasattr(chart, "svg"):
        svg_data = chart.svg
    else:
        raise ValueError("Chart object must have 'html' or 'svg' attribute")

    # Convert SVG to PNG using cairosvg
    try:
        import cairosvg
    except ImportError:
        raise ImportError(
            "cairosvg is required for SVG to PNG conversion. "
            "Install with: pip install 'cairosvg>=2.7.0' (dev dependency)"
        )

    png_data = cairosvg.svg2png(
        bytestring=svg_data.encode("utf-8"),
        output_width=width,
        output_height=height,
        scale=2,  # High resolution for better accuracy
    )

    return Image.open(__import__("io").BytesIO(png_data))
