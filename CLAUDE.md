# Chimera Lite

Personal research OS for a single PhD-student user. Not a framework. Not SaaS.

This is the **Claude-Code-native** successor to Project Chimera. The custom oligo
agent loop and the astrocyte frontend are retired; Claude Code *is* the agent loop,
and the surviving domain tools are exposed as MCP servers.

## Migration context
**This repo is mid-migration.** It is not a greenfield project — it is the operational
port of `project_chimera` (a bespoke agent + Tauri frontend) onto Claude Code + MCP.
Read this before assuming anything about how a feature "should" work.

> **Fresh session? Read [`docs/MIGRATION_LINEAGE.md`](docs/MIGRATION_LINEAGE.md) first.**
> It explains the *why* behind the inherited decisions (poll model, single-GPU convert,
> thin adapters, CUDA torch, BB persona, …) so you don't "fix" what's intentional or
> re-litigate settled choices. This file is *how*; that file is *why*.

- **Where we came from:** `../project_chimera` — oligo agent loop (`ChimeraAgent`, 1485
  lines of theater loop + text-DSL tool parsing) and the astrocyte Svelte/Tauri frontend.
  Both retired, preserved on the `archive/chimera-oligo` branch of that repo.
- **Why:** feasibility verdict — `../project_chimera/docs/audits/chimera-to-code-feasibility.md`.
  The tools migrate to MCP and improve; the agent loop is deleted (native loop replaces it).
- **Active phase:** **Phase M — Chimera Lite Migration** (`docs/phases/phase-M.md`).
  Its sprint sequence (M.0 audit → M.1 vault wiring → M.2 papers wiring → M.3 BB persona
  → M.4 cleanup → M.5 E2E) and red lines are authoritative for migration work.
- **Current state:** foundation scaffold only. The MCP servers declare tool **contracts**;
  their bodies lazy-import and return a NOT-WIRED sentinel. Domain wiring is Phase M.
  See "Migration status" below for the exact gap.
- **Phase M red lines (summary; full list in `phase-M.md`):** no oligo loop code, no
  astrocyte/Tauri/Svelte, no text-DSL parsing, no SSE protocol, MCP servers stay thin
  adapters (<200 lines), TaskService stays poll-model, BB persona via skill only.

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
**Phase M is SEALED** (full seal, 2026-07-03; sprints M.0.5–M.5). All tool bodies are
wired to real domain logic; the import layer is flat (`grep src.crucible` / `src.oligo` /
`astrocyte` → 0); the CUDA MinerU stack runs on the GPU. No NOT-WIRED sentinels remain.

**All five M.5 sealing conditions pass live** (`docs/audits/M.5-e2e-smoke.md`): Test 1
(vault) ✅, Test 2 (daily pipeline) ✅, Test 3 (BB voice) ✅, Test 4 (independence) ✅.
Test 2 was confirmed end-to-end on 2026-07-03 after the miner-pipeline incident chain
closed (final fix: headless-spawn isolation, incident `2026-07-02`) —
`new_pdfs=3 ingested=3 convert_failed=0 errors=0`, real titles.

**Known follow-ups (deferred, not blockers):** `status=?` across knowledge nodes (vault
frontmatter; Phase VI), and the concurrency lock's stale-task liveness gap
(`TaskService.has_active_long_task` trusts disk status — a crashed task reads as "busy"
until cleared). See `docs/sprints/phase-M/M.2a.md` and the M.5 notes.

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
6. `chimera-bb-persona` — always active; restyles the FINAL answer paragraph in BB's
   voice (Fate/EXTRA CCC Moon Cell AI). Reasoning + tool output stay plain. At
   `.claude/skills/chimera-bb-persona/`.
7. `chimera-academic-observe` — always active (Phase N.A); proactively surfaces vault-node
   connections during research analysis via `obsidian_graph_query` / `vault_query`,
   relevance-gated and silent by default. At `.claude/skills/chimera-academic-observe/`.

**Research lenses (Phase N.A — trigger-based, auto-selected by paper type).** Pure prompt
skills, no MCP changes. Each requires mechanism + evidence + falsifiability via the shared
contract `.claude/skills/_shared/falsifiability.md`:
- `chimera-lens-forensic-leakage` — empirical / eval papers: leakage & contamination audit.
- `chimera-lens-thermodynamic-decay` — memory / long-context papers: falsifiable decay probe.
- `chimera-lens-state-collision` — memory-update / belief-revision papers: conflict-arbitration stress test.
- `chimera-lens-agentic-illusion` — "agentic" papers: plumbing audit (real loop vs one-shot).
- `chimera-lens-math-decoration` — modeling / algorithm papers: load-bearing vs decorative math.
- `chimera-lens-ontological-map` — surveys / position papers: consolidated ontology (axes + categories + bottlenecks + gaps + edges).

## Hard rules
- This repo has ONE user. Do not generalize.
- Skill rules override generic best practices.
- Do not invent MCP tools that weren't in the oligo KEEP list without a friction
  signal — see `chimera-core-philosophy` and `chimera-dependency-veto`.
- Never auto-promote `docs/staging/` candidates to the vault — user-reviewed.
- Obsidian vault `templates/` are user-synced; edit repo sources, not vault copies.

## Development environment

### Python (MCP servers)
- Path: `.venv\Scripts\python.exe` (repo-root venv, created by `uv sync`; one venv shared by both servers)
- Version: 3.13 (`requires-python = ">=3.11"`)
- Package manager: uv
- Manifest: `pyproject.toml` (repo root)
- Activation prefix for tool calls: `D:\MAS\chimera-lite\.venv\Scripts\python.exe -m {tool}`
- Run a server directly: `uv run python mcp-servers/chimera-vault/server.py`
- External tool: `vault_query` shells out to **ripgrep (`rg`)** — must be on PATH.

#### GPU / CUDA (paper pipeline)
`mineru` PDF→Markdown ingest runs PyTorch on the GPU.
- GPU: **NVIDIA RTX 5060 (Blackwell, sm_120)**; driver supports CUDA 13.1.
- torch is installed from the **cu128** build, not the CPU-only PyPI wheel (which lacks
  sm_120). Wired via `[[tool.uv.index]] pytorch-cuda` → `https://download.pytorch.org/whl/cu128`
  + `[tool.uv.sources] torch/torchvision`. Installed: `torch 2.11.0+cu128`.
- Verify: `python -c "import torch; print(torch.cuda.is_available())"` → `True`
  (`torch.cuda.get_device_name(0)` → `NVIDIA GeForce RTX 5060`).
- First `uv sync` downloads the CUDA torch wheel (~GB) + the MinerU ML stack; later syncs
  use the cache. Do NOT let a plain `pip`/CPU wheel shadow it.

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
