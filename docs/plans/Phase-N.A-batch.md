# Batch Plan: Phase N.A — Lens Skills

**Output location:** `docs/plans/Phase-N.A-batch.md`
**Audit reference:** `docs/audits/N.A.0.md` (date: 2026-07-04)
**Phase doc:** `docs/phases/phase-N.A.md` (sparse manifest — distinct from this batch plan)
**Driving friction:** `friction-chimera-lite-01` — lens skills don't exist in chimera-lite
(project_chimera had them as `OpticsService` prompts, not Claude Code skills). *Note: this
friction is phase-declared but has no `docs/logs/` file; treated as user-authorized
anticipatory work per the explicit phase spec + the pre-planning decisions below.*

This document is a single unit. User approves the whole sequence or rejects the whole
sequence. After approval, hand off to `chimera-code-taste` batch_execution mode.

---

## Pre-planning decisions (confirmed with user, 2026-07-04)

| # | Decision | Effect on plan |
|---|---|---|
| 1 | **Ontological Map Scanner ABSORBS `survey_consensus` + `survey_gaps`** — the map lens is survey-native; consensus/gaps are map *dimensions*. | Resolves audit cross-finding #1. Target set stays **6 lenses**, not 8; N.A.3's Ontological lens emits taxonomy + bottlenecks + gaps as one consolidated map. No separate consensus/gaps skills. |
| 2 | **Create `.claude/skills/_shared/falsifiability.md`; all 6 lenses reference it.** Fallback: inline duplication (6 copies) with `SYNC` comments if cross-skill include is unsupported. | Resolves cross-finding #2. N.A.1 creates the fragment first; every lens references `../_shared/falsifiability.md`. Enforces sealing condition 2 from one source. |
| 3 | **TONE from unwired `.j2` scalpels + M.3-extracted `~/.chimera` voice; STRUCTURE from wired registry schemas.** | Resolves cross-finding #3. Scalpel tone + registry schema = sharp *and* structured; the two sources are compatible, not competing. |
| 4 | **`academic-observe` connection-surfacing uses `obsidian_graph_query` (BFS depth 1–2) + `vault_query(linked_to)`.** | Resolves cross-finding #4. Capability-ready with existing tools — zero MCP changes. |
| 5 | **`~/.chimera` divergence check = DEFER / ACCEPT PARTIAL.** In-project registry + M.3 extraction cover essentials. | Resolves cross-finding #5. Do NOT block N.A.1–4 on it; if the user later supplies `~/.chimera/skills/*.json`, validate as a follow-up. |

### Planner reconciliation (read before approving)

1. **Risk rubric vs reality.** The template's risk levels are code-change-sized. **Every sprint
   here is doc-only** (SKILL.md + references; no `.py`) → mechanically all 🟢 LOW. I reserve
   🟡 MED to flag elevated **design** risk (net-new lens authored from stance vocabulary;
   always-on trigger tuning), NOT code risk. A 🟡 here means "review the voice/behavior at
   execution," not "gate approval."

2. **The `_shared/` reference pattern already works in this repo.** `chimera-sprint-discipline`
   references `../_shared/expected_model.md`, `../_shared/doc_folders.md`, etc., and Claude
   reads them on activation. So Decision 2's primary path (reference `../_shared/falsifiability.md`)
   is **proven-viable**; inline duplication is a genuine fallback, not the expected outcome.

3. **Skill count & naming.** 6 lens skills + 1 always-on = **7 skills**. Proposed names
   (kebab, `chimera-lens-` prefix for grouping; auto-select keys off `description:`, not name):
   `chimera-lens-forensic-leakage`, `chimera-lens-thermodynamic-decay`,
   `chimera-lens-state-collision`, `chimera-lens-agentic-illusion`,
   `chimera-lens-math-decoration`, `chimera-lens-ontological-map`, and `chimera-academic-observe`.

---

## Sprint Sequence

