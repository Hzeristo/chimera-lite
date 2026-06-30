# Migration Lineage — read this before "fixing" anything

**Audience:** a fresh Claude Code session opening chimera-lite with **zero
project_chimera context.** `CLAUDE.md` tells you the *current* state and *how* things
work; this doc tells you *why* — the inherited decisions, so you don't "fix" things that
are intentional or re-litigate settled choices.

Rule of thumb: if something looks odd here, it's probably a deliberate consequence of the
migration. Check this doc and the cited lineage before changing it.

---

## 1. What chimera-lite is

chimera-lite is the **migrated form of project_chimera**: a single-user research OS,
re-platformed onto **Claude Code + MCP**. project_chimera was a *self-built agent* — a
bespoke `oligo` ReAct loop (1485 lines) plus an `Astrocyte` Svelte/Tauri frontend.
chimera-lite deletes both: **Claude Code is the agent loop**, and the surviving domain
logic (PaperMiner, Vault) is exposed as two thin MCP servers (`chimera-vault`,
`chimera-papers`). Same capabilities, none of the bespoke harness.

---

## 2. Inherited architecture decisions (the WHY / DON'T)

| Decision | What it is | WHY it's this way | DON'T |
|---|---|---|---|
| **TaskService poll model** | Long tools return a `task_id`; caller polls `check_task_status` across turns. | oligo could *suspend-resume within one SSE response* (`AWAITING_TASK`). Claude Code **cannot** suspend a turn. The poll model is the functional equivalent, split across turns. | Don't try to make it suspend-resume / block-until-done inside one tool call. That's a Claude Code harness limit, **not a bug**. |
| **daily_paper_pipeline producer-consumer** | 3 concurrent stages via `asyncio.Queue`: `download (sem=3) → pdf_queue → convert (single GPU worker) → md_queue → filter (sem=3)`. See `daily_chimera_service.py:150,201`. | A perf incident found **GPU sawtooth** (util 80→0→80) when stages ran serially — the GPU idled between PDFs. One GPU convert worker fed by concurrent download + drained by concurrent filter keeps the GPU saturated. | **Don't parallelize the convert stage.** It is deliberately a *single* GPU worker — RTX-class VRAM, parallel convert → OOM. (Download/filter are the parallel parts.) |
| **K/T/I/D vault ontology** | Typed nodes (Knowledge / Thought / Insight / Decision) with YAML frontmatter edges (`derives_from` / `synthesizes` / `supersedes`) + a staging protocol (`PENDING_REVIEW → PROMOTED`). | Phase V.A exocortex design — the vault is a typed graph, not a note pile. Edges + staging are the memory model. | Don't flatten K/T/I/D notes to plain markdown, and don't auto-promote staged candidates. The types and the review gate are the point. |
| **MCP servers are THIN adapters (<200 lines)** | `server.py` files just declare `@mcp.tool` contracts and delegate. Domain logic lives in `core/`, `ports/`, and the service modules. | The domain code (PaperMiner / Vault) was **ported verbatim** from project_chimera. The servers only *expose* it; the logic was already written and tested. | Don't put business logic in `server.py`. If you're adding logic there, it belongs in a service/port module. |
| **Server-side concurrency lock** (M.2a) | `chimera-papers/server.py` holds an `asyncio.Lock` + `TaskService.has_active_long_task()`; a 2nd pipeline start while one runs → `[Busy]`. | oligo enforced "no concurrent pipeline" inside its agent loop's `concurrency_safe` partition. **That loop is gone**, so the guard moved *into the MCP server*. | This is the **one** place the thin-adapter rule is intentionally exceeded (~20 net-new lines). Don't "simplify" it away — it's load-bearing. |
| **BB persona via skill (reasoning transparent)** | `chimera-bb-persona` restyles only the **final answer paragraph**; reasoning + tool output stay plain. | oligo hid its reasoning and streamed only persona-voiced output ("theater"). Claude Code **shows reasoning by design**. BB is voice-on-the-verdict, not a curtain. | Don't try to hide reasoning/tool calls to recreate the "theater." Reasoning transparency was **accepted as a tradeoff**, not lost. |
| **CUDA torch is mandatory (CPU torch = regression)** | `torch` is pinned to the **cu128** build via `[[tool.uv.index]] pytorch-cuda`; runs on the RTX 5060 (sm_120). | A profiling incident found CPU-only torch made MinerU ~**35s/pdf**. CUDA torch is required for usable ingest throughput. | Don't let `uv sync` resolve the default PyPI `torch` (CPU-only — and it lacks sm_120 for Blackwell). Keep the cu128 index + `[tool.uv.sources]`. Verify `torch.cuda.is_available()` → True. |

