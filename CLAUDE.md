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
nothing. Enforce it or delete it; the permanent adversary is the instrument's own theater — **the
Theater**, in house shorthand, and *"is this theater?"* is the standing question for any new flag,
criteria, or verifier. Two tests, in `PHILOSOPHY.md`: has anyone seen it fail, and would deleting it
change anything downstream. The
dev-phase codename motif encodes this arc (neural horror → epistemology); full *why* in
[`docs/phases/PHILOSOPHY.md`](docs/phases/PHILOSOPHY.md), the naming grammar in
[`docs/phases/CODENAMES.md`](docs/phases/CODENAMES.md).

## Current state
**Phase L.C — Colligo** is ⚠️ *functionally sealed* (2026-08-12) — candidate material (W1/extract
output) binds into committed artifacts across three consumption routes. Sealed on the mechanical
conditions only: two remain open and need real research sessions, not build sessions (`TBD.md`).
Next in the backward arc is **Phase K**.

The harness it sits on is Phase L: W1 (claim verbatim verification), W2 (breadth mapping), and deep
extraction, with paper-type criteria loaded dynamically from the vault. Judgment lives in Task
subagents; MCP provides the primitives.

Known deferred issues (not blockers): `status=?` across knowledge nodes (vault frontmatter); and the
concurrency lock's stale-task liveness gap (`TaskService.has_active_long_task` trusts disk status — a
crashed task reads as "busy" until cleared).

## Architecture invariants — the canonical (READ FIRST)
[`docs/ARCHITECTURE/INVARIANTS.md`](docs/ARCHITECTURE/INVARIANTS.md) is the **Architect-authored
canonical** — the single source of truth for what must hold across ALL phases. It is **FROZEN**:
reference it, never restate, reword, or extend it. If something looks missing or wrong, surface it as
a question.

Three documents, three jobs — never conflate them:

| Document | States |
|---|---|
| [`INVARIANTS.md`](docs/ARCHITECTURE/INVARIANTS.md) | **what must be true** — I0.x absolute (violation = no longer L2) · I1.x architectural · I2.x mutable · an explicit non-invariant list |
| [`FORMAL_MODEL.md`](docs/ARCHITECTURE/FORMAL_MODEL.md) | **the formal objects** — artifact graph, evidence tiers, tags, transitions |
| [`ENFORCEMENT_DEBT.md`](docs/ARCHITECTURE/ENFORCEMENT_DEBT.md) | **what the code actually holds** — enforcement mode vs observed compliance, every gap anchored |

