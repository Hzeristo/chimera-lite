# Chimera Lite

Personal research OS for a single PhD-student user. Not a framework. Not SaaS.

Claude Code *is* the agent loop; the surviving domain tools are exposed as MCP servers.

## Product philosophy
Chimera Lite is **not an agent** — it is an **epistemic instrument**. Claude supplies the
intelligence; what this repo engineers is the *fidelity of what the researcher comes to believe
through the tool*. Capability is cheap (Claude-provided); **fidelity is the scarce good**, and it
is bought by refactoring the foundation, not by adding features — which is why the hard recent
phases (**L — Locus**, **K — Katalepsis**) grow *backward* from the pivot. Corollary
(the north star, and it is self-suspicious): **advisory rigor is negative value** — a provenance
flag / criteria / verifier that only *performs* rigor launders opinion into knowledge, worse than
nothing. Enforce it or delete it; the permanent adversary is the instrument's own theater. The
dev-phase codename motif encodes this arc (neural horror → epistemology); full *why* in
[`docs/phases/PHILOSOPHY.md`](docs/phases/PHILOSOPHY.md), the naming grammar in
[`docs/phases/CODENAMES.md`](docs/phases/CODENAMES.md).

## Current state
Active build: **Phase L — Locus: The Research Harness** (`docs/phases/phase-L.md`) — automates the
manual research harness into two Claude-subagent workflows, W1 (claim verbatim verification) and W2
(breadth mapping), with paper-type criteria loaded dynamically from the vault. Judgment lives in Task
subagents; MCP provides the primitives.

Known deferred issues (not blockers): `status=?` across knowledge nodes (vault frontmatter); and the
concurrency lock's stale-task liveness gap (`TaskService.has_active_long_task` trusts disk status — a
crashed task reads as "busy" until cleared).

## Architecture invariants — the rule SOT (READ FIRST)
[`docs/ARCHITECTURE/ARCHITECTURE_RULES.md`](docs/ARCHITECTURE/ARCHITECTURE_RULES.md) is the **single
source of truth for invariant rules** — constraints that hold across ALL phases. It **overrides any
sprint- or style-level instruction**: the level hierarchy is **ARCHITECTURE (that file) > SPRINT
(`docs/phases/*`) > STYLE (`.claude/skills/*`)**, and on conflict the higher level always wins.

- **Before ANY change** (code, tool, skill, workflow), run its **Violation Detector** checklist
  (R1–R6). A "yes" is a stop, regardless of how small or sprint-scoped the change looks — this is the
  guard against L.B.2-class errors (an invariant invisible at the executor's altitude, silently
  violated by a locally-reasonable edit).
- The six invariants: **R1** no LLM call inside any MCP server process · **R2** no truth advance
  without a human action · **R3** staging-gate universality (`ascend_node` sole writer to
  `Knowledge/`) · **R4** `chimera_tier` integrity · **R5** provenance load-bearing (`[V]/[P]/[U]`) ·
  **R6** human authorship of T/I/D bodies.
- Each rule is marked **STRUCTURAL** (enforced) or **ADVISORY** (committed but not yet enforced —
  acknowledged debt, see that file's Appendix B). Do not read an ADVISORY rule as a shipped guarantee.
- Reference that file; **never restate or override it** (drift rule). Its *why* is
  [`docs/ARCHITECTURE/THEORETICAL_FRAMEWORK.md`](docs/ARCHITECTURE/THEORETICAL_FRAMEWORK.md); tag and
  edge semantics are `TAG_SYSTEM.md` / `NODE_ONTOLOGY.md`. The audit behind it is
  [`docs/ARCHITECTURE/INVARIANT_RULES_AUDIT.md`](docs/ARCHITECTURE/INVARIANT_RULES_AUDIT.md).

## MCP servers
Registered in `.mcp.json`. Tool **contracts** (names, args, docstrings) live in each
`server.py` and are authoritative.

- **`chimera-vault`** — read/query the Obsidian vault:
  `search_vault`, `search_vault_attribute`, `read_vault_file`,
  `obsidian_graph_query`, `vault_query`.
- **`chimera-papers`** — arXiv mining + the daily pipeline (long-running via
  `TaskService`, poll model): `arxiv_miner`, `daily_paper_pipeline`,
  `check_task_status`; plus `ingest_paper` — single known paper (arxiv_id **or**
  local pdf_path) → Knowledge node (synchronous; the single-paper counterpart to
  `daily_paper_pipeline`).

Web search and subagent delegation are **not** MCP servers — use Claude Code's native
WebSearch and Task tools.

## Start here
- **`docs/ARCHITECTURE/ARCHITECTURE_RULES.md` — the invariant rule SOT (read before any change).**
- This file (architecture + rules).
- `docs/ROADMAP.md` — phase history.
- `README.md` — quickstart.

## Skills
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

## Model routing (dev-time)
Worker model pins live in `.claude/agents/*.md` and are checked by
`.claude/skills/chimera-code-taste/scripts/check_model_routing.ps1` (rationale: `docs/audits/model-routing-gaps.md`).
Dev sessions default to Sonnet 5; escalate to Opus only for phase_audit, batch_planning, seal gate, and architectural decisions.

## Hard rules
- **Invariants R1–R6 in `docs/ARCHITECTURE/ARCHITECTURE_RULES.md` are binding and override sprint/style rules.** The rules below are the always-loaded subset; that file is the authority.
- This repo has ONE user. Do not generalize.
- Skill rules override generic best practices.
- Do not invent MCP tools without a friction signal — see `chimera-core-philosophy` and `chimera-dependency-veto`.
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
- Legacy `~/.chimera/config.toml` (`SystemConfig`) is still read by some domain code alongside the env vars above.

### Obsidian Vault
- Path: `D:\MAS\project_chimera_vault` — a SIBLING directory, not inside the repo.
- `chimera-vault` has read access for query/search; write access only for
  staging-area operations.

## Repository layout
- `.claude/skills/` — the `chimera-*` skills + `_shared/`.
- `.claude/agents/` — pinned subagent types (model bound in frontmatter).
- `mcp-servers/chimera-vault/` — vault MCP server (`server.py` + domain modules).
- `mcp-servers/chimera-papers/` — papers MCP server + domain code (ports/, services).
- `docs/` — ROADMAP, phases, plans, audits, friction logs, incidents.
- `.mcp.json` — MCP server registration for Claude Code.