---

## 3. What was deleted, and why

| Deleted | Replaced by |
|---|---|
| oligo agent loop (`ChimeraAgent`, 1485 lines: route→tool→wash→synthesize) | Claude Code's native agent loop |
| Astrocyte frontend (Svelte/Tauri/Rust) | Claude Code's UI |
| text-DSL tool parsing (`<tool_call>`/`<CMD>` + arg-repair) | native MCP tool-calling (zero parse code) |
| SSE `bb-*` protocol (`bb-stream-chunk`, `bb-phase-transition`, …) | Claude Code's native streaming |
| prompt_composer / late persona bind / two-model split | system prompt + `.claude/skills/` |

**All of it is preserved** on the `archive/chimera-oligo` branch of the **project_chimera**
repo. Nothing was lost — it was retired. If you need to see how oligo did something, read
the archive branch; don't reconstruct it here.

---

## 4. Where deeper history lives (don't duplicate — cite)

| For… | Read (in **project_chimera**, the sibling repo, unless noted) |
|---|---|
| Full phase history (Phases I–V) | `docs/phases/` , `docs/ROADMAP.md` |
| Perf + bug incident records | `docs/incidents/` , `docs/audits/perf-mineru-bubble.md` (the GPU-bubble rationale) |
| K/T/I/D ontology spec | `docs/architecture/NODE_ONTOLOGY.md` |
| The deleted oligo/Astrocyte code | `@ archive/chimera-oligo` branch |
| Why migrate at all (feasibility verdict) | `docs/audits/chimera-to-code-feasibility.md` |
| **This migration's spec + execution** | *(here)* `docs/phases/phase-M.md` , `docs/plans/Phase-M-batch.md` , `docs/sprints/phase-M/*.md` , `docs/audits/M.0.md` |

---

## 5. Settled decisions — DO NOT re-litigate

These are closed. If you're about to argue one of them, read the reference first.

| Question | Settled answer + reference |
|---|---|
| Why not keep the oligo agent? | The self-built loop was a maintenance liability; native loop + MCP is strictly better for the tool surface. → **ST feasibility audit, `project_chimera/docs/audits/chimera-to-code-feasibility.md` (2026-06-27)**. |
| Why flat imports, not a vendored `src/crucible` tree? | Flat + rewrite was chosen over re-vendoring the package tree. → **Phase M decision 1** (`docs/plans/Phase-M-batch.md`, "Pre-planning decisions"). |
| Why poll, not in-request await? | Claude Code can't suspend-resume a turn. → **feasibility audit Q2/Q4**; see §2 above. |
| Why MCP, not a REST service? | Interface/logic decoupling — the tools plug into Claude Code (or any MCP client) without a bespoke server/protocol. → **ST 2026-06-27**. |
| Why is `config.py` `extra="ignore"`? | chimera-lite shares `~/.chimera/config.toml` with project_chimera, which still carries retired `[oligo]`/`[astrocyte]` sections; they're tolerated/ignored, not errors. → `docs/sprints/phase-M/M.1.md`. |
| Why is the BB "warmth" defined as possessive devotion? | The 4-trait spec left "warmth" undefined; it was resolved via the Fate/EXTRA CCC BB archetype. Opinionated by design. → `.claude/skills/chimera-bb-persona/SKILL.md`, `docs/sprints/phase-M/M.3.md`. |

---

*This is a lineage doc: it explains WHY. For HOW (current architecture, dev env, commands)
see `CLAUDE.md`; for the code, read the modules. When WHY and code disagree, the code is
current — update this doc, don't silently diverge.*
