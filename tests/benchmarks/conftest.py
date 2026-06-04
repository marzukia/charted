"""Skip the benchmark suite when pytest-benchmark is not installed.

The benchmarks use the ``benchmark`` fixture provided by the optional
pytest-benchmark plugin, which is not in the base dev dependencies. Without it
pytest errors at fixture setup during collection, so skip this directory
entirely when the plugin is absent (CI and a default dev install both lack it).
Install pytest-benchmark to run these.
"""

try:
    import pytest_benchmark  # noqa: F401
except ImportError:
    collect_ignore_glob = ["*"]
