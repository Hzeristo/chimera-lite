# Chimera Lite

Personal research OS for a single PhD-student user. Not a framework. Not SaaS.

This is the **Claude-Code-native** successor to Project Chimera. The custom oligo
agent loop and the astrocyte frontend are retired; Claude Code *is* the agent loop,
and the surviving domain tools are exposed as MCP servers.

## Lineage
- Predecessor: `../project_chimera` (oligo agent + astrocyte frontend).
- Migration rationale & feasibility verdict: `../project_chimera/docs/audits/chimera-to-code-feasibility.md`.
- The oligo/astrocyte source is preserved on the `archive/chimera-oligo` branch of
  the `project_chimera` repo. Nothing was deleted — only retired.
- Inherited docs under `docs/` (ROADMAP, phases, plans, friction logs, incidents)
  describe the **old** architecture. They are history, not current spec. Phases that
  built the agent loop / SSE protocol / astrocyte UI are retired. Do not treat them
  as a second source for how Chimera Lite works — this file and the MCP servers are.

## What replaces what
| Old (oligo) | New (Chimera Lite) |
|---|---|
| `ChimeraAgent` theater loop (route → tool → wash → synthesize) | Claude Code's native agent loop |
| Text-DSL tool calls (`<CMD>` / `<tool_call>`) + arg-repair | Native MCP tool-calling |
| `bb-*` SSE protocol → astrocyte | Claude Code's native streaming (terminal/IDE) |
| Late-bound persona / prompt composer | `CLAUDE.md` + `.claude/skills/` |
| `web_search` tool | Claude Code native **WebSearch** |
| `fork_agent` / `fork_subagent` | Claude Code native **Task** subagents / workflows |
| Vault tools, PaperMiner, TaskService | MCP servers (see below) — domain logic kept |

## MCP servers
Registered in `.mcp.json`. Tool **contracts** (names, args, docstrings) live in each
`server.py` and are authoritative.

- **`chimera-vault`** — read/query the Obsidian vault:
  `search_vault`, `search_vault_attribute`, `read_vault_file`,
  `obsidian_graph_query`, `vault_query`.
- **`chimera-papers`** — arXiv mining + the daily pipeline (long-running via
  `TaskService`, poll model): `arxiv_miner`, `daily_paper_pipeline`,
  `check_task_status`.

Web search and subagent delegation are **not** MCP servers — use Claude Code's native
WebSearch and Task tools.

## Migration status (IMPORTANT)
The MCP servers currently declare the **tool contract only**. The domain code under
`mcp-servers/chimera-papers/` was copied verbatim from oligo and still imports
`from src.crucible…` / `from src.oligo…` and references not-yet-ported modules
(`config.py`, `schemas.py`, `naming.py`). Tool bodies return a clear NOT-WIRED
sentinel until wired.

**Migration sprint 1 (next):** port `config` / `schemas` / `naming`, rewrite the
`src.crucible` / `src.oligo` imports to the flat package layout, and connect each
`@mcp.tool` body to its domain function. Track this as a phase via
`chimera-sprint-discipline` before writing code.

## Start here
- This file (architecture + rules).
- `docs/ROADMAP.md` — inherited phase history (old architecture; read as lineage).
- `README.md` — quickstart.

## Skills
Ported from project_chimera; same authority model.
1. `chimera-core-philosophy` — always active
2. `chimera-sprint-discipline` — planning / reviewing
3. `chimera-code-taste` — batch sprint execution (code/UI taste)
4. `chimera-dependency-veto` — adding dependencies
5. `chimera-commit-style` — drafting commits

## Hard rules
- This repo has ONE user. Do not generalize.
- Skill rules override generic best practices.
- Do not invent MCP tools that weren't in the oligo KEEP list without a friction
  signal — see `chimera-core-philosophy` and `chimera-dependency-veto`.
- Never auto-promote `docs/staging/` candidates to the vault — user-reviewed.
- Obsidian vault `templates/` are user-synced; edit repo sources, not vault copies.

## Development environment

### Python (MCP servers)
- Package manager: uv
- Manifest: `pyproject.toml` (repo root; one venv shared by both servers)
- Version: 3.11+
- Run a server directly: `uv run python mcp-servers/chimera-vault/server.py`
- External tool: `vault_query` shells out to **ripgrep (`rg`)** — must be on PATH.

### Configuration
- Server paths come from environment variables set in `.mcp.json`:
  - `CHIMERA_VAULT_ROOT` — Obsidian vault path (sibling: `D:\MAS\project_chimera_vault`).
  - `CHIMERA_PAPERS_ROOT` — where mined papers land.
- Legacy `~/.chimera/config.toml` (`SystemConfig`) is still read by the copied domain
  code until sprint 1 decides whether to keep it or fold everything into env vars.

### Obsidian Vault
- Path: `D:\MAS\project_chimera_vault` — a SIBLING directory, not inside the repo.
- `chimera-vault` has read access for query/search; write access only for
  staging-area operations.

## Repository layout
- `.claude/skills/` — the five `chimera-*` skills + `_shared/` (ported).
- `mcp-servers/chimera-vault/` — vault MCP server (`server.py` + sprint-1 domain modules).
- `mcp-servers/chimera-papers/` — papers MCP server + copied domain code (ports/, services).
- `docs/` — inherited history (ROADMAP, phases, plans, audits, friction logs, incidents).
- `.mcp.json` — MCP server registration for Claude Code.
