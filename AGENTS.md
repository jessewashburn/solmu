# AGENTS.md

This repo's dev history lives in PromptRoot under tenant `solmu`.

Coding agents (Claude Code, Cursor, Continue, Cline, Jules) use that tenant
for SDD search and authoring. The MCP server resolves the tenant
automatically from the `.promptroot-tenant` file in this repo, so no
per-call configuration is needed.

## Quick start for agents

- Read SDDs: `promptroot_search_sdds` / `promptroot_get_sdd`.
- Create new SDDs: `promptroot_create_sdd` (frontmatter + body).
- Update an SDD: `promptroot_update_sdd` (writes a new version).

If no MCP server is configured, fall back to:

    POST https://us-central1-promptroot-b02a2.cloudfunctions.net/ragQuery
    {
      "query": "<question>",
      "topK": 5,
      "tenantId": "solmu"
    }
