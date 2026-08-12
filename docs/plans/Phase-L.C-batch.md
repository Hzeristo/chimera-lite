# Batch Plan: Phase L.C — Colligo: Candidate Consumption Paths (r2)

**Output location:** `docs/plans/Phase-L.C-batch.md`
**Audit reference:** `docs/audits/L.C.0.md` (2026-08-11) + a re-planning scout pass (2026-08-12)
**Phase doc:** `docs/phases/phase-L.C.md` (sparse manifest, re-specified 2026-08-12)
**Supersedes:** `docs/plans/Phase-L.C-batch-r1-retired.md` — planned against the withdrawn
C.0.5/C.1/C.2/C.3/C.4/C.5a sequence.
**Driving frictions:** `friction-260811-01` (OPEN — homed as C.2); the phase's own consumption-path
frictions; `ENFORCEMENT_DEBT` D-5 (I1.4 has no mechanical verifier).

This document is a single unit. User approves the whole sequence or rejects the whole sequence.
After approval, hand off to `chimera-code-taste` batch_execution mode.

---

## Sprint Sequence

```
C.0 (audit ✅)
      │
      ├→ C.1 (instrument) ──┬→ C.3a → C.3b → C.3c ──┐
      │                      │                        │
      │                      ├→ C.4 ─────────────────┤→ seal
      │                      │                        │
      │                      └→ C.5 (probe-first) ───┤
      │                                               │
      ├→ C.2 ────────────────────────────────────────┤
      └→ C.6 ────────────────────────────────────────┘
```

**C.1 gates every friction-changing sprint** (C.3*, C.4, C.5) — no route's friction moves before
its before-state is recorded. C.2 and C.6 are independent of the instrument and may land any time.
Seal requires C.1 / C.2 / C.3a / C.3b / C.3c / C.4.

**What changed from r1 and why.** r1's C.3 has been split three ways. The re-planning scout found
that `phase-L.md:139-142` declares a `PENDING_REVIEW → PROMOTED` lifecycle that **no code
implements** — `_VALID_MODES` is `{supersede, merge, reject, mark_stale}` (`result_service.py:56`),
and the statuses the code can produce are `PENDING_REVIEW`, `MERGED`, `REJECTED`, `STALE` only.
Route 3's terminal operation does not exist. Adding it, extending the edge vocabulary, and building
the review surface is three files' worth of work each; per the split rule (≤3 files / ≤50 lines)
it is three sprints, not one. This is a split, not an expansion — total scope is unchanged.

---

## Sprint C.1: The friction instrument

**Anticipatory justification:** I1.4 is the invariant this phase is named for and it is one of
eight canonical invariants with no mechanical verifier (`ENFORCEMENT_DEBT` D-5). Every other sprint
in this batch changes a route's friction. Measuring after the fact cannot establish parity, and
the phase would otherwise seal on an impression — the exact shape the north star refuses.

**Predecessor assumptions:**
- None. First sprint; gates C.3*, C.4, C.5.

**Risk level:** 🟢 LOW (measurement + one document; no code)

### Objective
Define the friction metric and record a baseline for all three routes, plus a composition-drift
baseline, before anything in this phase moves.

### Design notes (audit-derived)
- Three registers per phase-doc D1: **invocations**, **context switches** (Claude Code ↔ Obsidian
  crossings), **manual transcription** (characters retyped that a machine already held).
- Composition drift (D2) is computable today with **no code change**: `vault_query` filters on
  `type` / `status` / `linked_to` only, but returns `chimera_tier` in each row's excerpt
  (`vault_query.py:79`), so the K split by tier is counted from returned rows. `search_vault_attribute`
  can filter `chimera_tier` directly if the row count proves unwieldy — audit ref: scout Q-A.
- `vault_query` ripgreps the **whole vault** with no path filter (`vault_query.py:42-46`), so
  `Harness/` artifacts are in scope for the route-3 count.
- Route 1 has no repo surface at all (audit cross-finding 5), so its count is honest only if taken
  from a real authoring session, not estimated.

