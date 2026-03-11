#!/bin/bash
# claude-tdn setup
# Cria ambiente virtual Python e instala dependencias

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PLUGIN_DIR/.venv"

echo "=== claude-tdn setup ==="
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 e necessario mas nao foi encontrado."
    echo "Instale o Python 3.9+ e tente novamente."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found: $PYTHON_VERSION"

# Create venv
if [ -d "$VENV_DIR" ]; then
    echo "Ambiente virtual ja existe. Reinstalando dependencias..."
else
    echo "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
fi

# Activate
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
fi

# Install deps
echo "Instalando dependencias..."
pip install -r "$PLUGIN_DIR/server/requirements.txt" --quiet

# Generate .mcp.json with correct Python path for this platform
PYTHON_PATH="$VENV_DIR/bin/python"
if [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    PYTHON_PATH="$VENV_DIR/Scripts/python.exe"
fi

# Convert Git Bash paths (/c/...) to Windows paths (C:/...) if on Windows
# Use forward slashes (C:/...) which work in JSON and on both platforms
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "mingw"* ]]; then
    PYTHON_PATH="$(cygpath -m "$PYTHON_PATH" 2>/dev/null || echo "$PYTHON_PATH")"
    PLUGIN_DIR_MCP="$(cygpath -m "$PLUGIN_DIR" 2>/dev/null || echo "$PLUGIN_DIR")"
else
    PLUGIN_DIR_MCP="$PLUGIN_DIR"
fi

cat > "$PLUGIN_DIR/.mcp.json" << MCPEOF
{
  "tdn": {
    "type": "stdio",
    "command": "$PYTHON_PATH",
    "args": ["${PLUGIN_DIR_MCP}/server/tdn_server.py"]
  }
}
MCPEOF

echo ""
echo "=== Setup concluido! ==="
echo ""
echo "MCP configurado com Python: $PYTHON_PATH"
echo "Reinicie o Claude Code para ativar as ferramentas do TDN."
echo "Depois pergunte: 'Busca a documentacao do FWRest no TDN'"
