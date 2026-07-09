# Chimera Roadmap

Personal research OS for one user. Not a framework. Not SaaS.

> **Last sealed:** Phase N — Lens Skills + JIT Deep Recall — **SEALED / TRUNCATED 2026-07-09** (N.A Lens Skills sealed 2026-07-06; N.B JIT Deep Recall **cancelled** pre-execution). Verdict: `docs/sprints/phase-N/phase-review.md`. (Phase O — Exocortex Write Surface — sealed 2026-07-08.)
> **Active:** none. Next phase pending Architect authorship — the two open blockers are the **agentic defect** (`friction-260709-01`: vault absent from the loop) and **filling the vault with ARA-styled structured nodes** (`friction-260708-01`). Advanced retrieval stays retired until both are addressed.

---

## Sealed Phases

### Phase N.A — Lens Skills ✅ Sealed 2026-07-06

**First phase post-migration.** Crystallized the 6 research-analysis lenses (project_chimera's
`OpticsService` prompts) as Claude Code **skills** + the always-on `chimera-academic-observe`.
Pure prompt skills — zero new MCP tools, zero server changes. See `docs/phases/phase-N.A.md`,
`docs/plans/Phase-N.A-batch.md`, `docs/sprints/phase-N.A/*.md`, `docs/audits/N.A.0.md`.

| Sprint | Goal | Status |
|---|---|---|
| N.A.0 | Audit: reconcile ported lens configs + `~/.chimera` skills vs the 6 targets | Sealed |
| N.A.1 | Forensic Leakage + Thermodynamic Decay (+ `_shared/falsifiability.md`) | Sealed |
| N.A.2 | State Collision StressTest + Agentic Illusion Stripper | Sealed |
| N.A.3 | Math Decoration Validator + Ontological Map Scanner | Sealed |
| N.A.4 | chimera-academic-observe (always-on) | Sealed |

**HSC result (all green):** (1) auto-selection ✅ — all 6 lenses carry paper-type `description:`
triggers (the skill registry auto-loaded each); (2) academic taste ✅ — all 6 reference
`_shared/falsifiability.md` and mandate mechanism + evidence + falsifiability; (3) proactive
observation ✅ — academic-observe surfaces vault connections via `obsidian_graph_query` /
`vault_query`, capability live-verified at seal (200-node graph / 99 knowledge nodes; a relevant
node surfaced for a decay probe unprompted).

**Decisions realized:** Ontological Map absorbed `survey_consensus` + `survey_gaps` (6 lenses, not
8); the `../_shared/falsifiability.md` reference pattern proved viable (no inline fallback needed).

**Red lines:** all held. The seal red-line scan caught + fixed a stray Chinese clause in 6 lens
files (`d8d9cea`) — the Pure-English red line is now clean.

**Driving friction:** friction-chimera-lite-01 (phase-declared; no `docs/logs/` entry) — resolved
by this phase; the lens skills now exist natively.

**Commits:** `774dfce` (N.A.1), `6ee3ea6` (N.A.2), `ca9bb6b` (N.A.3), `35c999e` (N.A.4),
`d8d9cea` (Pure-English fix).
**Accepted partials:** `ACCEPTED_PARTIALS.md` Phase N.A section (`~/.chimera` divergence check deferred).
**Sealed:** 2026-07-06

---

### Phase M — Chimera Lite Migration ✅ Sealed (full seal) 2026-07-03

**First phase of the chimera-lite repo.** Migrated project_chimera (oligo agent +
Astrocyte) onto Claude Code + MCP. See `docs/phases/phase-M.md`, `docs/plans/Phase-M-batch.md`,
`docs/sprints/phase-M/*.md`, `docs/audits/M.0.md`.

| Sprint | Goal | Status |
|---|---|---|
| M.0.5 | Port core modules (config/schemas/naming/platform) flat, prune oligo | Sealed |
| M.1 | Vault MCP wiring (5 tools) | Sealed |
| M.2a | arxiv_miner + check_task_status + server concurrency lock | Sealed |
| M.2b | daily_paper_pipeline + CUDA MinerU stack | Sealed |
| M.3 | BB persona skill | Sealed |
| M.4 | Cleanup + independence (src.crucible/src.oligo/astrocyte = 0) | Sealed |
| M.5 | E2E smoke (user-run) | Sealed |