### Task scope
1. Author `docs/audits/L.C.1-friction-baseline.md`: the metric definition, the counting rules, and
   the exact commands/queries used, so the seal can re-run it identically (~40 lines).
2. Walk each of the three routes once on a real fixture, counting the three registers. Record raw
   counts, not averages (~1 table).
3. Record the composition-drift baseline: hand-authored T/I/D node count vs promoted K node count,
   with the window's start date stated explicitly (~1 table).

### Acceptance
- The baseline document exists with numbers for all three routes in all three registers.
- The counting method is reproducible: a second party could re-run it from the document alone.
- Composition-drift counts carry an explicit window start — a drift figure without a window is
  not a measurement.

### Red lines
- ❌ No code. This sprint ships a document and numbers.
- ❌ No estimated counts. A route not actually walked is recorded as unmeasured, not guessed.
- ❌ Do not tune any route while measuring it — measurement precedes smoothing (phase red line).
- ❌ No opportunistic refactoring.

### Output locations
- Docs: `docs/audits/L.C.1-friction-baseline.md`

---

## Sprint C.2: Registration reachability

**Friction reference:** `friction-260811-01` (OPEN — three instances, escalated from incidents;
this sprint is its phase home, Architect ruling 2026-08-11)

**Predecessor assumptions:**
- None. Independent of the instrument and of every other sprint.

**Risk level:** 🟢 LOW (test-only; no production path touched)

### Objective
Assert that every component this repo names is one the runtime can reach — across both
registration surfaces, in one test module.

### Design notes (audit-derived)
- Current coverage is 47 lines over **4 hardcoded skills**; 17 exist, so 13 are uncovered —
  audit ref: Q9, `tests/test_mcp_tool_registration.py:28,47-51`.
- **Zero** tests validate `.claude/agents/*.md`. `test_architecture_dataflow.py:136` globs the
  directory for diagram rendering but asserts nothing about parseability or required keys — the
  exact gap instance 3 fell through.
- The friction prescribes **one** assertion over both surfaces, not two, so instance 4 cannot
  arrive through a third door — `friction-260811.md:48-62`.
- Keep an **explicit** skill→tool map rather than regex-extracting names from prose: a regex
  false-positives on historical mentions and on names a skill deliberately forbids
  (`semantic_vault_search`, DEBT-019). Safety comes from a **completeness** assertion instead.

### Task scope
1. Rename `tests/test_mcp_tool_registration.py` → `tests/test_registration.py`; keep both
   `analyze_paper_data` regressions verbatim — they encode instance 2 (~0 net lines).
2. `test_every_skill_is_covered_by_the_map` — glob `.claude/skills/*/SKILL.md`, assert each
   directory is a key in `_SKILL_REQUIRED_TOOLS` (`[]` permitted) (~12 lines).
3. Populate the map for all 17 skills (~15 lines of data).
4. `test_every_agent_definition_parses` — per `.claude/agents/*.md`: fence opens at byte 0, YAML
   parses, `name`/`description`/`tools` present, `name` matches the filename stem (~20 lines).
5. `test_agents_named_by_skills_exist` — scan SKILL.md bodies for `chimera-*` agent references;
   assert each resolves to a file (~15 lines).

### Acceptance
- `pytest tests/test_registration.py -q` green.
- **Negative control, run manually and recorded in the sprint file:** renaming an agent file, or
  prepending a byte before its frontmatter fence, makes task 4 or 5 fail. A check that cannot be
  made to fail is the advisory rigor this sprint exists to remove.
- All 17 skill directories are map keys; all 8 agent files parse.

### Red lines
- ❌ `tests/` only — no production code.
- ❌ No regex-inference of tool names from skill prose.
- ❌ The two `analyze_paper_data` regressions survive verbatim.
- ❌ No opportunistic refactoring.

### Output locations
- Tests: `tests/test_registration.py` (renamed)

---

## Sprint C.3a: The `promote` transition

**Friction reference:** Spec/code divergence — `phase-L.md:139-142` declares
`PENDING_REVIEW → PROMOTED`; no code implements it. Route 3's terminal operation is missing.

