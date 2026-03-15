# TDS-CLI Integration — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate TDS-LS CLI (`advpls`) into the `protheus-toolkit` plugin to auto-validate syntax after edits, compile sources, and generate patches — all from Claude Code conversations.

**Architecture:** Shell scripts that auto-discover `advpls.exe` and read `~/.totvsls/servers.json`, map project folders to servers via `patchGenerateDir`, cache the config in `~/.claude/tds-cache.json`, and store credentials encrypted with Windows DPAPI. Three entry points: PostToolUse hook (auto-validate), `/compile` command, `/patch` command.

**Tech Stack:** Bash scripts, PowerShell (DPAPI only), `advpls` CLI (modes: `appre` for validation, `cli` for compile/patch), JSON parsing with `jq` or `python -c`.

---

## File Structure

```
plugins/protheus-toolkit/
├── scripts/                        # NEW directory
│   ├── tds-discover.sh             # Auto-discovery + cache management
│   ├── tds-credentials.sh          # DPAPI encrypt/decrypt helpers
│   ├── tds-validate.sh             # advpls appre wrapper
│   ├── tds-compile.sh              # advpls cli authenticate+compile
│   └── tds-patch.sh                # advpls cli authenticate+patchGen+rename
├── commands/
│   ├── compile.md                  # NEW — /compile slash command
│   └── patch.md                    # NEW — /patch slash command
├── hooks/
│   ├── check-ascii.sh              # EXISTS — no changes
│   ├── session-start.md            # EXISTS — no changes
│   └── post-edit-validate.sh       # NEW — PostToolUse hook for syntax validation
└── plugin.json                     # MODIFY — add new commands, hook, scripts
```

**Key design decisions:**
- `tds-discover.sh` is the foundation — all other scripts source it for paths/config
- Cache lives at `~/.claude/tds-cache.json` — auto-regenerates if `servers.json` or VS Code extensions change
- Credentials at `~/.claude/tds-credentials.enc` — one encrypted blob per serverId
- Temp `.ini` files generated in system temp dir, deleted after use
- Patch files renamed to `{name}_{YYYYMMDD}_{HHMMSS}.ptm` after generation

---

## Chunk 1: Foundation (discovery + credentials)

### Task 1: Create `tds-discover.sh` — auto-discovery and cache

**Files:**
- Create: `plugins/protheus-toolkit/scripts/tds-discover.sh`

This script finds `advpls.exe`, parses `servers.json`, builds the project→server mapping from `patchGenerateDir`, and caches everything in `~/.claude/tds-cache.json`.

- [ ] **Step 1: Create the script**

