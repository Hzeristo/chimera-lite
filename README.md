# Chimera Lite

Claude-Code-native successor to [Project Chimera](../project_chimera). A personal
research OS for one user: arXiv mining → Obsidian "Exocortex" vault, driven by
Claude Code instead of a bespoke agent loop.

Not a framework, not SaaS, and **not an agent** — Claude supplies the intelligence; what this repo
engineers is the fidelity of what the researcher comes to believe through the tool. See
[`CLAUDE.md`](./CLAUDE.md) for the architecture and the rules of the road, and
[`TBD.md`](./TBD.md) for what is currently waiting on the Architect.

## Why "chimera"
The name is the intake policy, not decoration. A chimera is assembled from parts taken wherever they
were found — so this repo grafts on **any useful component, from anywhere, provided it is
validated** before it becomes load-bearing. That second clause is the whole discipline, and it has
teeth: `chimera-dependency-veto` is where a proposed graft has to argue for itself.

The other half of the name is what it is *not*. This is one researcher's harness, not an official
product, and it is meant to stay that way — the same register as Kasane Teto, a fan-made voice that
was never a sanctioned Vocaloid and whose own lore makes her a chimera. Unofficial by construction,
assembled from what worked, and none the worse for it. Every design decision here assumes exactly
one user; "how would this generalize" is not a question this repo answers.

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
| `.claude/skills/` | 19 `chimera-*` skills (workflows, lenses, process discipline) + `_shared/` |
| `.claude/agents/` | 9 pinned subagent types; model bound in frontmatter |
| `docs/phases/`, `docs/plans/`, `docs/sprints/` | Phase specs, batch plans, sprint records |
| `docs/audits/`, `docs/incidents/`, `docs/logs/` | Audits, incidents, friction logs |
| `tests/` | 241 tests |

## House conventions
Four practices this repo already runs on, written down because they were only ever visible by
reading sprint records:

- **A check nobody has seen fail is not a check.** New assertions ship with a recorded negative
  control — break the thing on purpose, watch the check fail, restore it.
- **A functional seal is not a green seal.** ⚠️ means the mechanical conditions passed and
  longitudinal ones are still open. The marker is the honesty, not a formality.
- **Retract in place.** A claim that turns out wrong is narrowed where it stands, with the reason it
  was wrong attached — never silently rewritten. I0.4 (append-only) applied to our own documents.
- **Defects get names, not just ids.** *The CRLF trap*, *the green suite that lied* — the shape of
  the failure, never its location, so it is recognizable when it reappears elsewhere. One event is
  an incident (`docs/incidents/`); a reused name means a pair; three is a class and escalates to
  `docs/logs/friction-*.md`. Ledger and rules: [`docs/logs/DEFECTS.md`](docs/logs/DEFECTS.md).

- **"Is this load-bearing, or is it theater?"** The standing challenge to any new flag, criteria
  file, verifier, or status field. Two tests: has anyone ever watched it fail, and would deleting it
  change anything downstream. The Theater is the house name for the permanent adversary — see
  [`docs/phases/PHILOSOPHY.md`](docs/phases/PHILOSOPHY.md).

**Date-stamp anything that can decay.** Status claims, "verified" claims, counts — carry the date
they were checked (`ENFORCEMENT_DEBT.md` does this well). Nothing in this repo has ever gone stale
by being wrong; it goes stale by having been right on a day nobody recorded.

## The one thing to know before changing anything
`docs/ARCHITECTURE/INVARIANTS.md` is Architect-authored and **frozen** — reference it, never restate
or extend it. **An invariant is not a shipped guarantee:** check
[`ENFORCEMENT_DEBT.md`](docs/ARCHITECTURE/ENFORCEMENT_DEBT.md) before relying on one. Several are
stated targets whose enforcing code does not exist yet, and that file is the honest record of which.