**Predecessor assumptions:**
- **C.1 complete** (friction baseline recorded) — re-plan trigger if skipped.

**Risk level:** 🟡 MED (3 files, <30 lines, has tests)

### Objective
Implement the `promote` lifecycle transition the artifact spec has always declared.

### Design notes (audit-derived)
- `_VALID_MODES = frozenset({"supersede", "merge", "reject", "mark_stale"})`
  (`result_service.py:56`). `_transition(path, new_status)` already generalizes over a target
  status (`:245-258`) and is called only for reject/mark_stale (`:175`) — so the mechanism exists
  and only the mode and its dispatch are missing. Audit ref: scout Q-C.
- The MCP tool's `mode` is a mirrored `Literal` (`chimera-vault/server.py:304`). **Widen the
  Literal, never relax it to `str`** — `ENFORCEMENT_DEBT` R5a is *discharged* precisely because
  these are closed Literals rejected at the JSON-RPC boundary before the handler runs; relaxing
  one silently re-opens a closed gap.
- `ascend_node` is **not** the promote path for harness artifacts and must not become one: it
  requires `chimera_tier == "deep_read"` (`staging_service.py:182-186`) and writes only
  `Knowledge/`; Harness artifacts carry no tier so they are already refused — scout Q-D.

### Task scope
1. `result_service.py` — add `"promote"` to `_VALID_MODES`; dispatch it through `_transition(path,
   "PROMOTED")` alongside reject/mark_stale (~6 lines).
2. `chimera-vault/server.py` — widen the `mode` Literal to include `"promote"`; document the state
   in the docstring (~4 lines).
3. `tests/` — regression: promote flips `PENDING_REVIEW → PROMOTED`, leaves body and all other
   frontmatter byte-identical, and an unknown mode is still rejected at the boundary (~20 lines).

### Acceptance
- A `PENDING_REVIEW` W1 verdict transitions to `PROMOTED`; the body is untouched.
- The mode set remains a closed `Literal` — verified by reading the signature.
- `pytest -q` green.

### Red lines
- ❌ Do not relax any `Literal` to `str` (R5a).
- ❌ Do not route harness promotion through `ascend_node` — different tier, different gate.
- ❌ Promotion is Architect-invoked; nothing auto-promotes (I0.1).
- ❌ Do not rename `write_result`'s `depends_on` parameter — pinned to K.1 (D-4).
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera-papers/result_service.py`, `mcp-servers/chimera-vault/server.py`
- Tests: `tests/test_w2_result.py` or a new `tests/test_result_lifecycle.py`

---

## Sprint C.3b: `evidence_base` extended to K

**Friction reference:** No legal K edge expresses "supported by this verdict," so the Mission's
proof-graph normal form is unreachable. Ratified by the Architect 2026-08-12 (phase-doc D4).

**Predecessor assumptions:**
- Independent of C.3a; both precede C.3c. May run in parallel with C.3a.

**Risk level:** 🟡 MED (3 files, <20 lines, has tests)

### Objective
Make `evidence_base` a legal edge on Knowledge nodes, in the canonical and in code together.

### Design notes (audit-derived)
- `_TYPE_EDGES["knowledge"]` is `{derives_from, supersedes, contradicts}`
  (`staging_service.py:13-18`); `evidence_base` is I-only in both code and `NODE_ONTOLOGY.md:50,61-64`.
- I2.2 is Tier 2 and explicitly mutable ("edges may be added or merged"), documented in
  `NODE_ONTOLOGY.md` — a legal evolution, not a canonical breach.
- Constraint from I2.2: support-bearing edges must remain **structural** (auto-written,
  traversable). `evidence_base` is support-bearing, so Phase K's monotonicity will read it.
- Both patch functions validate against `_TYPE_EDGES` for the FROM node's declared type
  (`staging_service.py:227-231`, `:281-285`), so this one change unlocks both staging and applying.

### Task scope
1. `docs/ARCHITECTURE/NODE_ONTOLOGY.md` — extend `evidence_base` to K in §2's table and the §2
   per-type canonical set; record the ratification date and the justification against I0.2 and
   I1.3 (~10 lines).
2. `mcp-servers/chimera-papers/staging_service.py` — `_TYPE_EDGES["knowledge"]` gains
   `"evidence_base": []` (1 line).
3. `tests/test_link_tools.py` — `evidence_base` is accepted for a knowledge node, and still
   refused for a type that does not carry it (~15 lines).

### Acceptance
- `link_nodes(from_node=<K node>, edge_type="evidence_base", ...)` stages a patch instead of
  raising.
- The canonical doc and `_TYPE_EDGES` agree — verified by reading both.
- `pytest tests/test_link_tools.py -q` green.

### Red lines
- ❌ Extend **only** `evidence_base`, **only** to K. `collides_with` / `informed_by`
  (`ENFORCEMENT_DEBT` D-3) are explicitly out of scope **for this sprint** — they are C.4's, and
  they are not inert (a 2026-08-12 correction: `_TYPE_EDGES` also gates the patch functions, which
  edit existing hand-written T/I/D nodes).
- ❌ Do not touch `INVARIANTS.md` — it is FROZEN; I2.2 already permits this and the change is
  documented in `NODE_ONTOLOGY.md`.
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera-papers/staging_service.py`
- Docs: `docs/ARCHITECTURE/NODE_ONTOLOGY.md`
- Tests: `tests/test_link_tools.py`

