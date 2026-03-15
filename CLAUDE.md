# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin ecosystem for TOTVS Protheus ADVPL/TLPP development. Two integrated plugins:

- **claude-tdn** (`plugins/claude-tdn/`) - MCP server (Python/FastMCP) exposing `tdn_search` and `tdn_fetch` tools for TDN documentation
- **protheus-toolkit** (`plugins/protheus-toolkit/`) - 15 skills, 7 agents, 11 commands, 3 hooks for ADVPL/TLPP development

## Architecture

```
plugins/
├── claude-tdn/           # Python MCP server for TDN docs
│   ├── server/           # tdn_server.py (FastMCP), tests
│   ├── scripts/          # setup.sh, run-server.sh
│   └── skills/           # tdn-docs skill
└── protheus-toolkit/     # Main plugin (v2.1.0)
    ├── skills/           # Domain knowledge (templates, patterns, references)
    ├── agents/           # Context-aware personas (code-gen, review, debug, migrate, test, docs, process)
    ├── commands/         # Slash commands (entry points routing to agents/skills)
    ├── hooks/            # Automation (ASCII check, post-edit validation, session start detection)
    └── scripts/          # TDS-CLI integration (discover, compile, patch, credentials via DPAPI)
```

**Component responsibilities:**
- **Skills** = knowledge (patterns, templates, examples, anti-patterns)
- **Agents** = logic (workflow orchestration, 13-point validation checklist)
- **Commands** = UI (slash command entry points)
- **Hooks** = automation (validation on edit, project type detection on session start)

## Testing

### claude-tdn MCP server
```bash
cd plugins/claude-tdn/server
# Unit tests only
python -m pytest test_unit.py -v
# Integration tests (requires internet)
python -m pytest test_integration.py -v -m integration
# All tests
python -m pytest -v
```

Markers defined in `pytest.ini`: `integration` for tests requiring live HTTP calls.

## Key Development Patterns

- Plugin manifests are `plugin.json` at each plugin root
- Skills follow the pattern: `skills/<name>/SKILL.md` with optional `references/` subdirectory
- Agents, commands, hooks are markdown files with YAML frontmatter
- Shell scripts in `scripts/` target bash on Windows (cygpath for path conversion)
- TDS-CLI credentials use Windows DPAPI encryption stored at `~/.claude/tds-credentials.enc`
- Server/project config cached at `~/.claude/tds-cache.json`

## Language

All plugin content (skills, agents, commands, docs) is written in Brazilian Portuguese. README and user-facing text are also in Portuguese.

## Credits

Includes substantial portions from [advpl-specialist](https://github.com/thalysjuvenal/advpl-specialist) by Thalys Augusto (MIT License). See NOTICE file.
