#!/bin/bash
# claude-tdn - Launcher do servidor MCP
# Ativa o venv e executa o servidor

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PLUGIN_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Erro: Ambiente virtual nao encontrado em $VENV_DIR" >&2
    echo "Rode o setup primeiro: bash $PLUGIN_DIR/scripts/setup.sh" >&2
    exit 1
fi

# Ativar venv (funciona no Linux/macOS/WSL)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
fi

python "$PLUGIN_DIR/server/tdn_server.py"
