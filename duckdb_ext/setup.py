"""Setup script for the charted DuckDB extension."""

from setuptools import find_packages, setup

setup(
    name="charted-duckdb",
    version="0.1.0",
    description="DuckDB extension for generating SVG charts with charted",
    packages=find_packages(),
    install_requires=[
        "duckdb>=0.9.0",
        "charted",
    ],
    python_requires=">=3.10",
)
