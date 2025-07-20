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

You should see the installed version number.
