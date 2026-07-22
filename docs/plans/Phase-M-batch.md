# Batch Plan: Phase M — Chimera Lite Migration

**Output location:** `docs/plans/Phase-M-batch.md`
**Audit reference:** `docs/audits/M.0.md` (date: 2026-06-28)
**Phase doc:** `docs/phases/phase-M.md` (sparse manifest — distinct from this batch plan)
**Driving frictions:** self-built agent-loop maintenance liability; astrocyte burden;
text-DSL tool parsing (1485 lines) → native MCP. Per `../project_chimera/docs/audits/chimera-to-code-feasibility.md`.

This document is a single unit. User approves the whole sequence or rejects the whole
sequence. After approval, hand off to `chimera-code-taste` batch_execution mode.

---

## Pre-planning decisions (confirmed with user, 2026-06-28)

| # | Decision | Effect on plan |
|---|---|---|
| 1 | **Package layout: flat + rewrite imports** (NOT vendor the `src/crucible` tree) | The 74 `src.*` imports get rewritten to flat package paths. No `src/` tree is recreated. |
| 2 | **Prepend sprint M.0.5** (port `config`/`schemas`/`naming`/`platform`) | New foundation sprint before M.1/M.2; unblocks the "parallel" assumption (audit cross-finding #2). |
| 3 | **BB persona: port from `~/.chimera/skills/<unknown>.json`** (the "BB tone" skill) | M.3 first *locates* the tone JSON, then ports it into a `chimera-bb-persona` skill. Resolves the undefined-"warmth" ambiguity from the source, not from invention. |

### Planner reconciliation (scope-note tension — read before approving)
Your scope template put "rewrite 74 imports" in **M.4**. That is infeasible with the
sealing conditions: HSC-1 (M.1) and HSC-2 (M.2) require **live** MCP tool calls, so the
domain code must import cleanly *before* M.4. Flat imports cannot be deferred to a
cleanup sprint. **Resolution:** the import rewrite is **distributed** — M.0.5 rewrites
the core modules' own imports; M.1 rewrites the vault-path files; M.2a/M.2b rewrite the
papers-path files (as an intrinsic part of wiring each subsystem). **M.4 becomes a
verify-zero-`src.*`-remain + delete-sentinels + dead-ref sweep** over any straggler files
not on an HSC critical path (e.g. `optics_service.py`, `cli_presenter.py`). This preserves
"all functionality working before M.4 starts." Evidence: `M.0.md` Q6 (74 imports/24 files),
sealing conditions `phase-M.md:50-64`.

---

## Sprint Sequence

```
M.0.5 (foundation: core port + flat imports)
        ├─────────────► M.1  (vault MCP wiring) ───────────┐
        └─────────────► M.2a (arxiv + TaskService + lock) ─┤
                                 └► M.2b (daily pipeline) ──┤
M.3 (BB persona skill) ── independent, parallel-eligible ──┼─► M.4 (cleanup/verify) ─► M.5 (E2E seal)
```

- M.0.5 precedes all wiring. M.1 ∥ M.2a (independent after M.0.5). M.2a → M.2b.
- M.3 is independent of all code sprints (skill file only) — may run any time.
- M.4 after M.1 + M.2b. M.5 after M.4 + M.3.
- **Split applied (process step 3):** phase-doc M.2 exceeds ≤3 files / ≤50 lines →
  split into **M.2a** (long-running task plumbing + concurrency lock) and **M.2b**
  (full filter/ingest/notify pipeline + its heavy deps). Isolates the MinerU
  dependency-veto decision into M.2b.

---

## Sprint M.0.5: Domain foundation port (core modules + flat imports)

**Friction reference:** migration enablement (audit cross-finding #2 — shared blocker of M.1+M.2)

**Predecessor assumptions:**
- None — this is the foundation sprint. Source of truth for ports: `archive/chimera-oligo`
  branch + `../project_chimera/crucible_core/src/crucible/core/`.

**Risk level:** 🔴 HIGH (multi-file foundation; >3 files — requires per-sprint approval). Cognitively mechanical (pure port, no logic).

### Objective
Port the four missing core modules into a flat domain package and fix their internal
imports so the copied domain layer is importable.

### Design notes (audit-derived)
- Missing modules block everything: `config`, `naming`, `schemas`, `platform` — `M.0.md` Q2/Q3, cross-ref "ChimeraConfig is the lynchpin".
- `ToolOutput`/`Artifact` (the lone `src.oligo` coupling) fold into the flat `schemas` module — porting them here removes the only oligo import at the foundation. Audit ref: `M.0.md` Q7 (`daily_chimera_service.py:15`).
- **Flat-layout target (Decision 1):** establish a single domain package both servers share. Recommended: `mcp-servers/chimera_domain/` (or reuse the existing `chimera-papers/` package root) holding `core/{config,schemas,naming,platform}.py`; rewrite `src.crucible.core.X` → `core.X`. The "where shared core lives + how `chimera-vault` reaches it (sys.path vs shared package)" is the one execution design call this sprint must settle. Audit ref: `M.0.md` cross-ref "package-layout decision".
- `config.py` reads TOML → use stdlib `tomllib` (3.11+), no `tomli` dep.

### Task scope
1. Port `config.py` (`ChimeraConfig`, `get_config`, `require_path`, `PaperMinerSettings`) — audit Q2/Q4 (~from project_chimera core).
2. Port `schemas.py` incl. `ToolOutput`, `Artifact`, `Paper`, `PaperAnalysisResult`, `VerdictDecision`, `TaskEvent`, `TaskEventType`, `BatchFilterStats`, etc. — audit Q4/Q6/Q7.
3. Port `naming.py` (`extract_short_moniker_from_note_filename`, `sanitize_filename`, `compute_fancy_basename`, `expected_stem`) — audit Q1/Q6.
4. Port `platform.py` (`get_chimera_root`) — audit cross-ref (`task_service.py:57`).
5. Fix the four ported modules' own internal imports to flat. Do NOT touch consumer files yet (M.1/M.2 own those).

### Acceptance
- `python -c "import core.config, core.schemas, core.naming, core.platform"` succeeds from the domain package root.
- `grep -rn "from src\.oligo" core/` → 0 hits (ToolOutput/Artifact now local).
- No logic diff vs project_chimera originals (port = copy + import-path only) — spot-verify by `git diff`-style comparison against archive source.

### Red lines
- ❌ No logic changes — file copy + import-path fix only (phase constraint).
- ❌ No new dependencies beyond stdlib + already-declared (`pydantic`, `pyyaml`).
- ❌ Do not rewrite consumer-file imports (that is M.1/M.2 scope; avoid double-handling).
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera_domain/core/` (or agreed shared package)
- Tests: `tests/test_core_imports.py` (import smoke)
- Docs: deferred to M.5, updated together

---

## Sprint M.1: Vault MCP wiring

**Friction reference:** sealing condition 1 (`phase-M.md:50-52`)

**Predecessor assumptions:**
- M.0.5 done: `core.config.ChimeraConfig`/`get_config`, `core.naming` importable. Re-plan trigger if the shared-package location differs from M.0.5's choice.

**Risk level:** 🔴 HIGH (creates 2 tool modules + wires server + rewrites vault-file imports; >3 files — per-sprint approval).

### Objective
Connect the five `chimera-vault` MCP tools to the real `VaultReadAdapter` + ripgrep logic
and delete their NOT-WIRED sentinels.

### Design notes (audit-derived)
- Adapter is complete and needs only a `ChimeraConfig`: `vault_read_adapter.py:137`; methods `read_file@203`, `search_notes@397`, `search_by_attribute@404`, `query_graph@546` — `M.0.md` Q1.
- Tool wrappers were never copied — author `vault_tools.py` + `vault_query.py` fresh with flat imports: `M.0.md` Q2 (ABSENT).
- `vault_query` shells to ripgrep + uses `get_config().require_path("vault_root")` — external `rg` on PATH; `CHIMERA_VAULT_ROOT` already wired (`.mcp.json`). Audit Q2/Q8.
- Server bodies swap lazy `_NOT_WIRED` stubs for real imports — `server.py:48,64,78,120`.

### Task scope
1. Author `vault_tools.py` (flat): `search_vault`, `search_vault_attribute`, `read_vault_file`, `obsidian_graph_query` → adapter; return plain `str` (MCP has no `ToolOutput` channel — flatten `.text`). (~120 lines) — audit Q1/Q2.
2. Author `vault_query.py` (flat, ripgrep) (~70 lines) — audit Q2.
3. Construct + bind a process-wide `VaultReadAdapter(get_config())` in the vault server; replace 5 lazy stubs with real calls (`chimera-vault/server.py`).
4. Rewrite imports in `vault_read_adapter.py` (`src.crucible.core.*` → flat) — audit Q6.

### Acceptance (HSC — sealing condition 1)
- Live Claude Code session: `vault_query(type="knowledge")` via MCP returns real vault notes with titles + paths in **< 2s**.
- `read_vault_file` returns full note content for a known path.
- `grep -rn "NOT.WIRED" chimera-vault/` → 0.

### Red lines
- ❌ MCP server stays a thin adapter < 200 lines (phase red line `phase-M.md:39`).
- ❌ No domain-logic rewrite in `VaultReadAdapter` — import-path fixes only (`phase-M.md:41`).
- ❌ No `ToolOutput`/`Artifact`/SSE types leaking into the MCP return contract (MCP returns text/structured content, not oligo schemas).
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera-vault/{server.py,vault_tools.py,vault_query.py}`, `…/ports/vault/vault_read_adapter.py`
- Tests: `tests/test_vault_tools.py`
- Docs: deferred to M.5

---

## Sprint M.2a: arXiv miner + TaskService + server concurrency lock

**Friction reference:** sealing condition 2 (partial — long-running task plumbing) (`phase-M.md:53-56`)

**Predecessor assumptions:**
- M.0.5 done: `core.schemas` (TaskEvent/TaskEventType), `core.platform.get_chimera_root` importable (`task_service.py:21,57`).

**Risk level:** 🔴 HIGH (authors `miner_tools.py` + net-new lock + rewrites task plumbing imports — per-sprint approval).

### Objective
Wire `arxiv_miner` + `check_task_status` to `TaskService` (poll model) and add the
net-new server-held concurrency lock.

### Design notes (audit-derived)
- `miner_tools.py` absent — author fresh: `M.0.md` Q3.
- `task_id = uuid4()[:8]` (8 hex) — poll contract already correct in `server.py`; preserve it. `M.0.md` Q4 (`task_service.py:265`).
- **RED-LINE EXCEPTION (audit cross-finding #4):** no concurrent-pipeline guard exists today (`phase-M.md:92-96`). The server must hold an `asyncio.Lock` (or file lock) rejecting a second `daily_paper_pipeline`/`arxiv_miner` start while one runs. **This is the one place the "thin adapter, minimal logic" rule is intentionally exceeded** (~20 net-new lines). Declared, not incidental.
- Poll model, NOT in-request await (`phase-M.md:74-78`).

### Task scope
1. Author `miner_tools.py` `arxiv_miner` + `check_task_status` (flat imports) (~60 lines) — audit Q3.
2. Add server-level concurrency lock in `chimera-papers/server.py` (~20 lines, net-new) — cross-finding #4 / `phase-M.md:92-96`.
3. Rewrite imports in `task_service.py`, `fetch_arxiv_workflow.py` (`src.crucible.*` → flat) — audit Q6.
4. Wire the two server tool bodies; remove their `_NOT_WIRED` stubs.

### Acceptance (HSC — sealing condition 2, part A)
- Live: `arxiv_miner(query=…)` returns an 8-hex `task_id` immediately; `check_task_status(task_id)` polls and eventually returns real fetched-paper info.
- Starting a second long-running tool while one runs returns a clear "already running" rejection (lock proven by a 2-call test).
- `grep -rn "NOT.WIRED" chimera-papers/server.py` for these two tools → 0.

### Red lines
- ❌ No in-request await / suspend-resume — poll model only (`phase-M.md:74-78`).
- ❌ Lock lives in the **server**, not re-introduced into a deleted agent loop.
- ❌ Adapter stays thin except the declared ~20-line lock (the sanctioned exception).
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera-papers/{server.py,miner_tools.py,task_service.py,fetch_arxiv_workflow.py}`
- Tests: `tests/test_miner_tools.py`, `tests/test_server_lock.py`
- Docs: deferred to M.5

---

## Sprint M.2b: Daily paper pipeline (filter / ingest / notify)

**Friction reference:** sealing condition 2 (full pipeline) (`phase-M.md:53-56`)

**Predecessor assumptions:**
- M.2a done: `miner_tools.py` exists, `TaskService` imports flat, server lock present.
- Re-plan trigger: if MinerU is vetoed (see deps), the ingest stage must become lazy/optional and the HSC adjusted to "titles from filter stage."

**Risk level:** 🔴 HIGH (wires the full pipeline + multiple heavy deps + many file imports — per-sprint approval).

### Design notes (audit-derived)
- `daily_paper_pipeline` chains filter → ingest → notify across many files: `daily_chimera_service.py`, `batch_filter_workflow.py`, `filter_service.py`, `ports/ingest/*`, `ports/notify/*`, `ports/prompts/*`, `ports/papers/*` — audit Q6 import list.
- The lone `src.oligo` coupling is resolved at M.0.5; confirm `daily_chimera_service.py:189` now uses local `ToolOutput` — audit Q7.
- **Dependency additions (cross-finding #5) — each subject to `chimera-dependency-veto`:**
  - `jinja2` (PromptManager) — likely ACCEPT (small, already implied by domain).
  - arXiv client used by `arxiv_fetch.py` — ACCEPT (core capability).
  - OpenAI-compatible LLM client deps (`openai` or httpx-only) — verify which; prefer httpx (already declared) if possible.
  - **`mineru` / paper2md — VETO FLASHPOINT** (heavy ML stack). Recommendation: make ingest a **lazy import** so the pipeline degrades gracefully (`MineruNotInstalledError` already exists, `single_paper_pipeline_service.py:12`) and the M.2b HSC can pass on filter-stage titles without the full ML install. Decision required at execution.
  - `telegram` notifier — httpx-based; `skip_telegram=True` path already exists (`server.py` arg) so the smoke can bypass it.

### Task scope
1. Rewrite imports (`src.crucible.*` → flat) across pipeline files: `daily_chimera_service.py`, `batch_filter_workflow.py`, `filter_service.py`, `ports/ingest/{mineru_pipeline,paper2md}.py`, `ports/notify/telegram_notifier.py`, `ports/prompts/jinja_prompt_manager.py`, `ports/papers/*`, `ports/arxiv/arxiv_fetch.py` — audit Q6 (the bulk of the 24 files).
2. Wire `daily_paper_pipeline` server body (poll model, behind the M.2a lock); remove `_NOT_WIRED`.
3. Extend `pyproject.toml` deps with veto-justified additions; gate `mineru` as lazy/optional — cross-finding #5.

### Acceptance (HSC — sealing condition 2, full)
- Live: `daily_paper_pipeline(skip_telegram=True)` → `task_id` → `check_task_status` eventually returns **real paper titles** from a completed run (minutes is acceptable).
- `uv run python -c "import daily_chimera_service"` (and the pipeline modules) succeeds.
- `grep -rn "from src\." chimera-papers/` over pipeline-path files → 0.

### Red lines
- ❌ No domain-logic rewrite — import-path + lazy-import guard only (`phase-M.md:41`).
- ❌ Each new dependency must carry a one-line veto justification (`chimera-dependency-veto`).
- ❌ Telegram/MinerU must not be hard-required for the smoke path.
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera-papers/` (pipeline files), `pyproject.toml`
- Tests: `tests/test_daily_pipeline_imports.py` (+ live smoke in M.5)
- Docs: deferred to M.5

---

## Sprint M.3: BB persona skill

**Friction reference:** sealing condition 3 (`phase-M.md:57-59`); Decision 3

**Predecessor assumptions:**
- None — skill file only, independent of all code sprints. Parallel-eligible from batch start.

**Risk level:** 🟡 MED (skill authoring + external-source locate + voice verification; no code).

### Objective
Locate the user's "BB tone" skill JSON in `~/.chimera/skills/` and port it into an
always-on `chimera-bb-persona` skill carrying the four traits.

### Design notes (audit-derived)
- BB voice text is **not in repo or archive** (templates only) — must come from `~/.chimera/skills/*.json` — `M.0.md` Q5 + cross-finding #3.
- Trait spec is authoritative: `toxicity + warmth + anti-hype + forensic` (`phase-M.md:57-58`). The source JSON resolves the undefined "warmth" vector (do NOT invent it).
- Skill ONLY — no system-prompt hack, no CLAUDE.md persona injection (`phase-M.md:45,80-90`).
- Structural precedent: "Reviewer Zero" (`archive:…/prompt_archive/review_zero_v3.md`).

### Task scope
1. Locate the tone JSON: enumerate `~/.chimera/skills/*.json`, identify the BB-tone one by content (filename unknown). If absent, halt and report (do not invent voice).
2. Author `.claude/chimera-bb-persona/SKILL.md` — always-on restyle of final output; encode the 4 traits from the located source.
3. Capture the source's "warmth" expression verbatim-in-spirit so it is grounded, not guessed.

### Acceptance (HSC — sealing condition 3)
- Read 3 research-conversation responses; each carries BB voice (toxicity + warmth + anti-hype + forensic) — confirmed by user.
- Skill triggers always-on (description verified against skill-loading).

### Red lines
- ❌ Persona via skill ONLY — no system prompt / CLAUDE.md persona injection (`phase-M.md:45`).
- ❌ No invented "warmth" — must derive from the located source; halt if source missing.
- ❌ No "theater"/hidden-reasoning re-introduction — reasoning stays transparent (`phase-M.md:87-90`).
- ❌ No opportunistic refactoring.

### Output locations
- Code: `.claude/chimera-bb-persona/SKILL.md`
- Tests: manual voice read (3 responses)
- Docs: this skill is self-documenting

---

## Sprint M.4: Cleanup + independence verification

**Friction reference:** sealing conditions 4 & 5 (`phase-M.md:60-64`)

**Predecessor assumptions:**
- M.1 + M.2b done: all HSC-critical functionality working. M.4 touches only stragglers + sentinels (no feature work). Re-plan trigger if any tool still returns NOT-WIRED at M.4 start.

**Risk level:** 🟡 MED (mechanical import sweep + deletions; grep-verifiable).

### Objective
Rewrite any remaining `src.*` import stragglers, delete all NOT-WIRED sentinels, and
remove dead oligo references so the independence grep is clean.

### Design notes (audit-derived)
- Distributed-rewrite remainder: files NOT on an HSC critical path still hold `src.crucible.*` imports — `optics_service.py`, `optics_lens_registry.py`, `single_paper_pipeline_service.py`, `cli_presenter.py` — audit Q6.
- Sentinel removal target: sealing condition 4 (`phase-M.md:60-61`).
- Independence target: zero `src.oligo` / `oligo.core` / `astrocyte` — sealing condition 5 (`phase-M.md:62-64`). The server.py docstring oligo mentions (audit Q7) are also cleaned here.

### Task scope
1. Rewrite straggler imports to flat across remaining domain files — audit Q6.
2. Delete every `_NOT_WIRED` constant + lazy-import fallback now that bodies are real.
3. Remove dead oligo references/comments (incl. server.py docstrings) — audit Q7.

### Acceptance (HSC — sealing conditions 4 & 5)
- `grep -rn "NOT.WIRED\|NotImplementedError" mcp-servers/` → **0**.
- `grep -rn "from src\.oligo\|import.*oligo\.core\|astrocyte" mcp-servers/` → **0**.
- `grep -rn "from src\." mcp-servers/` → **0** (flat rewrite complete).
- Both servers still start; tool list unchanged.

### Red lines
- ❌ Cleanup only — no new functionality (all working before M.4).
- ❌ No behavioral change to any wired tool.
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/` (straggler files, both servers)
- Tests: existing tests stay green
- Docs: deferred to M.5

---

## Sprint M.5: E2E smoke + phase seal

**Friction reference:** all sealing conditions (`phase-M.md:50-64`)

**Predecessor assumptions:**
- M.1, M.2b, M.3, M.4 done. Full stack wired, clean, BB voice live.

**Risk level:** 🟢 LOW (verify-only; produces a checklist doc, no code).

### Objective
Run the full research workflow live on Claude Code and document the E2E smoke result.

### Design notes (audit-derived)
- Full workflow: Fetch papers (papers MCP) → Deep Read → vault query (vault MCP) → BB analysis (skill) — `phase-M.md:27`.
- Prereqs must be present: `rg`, LLM key, vault/papers roots, (optional) MinerU/Telegram — `M.0.md` Q8.

### Task scope
1. Execute the 4-stage workflow in a live Claude Code session.
2. Record pass/fail per sealing condition in `docs/audits/M.5-e2e-smoke.md`.
3. Confirm zero oligo/astrocyte dependency in the running system (sealing condition 5 re-check).

### Acceptance (all sealing conditions)
- Sealing 1–5 each marked PASS with evidence in the smoke doc.
- `chimera-sprint-discipline` phase_review can seal Phase M from this evidence.

### Red lines
- ❌ Verify-only — no code changes (incidents → separate hotfix per incident protocol).
- ❌ No automated E2E harness introduced (`chimera-dependency-veto`; single-user manual smoke is sufficient — precedent FC.6).
- ❌ No opportunistic refactoring.

### Output locations
- Docs: `docs/audits/M.5-e2e-smoke.md`

---

## Phase-wide Red Lines

Apply across ALL sprints; violation in any sprint halts the batch (`phase-M.md:32-46`):

- ❌ NO oligo agent-loop code (`ChimeraAgent`, `_run_theater`, `_step_*`).
- ❌ NO astrocyte / Tauri / Svelte code.
- ❌ NO text-DSL tool parsing (`<tool_call>`, `<CMD:>`, `parse_args_with_repair`).
- ❌ NO SSE protocol (`bb-stream-chunk`, `bb-phase-transition`, `sse_event`).
- ❌ NO `prompt_composer` / late persona bind / two-model split.
- ❌ MCP servers stay thin adapters < 200 lines — **except** M.2a's declared ~20-line concurrency lock (the one sanctioned exception, cross-finding #4).
- ❌ Domain service code: import-path fixes only, NOT logic rewrites (`phase-M.md:41`).
- ❌ TaskService poll model, NOT in-request await.
- ❌ BB persona via skill ONLY.
- ❌ Every dependency addition carries a `chimera-dependency-veto` justification (cross-finding #5).

---

## Hard Sealing Conditions (carried from phase doc, `phase-M.md:50-64`)

Must Pass at phase_review for sealing:

1. **Vault MCP** — `vault_query(type="knowledge")` via MCP returns real notes (titles + paths) in < 2s. Verified live (M.1 HSC).
2. **Papers MCP** — `daily_paper_pipeline` → `task_id` → poll `check_task_status` → real paper titles from a completed run. Verified live, minutes acceptable (M.2b HSC).
3. **BB voice** — final research output carries BB persona (toxicity + warmth + anti-hype + forensic). Verified by reading 3 responses (M.3 HSC).
4. **Zero sentinel** — `grep "NOT.WIRED\|NotImplementedError"` across `mcp-servers/` → 0 (M.4 HSC).
5. **Independence** — zero imports from `oligo.core`/`oligo.api`/`astrocyte`/`src.oligo`; may import the reused domain layer (M.0.5 establishes, M.4 verifies).

---

## Approval

User approves whole sequence or rejects whole sequence.

Upon approval, hand off to `chimera-code-taste` with:
> "Execute batch for Phase M per `docs/plans/Phase-M-batch.md`."

Note: M.0.5, M.1, M.2a, M.2b are 🔴 HIGH → each requires explicit per-sprint approval
before execution even after batch approval. M.3/M.4 (🟡) self-execute and halt on red
line. M.5 (🟢) self-executes.

---

*Generated by chimera-sprint-discipline batch_planning mode.*