```bash
#!/bin/bash
# tds-discover.sh — Auto-discovery of TDS-LS environment
# Sources: advpls binary, servers.json, project-server mapping
# Cache: ~/.claude/tds-cache.json (auto-regenerates on change)

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_FILE="$HOME/.claude/tds-cache.json"
SERVERS_JSON="$HOME/.totvsls/servers.json"

# --- Find advpls binary ---
find_advpls() {
    # Check cache first
    if [ -f "$CACHE_FILE" ]; then
        local cached
        cached=$(python3 -c "import json; d=json.load(open('$CACHE_FILE')); print(d.get('advplsPath',''))" 2>/dev/null)
        if [ -n "$cached" ] && [ -f "$cached" ]; then
            echo "$cached"
            return 0
        fi
    fi

    # Search in VS Code extensions
    local found
    found=$(find "$HOME/.vscode/extensions" -path "*/totvs.tds-vscode-*/node_modules/@totvs/tds-ls/bin/windows/advpls.exe" 2>/dev/null | sort -rV | head -1)
    if [ -z "$found" ]; then
        # Try VS Code Insiders
        found=$(find "$HOME/.vscode-insiders/extensions" -path "*/totvs.tds-vscode-*/node_modules/@totvs/tds-ls/bin/windows/advpls.exe" 2>/dev/null | sort -rV | head -1)
    fi
    if [ -z "$found" ]; then
        # Try global npm
        found=$(find "$(npm root -g 2>/dev/null)" -path "*/@totvs/tds-ls/bin/windows/advpls.exe" 2>/dev/null | head -1)
    fi

    echo "$found"
}

# --- Check if cache is stale ---
cache_is_valid() {
    [ -f "$CACHE_FILE" ] || return 1
    [ -f "$SERVERS_JSON" ] || return 1

    local cache_ts servers_ts
    cache_ts=$(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null)
    servers_ts=$(stat -c %Y "$SERVERS_JSON" 2>/dev/null || stat -f %m "$SERVERS_JSON" 2>/dev/null)

    # Cache is stale if servers.json is newer
    [ "$cache_ts" -gt "$servers_ts" ] 2>/dev/null
}

# --- Build cache from servers.json ---
build_cache() {
    local advpls_path
    advpls_path=$(find_advpls)

    if [ -z "$advpls_path" ]; then
        echo "ERRO: advpls.exe nao encontrado. Instale a extensao TDS-VSCode ou npm install -g @totvs/tds-ls" >&2
        return 1
    fi

    if [ ! -f "$SERVERS_JSON" ]; then
        echo "ERRO: servers.json nao encontrado em $SERVERS_JSON" >&2
        return 1
    fi

    # Parse servers.json and build project mapping
    python3 -c "
import json, os, sys
from datetime import datetime

servers_path = '$SERVERS_JSON'
advpls_path = '$advpls_path'

with open(servers_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

includes = data.get('includes', [])
configs = data.get('configurations', [])

projects = {}
for srv in configs:
    patch_dir = srv.get('patchGenerateDir', '')
    if not patch_dir:
        continue
    # Normalize path
    patch_dir = patch_dir.replace('\\\\', '/').rstrip('/')
    folder_name = os.path.basename(patch_dir).upper()

    # Prefer DEV servers (skip PROD/HOMOLOG unless only option)
    name = srv.get('name', '')
    is_dev = any(k in name.upper() for k in ['DEV', 'TESTE', 'HOMOLOG'])
    is_prod = any(k in name.upper() for k in ['PROD', 'PRO '])

    existing = projects.get(folder_name)
    if existing:
        # Keep DEV over PROD
        existing_is_dev = existing.get('_is_dev', False)
        if existing_is_dev and not is_dev:
            continue
        if is_prod and not is_dev:
            continue

    projects[folder_name] = {
        'serverId': srv['id'],
        'name': name,
        'address': srv.get('address', ''),
        'port': srv.get('port', 0),
        'secure': 1 if srv.get('secure') else 0,
        'build': srv.get('buildVersion', ''),
        'environment': srv.get('environment', ''),
        'username': srv.get('username', ''),
        'includes': srv.get('includes', includes),
        'patchDir': patch_dir,
        '_is_dev': is_dev
    }

# Remove internal flags
for p in projects.values():
    p.pop('_is_dev', None)

cache = {
    'generated': datetime.now().isoformat(),
    'advplsPath': advpls_path.replace('\\\\', '/'),
    'serversJsonPath': servers_path.replace('\\\\', '/'),
    'globalIncludes': [i.replace('\\\\', '/') for i in includes],
    'projects': projects
}

os.makedirs(os.path.dirname('$CACHE_FILE'), exist_ok=True)
with open('$CACHE_FILE', 'w') as f:
    json.dump(cache, f, indent=2)

print(f'Cache gerado: {len(projects)} projetos mapeados', file=sys.stderr)
" 2>&1

    return $?
}

# --- Get value from cache ---
# Usage: tds_get advplsPath
#        tds_get project CBM address
tds_get() {
    # Ensure cache exists and is valid
    if ! cache_is_valid; then
        build_cache >/dev/null 2>&1 || return 1
    fi

    local key="$1"
    shift

    if [ "$key" = "project" ]; then
        local project="$1"
        local field="$2"
        python3 -c "
import json
d = json.load(open('$CACHE_FILE'))
proj = d.get('projects', {}).get('${project}'.upper(), {})
print(proj.get('$field', ''))
"
    else
        python3 -c "
import json
d = json.load(open('$CACHE_FILE'))
val = d.get('$key', '')
if isinstance(val, list):
    print(';'.join(str(v) for v in val))
else:
    print(val)
"
    fi
}

# --- Detect project from current path ---
detect_project() {
    local dir="$1"
    [ -z "$dir" ] && dir="$(pwd)"
    dir=$(echo "$dir" | sed 's|\\|/|g')

    # Walk up until we find a matching project folder
    while [ "$dir" != "/" ] && [ -n "$dir" ]; do
        local folder
        folder=$(basename "$dir" | tr '[:lower:]' '[:upper:]')

        # Check if this folder is a mapped project
        local server_name
        server_name=$(tds_get project "$folder" name 2>/dev/null)
        if [ -n "$server_name" ]; then
            echo "$folder"
            return 0
        fi
        dir=$(dirname "$dir")
    done

    return 1
}

# --- Main: if called directly, rebuild cache ---
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    case "${1:-}" in
        --refresh|-r)
            rm -f "$CACHE_FILE"
            build_cache
            ;;
        --show|-s)
            if ! cache_is_valid; then
                build_cache >/dev/null 2>&1
            fi
            cat "$CACHE_FILE"
            ;;
        --detect|-d)
            detect_project "${2:-$(pwd)}"
            ;;
        *)
            if ! cache_is_valid; then
                build_cache
            else
                echo "Cache valido: $CACHE_FILE"
            fi
            ;;
    esac
fi
```