**HSC result (M.5 live):** all four green — Test 1 (vault) ✅, Test 2 (daily pipeline) ✅,
Test 3 (BB voice) ✅, Test 4 (independence) ✅. Test 2 confirmed end-to-end on 2026-07-03
(`task_id 436be5bd`: `new_pdfs=3 ingested=3 convert_failed=0 errors=0`, real titles) after
the miner-pipeline incident chain closed.

**Seal history:** functional seal 2026-06-30 (3/4 HSC, user override — Test 2's runtime
defects tracked as incidents, not a migration gap) → **full seal 2026-07-03** once the
final incident (headless-spawn hang) was fixed and Test 2 ran clean.

**Accepted partials:** `ACCEPTED_PARTIALS.md` Phase M section.
**Incidents (Test-2 chain, all fixed):** `2026-06-30-missing-prompts-tree.md`,
`2026-06-30-mineru-not-on-path.md`, `2026-07-01-mineru-capture-deadlock.md`,
`2026-07-01-convert-swallow-as-skip.md`, `2026-07-02-mineru-hang-in-mcp-server.md`.

### Phase I — Foundation
**Goal:** System never crashes silently. Configuration has single source of truth. Logs are greppable.

| Milestone | Deliverable | Commit |
|---|---|---|
| M1 Error Handling | LLM timeout protection (`generate_raw_text` + outer 120s watchdog), per-tool timeout, `web_search` async via `to_thread`, `BaseException` black hole eliminated, FastAPI streaming exception capture | `{commit}` |
| M2 Configuration Unification | `platform.py` / `platform.rs` cross-language path abstraction, `~/.chimera/config.toml` as single truth, `config.example.toml`, multi-LLM slot config (working/wash/router) | `{commit}` |
| M3 Observability Baseline | Uniform Python log format `%(asctime)s \| %(levelname)-8s \| %(name)s \| %(message)s`, bracket-prefix convention `[Oligo]/[Router]/[Tool]/[Wash]/[Final]/[Vault]/[LLM]/[Config]`, SSE event protocol (`bb-stream-chunk`, `bb-sys-event`, `bb-stream-done`) | `{commit}` |

**Accepted partials:** front-end Provider deletion UI dropped — TOML is authoritative.
**Sealed:** 2026-04-XX.

---

### Phase II — Cognition
**Goal:** System knows what to do with tools, has skills, and we know if any of it is actually used.

| Milestone | Deliverable | Commit |
|---|---|---|
| II.A Skill Ecosystem | Six skill JSONs in `~/.chimera/skills/`, `SkillStatsService` writing `~/.chimera/skill_stats.json`, frontend skill card grid with usage / success-rate / avg-tokens | `{commit}` |
| II.B Tool Registry | `search_vault`, `search_vault_attribute`, `obsidian_graph_query`, `web_search`, `arxiv_miner`, `check_task_status`, `daily_paper_pipeline` registered. Gravedigger deferred to Phase IV. | `{commit}` |
| II.C Wash Refinement | Intent-driven `_wash_tool_result` consuming context window, `_BYPASS_WASH_TOOLS` / `_FORCE_WASH_TOOLS` policy split, dual-engine (cheap wash + premium working) | `{commit}` |
| II.D Observability & Metrics | `MetricsService` with system / tool / wash dimensions, persisted to `~/.chimera/metrics.json`, frontend health panel | `{commit}` |
| II.E Dogfooding (Use Week) | Five friction entries logged. Pattern: all five point to "Astrocyte ↔ CLI workflows not bridged." | `{commit}` |

**Sealed:** 2026-05-XX.

---

### Phase III.A — Connection Convergence
**Goal:** Astrocyte becomes the trigger surface for existing CLI workflows.

| Step | Deliverable | Commit |
|---|---|---|
| Step 0: Contamination Fix (S0.1–S0.4) | `_FINAL_GUARDRAIL` block, Router CMD-syntax relaxation, tool whitelist enforcement, code-block-aware CMD regex pre-strip | `{commit}` |
| Step 1: Boundary Audit | Skill / Tool / Lens conceptual boundary documented. Decision: existing 6 "skills" are *disguised lenses*, retain as legacy markers, no refactor | `{commit}` |
| Step 2: Event-Driven Task Progress | `TaskService.event_queue` + `/v1/tasks/stream` SSE channel, Rust `task_stream.rs` with exponential reconnect, Svelte `ActiveTaskPanel` with 0.1s tabular-num timer using local `Date.now()` basis | `{commit}` |
| Step 3: Daily Pipeline Tool | `daily_paper_pipeline(skip_telegram?)` registered, 4-stage progress emission via `start_stage`, idempotent via `audit_log.csv` | `{commit}` |

