# Chimera Lite

Claude-Code-native successor to [Project Chimera](../project_chimera). A personal
research OS for one user: arXiv mining → Obsidian "Exocortex" vault, driven by
Claude Code instead of a bespoke agent loop.

See [`CLAUDE.md`](./CLAUDE.md) for the architecture and the rules of the road.

## Architecture in one breath
Claude Code is the agent loop. Domain capabilities are MCP servers. Persona and
process discipline are skills under `.claude/`. No custom streaming protocol, no
custom frontend.

```
Claude Code  ──native tool-calling──►  MCP servers
                                        ├─ chimera-vault   (Obsidian read/query)
                                        └─ chimera-papers  (arXiv miner + daily pipeline)
   + native WebSearch, Task subagents
```

## Quickstart
Prereqs: [uv](https://docs.astral.sh/uv/), Python 3.11+, and `rg` (ripgrep) on PATH.

```bash
uv sync                 # install MCP server deps into .venv
# edit .mcp.json env paths if your vault/papers dirs differ
```

Claude Code reads `.mcp.json` automatically when launched in this directory.
Smoke-check a server starts:

```bash
uv run python mcp-servers/chimera-vault/server.py    # Ctrl-C to stop
```

## Status
**Foundation scaffold.** MCP servers declare the tool contract; the domain
import-wiring is migration sprint 1 — see the "Migration status" section in
`CLAUDE.md`. Tool calls return a NOT-WIRED sentinel until then.

## Layout
| Path | What |
|---|---|
| `CLAUDE.md` | Architecture + hard rules (read first) |
| `.mcp.json` | MCP server registration |
| `mcp-servers/chimera-vault/` | Vault MCP server |
| `mcp-servers/chimera-papers/` | Papers MCP server + copied domain code |
| `.claude/skills/` | The five `chimera-*` skills |
| `docs/` | Inherited history (old oligo architecture) |
