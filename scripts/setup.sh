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

echo ""
echo "=== Setup concluido! ==="
echo ""
echo "Reinicie o Claude Code para ativar as ferramentas do TDN."
echo "Depois pergunte: 'Busca a documentacao do FWRest no TDN'"
