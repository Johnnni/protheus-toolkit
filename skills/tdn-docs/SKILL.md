---
name: tdn-docs
description: This skill should be used when the user asks about TOTVS Protheus documentation, ADVPL/TLPP functions, Protheus framework classes, or mentions "TDN", "busca no TDN", "documentacao do Protheus", "como funciona o FWRest", "parametros do MsExecAuto", or any TOTVS/Protheus API reference lookup. Also activate when the user asks "what does this function do" for Protheus-specific functions.
---

# TDN Documentation Lookup

Search and retrieve official TOTVS Protheus documentation from TDN (TOTVS Developer Network) directly during the conversation.

## Available Tools

Two MCP tools are available via the `tdn` server:

### tdn_search

Search TDN pages by keyword. Returns a list of matching pages with IDs, titles, and URLs.

**When to use:** When the user asks about a Protheus function, class, or concept and the exact page is unknown.

```
tdn_search(query="FWRest", limit=5)
```

### tdn_fetch

Fetch the full content of a TDN page as Markdown. Accepts a page ID (from search results) or a full TDN URL.

**When to use:** After identifying the right page via search, or when the user provides a TDN URL.

```
tdn_fetch(source="417696190")
tdn_fetch(source="https://tdn.totvs.com/display/framework/FWRest")
```

## Recommended Workflow

1. When the user asks about a Protheus topic, use `tdn_search` to find relevant pages
2. Review the search results and identify the most relevant page
3. Use `tdn_fetch` to retrieve the full documentation
4. Summarize the key information for the user, citing the source URL

## Tips

- Search by function/class name for precise results (e.g. "FWRest", "TReport", "MsExecAuto")
- Search by topic for broader results (e.g. "REST API", "relatorio", "ponto de entrada")
- The TDN content is in Portuguese; search terms in Portuguese may yield better results
- Large pages may return extensive Markdown; focus on the sections relevant to the user's question
- Always provide the source URL so the user can visit the full page if needed