```
N.A.0 (audit ✓)
   │
   ▼
N.A.1  Forensic + Thermodynamic  (+ _shared/falsifiability.md)
   │
   ├──────────────► N.A.2  State Collision + Agentic Illusion ─┐
   └──────────────► N.A.3  Math + Ontological ─────────────────┤
                    (N.A.2 ∥ N.A.3, both after N.A.1)          │
                                                               ▼
                                            N.A.4  academic-observe (always-on)
                                                               │
                                                               ▼
                                              seal (chimera-sprint-discipline phase_review)
```

- **N.A.1 first** — it creates `_shared/falsifiability.md` (referenced by all later lenses) and
  establishes the forensic/anti-hype tone that N.A.2's Agentic Illusion extends.
- **N.A.2 ∥ N.A.3** — independent of each other, both depend only on N.A.1's shared fragment.
- **N.A.4 last** — academic-observe references the lens outputs / connects analysis to vault nodes.
- **Split analysis (process step 3):** each sprint authors ≤3 files (2 SKILL.md, +1 shared
  fragment in N.A.1). No split needed. N.A.3's Ontological lens *consolidates* 3 registry
  lenses into 1 skill — a consolidation (Decision 1), not an expansion.

---

## Sprint N.A.1: Forensic Leakage Audit + Thermodynamic Decay Probe

**Friction reference:** `friction-chimera-lite-01` (phase-declared; user-authorized)

**Predecessor assumptions:**
- None — first sprint. **Produces** `.claude/skills/_shared/falsifiability.md`, which N.A.2,
  N.A.3 (and academic-observe) reference. Re-plan trigger: if the shared-fragment reference
  pattern proves unreliable at execution → switch to Decision 2's inline+SYNC fallback for all lenses.

**Risk level:** 🟢 LOW (doc-only). Thermodynamic's description→**probe** reframe is a design point, not code risk.

### Objective
Author `chimera-lens-forensic-leakage` and `chimera-lens-thermodynamic-decay` skills, and
create the shared `_shared/falsifiability.md` fragment every lens references.

### Design notes (audit-derived)
- **Shared falsifiability fragment** — derived from `user_profile.j2:21-25` "The Falsifiability
  Check": reject endpoint-only metrics (QA accuracy / win-rate); reward white-box process-oriented
  metrics (turn-wise, oracle-decoupled failure attribution); expose context-buffer scaling that
  lacks true state dynamics. Audit ref: `N.A.0.md` Q9, cross-finding #2.
- **Forensic tone from the scalpel, structure from the registry** — port sharp forensic content
  from `eval_scalpel.j2:2-11` (LLM-as-Judge self-enhancement bias; mock-feeding vs turn-by-turn
  streaming; asymmetric prompting advantages) over the wired `eval_rigor` schema
  (baselines / datasets / metrics / ablation_target). Audit ref: `N.A.0.md` Q1, cross-finding #3.
- **Thermodynamic as a PROBE, not a description** — reframe `memory_physics`
  (`schemas.py:186-206` forgetting_mechanism) + `user_profile.j2:11` "Temporal Decay across long,
  high-entropy interaction horizons" into falsifiable probes: *does the paper measure decay over
  horizon length? is forgetting attributed or asserted?* Audit ref: `N.A.0.md` Q2.
- **Auto-select `description:`** (sealing condition 1): Forensic triggers on empirical/eval-heavy
  papers; Thermodynamic on memory / long-context / state papers.

### Task scope
1. `.claude/skills/_shared/falsifiability.md` (~30 lines) — shared academic-taste fragment. Audit ref: Q9.
2. `.claude/skills/chimera-lens-forensic-leakage/SKILL.md` (~60 lines). Audit ref: Q1.
3. `.claude/skills/chimera-lens-thermodynamic-decay/SKILL.md` (~60 lines). Audit ref: Q2.

### Acceptance
- Both `SKILL.md` carry a `description:` that enables auto-select by paper type (no manual
  invocation) — verify by reading each description against its target paper type.
