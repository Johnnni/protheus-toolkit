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

servers_path = sys.argv[1]
advpls_path = sys.argv[2]
cache_file = sys.argv[3]

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
    name_upper = name.upper()
    is_dev = any(k in name_upper for k in ['DEV', 'TESTE', 'HOMOLOG'])
    is_prod = any(k in name_upper for k in ['PROD', 'PRO '])

    existing = projects.get(folder_name)
    if existing:
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

os.makedirs(os.path.dirname(cache_file), exist_ok=True)
with open(cache_file, 'w') as f:
    json.dump(cache, f, indent=2)

print(f'Cache gerado: {len(projects)} projetos mapeados', file=sys.stderr)
" "$SERVERS_JSON" "$advpls_path" "$CACHE_FILE" 2>&1

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
import json, sys
d = json.load(open(sys.argv[1]))
proj = d.get('projects', {}).get(sys.argv[2].upper(), {})
val = proj.get(sys.argv[3], '')
if isinstance(val, list):
    print(';'.join(str(v) for v in val))
else:
    print(val)
" "$CACHE_FILE" "$project" "$field"
    else
        python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
val = d.get(sys.argv[2], '')
if isinstance(val, list):
    print(';'.join(str(v) for v in val))
else:
    print(val)
" "$CACHE_FILE" "$key"
    fi
}

# --- Detect project from current path ---
detect_project() {
    local dir="$1"
    [ -z "$dir" ] && dir="$(pwd)"
    dir=$(echo "$dir" | sed 's|\\|/|g')

    # Ensure cache
    if ! cache_is_valid; then
        build_cache >/dev/null 2>&1 || return 1
    fi

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

# --- List all mapped projects ---
list_projects() {
    if ! cache_is_valid; then
        build_cache >/dev/null 2>&1 || return 1
    fi

    python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
for k, v in sorted(d.get('projects', {}).items()):
    print(f'{k:20s} -> {v[\"name\"]:30s} ({v[\"environment\"]})')
" "$CACHE_FILE"
}

# --- Main: if called directly ---
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
        --list|-l)
            list_projects
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
