# Chimera Lite

Claude-Code-native successor to [Project Chimera](../project_chimera). A personal
research OS for one user: arXiv mining → Obsidian "Exocortex" vault, driven by
Claude Code instead of a bespoke agent loop.

Not a framework, not SaaS, and **not an agent** — Claude supplies the intelligence; what this repo
engineers is the fidelity of what the researcher comes to believe through the tool. See
[`CLAUDE.md`](./CLAUDE.md) for the architecture and the rules of the road, and
[`TBD.md`](./TBD.md) for what is currently waiting on the Architect.

## Architecture in one breath
Claude Code is the agent loop. Domain capabilities are MCP servers. Persona and
process discipline are skills under `.claude/`. No custom streaming protocol, no
custom frontend.

```
Claude Code  ──native tool-calling──►  MCP servers
                                        ├─ chimera-vault   (vault read/query + staging writes)
                                        └─ chimera-papers  (arXiv mining, ingest, extraction)
   + native WebSearch, Task subagents (9 pinned worker types in .claude/agents/)
```

Judgment never lives in a tool call. Both servers announce it themselves: *"Primitives only. No
tool returns a verdict or makes a judgment."* Verdicts are produced by Claude in isolated
subagents, orchestrated by skills.

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

**GPU note.** PDF→Markdown ingest runs `mineru` on PyTorch/CUDA. `torch` comes from the **cu128**
index (pinned in `pyproject.toml`), not the CPU-only PyPI wheel — the first `uv sync` pulls a
multi-GB wheel plus the MinerU ML stack. Verify with
`python -c "import torch; print(torch.cuda.is_available())"`. Everything except ingest works without
a GPU.

Run the tests:

```bash
.venv/Scripts/python.exe -m pytest -q
```

## Status
**Live, and in active development.** Both MCP servers are fully wired — 22 registered tools — and
the research harness (W1 claim verification, W2 breadth mapping, deep extraction) runs end-to-end
against the real vault.

Current position: **Phase L.C — Colligo** is ⚠️ *functionally sealed* (2026-08-12);
[seal review](docs/audits/phase-L.C-seal-review.md). Next in the backward arc is **Phase K**.
Phase history is [`docs/ROADMAP.md`](docs/ROADMAP.md).

A *functional* seal is not a green one — two of L.C's sealing conditions are open and need real
research sessions, not build sessions. They are listed in [`TBD.md`](./TBD.md).

## Layout
| Path | What |
|---|---|
| `docs/ARCHITECTURE/INVARIANTS.md` | **The canonical — read before any change.** FROZEN |
| `docs/ARCHITECTURE/` | `FORMAL_MODEL` (the objects) · `ENFORCEMENT_DEBT` (what the code actually holds) · `ARCHITECTURE_RULES` (the Violation Detector checklist) |
| `CLAUDE.md` | Architecture + hard rules |
| `TBD.md` | Open items waiting on the Architect (a pointer file; holds no authority) |
| `.mcp.json` | MCP server registration |
| `mcp-servers/chimera-vault/` | Vault MCP server — query, staging, harness artifacts, edges |
| `mcp-servers/chimera-papers/` | Papers MCP server — mining, ingest, conversion, extraction |
| `.claude/skills/` | 20 `chimera-*` skills (workflows, lenses, process discipline) |
| `.claude/agents/` | 9 pinned subagent types; model bound in frontmatter |
| `docs/phases/`, `docs/plans/`, `docs/sprints/` | Phase specs, batch plans, sprint records |
| `docs/audits/`, `docs/incidents/`, `docs/logs/` | Audits, incidents, friction logs |
| `tests/` | 241 tests |

## The one thing to know before changing anything
`docs/ARCHITECTURE/INVARIANTS.md` is Architect-authored and **frozen** — reference it, never restate
or extend it. **An invariant is not a shipped guarantee:** check
[`ENFORCEMENT_DEBT.md`](docs/ARCHITECTURE/ENFORCEMENT_DEBT.md) before relying on one. Several are
stated targets whose enforcing code does not exist yet, and that file is the honest record of which.