- [ ] **Step 2: Make executable and test**

Run: `chmod +x plugins/protheus-toolkit/scripts/tds-discover.sh && bash plugins/protheus-toolkit/scripts/tds-discover.sh --refresh`
Expected: `Cache gerado: X projetos mapeados`

- [ ] **Step 3: Test project detection**

Run: `bash plugins/protheus-toolkit/scripts/tds-discover.sh --detect C:/PROJETOS/ASCENSUS`
Expected: `ASCENSUS`

- [ ] **Step 4: Test cache read**

Run: `source plugins/protheus-toolkit/scripts/tds-discover.sh && tds_get project ASCENSUS name`
Expected: Server name for ASCENSUS

- [ ] **Step 5: Commit**

```bash
git add plugins/protheus-toolkit/scripts/tds-discover.sh
git commit -m "feat(tds-cli): add auto-discovery script with cache"
```

---

### Task 2: Create `tds-credentials.sh` — DPAPI credential management

**Files:**
- Create: `plugins/protheus-toolkit/scripts/tds-credentials.sh`

Encrypts/decrypts server passwords using Windows DPAPI. Stores encrypted blobs in `~/.claude/tds-credentials.enc` as JSON `{serverId: encryptedBase64}`.

- [ ] **Step 1: Create the script**

```bash
#!/bin/bash
# tds-credentials.sh — DPAPI credential management for TDS servers
# Stores: ~/.claude/tds-credentials.enc (JSON: {serverId: encryptedBase64})

CRED_FILE="$HOME/.claude/tds-credentials.enc"

# --- Encrypt a password with DPAPI ---
dpapi_encrypt() {
    local plaintext="$1"
    powershell -Command "
        Add-Type -AssemblyName System.Security
        \$bytes = [System.Text.Encoding]::UTF8.GetBytes('$plaintext')
        \$encrypted = [System.Security.Cryptography.ProtectedData]::Protect(\$bytes, \$null, 'CurrentUser')
        [Convert]::ToBase64String(\$encrypted)
    " 2>/dev/null
}

# --- Decrypt a password with DPAPI ---
dpapi_decrypt() {
    local encrypted_b64="$1"
    powershell -Command "
        Add-Type -AssemblyName System.Security
        \$bytes = [Convert]::FromBase64String('$encrypted_b64')
        \$decrypted = [System.Security.Cryptography.ProtectedData]::Unprotect(\$bytes, \$null, 'CurrentUser')
        [System.Text.Encoding]::UTF8.GetString(\$decrypted)
    " 2>/dev/null
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
    echo "$creds" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d['$server_id'] = '$encrypted'
print(json.dumps(d, indent=2))
" > "$CRED_FILE"

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
import json
d = json.load(open('$CRED_FILE'))
print(d.get('$server_id', ''))
" 2>/dev/null)

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
d = json.load(open('$CRED_FILE'))
sys.exit(0 if '$server_id' in d else 1)
" 2>/dev/null
}

# --- Remove credentials for a server ---
cred_remove() {
    local server_id="$1"
    [ -f "$CRED_FILE" ] || return 0

    python3 -c "
import json
d = json.load(open('$CRED_FILE'))
d.pop('$server_id', None)
with open('$CRED_FILE', 'w') as f:
    json.dump(d, f, indent=2)
" 2>/dev/null

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
```

