#!/bin/bash
# Universal installer for charted
# Detects package manager and installs accordingly

set -e

echo "🔍 Detecting system..."

# Homebrew (macOS/Linux)
if command -v brew &> /dev/null; then
    echo "📦 Homebrew detected. Installing charted..."
    brew install marzukia/tap/charted
    exit 0
fi

# DNF (Fedora/RHEL 8+)
if command -v dnf &> /dev/null; then
    echo "📦 DNF detected. Installing charted..."
    sudo dnf install charted
    exit 0
fi

# APT (Ubuntu/Debian)
if command -v apt &> /dev/null; then
    echo "📦 APT detected. Installing charted..."
    sudo apt install charted
    exit 0
fi

# Fallback: pipx (universal)
if command -v pipx &> /dev/null; then
    echo "📦 pipx detected. Installing charted..."
    pipx install charted
    exit 0
fi

# Fallback: pip
if command -v pip &> /dev/null; then
    echo "📦 pip detected. Installing charted..."
    pip install --user charted
    exit 0
fi

echo "❌ No supported package manager found."
echo ""
echo "Please install one of the following:"
echo "  - Homebrew: https://brew.sh"
echo "  - pipx: https://pypa.github.io/pipx/"
echo "  - pip: python -m pip install --user pip"
echo ""
echo "Or install manually:"
echo "  python -m pip install charted"
exit 1
