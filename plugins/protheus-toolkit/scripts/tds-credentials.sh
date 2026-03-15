#!/bin/bash
# tds-credentials.sh — DPAPI credential management for TDS servers
# Stores: ~/.claude/tds-credentials.enc (JSON: {serverId: encryptedBase64})

CRED_FILE="$HOME/.claude/tds-credentials.enc"

# --- Encrypt a password with DPAPI ---
dpapi_encrypt() {
    local plaintext="$1"
    powershell -Command 'Add-Type -AssemblyName System.Security; $bytes = [System.Text.Encoding]::UTF8.GetBytes("'"$plaintext"'"); $encrypted = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, "CurrentUser"); [Convert]::ToBase64String($encrypted)' 2>/dev/null
}

# --- Decrypt a password with DPAPI ---
dpapi_decrypt() {
    local encrypted_b64="$1"
    powershell -Command 'Add-Type -AssemblyName System.Security; $bytes = [Convert]::FromBase64String("'"$encrypted_b64"'"); $decrypted = [System.Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, "CurrentUser"); [System.Text.Encoding]::UTF8.GetString($decrypted)' 2>/dev/null
}

# --- Save encrypted password for a server ---
cred_save() {
    local server_id="$1"
    local password="$2"

    local encrypted
    encrypted=$(dpapi_encrypt "$password")
    if [ -z "$encrypted" ]; then
        echo "ERRO: Falha ao criptografar senha" >&2
        return 1
    fi

    # Read existing or create new
    local creds="{}"
    if [ -f "$CRED_FILE" ]; then
        creds=$(cat "$CRED_FILE")
    fi

    # Update entry
    python3 -c "
import json, sys, os
creds = json.loads(sys.argv[1])
creds[sys.argv[2]] = sys.argv[3]
os.makedirs(os.path.dirname(sys.argv[4]), exist_ok=True)
with open(sys.argv[4], 'w') as f:
    json.dump(creds, f, indent=2)
" "$creds" "$server_id" "$encrypted" "$CRED_FILE"

    echo "Credencial salva para servidor $server_id"
}

# --- Get decrypted password for a server ---
cred_get() {
    local server_id="$1"

    if [ ! -f "$CRED_FILE" ]; then
        return 1
    fi

    local encrypted
    encrypted=$(python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
print(d.get(sys.argv[2], ''))
" "$CRED_FILE" "$server_id" 2>/dev/null)

    if [ -z "$encrypted" ]; then
        return 1
    fi

    dpapi_decrypt "$encrypted"
}

# --- Check if credentials exist for a server ---
cred_exists() {
    local server_id="$1"
    [ -f "$CRED_FILE" ] || return 1

    python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if sys.argv[2] in d else 1)
" "$CRED_FILE" "$server_id" 2>/dev/null
}

# --- Remove credentials for a server ---
cred_remove() {
    local server_id="$1"
    [ -f "$CRED_FILE" ] || return 0

    python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
d.pop(sys.argv[2], None)
with open(sys.argv[1], 'w') as f:
    json.dump(d, f, indent=2)
" "$CRED_FILE" "$server_id" 2>/dev/null

    echo "Credencial removida para servidor $server_id"
}

# --- Main: CLI interface ---
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    case "${1:-}" in
        save)
            cred_save "$2" "$3"
            ;;
        get)
            cred_get "$2"
            ;;
        exists)
            cred_exists "$2" && echo "sim" || echo "nao"
            ;;
        remove)
            cred_remove "$2"
            ;;
        *)
            echo "Uso: tds-credentials.sh {save|get|exists|remove} <serverId> [password]"
            ;;
    esac
fi