- [ ] **Step 2: Make executable and test encrypt/decrypt round-trip**

Run: `chmod +x plugins/protheus-toolkit/scripts/tds-credentials.sh && bash plugins/protheus-toolkit/scripts/tds-credentials.sh save test_server "minhasenha123" && bash plugins/protheus-toolkit/scripts/tds-credentials.sh get test_server`
Expected: `minhasenha123`

- [ ] **Step 3: Test exists check**

Run: `bash plugins/protheus-toolkit/scripts/tds-credentials.sh exists test_server`
Expected: `sim`

- [ ] **Step 4: Cleanup test data and commit**

```bash
bash plugins/protheus-toolkit/scripts/tds-credentials.sh remove test_server
git add plugins/protheus-toolkit/scripts/tds-credentials.sh
git commit -m "feat(tds-cli): add DPAPI credential management"
```

---

## Chunk 2: Validation hook (offline, auto)

### Task 3: Create `tds-validate.sh` — syntax validation wrapper

**Files:**
- Create: `plugins/protheus-toolkit/scripts/tds-validate.sh`

Wraps `advpls appre` for syntax-only validation without AppServer.

- [ ] **Step 1: Create the script**

```bash
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

    # Get includes
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
```

- [ ] **Step 2: Test with valid file**

Run: `chmod +x plugins/protheus-toolkit/scripts/tds-validate.sh && bash plugins/protheus-toolkit/scripts/tds-validate.sh C:/TOTVS/poc_test.tlpp; echo "EXIT=$?"`
Expected: `EXIT=0` (no output = success)

- [ ] **Step 3: Test with invalid file**

Run: `bash plugins/protheus-toolkit/scripts/tds-validate.sh C:/TOTVS/poc_erro.tlpp; echo "EXIT=$?"`
Expected: Error message + `EXIT=1`

- [ ] **Step 4: Commit**

```bash
git add plugins/protheus-toolkit/scripts/tds-validate.sh
git commit -m "feat(tds-cli): add syntax validation wrapper (advpls appre)"
```

---

### Task 4: Create `post-edit-validate.sh` — PostToolUse hook

**Files:**
- Create: `plugins/protheus-toolkit/hooks/post-edit-validate.sh`
- Modify: `plugins/protheus-toolkit/plugin.json` — add hook

- [ ] **Step 1: Create the hook script**

```bash
#!/bin/bash
# Hook: post-edit-validate
# Event: PostToolUse (Write, Edit)
# Validates ADVPL/TLPP syntax after every file edit using advpls appre

# Read tool result from stdin
INPUT=$(cat)

# Extract file path
FILE_PATH=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"([^"]+)"' | head -1 | sed 's/.*"file_path"\s*:\s*"//;s/"$//')

# Only validate Protheus source files
if [[ ! "$FILE_PATH" =~ \.(prw|tlpp|prx|prg)$ ]]; then
    exit 0
fi

# Run syntax validation
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)"
if [ -f "$SCRIPT_DIR/tds-validate.sh" ]; then
    "$SCRIPT_DIR/tds-validate.sh" "$FILE_PATH"
fi
```

- [ ] **Step 2: Make executable**

Run: `chmod +x plugins/protheus-toolkit/hooks/post-edit-validate.sh`

- [ ] **Step 3: Add hook to plugin.json**

Add `"hooks/post-edit-validate.sh"` to the hooks array in `plugin.json`.