---

## Sprint C.3c: Route 3 collapse — the batch review surface

**Friction reference:** Route 3 today is one full skill re-invocation per claim plus hand-curation
in Obsidian (audit Q8).

**Predecessor assumptions:**
- **C.3a complete** — `promote` exists as a mode. Re-plan trigger if absent.
- **C.3b complete** — `evidence_base` is legal for K. Re-plan trigger if absent.
- **C.1 complete** — the baseline this sprint will be measured against exists.

**Risk level:** 🟡 MED (one skill file; no Python)

### Objective
Turn review-and-promote from N invocations into one structured decision that promotes the chosen
verdicts and stages their support edges.

### Design notes (audit-derived)
- Enumeration works today: `vault_query` ripgreps the whole vault including `Harness/`
  (`vault_query.py:42-46`) and filters on `status`, so pending verdicts are retrievable by
  `status="PENDING_REVIEW"` — scout Q-A.
- Verdict artifacts carry `type`, `status`, `identity`, `created_at`, `superseded_prior` plus
  metadata passthrough (`verdict`, `depends_on`) — `result_service.py:203-211` — enough to render
  a review row without opening each file.
- **Build nothing that the harness supplies (D7).** The multi-select review surface is
  `AskUserQuestion` with `multiSelect: true`; there is no picker to implement.
- Per D5, this sprint stages the `evidence_base` patch via `link_nodes` and stops. The
  `apply_link_patch` call stays the Architect's.
- **Legibility over speed (the C.3 design risk).** With edges now cheap to mint (`ENFORCEMENT_DEBT`
  D-7 settles that an edge is metadata, not committed content), nothing structural stands between
  an automated proposal and a committed node's frontmatter — the protection is the Architect
  reading the patch. A review surface that renders N verdicts as one undifferentiated confirmation
  converts that protection into a formality. Each row must show its verdict tag, its grounding
  quote, and the exact edge proposed.

### Task scope
1. `.claude/skills/chimera-w1-verify/SKILL.md` (or a sibling review skill) — a review mode:
   `vault_query(status="PENDING_REVIEW")` → filter `kind="w1_verdict"` → render one row per
   verdict carrying tag, quote, and proposed edge (~15 lines).
2. Present the rows as a single `AskUserQuestion` multi-select; the Architect chooses (~8 lines).
3. For each chosen verdict: `write_result(mode="promote", ...)`, then `link_nodes(...,
   edge_type="evidence_base")` to stage the patch. Report the staged patch paths and state
   plainly that the Architect applies them (~10 lines).
4. `[P]` / `[U]` rows are shown but stage no edge (~2 lines).

### Acceptance
- One invocation surfaces all pending `w1_verdict` artifacts and promotes the selected subset.
- Each promoted `[V]` yields a staged `evidence_base` patch naming the K node as `from`.
- Each rendered row shows its grounding quote — verified by inspection, and the reason is
  recorded in the sprint file.
