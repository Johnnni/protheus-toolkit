#!/bin/bash
# tds-validate.sh — Syntax validation via advpls appre (no server needed)
# Usage: tds-validate.sh <file.tlpp|file.prw>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tds-discover.sh"

validate_syntax() {
    local file_path="$1"

    # Get advpls path
    local advpls
    advpls=$(tds_get advplsPath)
    if [ -z "$advpls" ] || [ ! -f "$advpls" ]; then
        echo "ERRO: advpls nao encontrado. Execute tds-discover.sh --refresh" >&2
        return 1
    fi

    # Get includes (first entry)
    local includes
    includes=$(tds_get globalIncludes | tr ';' '\n' | head -1)

    # Run pre-compilation (syntax check only, no server)
    local output
    output=$("$advpls" appre "$file_path" -I "$includes" 2>&1)
    local exit_code=$?

    if [ $exit_code -ne 0 ] || echo "$output" | grep -qi "ERR\|error\|no valid content"; then
        echo "ERRO DE SINTAXE em $(basename "$file_path"):"
        echo "$output" | grep -i "err\|error\|warning\|no valid" | head -10
        return 1
    fi

    # Success — no output needed
    return 0
}

# --- Main ---
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    if [ -z "$1" ]; then
        echo "Uso: tds-validate.sh <arquivo.tlpp|arquivo.prw>"
        exit 1
    fi
    validate_syntax "$1"
fi
