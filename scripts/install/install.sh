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

# DNF (Fedora/RHEL 8+) - fallback to pip if package not available
if command -v dnf &> /dev/null; then
    echo "📦 DNF detected. Checking for charted package..."
    if dnf list charted 2>&1 | grep -q "charted"; then
        sudo dnf install -y charted
        echo "✅ Installed via DNF"
        exit 0
    else
        echo "⚠️  charted not found in DNF repos. Falling back to pip..."
        sudo dnf install -y python3-pip python3-pipx --skip-unavailable || sudo dnf install -y python3-pip
        if command -v pipx &> /dev/null; then
            pipx install charted
        else
            pip3 install --user charted
            echo "💡 Add ~/.local/bin to your PATH if needed"
        fi
        echo "✅ Installed via pip"
        exit 0
    fi
fi


# APT (Ubuntu/Debian) - fallback to pip if package not available
if command -v apt &> /dev/null; then
    echo "📦 APT detected. Checking for charted package..."
    if apt-cache search charted | grep -q "^charted "; then
        sudo apt update
        sudo apt install -y charted
        echo "✅ Installed via APT"
        exit 0
    else
        echo "⚠️  charted not found in APT repos. Falling back to pip..."
        sudo apt update
        sudo apt install -y python3-pip
        pip3 install --user charted
        echo "✅ Installed via pip"
        echo "💡 Add ~/.local/bin to your PATH if needed"
        exit 0
    fi
fi

# Fallback: pipx (universal)
if command -v pipx &> /dev/null; then
    echo "📦 pipx detected. Installing charted..."
    pipx install charted
    echo "✅ Installed via pipx"
    exit 0
fi

# Fallback: pip
if command -v pip &> /dev/null; then
    echo "📦 pip detected. Installing charted..."
    pip install --user charted
    echo "✅ Installed via pip"
    echo "💡 Add ~/.local/bin to your PATH if needed"
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