Current hooks array:
```json
"hooks": [
    "hooks/check-ascii.sh",
    "hooks/session-start.md"
]
```

New hooks array:
```json
"hooks": [
    "hooks/check-ascii.sh",
    "hooks/post-edit-validate.sh",
    "hooks/session-start.md"
]
```

- [ ] **Step 4: Commit**

```bash
git add plugins/protheus-toolkit/hooks/post-edit-validate.sh plugins/protheus-toolkit/plugin.json
git commit -m "feat(tds-cli): add PostToolUse hook for auto syntax validation"
```

---

## Chunk 3: Compile command

### Task 5: Create `tds-compile.sh` — compilation wrapper

**Files:**
- Create: `plugins/protheus-toolkit/scripts/tds-compile.sh`

Generates a temp `.ini`, authenticates, compiles, and cleans up.

- [ ] **Step 1: Create the script**

```bash
#!/bin/bash
# tds-compile.sh — Compile source files via advpls cli
# Usage: tds-compile.sh <project> <file1[,file2,...]> [--recompile]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tds-discover.sh"
source "$SCRIPT_DIR/tds-credentials.sh"

compile() {
    local project="$1"
    local files="$2"
    local recompile="${3:-T}"

    # Resolve server config from cache
    local server_id address port secure build environment username includes
    server_id=$(tds_get project "$project" serverId)
    if [ -z "$server_id" ]; then
        echo "ERRO: Projeto '$project' nao mapeado. Servidores disponiveis:" >&2
        python3 -c "
import json
d = json.load(open('$CACHE_FILE'))
for k, v in d.get('projects', {}).items():
    print(f'  {k} -> {v[\"name\"]}')
" >&2
        return 1
    fi

    address=$(tds_get project "$project" address)
    port=$(tds_get project "$project" port)
    secure=$(tds_get project "$project" secure)
    build=$(tds_get project "$project" build)
    environment=$(tds_get project "$project" environment)
    username=$(tds_get project "$project" username)
    includes=$(tds_get project "$project" includes | python3 -c "import sys; print(sys.stdin.read().strip().replace(\"'\",\"\").strip(\"[]\"))")

    # Get password (from DPAPI store)
    local password
    if ! cred_exists "$server_id"; then
        echo "ERRO: Credenciais nao encontradas para servidor '$server_id'." >&2
        echo "Use: tds-credentials.sh save $server_id <senha>" >&2
        return 1
    fi
    password=$(cred_get "$server_id")

    if [ -z "$password" ]; then
        echo "ERRO: Falha ao descriptografar senha do servidor." >&2
        return 1
    fi

    # Get advpls path
    local advpls
    advpls=$(tds_get advplsPath)

    # Generate temp .ini
    local ini_file
    ini_file=$(mktemp /tmp/tds-compile-XXXXXX.ini)

    local server_name
    server_name=$(tds_get project "$project" name)

    cat > "$ini_file" <<EOF
; Auto-generated by tds-compile.sh for project $project
; Server: $server_name ($address:$port)
showConsoleOutput=true

[auth]
action=authentication
server=$address
port=$port
secure=$secure
build=$build
environment=$environment
user=$username
psw=$password

[compile]
action=compile
program=$files
recompile=$recompile
includes=$includes
EOF

    echo "[TDS-CLI] Compilando em $server_name ($environment)..."
    echo "[TDS-CLI] Arquivos: $files"

    # Execute
    local output
    output=$("$advpls" cli "$ini_file" 2>&1)
    local exit_code=$?

    # Cleanup temp file (contains password)
    rm -f "$ini_file"

    echo "$output"

    # Check result
    if echo "$output" | grep -q "All files compiled successfully"; then
        echo "[TDS-CLI] Compilacao concluida com sucesso!"
        return 0
    elif echo "$output" | grep -q "compiled successfully"; then
        echo "[TDS-CLI] Compilacao concluida com sucesso!"
        return 0
    else
        echo "[TDS-CLI] ERRO na compilacao." >&2
        return 1
    fi
}

# --- Main ---
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Uso: tds-compile.sh <PROJETO> <arquivo1[,arquivo2]> [T|F]"
        exit 1
    fi
    compile "$1" "$2" "${3:-T}"
fi
```

