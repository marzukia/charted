# Package Manager Installation

Install `charted` using your system's package manager.

## Universal Installer (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/marzukia/charted/main/scripts/install/install.sh | bash
```

The installer automatically detects your package manager and uses it.

## Homebrew (macOS/Linux)

First, add the tap:
```bash
brew tap marzukia/tap
```

Then install:
```bash
brew install charted
```

### Building from Source

```bash
brew install --build-from-source charted
```

## APT (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install charted
```

## DNF/RPM (Fedora/RHEL)

```bash
sudo dnf install charted
```

## pipx (Universal Python)

```bash
pipx install charted
```

## pip (Fallback)

```bash
pip install --user charted
```

## Verifying Installation

```bash
charted --version
```

## Usage

```bash
# Interactive chart creation
charted create bar output.svg --data "10,20,30,40" --labels "A,B,C,D" --title "My Chart"

# Batch processing
charted batch ./data ./output --chart-type bar

# Help
charted --help
charted create --help
```
