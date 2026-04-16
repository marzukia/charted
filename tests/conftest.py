"""
Baseline protection: keeps test/baselines/*.svg immutable during test runs.

To legitimately update baselines run:
    python scripts/update_baselines.py
which regenerates both the SVGs and MANIFEST.sha256.
"""
import hashlib
import json
import pathlib
import stat

import pytest

BASELINES_DIR = pathlib.Path(__file__).parent / "baselines"
MANIFEST_PATH = BASELINES_DIR / "MANIFEST.sha256"


def _make_readonly(path: pathlib.Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def _make_writable(path: pathlib.Path) -> None:
    path.chmod(
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    )


@pytest.fixture(autouse=True, scope="session")
def protect_baselines(request):
    """Lock all baseline SVGs read-only before the session; restore after."""
    svgs = list(BASELINES_DIR.glob("*.svg"))
    for svg in svgs:
        _make_readonly(svg)
    yield
    for svg in svgs:
        _make_writable(svg)


def pytest_sessionstart(session):
    """Verify baselines match the committed MANIFEST before any test runs."""
    if not MANIFEST_PATH.exists():
        pytest.exit(
            f"Baseline MANIFEST missing: {MANIFEST_PATH}\n"
            "Run `python scripts/update_baselines.py` to regenerate.",
            returncode=1,
        )

    manifest = json.loads(MANIFEST_PATH.read_text())
    failures = []
    for name, expected_hash in manifest.items():
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

    if failures:
        pytest.exit(
            "Baselines have been modified outside of the update script:\n"
            + "\n".join(failures)
            + "\nRun `python scripts/update_baselines.py` to update intentionally.",
            returncode=1,
        )