- `[P]`/`[U]` selections promote (if chosen) but stage no support edge.
- Route-3 friction re-measured against the C.1 baseline and recorded.

### Red lines
- ❌ Nothing auto-applies a patch, and nothing auto-promotes. Both are Architect actions (I0.1).
- ❌ `[P]` and `[U]` never stage a support edge — a weak tag is not support (I1.3).
- ❌ No picker, queue, or scheduler built by hand — use the harness affordance (D7).
- ❌ No bulk "approve all" affordance. The review is per-row or it is not a review.
- ❌ No new MCP tool.
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-w1-verify/SKILL.md`
- Docs: route-3 re-measurement appended to `docs/audits/L.C.1-friction-baseline.md`

---

## Sprint C.4: The boundary bridge

**Friction reference:** I0.5 mandates `informed_by` as the provenance record for AI-informed
judgment nodes; `ENFORCEMENT_DEBT` D-3 records that the invariant has **no mechanism at all**.

**Predecessor assumptions:**
- **C.1 complete.** Independent of C.3*.

**Risk level:** 🟡 MED — but the widest file scope in the batch after the 2026-08-12 revision
(1 domain file + 2 test files + 3 templates + 2 skills + 1 arch doc + a probe). If it does not
fit one sprint cleanly, split C.4a (close D-3: tasks 1-3, 5) / C.4b (the proposal path: tasks
4, 6, 7) rather than widening it.

### Objective
Give `informed_by` a real mechanism by closing D-3, then **proposing** the edge onto a
hand-authored node the Architect explicitly orders applied — the tool writing the edge, never the
body.

### Design notes — **REVISED 2026-08-12** (the prior premise was wrong)
- **Withdrawn:** "fixing D-3 would not help — `_TYPE_EDGES` serves only writers that reject
  T/I/D." **False.** `_TYPE_EDGES` has three consumers: `staging_service.py:104`
  (`create_staging_node`, which does reject T/I/D) and `:225-230` / `:279-284`
  (`stage_link_patch` / `apply_link_patch`), which operate on **existing** vault nodes of any
  K/T/I/D type — routinely hand-written Thoughts. `tests/test_staging_tools.py:51` says so outright.
- **I0.5 reserves the *body*.** D-7 settled that an edge is metadata, not content, so a tool
  appending `informed_by` to a hand-authored T-node authors no judgment. No node is ever created
  by a tool and no body is ever opened.
- **Edges are format work, and the Architect does not do format work.** Route-1 datum
  (2026-08-12): *"create a T node via keyboard shortcut, fill the contents, **no links**."*
  `informed_by` is **skipped entirely**; all six vault T-nodes carry empty edge lists. A
  paste-ready block was therefore the wrong deliverable — the barrier was never typing
  convenience, it is that filling a structured edge is not the work being done at that moment.
- **Propose, never auto-apply (Architect constraint, 2026-08-12).** Claude proposes on a node
  found unlinked; the Architect **explicitly orders** the apply — not inferred, not defaulted, not
  batched by convenience. D-7 makes the edge legal to write; it does not license the machine to
  decide the edge should exist.
- `Tpl_thought.md:8-12` carries `graph_edges` with four keys and no `informed_by`. Repo templates
  are the source; vault copies are **user-synced** (CLAUDE.md) — edit the repo, the Architect syncs.
- **Detection probe (D7).** `Monitor` can watch the vault's judgment folders, one event per new
  file, session-scoped — which covers route 2 exactly, since route 2 means a session is open. It
  does not cover authoring outside a session: a stated limitation, not a bug.
- **`apply_link_patch` does not become redundant — it becomes the load-bearing half.** Without a
  separate apply, `link_nodes` would write directly and propose-and-commit would collapse into one
  machine act. Two tool calls are what make the Architect's order structural rather than
  conventional. **Known weakness, recorded not fixed here:** the patch is consumed on apply
  (`staging_service.py:294,301`), so the gate is enforced at the moment and leaves **no durable
  record** — a later observer cannot distinguish a proposed-and-ordered edge from a hand-typed one.
  **Consequence for this phase:** D2's composition-drift measure goes partly blind on the surface
  C.4 opens, since machine-proposed edges become indistinguishable from hand-written ones. This
  cannot be fixed by stamping the edge: D-7 ruled that an edge carries no identity or provenance of
  its own, which is precisely why a tool may write one. Any such record must live at the node level
  or out of band — **Phase K's concern** (provenance load-bearing), not L.C's. Do not attempt it here.

### Task scope
1. `mcp-servers/chimera-papers/staging_service.py` — **close D-3**: `_TYPE_EDGES` gains
   `informed_by` for `thought` / `insight` / `decision` and `collides_with` for all four types,
   mirroring `NODE_ONTOLOGY.md` §2 exactly (~4 lines).
2. `tests/test_staging_tools.py` — update `CANONICAL` to the true §2 sets. It currently mirrors
   the *code* rather than the doc, which is why it did not already fail (~4 lines).
3. `prompts/obsidian_tpl/Tpl_{thought,insight,decision}.md` — add `informed_by: []` so a
   hand-filled node and a patched one carry the same shape (1 line each).
4. `.claude/skills/chimera-deep-extract/SKILL.md` and `chimera-w2-map/SKILL.md` — on completion,
   **propose** an `informed_by` edge naming the artifact just produced, stage it via `link_nodes`,
   and state that applying requires an explicit order. Never call `apply_link_patch` (~8 lines each).
5. `tests/test_link_tools.py` — `informed_by` accepted for `thought`, still refused for
   `knowledge` (I0.5 scopes it to judgment types) (~15 lines).
6. **Probe:** a persistent `Monitor` over the vault's judgment folders; on a new unlinked node,
   surface the proposal. Record whether it fires reliably. **If not, ship tasks 1-5 and record the
   finding** — Architect-initiated ("propose links for this node") always works.
7. `docs/ARCHITECTURE/ENFORCEMENT_DEBT.md` — mark **D-3 discharged**: the gap was the vocabulary
   entry, and I0.5's provenance mandate now has a mechanism.

### Acceptance
- A real authoring session: the Architect writes a T node by hand and leaves it unlinked (the
  observed default); a proposal appears; the Architect orders it; the edge lands via
  `apply_link_patch` — **and no tool wrote the body, and nothing applied without the order.**
- `informed_by` is stageable for `thought` and refused for `knowledge`.
- `rg "informed_by" prompts/obsidian_tpl/` returns all three templates.
- The Monitor probe's result is recorded either way.
- Route-2 friction re-measured against the C.1 baseline.
- Negative control: revert the `_TYPE_EDGES` entry → the `informed_by` staging test must FAIL.

### Red lines
- ❌ **No tool writes, stages, pre-fills, or scaffolds a T/I/D node BODY**, and no tool creates a
  judgment node (I0.5). Writing an *edge* on an existing hand-authored node is permitted; the line
  is the body.
- ❌ **Nothing auto-applies.** Propose and stage only; `apply_link_patch` is the Architect's
  explicit order. Never call it from a skill.
- ❌ `informed_by` is never support-bearing — it must not enter any monotonicity or support-chain
  computation (I2.2).
- ❌ `informed_by` stays T/I/D-only — do not extend it to `knowledge` (I0.5 scopes it to judgment).
- ❌ Do not edit the vault's `templates/` copies — repo sources only (CLAUDE.md).
- ❌ No opportunistic refactoring.

### Output locations
- Templates: `prompts/obsidian_tpl/Tpl_{thought,insight,decision}.md`
- Skills: `.claude/skills/chimera-deep-extract/SKILL.md`, `.claude/skills/chimera-w2-map/SKILL.md`
- Docs: `docs/ARCHITECTURE/ENFORCEMENT_DEBT.md` (D-3 row)

---

## Sprint C.5: Mid-read verification

**Friction reference:** The VISION's opening — "a claim spotted mid-read wants immediate
verification; the verdict shapes the rest of the read."

**Predecessor assumptions:**
- **C.1 complete.**
- **Probe passes** (task 1). If it fails, C.5 ends at its probe and the phase seals without it —
  the phase doc permits this explicitly.

**Risk level:** 🔴 HIGH — requires explicit per-sprint approval before execution

### Objective
Let the Architect queue a claim mid-read and receive its verdict by notification without blocking.

### Design notes (audit-derived)
- **Structural, not sizing** (audit cross-finding 6). W1's judgment must run in a subagent; MCP
  cannot spawn subagents (`phase-L.md:166-169`); therefore `TaskService` can never host a
  backgrounded W1 at any budget. Any plan routing this through `TaskService` is planning against a
  wall.
- The substrate that works is the harness's **native background Task**, verified empirically during
  the C.0 audit — five background scouts ran detached and returned by completion notification.
- Consequence: the risk is dependency on harness behaviour **no test in this repo can pin**. Hence
  probe-first, and hence a sprint permitted to end at its probe with a recorded finding rather than
  a deliverable. A recorded negative is this sprint's legitimate output.

### Task scope
1. **Probe first, build second.** Confirm and record: (a) a background subagent can call
   `chimera-vault` MCP tools (`load_criteria`, `write_result`); (b) it can spawn its own judgment
   sub-subagent, or else perform the verbatim check itself under isolation; (c) the completion
   notification identifies which queued claim finished. **If (a) or (b) fails, stop.**
2. `.claude/skills/chimera-w1-verify/SKILL.md` — queue mode: spawn the W1 run as a background
   task, return the handle immediately, report on notification (~20 lines).
3. Identity discipline: a queued claim uses `<arxiv_id>__<claim_slug>`, so a queued and a
   foreground run of the same claim supersede rather than duplicate. **Note the latent defect this
   inherits:** today `identity` is the bare arXiv id for a single-paper claim
   (`chimera-w1-verify/SKILL.md:35-36`) and `write_result` defaults to `supersede`, so two claims
   about one paper silently overwrite each other. Fix it here (~5 lines).

### Acceptance
- A claim queued mid-read leaves the session responsive; the verdict arrives attributable to the
  claim queued.
- Two claims against the same paper produce two artifacts, neither overwriting the other.
- Both W1 modes coexist; the foreground path is unchanged.

### Red lines
- ❌ Stream mode does not replace batch — both coexist.
- ❌ Judgment stays in an isolated subagent; backgrounding must not move the verbatim check into
  the main context.
- ❌ Do not route through `TaskService` or add a queue to an MCP server.
- ❌ No inline rendering of verdicts into the reading context — that is L.D.
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-w1-verify/SKILL.md`
- Docs: `docs/sprints/phase-L.C/C.5.md` records the probe result either way

