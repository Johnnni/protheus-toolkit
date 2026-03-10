# claude-tdn

Search and fetch [TOTVS Protheus](https://www.totvs.com/protheus/) documentation from [TDN (TOTVS Developer Network)](https://tdn.totvs.com) directly in your Claude Code conversations.

## What it does

This plugin gives Claude Code two tools:

- **tdn_search** - Search TDN pages by keyword (e.g. "FWRest", "TReport", "MsExecAuto")
- **tdn_fetch** - Fetch the full content of any TDN page as Markdown

Just ask Claude about any Protheus function, class, or concept, and it will automatically search TDN and bring the documentation into the conversation.

## Installation

### 1. Install the plugin

```bash
claude plugin add github:Johnnni/claude-tdn
```

### 2. Prerequisites

You need **Python 3.9+** installed:

- **Linux/WSL**: Usually pre-installed. Check with `python3 --version`
- **macOS**: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 3. Run the setup

After installing the plugin, run the setup script to install Python dependencies:

```bash
# Find where the plugin was installed and run setup
bash ~/.claude/plugins/claude-tdn/scripts/setup.sh
```

### 4. Restart Claude Code

Close and reopen Claude Code (or start a new session) to activate the TDN tools.

## Usage

Just ask naturally:

- "What does FWRest do in Protheus?"
- "Search TDN for TReport documentation"
- "How do I use MsExecAuto?"
- "Fetch the TDN page for DbSelectArea"

Claude will automatically search TDN and show you the relevant documentation.

## How it works

The plugin runs a local Python MCP server that:

1. Uses the TDN Confluence REST API to search pages
2. Fetches page source HTML and converts to clean Markdown
3. Returns the content to Claude Code for analysis

## Troubleshooting

### "Virtual environment not found"

Run the setup script:
```bash
bash ~/.claude/plugins/claude-tdn/scripts/setup.sh
```

### Tools not appearing

1. Check the plugin is installed: run `/mcp` in Claude Code
2. Restart Claude Code
3. Verify Python 3 is available: `python3 --version`

### Search returns no results

- Try different keywords (Portuguese terms often work better)
- Use the exact function/class name
- Check your internet connection

## License

MIT

## Author

[Johnnni](https://github.com/Johnnni)