**Sealed:** 2026-05-XX.

---

### Phase III.B & C — Middleware & Harness (Functional Seal)
**Goal:** Prompt assembly stops being string concatenation roulette. Tool calling stops being regex prayer.

| Sub-phase | Deliverable | Commit |
|---|---|---|
| III.B.1 Prompt Middleware (MW.0–4) | `PromptComposer` with 9 registered components, stable/dynamic prefix split via `cacheable` flag, `TextSanitizer` three-layer strip (reasoning / tool-syntax-in-visible / message-history-sanitization), `docs/ARCHITECTURE/PROMPT_MIDDLEWARE.md` | `{commit}` |
| III.B.2 Tool Protocol Lite (TP.0–5) | `ToolRegistry` with `ToolSpec` (concurrency_safe, long_running, args_schema, examples), XML `<tool_call>` parsing alongside legacy `<CMD:...>`, 5-rule argument-repair (code fence / quote style / trailing comma / brace wrap / smart quotes), `partition_tool_calls` by concurrency safety, `docs/ARCHITECTURE/TOOL_PROTOCOL.md` | `{commit}` |
| III.B.3 Intent Recognition (IR.0–5) | Tri-tier tool list rendering (verbose/compact/micro under length budget), `<tool_result status=...>` typed wrapper with reflection hints (failure-only), `EMPTY_RESULT` fallback suggestion, `bb-tool-start`/`bb-tool-done` per-call telemetry, `ActiveToolStrip` 0.1s tool-level timer, `xml_structured` renderer reserved for Phase IV PPR injection, `docs/ARCHITECTURE/INTENT_AND_DEGRADATION.md` | `{commit}` |
| III.B.4 Context-Folding | **Deferred indefinitely.** Friction log shows no demand. May surface in Phase IV trajectory reasoning. |
| III.B.5 Memory CRUD | **Merged into Phase IV.** Will design alongside Exocortex K/T/I/D ontology. |
| III.B.6 UI Visualization | **Folded into Phase III.C.** Attachment rendering and message ops handle the visualization needs. |
| III.C Structured Final Contract (FC.0–6) | `ToolOutput`/`Artifact` for vault tools → `bb-message-artifacts` SSE → Tauri persistence → Svelte chip UI + `open_vault_note`; Router persona-invariance tests; message delete verified. Resolves E3/E4. `docs/ARCHITECTURE/FINAL_CONTRACT.md` | `421a526` |

**Functional seal** rather than full administrative seal — see `ACCEPTED_PARTIALS.md` for trade-offs and `TECHNICAL_DEBT.md` for tracked items.
**Sealed:** 2026-05-25.

---

---

### Phase EXT — Prompt Externalization & Router Rewrite

**Goal:** Upgrade Oligo prompt architecture from inline Python constants to external Jinja2 templates; give Router intent-classification capability.

| Sprint | Deliverable | Commit |
|---|---|---|
| EXT.0 | Inline prompt audit + PromptComposer render chain map | — |
| EXT.1 | All inline prompts → .md/.md.j2, behaviour unchanged | `10a282a` |
| EXT.2a–2d | 4000-char cap removed; router_intro.md.j2 verified; router_continuation.md.j2 + turn-based system prompt switch; `<thinking>` strip | `d458009`, `b757ced` |
| EXT.3 | ToolSpec enriched: user_aliases / examples / common_mistakes | `a79fa0f` |
| EXT.4 | Agentic theater design discussion — resolved, no code needed | — |

**Sealed:** 2026-06-11 (condition 3 waived by user).

---

### Phase III.E — Oligo Orchestration Primitives

**Goal:** Upgrade Oligo from single-thread theater to multi-context orchestrator; three new primitives as Phase IV prerequisites.