- [ ] **Step 2: Make executable and test with local server**

Run: `chmod +x plugins/protheus-toolkit/scripts/tds-compile.sh`

Test requires: local AppServer running + credentials saved:
```bash
bash plugins/protheus-toolkit/scripts/tds-credentials.sh save o593176oktamdukmno14luuw6d5bks "123"
```

Note: For local server, add LOCAL2410 to cache manually or ensure `patchGenerateDir` maps it.

- [ ] **Step 3: Commit**

```bash
git add plugins/protheus-toolkit/scripts/tds-compile.sh
git commit -m "feat(tds-cli): add compile wrapper script"
```

---

### Task 6: Create `/compile` command

**Files:**
- Create: `plugins/protheus-toolkit/commands/compile.md`
- Modify: `plugins/protheus-toolkit/plugin.json` — add command

- [ ] **Step 1: Create the command**

```markdown
---
name: compile
description: Compila fontes ADVPL/TLPP no servidor Protheus do projeto atual via TDS-CLI
arguments:
  - name: files
    description: Arquivos para compilar (opcional - usa o arquivo atual se omitido)
    required: false
---

Compile os fontes solicitados no servidor Protheus associado ao projeto atual.

## Instrucoes

1. **Detectar projeto**: Identifique o projeto atual pelo diretorio de trabalho usando o mapeamento em `~/.claude/tds-cache.json`. Se o cache nao existir, execute `${CLAUDE_PLUGIN_ROOT}/scripts/tds-discover.sh --refresh`.

2. **Identificar arquivos**:
   - Se `$ARGUMENTS` especifica arquivos, use-os
   - Se nao, use o(s) arquivo(s) .tlpp/.prw que foram editados na conversa atual
   - Converta caminhos relativos para absolutos

3. **Verificar credenciais**: Execute `${CLAUDE_PLUGIN_ROOT}/scripts/tds-credentials.sh exists <serverId>`. Se nao existir, pergunte a senha ao usuario com AskUserQuestion e salve com `tds-credentials.sh save <serverId> <senha>`.

4. **Compilar**: Execute:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-compile.sh <PROJETO> <arquivos> T
   ```

5. **Reportar resultado**: Mostre se compilou com sucesso ou os erros encontrados.

## Exemplo de uso
- `/compile` — compila os arquivos editados na conversa
- `/compile C:/PROJETOS/ASCENSUS/fontes/XPTO.tlpp` — compila arquivo especifico
- `/compile XPTO.tlpp,XPTO2.prw` — compila multiplos arquivos
```

- [ ] **Step 2: Add to plugin.json commands array**

Add `"commands/compile.md"` to the commands array.

- [ ] **Step 3: Commit**

```bash
git add plugins/protheus-toolkit/commands/compile.md plugins/protheus-toolkit/plugin.json
git commit -m "feat(tds-cli): add /compile slash command"
```

---

## Chunk 4: Patch command

### Task 7: Create `tds-patch.sh` — patch generation wrapper

**Files:**
- Create: `plugins/protheus-toolkit/scripts/tds-patch.sh`

Generates patch via `advpls cli`, then renames with `_YYYYMMDD_HHMMSS` suffix.

- [ ] **Step 1: Create the script**

```bash
#!/bin/bash
# tds-patch.sh — Generate patch via advpls cli
# Usage: tds-patch.sh <project> <resources> <patchName> [PTM|UPD|PAK]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tds-discover.sh"
source "$SCRIPT_DIR/tds-credentials.sh"