---

## Sprint C.6: W2 handoff

**Anticipatory justification:** W2's artifact form carries **no protection** (`INVARIANTS.md`
non-invariant list). This buys the one thing that survives its reshaping in L.D — the handoff —
and deliberately nothing else.

**Predecessor assumptions:**
- None. Independent of the instrument and of every other sprint.

**Risk level:** 🟢 LOW (one skill file, handoff prose only)

### Objective
Make a W2 promote-candidate directly actionable as an extract carrying its gap sentence, without
depending on the map existing as a persistent artifact.

### Design notes (audit-derived)
- `promote-candidate: yes|no` + a ≤12-word reason is already emitted per paper block
  (`chimera-breadth-reducer.md:18`) as plain text inside a keyed block — not a map structure. This
  is why C.6 can stay thin — audit Q3.
- Thinnest extract entry: `ingest_paper(arxiv_id)` → markdown path; no LLM call, no node written
  (`single_paper_ingest.py:66`).
- DEBT-020 (no reference parser) and DEBT-021 (BFS caps enforced in prose) bound W2 upstream —
  do not assume a crawl produced the candidate.

### Task scope
1. `.claude/skills/chimera-w2-map/SKILL.md` — after the merge step, list `promote-candidate: yes`
   papers as runnable handoff lines: `ingest_paper(<id>)` → `chimera-deep-extract <id>`, with the
   gap sentence quoted as the extract's context (~12 lines).

