#!/bin/bash
# Hook: check-ascii
# Event: PostToolUse (Write, Edit)
# Verifica se arquivos ADVPL/TLPP contem apenas caracteres ASCII validos
# O compilador ADVPL nao suporta UTF-8 — acentos causam erro de compilacao

# Recebe o path do arquivo via stdin (JSON do tool result)
FILE_PATH=$(cat | grep -oP '"file_path"\s*:\s*"([^"]+)"' | head -1 | sed 's/.*"file_path"\s*:\s*"//;s/"$//')

# Só verifica arquivos Protheus
if [[ ! "$FILE_PATH" =~ \.(prw|tlpp|prx|aph|ch)$ ]]; then
  exit 0
fi

# Verifica caracteres não-ASCII
if [ -f "$FILE_PATH" ]; then
  NON_ASCII=$(grep -Pn '[^\x00-\x7F]' "$FILE_PATH" 2>/dev/null | head -5)
  if [ -n "$NON_ASCII" ]; then
    echo "AVISO: Caracteres nao-ASCII detectados em $FILE_PATH"
    echo "O compilador ADVPL nao suporta UTF-8. Linhas com problema:"
    echo "$NON_ASCII"
    echo "Substitua acentos por equivalentes ASCII (ex: ã→a, ç→c, é→e)"
    exit 1
  fi
fi

exit 0
