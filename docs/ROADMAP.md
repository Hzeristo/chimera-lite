# Chimera Roadmap

Personal research OS for one user. Not a framework. Not SaaS.

> **Last sealed:** Phase N.A — Lens Skills (6 lenses + academic-observe) — 2026-07-06
> **Active:** Phase O — Exocortex Write Surface (O.0 audit pending) — unblocks the deferred Phase N.B

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

## Active Phase

### Phase O — Exocortex Write Surface 🔬 Active (opened 2026-07-07)

**The write-path phase the N.B.0 audit demanded.** N.B was deferred because the vault's typed
K/T/I/D graph is empty (`docs/audits/N.B.0.md`), and the root cause is the write path: no tools
create T/I/D nodes or fill `derives_from` / `synthesizes` edges (PaperMiner only writes K Nodes).
Phase O builds that surface, then N.B resumes over a populated graph. Spec: `docs/phases/phase-O.md`.

**Driving frictions:** N.B.0 found the typed-edge graph empty; no tools create T/I/D nodes or fill
typed edges; PaperMiner writes only K Nodes, so T/I/D + edges are manual with no workflow support.

| Sprint | One-line goal | Status |
|---|---|---|
| O.0 | Audit: what write ops exist (PaperMiner K-Node creation), what's missing (T/I/D + typed-edge fill), Obsidian MCP capabilities | Pending |
| O.1 | `create_node(type, title, body, edges)` → writes K/T/I/D with frontmatter + typed edges (returns staging path) | Pending |
| O.2 | `link_nodes(from, to, edge_type)` → adds `derives_from` / `synthesizes` / `contradicts` to existing nodes | Pending |
| O.3 | Obsidian MCP integration: adapt a market MCP if one exists, else a minimal file-write tool | Pending |

**Hard sealing conditions:** (1) `create_node` writes all 4 types (K/T/I/D) with typed edges in
frontmatter; (2) `link_nodes` adds `derives_from` / `synthesizes` edges to existing nodes; (3) after
O.3, manually create 5 T Nodes + 10 typed edges → vault probe confirms ≥ 20 nodes with typed edges
(the N.B unblock threshold).

**Red lines / design:** thin adapter (tools write markdown, don't embed Obsidian); reuse the Phase
V.A K/T/I/D frontmatter schema (already defined); `create_node` returns a staging path for user
review before vault promotion (never auto-promote — CLAUDE.md). Out of scope: AI auto-linking
(Phase P+), graph visualization, bulk backfill of the ~250 existing K Nodes (user work post-O.3).

**Batch-planning precondition:** the O.0 audit artifact (`docs/audits/O.0.md`) must exist before
sprints are batch-planned — `chimera-sprint-discipline` enforces audit-before-plan.

---

## Deferred Phase

### Phase N.B — JIT Deep Recall ⏸ Deferred 2026-07-07 (blocked on graph population)

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

| Sprint | One-line goal | Status |
|---|---|---|
| N.B.0 | Audit: existing graph traversal, ripgrep seeds, K/T/I/D schema, realistic BFS depth | ✅ Complete — gate FAILED (`3f621a8`) |
| N.B.1 | `deep_recall(...)` → structured subgraph; BFS over `derives_from` / `synthesizes` / `contradicts` | ⏸ Blocked (empty graph) |
| N.B.2 | Verify: a complex 3-hop query synthesized from the subgraph (not raw keyword match) | ⏸ Blocked (empty graph) |

**Hard sealing conditions (unchanged; currently unsatisfiable):** (1) `deep_recall` on "memory
decay graph-based deletion" returns K/T/I nodes spanning ≥ 2 hop depths; (2) result subgraph
≤ 20 nodes (bounded BFS); (3) Claude synthesizes a coherent multi-hop answer without additional
vault calls.

**Unblock condition:** ≥ 20 live nodes carry non-empty typed `graph_edges` pointing to other
knowledge nodes (the N.B.0 gate threshold). Reaching it is **write-path work**, now scoped as the
active **Phase O — Exocortex Write Surface** (`docs/phases/phase-O.md`): tools to create T/I/D nodes
and fill typed edges. N.B resumes once Phase O's HSC 3 confirms ≥ 20 nodes with typed edges; the
N.B.1/N.B.2 disposition (typed-edge BFS as written vs. a rescope to body-wikilink recall) is
re-decided then. Batch-planning of N.B is **held** until then.

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