| Sprint | Deliverable | Commit |
|---|---|---|
| III.E.0 | Phase audit: context accumulation points + ChimeraAgent instantiation chain | — |
| III.E.A | `fork_subagent` + `run_isolated`: isolated child agent, reuses wash/router clients, budget conservation, returns summary ≤ 4096 chars | `b40d69f` |
| III.E.C | `archive_segment` / `unarchive_segment`: tombstone replaces segment in `self.messages`, original persisted to `~/.chimera/archive_log/` | `b40d69f` |
| III.E.B | `TaskService.run_subprocess_task`: asyncio subprocess, stdout → `emit_stage_progress`, stall detection, exit≠0 → lesson via backward trace | `b40d69f` |
| — | `fork_agent` registered as tool stub (e2e wiring deferred to Phase IV) | `b40d69f` |

**HSC verification:**
- HSC 1 (downgraded): 50K-token prompt via `fork_subagent` stays out of parent messages — unit test
- HSC 2: `archive_segment` → tombstone in live context, recoverable via `unarchive_segment` — manually verified 2026-06-11
- HSC 3: `run_subprocess_task` shows live progress in `ActiveTaskPanel`, produces DEAD_END lesson on failure — manually verified 2026-06-11

**Sealed:** 2026-06-11.

---

### Phase III.F — Path Canonicalization

**Goal:** Single canonical project-root via `platform.get_project_root()`; papers land at
`<repo_root>/papers` by default, overridable via `config.toml`; closes Phase I.M2 gap.