- Each references `../_shared/falsifiability.md` (or inline+SYNC fallback).
- Each output spec mandates **mechanism + evidence + falsifiability**.
- Forensic exposes ≥3 concrete leakage/contamination patterns (LLM-as-Judge bias, mock-vs-streaming, asymmetric prompting).
- Thermodynamic frames ≥2 falsifiable decay tests (not prose description).

### Red lines
- ❌ Pure prompt skills — no new tools, no MCP/`.mcp.json` changes (phase-wide).
- ❌ No `.py` edits; do not touch `optics_lens_registry.py` / `optics_service.py` (they stay wired-as-is).
- ❌ Falsifiability is not optional — every output carries the check.
- ❌ Pure English only.
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/_shared/falsifiability.md`, `.claude/skills/chimera-lens-forensic-leakage/`, `.claude/skills/chimera-lens-thermodynamic-decay/`
- Docs (CLAUDE.md skills list + ROADMAP sprint status): deferred to seal, updated together.

---

## Sprint N.A.2: State Collision StressTest + Agentic Illusion Stripper

**Friction reference:** `friction-chimera-lite-01` (phase-declared; user-authorized)

**Predecessor assumptions:**
- N.A.1 done — `_shared/falsifiability.md` exists and is referenced.
- Forensic lens established the anti-hype **tone**; Agentic Illusion extends it toward
  *architectural* hype. Re-plan trigger: if Forensic's tone/structure diverges from the plan.
- State Collision draws the same `user_profile.j2` "Big Three" stance vocabulary exercised while
  building Thermodynamic. Independent of N.A.3 (parallel-eligible).

**Risk level:** 🟡 MED (doc-only, elevated **design** risk) — State Collision is **net-new**
(no registry ancestor; authored from stance vocabulary). Review its voice + output shape at execution.

### Objective
Author `chimera-lens-state-collision` (net-new) and `chimera-lens-agentic-illusion` skills.

### Design notes (audit-derived)
- **State Collision — author fresh** from `user_profile.j2:12-13` "State Overwrite" (resolve
  conflicting info without naive superposition) + "Cognitive Inertia" (evidence threshold to
  revise embedded belief) + `memory_physics` "overwrites" (`schemas.py:192`). Operationalize as a
  stress-test lens: how does the architecture arbitrate conflicting state, and at what threshold?
  Audit ref: `N.A.0.md` Q3 (the one target with no wired ancestor).
- **Agentic Illusion — port** `method_scalpel.j2:9-13` "AGENTIC REALITY CHECK (Plumbing Audit)"
  (orchestration: heavy framework vs `while`-loop vs single-pass-disguised-as-agent; state: true
  mutable vs context-stuffing) + `M.3.md:17` "Strip the illusion" + `bb-persona` anti-hype
  (`SKILL.md:41`). Output the plumbing verdict: is the "agent" a real loop or a one-shot call?
  Audit ref: `N.A.0.md` Q4.
- **De-conflict the two anti-hype lenses** — Forensic targets **empirical** leakage (eval);
  Agentic Illusion targets **architectural** illusion (is the agent real?). Keep `description:`
  triggers distinct so auto-select doesn't fire both on the same axis.

### Task scope
1. `.claude/skills/chimera-lens-state-collision/SKILL.md` (~60 lines). Audit ref: Q3.
2. `.claude/skills/chimera-lens-agentic-illusion/SKILL.md` (~60 lines). Audit ref: Q4.

### Acceptance
- Auto-select `description:` — State Collision → memory/state/multi-turn-agent papers; Agentic
  Illusion → agent/autonomous-loop papers. Triggers do not collide with Forensic.
- Both reference the falsifiability fragment.
- Agentic Illusion emits an explicit plumbing verdict (real loop vs one-shot API call).
- State Collision emits a conflict-resolution + inertia-threshold analysis (mechanism + evidence + falsifiability).

### Red lines
- ❌ Pure prompt skills — no tools, no MCP changes (phase-wide).
- ❌ State Collision must not silently duplicate Thermodynamic (**decay ≠ collision**).
- ❌ Agentic Illusion must not duplicate `bb-persona`'s restyle role — it is an ANALYSIS lens
  with structured output, not a tone filter over the final answer.
- ❌ Pure English only. No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-lens-state-collision/`, `.claude/skills/chimera-lens-agentic-illusion/`
- Docs: deferred to seal.

