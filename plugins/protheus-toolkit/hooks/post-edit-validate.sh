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