| Sprint | Deliverable | Commit |
|---|---|---|
| F.0 | Root-anchor consumer audit: 4 conflicting definitions mapped, scripts classified | — |
| F.1 | `platform.get_project_root()` added; `config.py` `_repo_root()` eliminated; `PROJECT_ROOT` fixed (was `parents[3]` = `crucible_core/`, now `parents[4]` = repo root) | — |
| F.2 | `arxiv_fetch._load_seen_ids` + `daily_chimera_service` fallbacks routed through `papers_root`; `config.example.toml` `[paper_miner]` section added | — |
| F.3 | `D:\MAS\crucible_core\papers\` → `D:\MAS\project_chimera\papers\`; stale `config.toml` subdir overrides removed | — |
| F.4 | `root_anchor_bypass` anti-pattern added to chimera-code-taste; grep verified (2 known-OK local-resource sites only); cross-device sim passed | — |

**HSC verification:**
- HSC 1: `grep parents` shows only `platform.py:27` (canonical) + `jinja_prompt_manager.py:26` (local resource, commented) — ✅
- HSC 2: `papers_root` defaults to `<repo_root>/papers`; config override removes stale hardcodes — ✅
- HSC 3: 10 files migrated; no `audit_log.csv` (no prior dedup state to preserve) — ✅
- HSC 4: `get_project_root()` CWD-independent (verified by running from `C:\`) — ✅

**Sealed:** 2026-06-12.

---

### Phase IV.A — Async Agent Core ✅ Sealed 2026-06-14

**Driving frictions resolved:** friction-260611 E1 — long-running task → Final fabricates. Root fix: AWAITING_TASK coroutine suspension; agent awaits real TaskService completion event before synthesizing.

| Sprint | One-line goal | Status |
|---|---|---|
| A.0 | Audit: theater loop control flow, implicit states, TaskService event surface, SSE protocol, sync assumptions baked in | Sealed |
| A.1 | Identity DDD (Layer 2): TurnId + explicit Conversation/Turn context objects | Sealed |
| A.2 | Phase labels + narrow result objects (RouteResult, ExecuteResult) + TerminalReason enum | Sealed |
| A.3 | Coroutine refactor: decompose `_run_theater_stream` into 5 async step methods. PURE REFACTOR — byte-identical SSE | Sealed |
| A.4 | AWAITING_TASK: long_running tools suspend via `await svc.await_completion()`; real result re-enters flow | Sealed |
| A.5 | SSE protocol: `bb-phase-transition` events for all 6 phases; backward-compat | Sealed |
| A.6 | Lifecycle integrity: post-await history correct, no subscription leak | Sealed |

**Commits:** `02ffd48` (A.1), `0490314` (A.0 state), `e561581` (A.3–A.6), `4109c78` (hotfix)
**Accepted partials:** `ACCEPTED_PARTIALS.md` IV.A section
**Sealed:** 2026-06-14

---

### Phase V.A — Exocortex Node Ontology & Research Production Line ✅ Sealed 2026-06-16

**Driving frictions resolved:** friction-260611 E1 (structured output), E3 (vault paths)

| Sprint | One-line goal | Status |
|---|---|---|
| V.A.0 | Audit: vault structure, existing node formats, gap analysis | Sealed |
| V.A.1 | K/T/I/D schema authority: render smoke + NODE_ONTOLOGY.md | Sealed |
| V.A.2a | Pipeline result enrichment: real paper titles in task result text | Sealed |
| V.A.2b | Structured artifact propagation: ToolOutput through check_task_status | Sealed |
| V.A.3 | Staging protocol: docs/staging/ lifecycle + StagingService | Sealed |
| V.A.4 | Astrocyte one-click node creation: Tauri commands + staging panel | Sealed |
| V.A.5 | vault_query tool: ripgrep frontmatter query, <2s on current vault | Sealed |
| V.A.6 | Seal: FINAL_CONTRACT + E2E smoke checklist | Sealed |

**Final contract:** `docs/FINAL_CONTRACT/V.A-final-contract.md`
**E2E smoke:** `docs/audits/V.A.6-e2e-smoke.md` (pending user execution)
**Accepted partials:** `ACCEPTED_PARTIALS.md` V.A section
**Sealed:** 2026-06-16

---

## Just Sealed

### Phase O — Exocortex Write Surface ✅ Sealed 2026-07-08

**Sealed** (`docs/sprints/phase-O/phase-review.md`): `create_node` / `link_nodes` / `apply_link_patch`
are live on chimera-vault (staging → review → apply, never auto-promote); the K/T/I/D typed-edge
vocabulary is authored in `docs/ARCHITECTURE/NODE_ONTOLOGY.md`; and the vault graph reached **20
participating nodes** (HSC 3), which unblocks Phase N.B. All 5 sprints Pass, all 3 HSC Pass, 1 Accepted
Partial (server.py 225 > 200 lines — thin-adapter spirit held).

**The write-path phase the N.B.0 audit demanded.** N.B was deferred because the vault's typed
K/T/I/D graph is empty (`docs/audits/N.B.0.md`), and the root cause is the write path: no tools
create T/I/D nodes or fill `derives_from` / `synthesizes` edges (PaperMiner only writes K Nodes).
Phase O builds that surface, then N.B resumes over a populated graph. Spec: `docs/phases/phase-O.md`.

**Driving frictions:** N.B.0 found the typed-edge graph empty; no tools create T/I/D nodes or fill
typed edges; PaperMiner writes only K Nodes, so T/I/D + edges are manual with no workflow support.

| Sprint | One-line goal | Status |
|---|---|---|
| O.0 | Audit (`docs/audits/O.0.md`) | ✅ Complete |
| O.1 | `create_node` — K/T/I/D + typed edges → staging (split O.1a NODE_ONTOLOGY authority + O.1b tool) | ✅ Complete (`dac1629`, `caccd52`) |
| O.2 | `link_nodes` + `apply_link_patch` — reviewed typed-edge links (stage-a-patch; O.2a/O.2b) | ✅ Complete (`c8a4b7f`, `d4659d9`) |
| O.3 | Obsidian-MCP dependency-veto (Option C) + HSC-3 seal seed | ✅ Complete (`5caceaa`) |

**Hard sealing conditions (all met at seal):** (1) `create_node` writes all 4 types (K/T/I/D) with
typed edges ✅; (2) `link_nodes` adds edges to existing nodes ✅; (3) the vault graph reaches ≥ 20
**participating** nodes (source ∪ target — the metric was corrected from origin-count to match N.B's
bidirectional traversal) ✅, via `scripts/seed_hsc3.py probe` = 20.

**Red lines / design:** thin adapter (tools write markdown, don't embed Obsidian); reuse the Phase
V.A K/T/I/D frontmatter schema (already defined); `create_node` returns a staging path for user
review before vault promotion (never auto-promote — CLAUDE.md). Out of scope: AI auto-linking
(Phase P+), graph visualization, bulk backfill of the ~250 existing K Nodes (user work post-O.3).

**Batch-planning precondition:** the O.0 audit artifact (`docs/audits/O.0.md`) must exist before
sprints are batch-planned — `chimera-sprint-discipline` enforces audit-before-plan.

---

## Active Phase

**None** — Phase N sealed/truncated 2026-07-09. The next phase is pending Architect authorship.

**Two named blockers** gate any resumed advanced-retrieval work:
- **Agentic defect** — the vault is absent from the agentic loop; the always-active observer never fires
  (`friction-260709-01`). The consumer retrieval was missing is a vault-grounded reading loop (Architect's
  preference: a forked subagent over the vault MCP methods).
- **ARA-styled node population** — the vault graph is wide-and-shallow; it needs deep structured nodes
  (ARA workflow-graph style, arXiv 2605.02651) before multi-hop recall has anything to traverse
  (`friction-260708-01`; Phase O's write surface is the tooling for this).

### Phase N — Lens Skills + JIT Deep Recall ⚠️✅ SEALED / TRUNCATED 2026-07-09

Verdict: `docs/sprints/phase-N/phase-review.md`.
- **N.A — Lens Skills** ✅ Sealed 2026-07-06 — 6 `chimera-lens-*` skills + `chimera-academic-observe`,
  pure prompt skills, zero MCP changes, 3 HSC met. HSC-3's proactive observer is re-opened as a *usage*
  defect (`friction-260709-01`): it passed its build test but never fires under real reading load.
- **N.B — JIT Deep Recall** ⛔ Cancelled pre-execution (never batch-planned; `deep_recall` = 0 code).
  Cause: no adequate typed edges / no path for deep recall (`docs/audits/N.B.0.md` + `N.B.0-reaudit.md`)
  and the vault absent from the loop (`friction-260709-01`). The interim disposition-A rescope was
  superseded by this cancellation. **Lesson:** retrieval is downstream of a loop that retrieves and a
  graph worth retrieving from — N.B built neither. Phase O's write surface survives its stated purpose
  (it is the tooling for ARA-node population).

<details><summary>⤵ Retired lineage — pre-truncation N.B context (kept for history; superseded by the verdict above)</summary>

### Phase N.B — JIT Deep Recall ▶ Rescoped 2026-07-09 (Architect disposition A — enhancement, not new tool)

**Rescoped 2026-07-09 (Architect disposition A).** The post-O re-audit (`docs/audits/N.B.0-reaudit.md`)
re-measured the graph: the ≥ 20-participation **count** gate is met, but the **structural depth** gate is
not — the typed graph is 5 disjoint 1-hop stars (0 shared papers, directional BFS depth 1), so a typed
multi-hop `deep_recall` has nothing to traverse. The Architect selected **Option A**: ship N.B as an
*enhancement* to the existing `obsidian_graph_query` — add `edge_types` (typed filter), `edge_from`/`hops`
provenance, and an optional `bidirectional` flag (which unlocks the one real depth-2 structure: the
`paper → thought → sibling papers` co-citation 2-hop). **No new `deep_recall` tool; `.mcp.json` stays 2.**
The rescoped mission / sprints / HSC live in `docs/audits/N.B.0-reaudit.md` §Disposition and supersede the
original spec. Deepening the graph for true typed multi-hop is **Option B / write-path work** (`friction-260708-01`,
stays OPEN; Architect-authored phasing). N.B batch-planning is now unblocked. Original deferral context retained below.

**Prior unblock note (2026-07-08, superseded by the rescope above).** Phase O built the write surface and
grew the vault to 20 participating K/T/I/D nodes — real, but a width measure; the re-audit showed it did
not deliver the depth HSC 1 assumed.

**Deferred at N.B.0 — the audit gate failed.** The phase specs `deep_recall` to BFS over typed
K/T/I/D edges, but the N.B.0 audit (`docs/audits/N.B.0.md`, `3f621a8`) found the live vault has
**zero populated typed `graph_edges`**: every block is `[]` or an unfilled `{{PLACEHOLDER}}`, the
~250+ pipeline-written knowledge nodes carry no `graph_edges` at all, and the only real cross-node
links are body prose in ~5 nodes that dead-end at ~1 hop (`_Deep_Read` nodes are PDF-only leaves).
HSC 1 (≥ 2 hop depths) and HSC 3 (multi-hop synthesis) are unreachable on today's graph — for *any*
edge type, not just typed ones. Root cause is the **write path** (`knowledge_node.j2` /
`deep_read_node.j2` emit no typed edges), not the read tool.

**Original intent (retained for when unblocked).** Add `deep_recall(query, depth=2, max_nodes=20)`
to **chimera-vault**: a thin-adapter BFS over the K/T/I/D graph from ripgrep-matched seeds,
returning a bounded structured subgraph Claude synthesizes natively. NOT a JIT agentic loop; no
vector store / embeddings. Spec: `docs/phases/phase-N.B.md`.

**Driving frictions:** `vault_query` is keyword-only (fuzzy queries like "那篇 memory 的" miss);
complex multi-hop queries need 5+ tool calls (slow + context bloat); the K/T/I/D typed edges
(`derives_from` / `synthesizes` / `contradicts`) go untraversed.

| Sprint | Rescoped goal (disposition A) | Status |
|---|---|---|
| N.B.0 | Audit + post-O re-audit | ✅ Complete — count gate met, depth gate not (`docs/audits/N.B.0-reaudit.md`) |
| N.B.1 | Add `edge_types` / `edge_from`+`hops` provenance / `bidirectional` params to **`obsidian_graph_query`** (no new tool; thin adapter) | ▶ Ready to batch-plan (rescoped 2026-07-09) |
| N.B.2 | Verify: paper-seeded, typed-filtered, bidirectional query → co-citation subgraph with provenance ≤ `max_nodes`, synthesized in one call | ▶ Ready to batch-plan (rescoped 2026-07-09) |

**Hard sealing conditions (rescoped 2026-07-09 — original "≥ 2 typed hop depths" withdrawn as
structurally unreachable per RE-Q4):** (1) `obsidian_graph_query` accepts `edge_types` and returns per-row
`edge_from` + `hops`, verified live; (2) opt-in `bidirectional` surfaces the `paper → thought → sibling
papers` co-citation 2-hop, bounded ≤ `max_nodes`; (3) Claude synthesizes a multi-hop answer from the single
enhanced call, no additional vault calls. Full text: `docs/audits/N.B.0-reaudit.md` §Disposition.

**Unblock condition:** ≥ 20 live nodes carry non-empty typed `graph_edges` pointing to other
knowledge nodes (the N.B.0 gate threshold). Reaching it is **write-path work**, now scoped as the
active **Phase O — Exocortex Write Surface** (`docs/phases/phase-O.md`): tools to create T/I/D nodes
and fill typed edges. N.B resumes once Phase O's HSC 3 confirms ≥ 20 nodes with typed edges; the
N.B.1/N.B.2 disposition (typed-edge BFS as written vs. a rescope to body-wikilink recall) is
re-decided then. Batch-planning of N.B is **held** until then.

</details>

---

## Queued

### Phase V — Exocortex & Memory
- K/T/I/D node ontology (Knowledge / Thought / Insight / Decision)
- PaperMiner → Knowledge Node automation (via Lens output → vault note write)
- Shallow PPR retrieval with pruning + fanout activation (star-expansion for hyperedges, no theoretical purity tax)
- Memory CRUD operators (entity + attribute as RDF triple, LLM-as-judge for conflict resolution)
- Gravedigger (OpenReview-Miner with reuse of `FilterService` + `VaultNoteWriter` + `PaperArchiveAdapter`)
- Trajectory reasoning emerges from PPR-tool multi-turn ReAct (no separate infrastructure)

### Phase IV — Horizon (speculative)
- Inspiration mechanics (nightly random walk over graph)
- External orchestration (Claude Code as long-task tool, MLLM image gen for slides)
- Self-evolving agent (APO via human-in-the-loop, not full RLAIF)

---

## Status Glossary

- **Sealed:** Phase complete, friction resolved, accepted partials documented.
- **Functional seal:** Phase deliverables work, but some review-time partials remain tracked.
- **Active:** Currently in execution.
- **Queued:** Planned but not started. Scope may shift based on friction logs.
- **Deferred:** Originally planned, now postponed indefinitely. Re-evaluate when triggered by friction.

## Version

This roadmap is updated only at sprint review seal events, by `chimera-sprint-discipline` skill in review mode, with proposed diffs presented for user confirmation.
