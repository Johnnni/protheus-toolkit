#!/bin/bash
# claude-tdn MCP server launcher
# Activates venv and runs the MCP server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PLUGIN_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR" >&2
    echo "Run the setup script first: bash $PLUGIN_DIR/scripts/setup.sh" >&2
    exit 1
fi

# Activate venv (works on Linux/macOS/WSL)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
fi

python "$PLUGIN_DIR/server/tdn_server.py"
