"""
Baseline protection: keeps test/baselines/*.svg and *.png immutable during test runs.

To legitimately update baselines run:
    python scripts/update_baselines.py
which regenerates SVGs, PNGs, and both MANIFEST files.
"""

import hashlib
import json
import pathlib
import stat

import pytest

BASELINES_DIR = pathlib.Path(__file__).parent / "baselines"
MANIFEST_PATH = BASELINES_DIR / "MANIFEST.sha256"
PNG_MANIFEST_PATH = BASELINES_DIR / "PNG_MANIFEST.sha256"


def _make_readonly(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def _make_writable(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


@pytest.fixture(autouse=True, scope="session")
def protect_baselines(request):
    """Lock all baseline SVGs and PNGs read-only before the session; restore after."""
    # Protect SVG baselines
    svgs = list(BASELINES_DIR.glob("*.svg"))
    for svg in svgs:
        _make_readonly(svg)

    # Protect PNG baselines
    pngs = list(BASELINES_DIR.glob("*.png"))
    for png in pngs:
        _make_readonly(png)

    yield

    # Restore write permissions
    for svg in svgs:
        _make_writable(svg)
    for png in pngs:
        _make_writable(png)


def pytest_sessionstart(session):
    """Verify baselines match the committed MANIFESTs before any test runs."""
    failures = []

    # Check SVG baselines
    if not MANIFEST_PATH.exists():
        pytest.exit(
            f"Baseline MANIFEST missing: {MANIFEST_PATH}\n"
            "Run `python scripts/update_baselines.py` to regenerate.",
            returncode=1,
        )

    svg_manifest = json.loads(MANIFEST_PATH.read_text())
    for name, expected_hash in svg_manifest.items():
        svg_path = BASELINES_DIR / name
        if not svg_path.exists():
            failures.append(f"  MISSING: {name}")
            continue
        actual_hash = hashlib.sha256(svg_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            failures.append(
                f"  TAMPERED: {name}\n"
                f"    expected {expected_hash[:16]}...\n"
                f"    got      {actual_hash[:16]}..."
            )

    # Check PNG baselines (if they exist)
    if PNG_MANIFEST_PATH.exists():
        png_manifest = json.loads(PNG_MANIFEST_PATH.read_text())
        for name, expected_hash in png_manifest.items():
            png_path = BASELINES_DIR / name
            if not png_path.exists():
                failures.append(f"  MISSING PNG: {name}")
                continue
            actual_hash = hashlib.sha256(png_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                failures.append(
                    f"  TAMPERED PNG: {name}\n"
                    f"    expected {expected_hash[:16]}...\n"
                    f"    got      {actual_hash[:16]}..."
                )
    else:
        # Warn if PNG baselines are expected but manifest is missing
        png_files = list(BASELINES_DIR.glob("*.png"))
        if png_files:
            failures.append(
                "  PNG baselines exist but PNG_MANIFEST.sha256 is missing.\n"
                "  Run `python scripts/update_baselines.py` to create manifest."
            )

    if failures:
        pytest.exit(
            "Baselines have been modified outside of the update script:\n"
            + "\n".join(failures)
            + "\nRun `python scripts/update_baselines.py` to update intentionally.",
            returncode=1,
        )
