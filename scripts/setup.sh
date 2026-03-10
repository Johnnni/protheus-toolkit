#!/bin/bash
# claude-tdn setup script
# Creates a Python virtual environment and installs dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PLUGIN_DIR/.venv"

echo "=== claude-tdn setup ==="
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Install Python 3.9+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found: $PYTHON_VERSION"

# Create venv
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Reinstalling dependencies..."
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
fi

# Install deps
echo "Installing dependencies..."
pip install -r "$PLUGIN_DIR/server/requirements.txt" --quiet

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Restart Claude Code to activate the TDN tools."
echo "Then ask: 'Search TDN for FWRest documentation'"