### Acceptance
- A real W2 run surfaces runnable candidate lines; running one reaches a staged `deep_read` node
  with the gap sentence visible in context.
- The handoff references **no** map path and **no** block offset — it works from a candidate handed
  over in conversation. That is the test that it survives W2's reshaping.

### Red lines
- ❌ No map parsing, ranking, or persistent-map dependency — interface, not workflow (D2 of the
  original spec; phase red line).
- ❌ No auto-ingest. W2 nominates; the Architect promotes.
- ❌ No new MCP tool.
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-w2-map/SKILL.md`

---

## Phase-wide Red Lines

Violation in any sprint halts the batch:

- ❌ **No tool authors a T/I/D node** — no writer, staging path, body-filler, or frontmatter-only
  scaffold (I0.5).
- ❌ **No friction-changing sprint lands before C.1.**
- ❌ **No route privileged.** Where a route is against the grain, fix that route — never handicap
  another to restore parity.
- ❌ **Nothing auto-commits, and nothing auto-applies.** Machine-time *proposes* and stages;
  human-time applies and promotes on an explicit order (I0.1). No skill calls `apply_link_patch`.
- ❌ **Nothing ships unregistered** — covered by C.2; the seal exercises new components through the
  **live client**, never in-process imports (`friction-260811-01`).
- ❌ **Do not relax a closed `Literal` to `str`** (R5a is discharged only while they stay closed).
- ❌ **Do not rename `write_result`'s `depends_on` parameter** — pinned to K.1 (D-4).
- ❌ **Do not touch `INVARIANTS.md`** — FROZEN. Tier-2 changes are documented in `NODE_ONTOLOGY.md`.
- ❌ **W2 consumption stays thin.**
- ❌ **No new MCP server**; `.mcp.json` stays two.
- ❌ No opportunistic refactoring.

---

## Hard Sealing Conditions (carried from the phase doc)

1. **(C.1)** Metric defined; all three routes baselined in three registers; composition-drift
   baseline recorded with an explicit window — all before C.3*/C.4/C.5 execute.
2. **(C.2)** One assertion covers `@mcp.tool` names and `.claude/agents/*.md`; every skill covered,
   every agent parses — verified by `pytest` **plus a recorded negative control.**
3. **(C.3a+b+c)** Pending `[V]` verdicts reviewed and promoted in one structured decision; the
   `evidence_base` patch staged with correct type and direction; no manual YAML, no `depends_on`.
4. **(C.4)** A hand-authored T/I/D node carries `informed_by` from template + paste, with **no tool
   having written the node.**
5. **(C.5 — may end at its probe)** A queued claim returns without blocking and both modes coexist;
   or the probe's failure is recorded as the finding.
6. **(C.6)** A W2 promote-candidate triggers extract with gap context, no map dependency.
7. **(VISION gate — Architect-assessed)** Three sessions run with seal-time friction numbers beside
   the C.1 baseline, and no route reported as against the grain. **If a route got worse, this does
   not seal green** regardless of how the sessions felt. Composition drift is longitudinal: L.C
   delivers the baseline; a widening trend later is a re-opening trigger, not a seal blocker.

---

## Notes carried for the executor

- **`ascend_node` validates by frontmatter, not by path** (`staging_service.py:174-189`): a file
  outside `docs/staging/` carrying `chimera_tier: deep_read` and `type: knowledge` would ascend.
  Not exploitable today — Harness artifacts carry no tier — and **not in scope** (no opportunistic
  refactoring). Recorded so it is not rediscovered as a surprise.
- **`CLAUDE.md` is stale** (lists 5 chimera-vault tools; 11 exist). Architect-confirmed. Outside
  this batch's write authority — needs its own pass.

---

## Approval

User approves whole sequence or rejects whole sequence.

Upon approval, hand off to `chimera-code-taste` with:
> "Execute batch for Phase L.C per `docs/plans/Phase-L.C-batch.md`."

C.5 additionally requires explicit per-sprint approval at its turn (🔴), and its probe may end it.

---

*Generated by chimera-sprint-discipline batch_planning mode.*