---

## Sprint N.A.3: Math Decoration Validator + Ontological Map Scanner

**Friction reference:** `friction-chimera-lite-01` (phase-declared; user-authorized)

**Predecessor assumptions:**
- N.A.1 done — `_shared/falsifiability.md` exists and is referenced.
- **Independent of N.A.2** (both port from the registry) — parallel-eligible with N.A.2.

**Risk level:** 🟢 LOW (doc-only). Both port from registry schemas; Ontological's 3→1 consolidation is a moderate design step.

### Objective
Author `chimera-lens-math-decoration` and `chimera-lens-ontological-map` (the map lens **absorbs**
`survey_consensus` + `survey_gaps` per Decision 1).

### Design notes (audit-derived)
- **Math Decoration — extraction + judgment.** Port extraction from `math_arch`
  (`core_equations` / `pseudo_code` / `architecture_narrative`, `schemas.py:156-167`) +
  `method_scalpel.j2` Obj 1, then FUSE the validation judgment (**load-bearing vs decorative**)
  from `user_profile.j2:24-25` ("value grounded modeling over boilerplate; EXPOSE if it only
  scales context without true dynamics"). The judgment layer is the delta. Audit ref: `N.A.0.md` Q5.
- **Ontological Map — consolidate 3 registry lenses (Decision 1).** Port `survey_taxonomy`
  (`classification_axes` + `core_categories` with architectural-bound distinctions, `registry:129-143`)
  and ABSORB `survey_consensus` (`major_limitations` / bottlenecks) + `survey_gaps`
  (`future_directions` / technical_void) as **map dimensions**. Add **inter-concept edges** — the
  "map" delta beyond a flat category list. Audit ref: `N.A.0.md` Q6, Decision 1.

### Task scope
1. `.claude/skills/chimera-lens-math-decoration/SKILL.md` (~60 lines). Audit ref: Q5.
2. `.claude/skills/chimera-lens-ontological-map/SKILL.md` (~70 lines — larger; absorbs 3 registry lenses). Audit ref: Q6.

### Acceptance
- Math Decoration outputs extraction **plus** an explicit decorative-vs-load-bearing verdict.
- Ontological Map outputs one consolidated map: axes + categories + bottlenecks + gaps + inter-concept edges.
- Auto-select `description:` — Math Decoration → any modeling/algorithm paper; Ontological → survey/review/position papers.
- Both reference the falsifiability fragment.

### Red lines
- ❌ Pure prompt skills — no tools, no MCP changes (phase-wide).
- ❌ Ontological Map produces ONE consolidated map, not three separate survey outputs.
- ❌ Math Decoration must ADD judgment, not merely re-extract what `math_arch` already extracts.
- ❌ Pure English only. No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-lens-math-decoration/`, `.claude/skills/chimera-lens-ontological-map/`
- Docs: deferred to seal.

---

## Sprint N.A.4: chimera-academic-observe (always-on proactive skill)

**Friction reference:** `friction-chimera-lite-01` (phase-declared; user-authorized)

**Predecessor assumptions:**
- N.A.1–N.A.3 done — all 6 lens skills exist. academic-observe connects current analysis to vault
  knowledge nodes and may reference lens output shapes. Re-plan trigger: if lens output shapes change.

**Risk level:** 🟡 MED (doc-only, elevated **design** risk) — net-new always-on behavior; the
trigger/relevance gate is the real risk (proactive without being noisy). Review behavior at execution.

### Objective
Author an always-on `chimera-academic-observe` skill that proactively surfaces connections between
the current work and vault knowledge nodes, unprompted, without noise.

### Design notes (audit-derived)
- **Always-on pattern from `bb-persona`** — universal trigger phrasing in `description:`
  ("Activate whenever…") + a body that acts on relevant research outputs. Audit ref: `N.A.0.md` Q7.
- **Connection-surfacing via existing vault tools (zero MCP changes)** — `obsidian_graph_query`
  (BFS over wikilinks + `graph_edges`, depth 1–2 typical) + `vault_query(linked_to=…)`.
  Audit ref: `N.A.0.md` Q8, cross-finding #4; Decision 4.
- **Content angle** — the "cross-domain thief / Transplantability" heuristic from
  `user_profile.j2:15-19` ("can this mechanism be hijacked for Memory Physics?") is the natural
  substance of a proactive "this connects to X you filed" observation.
- **Noise gate (the risk)** — surface a connection ONLY when a vault node is materially relevant to
  the current paper/topic; define an explicit relevance threshold in the body so it does not fire
  every turn.

### Task scope
1. `.claude/skills/chimera-academic-observe/SKILL.md` (~70 lines). Audit ref: Q7 / Q8.

### Acceptance (sealing condition 3)
- In a live research conversation, proactively surfaces a genuine vault-node connection **without
  being asked**, via `obsidian_graph_query` / `vault_query`.
- Does NOT fire on irrelevant turns (relevance gate holds) — spot-check on an unrelated turn.
- Registered always-on in the `CLAUDE.md` skills list.

### Red lines
- ❌ Pure prompt skill — **NO new MCP tools**; uses existing vault tools only (phase-wide red line).
- ❌ Must not spam — the relevance gate is mandatory.
- ❌ Must not duplicate `bb-persona` — observe SURFACES connections; bb STYLES the verdict. Different jobs.
- ❌ Pure English only. No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-academic-observe/`
- Docs: `CLAUDE.md` skills list (always-on registration) — deferred to seal, updated together.

---

## Phase-wide Red Lines

Apply across ALL sprints. Violation in any sprint halts the batch:

- ❌ **Pure prompt skills only** — zero new MCP tools, zero server / `.mcp.json` changes.
- ❌ **No code modification** — no `.py`; the wired `optics_lens_registry.py` / `optics_service.py`
  pipeline stays untouched. Lenses are NEW skills, not edits to the pipeline.
- ❌ **Falsifiability is mandatory** in every lens output (via `_shared/falsifiability.md` or inline+SYNC).
- ❌ **Pure English** in all skill files.
- ❌ **Lenses are trigger-based; only `academic-observe` is always-on.**
- ❌ No opportunistic refactoring across the batch.

---

## Hard Sealing Conditions (carried from `docs/phases/phase-N.A.md`)

MUST pass at `phase_review`:

1. **Auto-selection** — all 6 lens skills have a `description:` that lets Claude auto-select by
   paper type (no manual `/lens-name` invocation) — verified by reading each description + a live
   auto-select spot-check across paper types.
2. **Academic taste** — each lens requires **mechanism + evidence + falsifiability** in output —
   verified by inspecting each `SKILL.md` output spec + its `_shared/falsifiability.md` reference.
3. **Proactive observation** — `chimera-academic-observe` proactively surfaces connections to vault
   nodes unprompted — verified by a live research conversation (and a noise-gate spot-check).

---

## Deferred / open (do not block N.A.1–4)

- **`~/.chimera/skills/*.json` divergence check** (audit cross-finding #5) — accepted PARTIAL;
  validate as a follow-up if the user later supplies the files.
- **`friction-chimera-lite-01` log** — the driving friction has no `docs/logs/` entry; consider
  logging it at seal for the audit trail (not a blocker).

---

## Approval

User approves the whole sequence or rejects the whole sequence.

Upon approval, hand off to `chimera-code-taste`:
> "Execute batch for Phase N.A per `docs/plans/Phase-N.A-batch.md`."

---

*Generated by chimera-sprint-discipline batch_planning mode.*