generate_patch() {
    local project="$1"
    local resources="$2"
    local patch_name="$3"
    local patch_type="${4:-PTM}"

    # Resolve server config
    local server_id address port secure build environment username
    server_id=$(tds_get project "$project" serverId)
    if [ -z "$server_id" ]; then
        echo "ERRO: Projeto '$project' nao mapeado." >&2
        return 1
    fi

    address=$(tds_get project "$project" address)
    port=$(tds_get project "$project" port)
    secure=$(tds_get project "$project" secure)
    build=$(tds_get project "$project" build)
    environment=$(tds_get project "$project" environment)
    username=$(tds_get project "$project" username)

    # Get password
    if ! cred_exists "$server_id"; then
        echo "ERRO: Credenciais nao encontradas para servidor '$server_id'." >&2
        return 1
    fi
    local password
    password=$(cred_get "$server_id")

    # Patch output directory
    local patch_dir
    patch_dir=$(tds_get project "$project" patchDir)
    [ -z "$patch_dir" ] && patch_dir="/tmp"
    mkdir -p "$patch_dir"

    # Get advpls
    local advpls
    advpls=$(tds_get advplsPath)

    # Generate temp .ini
    local ini_file
    ini_file=$(mktemp /tmp/tds-patch-XXXXXX.ini)

    local server_name
    server_name=$(tds_get project "$project" name)

    cat > "$ini_file" <<EOF
; Auto-generated by tds-patch.sh for project $project
showConsoleOutput=true

[auth]
action=authentication
server=$address
port=$port
secure=$secure
build=$build
environment=$environment
user=$username
psw=$password

[patchGen]
action=patchGen
fileResource=$resources
patchType=$patch_type
saveLocal=$patch_dir/
patchName=$patch_name
EOF

    echo "[TDS-CLI] Gerando patch em $server_name ($environment)..."
    echo "[TDS-CLI] Recursos: $resources"
    echo "[TDS-CLI] Destino: $patch_dir/"

    # Execute
    local output
    output=$("$advpls" cli "$ini_file" 2>&1)
    local exit_code=$?

    # Cleanup temp .ini
    rm -f "$ini_file"

    echo "$output"

    # Check result and rename with timestamp
    if echo "$output" | grep -q "Patch generated successfully"; then
        # Find the generated patch file
        local generated_file
        generated_file=$(echo "$output" | grep -oP 'Patch \K[^ ]+\.ptm' | head -1)

        if [ -n "$generated_file" ] && [ -f "$patch_dir/$generated_file" ]; then
            # Rename with timestamp suffix
            local timestamp
            timestamp=$(date +%Y%m%d_%H%M%S)
            local ext="${generated_file##*.}"
            local new_name="${patch_name}_${timestamp}.${ext}"
            mv "$patch_dir/$generated_file" "$patch_dir/$new_name"
            echo "[TDS-CLI] Patch gerado: $patch_dir/$new_name"
        else
            # Try to find most recent file in patch_dir
            local newest
            newest=$(ls -t "$patch_dir"/*.ptm "$patch_dir"/*.upd "$patch_dir"/*.pak 2>/dev/null | head -1)
            if [ -n "$newest" ]; then
                local timestamp
                timestamp=$(date +%Y%m%d_%H%M%S)
                local base ext
                base=$(basename "$newest")
                ext="${base##*.}"
                local new_name="${patch_name}_${timestamp}.${ext}"
                mv "$newest" "$patch_dir/$new_name"
                echo "[TDS-CLI] Patch gerado: $patch_dir/$new_name"
            fi
        fi
        return 0
    else
        echo "[TDS-CLI] ERRO na geracao do patch." >&2
        return 1
    fi
}

# --- Main ---
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
        echo "Uso: tds-patch.sh <PROJETO> <recurso1,recurso2> <nomePatch> [PTM|UPD|PAK]"
        exit 1
    fi
    generate_patch "$1" "$2" "$3" "${4:-PTM}"
fi
```

- [ ] **Step 2: Make executable and commit**

```bash
chmod +x plugins/protheus-toolkit/scripts/tds-patch.sh
git add plugins/protheus-toolkit/scripts/tds-patch.sh
git commit -m "feat(tds-cli): add patch generation wrapper with timestamp rename"
```

---

### Task 8: Create `/patch` command

**Files:**
- Create: `plugins/protheus-toolkit/commands/patch.md`
- Modify: `plugins/protheus-toolkit/plugin.json` — add command

- [ ] **Step 1: Create the command**

```markdown
---
name: patch
description: Gera patch PTM/UPD/PAK dos fontes compilados no servidor Protheus do projeto atual
arguments:
  - name: args
    description: Nome do patch e/ou arquivos (opcional)
    required: false
---

Gere um patch dos fontes no servidor Protheus do projeto atual.

## Instrucoes

1. **Detectar projeto**: Identifique o projeto atual pelo diretorio de trabalho usando `~/.claude/tds-cache.json`.

2. **Identificar recursos**:
   - Se `$ARGUMENTS` especifica nomes de fontes, use-os (ex: `XPTO.tlpp,XPTO2.prw`)
   - Se nao, identifique os arquivos .tlpp/.prw editados/compilados na conversa atual
   - Os nomes devem incluir a extensao (ex: `meu_fonte.tlpp`)

3. **Nome do patch**:
   - Se `$ARGUMENTS` inclui um nome, use-o
   - Caso contrario, sugira um nome baseado no contexto (nome da rotina principal, ticket, etc.)
   - Pergunte ao usuario: "Sugiro o nome `<sugestao>`. Quer usar esse ou prefere outro?"
   - O sufixo `_AAAAMMDD_HHMMSS` sera adicionado automaticamente

4. **Verificar credenciais**: Mesmo fluxo do `/compile`.

5. **Gerar patch**: Execute:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-patch.sh <PROJETO> <recursos> <nomePatch> PTM
   ```

6. **Reportar**: Mostre o caminho completo do patch gerado.

## Exemplo de uso
- `/patch` — gera patch dos fontes da conversa, sugere nome
- `/patch XPTO.tlpp MeuPatch` — gera patch com nome especifico
- `/patch XPTO.tlpp,XPTO2.prw CorrecaoNF` — multiplos fontes
```

- [ ] **Step 2: Add to plugin.json commands array**

Add `"commands/patch.md"` to the commands array.

- [ ] **Step 3: Commit**

```bash
git add plugins/protheus-toolkit/commands/patch.md plugins/protheus-toolkit/plugin.json
git commit -m "feat(tds-cli): add /patch slash command"
```

---

## Chunk 5: Final integration

### Task 9: Update `plugin.json` with all new components

**Files:**
- Modify: `plugins/protheus-toolkit/plugin.json`

- [ ] **Step 1: Final plugin.json**

The complete updated commands and hooks arrays:

```json
{
  "commands": [
    "commands/protheus.md",
    "commands/diagnose.md",
    "commands/debug.md",
    "commands/generate.md",
    "commands/migrate.md",
    "commands/review.md",
    "commands/test.md",
    "commands/docs.md",
    "commands/process.md",
    "commands/compile.md",
    "commands/patch.md"
  ],
  "hooks": [
    "hooks/check-ascii.sh",
    "hooks/post-edit-validate.sh",
    "hooks/session-start.md"
  ]
}
```

- [ ] **Step 2: Commit final plugin.json**

```bash
git add plugins/protheus-toolkit/plugin.json
git commit -m "feat(tds-cli): register compile/patch commands and validate hook in plugin.json"
```

---

### Task 10: End-to-end test with local server

- [ ] **Step 1: Refresh cache**

Run: `bash plugins/protheus-toolkit/scripts/tds-discover.sh --refresh`

- [ ] **Step 2: Save credentials for local server**

Run: `bash plugins/protheus-toolkit/scripts/tds-credentials.sh save <local_server_id> "123"`

- [ ] **Step 3: Test validate hook**

Create/edit a `.tlpp` file and verify the hook runs `advpls appre`.

- [ ] **Step 4: Test /compile**

Run `/compile` on a test file against local server.

- [ ] **Step 5: Test /patch**

Run `/patch` on compiled file, verify:
- Patch generated
- Renamed with `_YYYYMMDD_HHMMSS` suffix
- Saved in correct `patchGenerateDir`

- [ ] **Step 6: Final commit**

```bash
git commit -m "test(tds-cli): end-to-end validation complete"
```