- **Before ANY change** (code, tool, skill, workflow), run the **Violation Detector** checklist in
  [`ARCHITECTURE_RULES.md`](docs/ARCHITECTURE/ARCHITECTURE_RULES.md). A "yes" is a stop, regardless of
  how small or sprint-scoped the change looks — this is the guard against L.B.2-class errors (an
  invariant invisible at the executor's altitude, silently violated by a locally-reasonable edit).
- The level hierarchy is **ARCHITECTURE (the canonical) > SPRINT (`docs/phases/*`) > STYLE
  (`.claude/skills/*`)**; on conflict the higher level always wins. `ARCHITECTURE_RULES.md` is now
  **subordinate** — it holds only the precedence rule, the checklist, and an R1–R6 → I-id pointer
  table for the legacy ids cited across sprint docs.
- **An invariant is not a shipped guarantee.** Check `ENFORCEMENT_DEBT.md` before relying on one:
  monotonicity (I0.2) and provenance decay (I0.4) are stated targets whose enforcing code does not
  exist yet.
- The *why* is
  [`docs/ARCHITECTURE/THEORETICAL_FRAMEWORK.md`](docs/ARCHITECTURE/THEORETICAL_FRAMEWORK.md); tag and
  edge semantics are `TAG_SYSTEM.md` / `NODE_ONTOLOGY.md`. All three are **subordinate** to the
  canonical and defer to it on any divergence.

## MCP servers
Registered in `.mcp.json`. Tool **contracts** (names, args, docstrings) live in each
`server.py` and are authoritative.

- **`chimera-vault`** (11) — vault read/query: `search_vault`, `search_vault_attribute`,
  `read_vault_file`, `obsidian_graph_query`, `vault_query`, `load_criteria`. Writes:
  `create_node` (knowledge-only), `ascend_node` (sole writer of `Knowledge/`), `link_nodes`
  (stages an edge patch) / `apply_link_patch` (applies one — Architect-invoked),
  `write_result` (harness artifacts + their lifecycle transitions).
- **`chimera-papers`** (11) — arXiv mining + the daily pipeline (long-running via `TaskService`,
  poll model): `arxiv_miner`, `daily_paper_pipeline`, `check_task_status`. Single-paper:
  `ingest_paper`, `fetch_paper`, `convert_pdf_to_md`, `get_paper_markdown`, `mineru_sidecar`.
  Judgment-adjacent primitives (the server never judges): `analyze_paper_data`,
  `stage_deep_read_node`, `write_scout_card`.

Web search and subagent delegation are **not** MCP servers — use Claude Code's native
WebSearch and Task tools.

## Start here
- **`docs/ARCHITECTURE/INVARIANTS.md` — the canonical (read before any change), with
  `FORMAL_MODEL.md` for the objects and `ENFORCEMENT_DEBT.md` for what actually holds.**
- `docs/ARCHITECTURE/ARCHITECTURE_RULES.md` — the Violation Detector checklist to run first.
- This file (architecture + rules).
- **`docs/README.md` — the router: who reads what, and which directories are archives.** `docs/` is
  ~1.6 MB; **context is the load**, so archives are grepped, never browsed. Progressive disclosure
  is the red line.
- `docs/ROADMAP.md` — phase history.
- `README.md` — quickstart · `TBD.md` — what is open and waiting on the Architect.

## Skills
19 under `.claude/skills/` (+ `_shared/`). Dev-process:
1. `chimera-sprint-discipline` — planning / reviewing
2. `chimera-code-taste` — batch sprint execution (code/UI taste)
3. `chimera-dependency-veto` — adding dependencies
4. `chimera-commit-style` — drafting commits
5. `chimera-mcp-taste` — designing / changing an MCP tool surface
6. `chimera-bb-persona` — always active; restyles the FINAL answer paragraph in BB's
   voice (Fate/EXTRA CCC Moon Cell AI). Reasoning + tool output stay plain. At
   `.claude/skills/chimera-bb-persona/`.
7. `chimera-academic-observe` — always active (Phase N.A); proactively surfaces vault-node
   connections during research analysis via `obsidian_graph_query` / `vault_query`,
   relevance-gated and silent by default. At `.claude/skills/chimera-academic-observe/`.

**Research workflows (explicitly invoked, never ambient).** Each orchestrates MCP primitives and
delegates every unit of judgment to a pinned subagent:
- `chimera-triage-paper` — cheap bulk screen → a scout-tier card.
- `chimera-deep-extract` — ONE paper → a staged `deep_read` Knowledge node.
- `chimera-w1-verify` — verify a claim against its cited paper → `[V]`/`[P]`/`[U]`. Has a queue
  mode for a claim spotted mid-read (`chimera-w1-runner`, detached).
- `chimera-w1-review` — review pending verdicts, promote the selected, stage `evidence_base`.
- `chimera-w2-map` — breadth map from seed papers; nominates promote-candidates.
- `chimera-propose-links` — propose `informed_by` onto a hand-authored T/I/D node. Proposes and
  stages only; the apply is the Architect's explicit order.

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
- **The invariants in `docs/ARCHITECTURE/INVARIANTS.md` (I0.x / I1.x / I2.x) are binding and override sprint/style rules.** The rules below are the always-loaded subset; that file is the authority and is FROZEN — never restate or extend it.
- This repo has ONE user. Do not generalize.
- Skill rules override generic best practices.
- Do not invent MCP tools without a friction signal — see `chimera-dependency-veto`.
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
