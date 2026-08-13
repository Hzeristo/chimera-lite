# Batch Plan: Phase L.C — Colligo (r1) — ⛔ RETIRED, SUPERSEDED

> ⛔ **RETIRED 2026-08-12. Superseded by `docs/plans/Phase-L.C-batch.md` (r2).**
> This plan targets the original C.0.5/C.1/C.2/C.3/C.4/C.5a sequence, which
> `docs/phases/phase-L.C.md` no longer declares. The live sequence is C.1 friction instrument →
> C.2 registration → C.3 route-3 collapse → C.4 boundary bridge → C.5 mid-read verification →
> C.6 W2 handoff, with measurement gating every friction-changing sprint.
> **Do not execute this document.** Retained, not deleted: it is the record of what was planned
> before the spec was corrected, and its audit citations and red lines carried forward into r2.
> Both of its Open Decisions have since been settled — `evidence_base` extended to K (ratified),
> and `apply_link_patch` ruled outside I1.2 (`ENFORCEMENT_DEBT` D-7).

**Output location (superseded):** `docs/plans/Phase-L.C-batch.md` — now held by r2
**Audit reference:** `docs/audits/L.C.0.md` (2026-08-11)
**Phase doc:** `docs/phases/phase-L.C.md` (sparse manifest — amended 2026-08-11 per Architect
authorization; D6/D7/D8 added, C.3/C.4 re-specified against the canonical vocabulary)
**Driving frictions:** `friction-260811-01` (OPEN — homed here as C.0.5); the phase's own
consumption-path frictions declared in `phase-L.C.md` VISION.

This document is a single unit. User approves the whole sequence or rejects the whole
sequence. After approval, hand off to `chimera-code-taste` batch_execution mode.

---

## Sprint Sequence

```
C.0 (audit ✅ complete)
      │
      ├→ C.0.5 ──────────────────────────────────────┐
      │                                               │
      ├→ C.1 ──────────────────────────┬→ C.5a ──────┤
      │                                 │             ├→ seal
      ├→ C.2 ──────────────────────────┘             │
      │                                               │
      ├→ C.3 ⚠ ontology-gated ──────────────────────┤
      │                                               │
      └→ C.4 ────────────────────────────────────────┘
```

C.0.5, C.1, C.2, C.3, C.4 are parallel-eligible after the audit. C.5a depends on C.1
(it backgrounds the loop C.1 makes batch-capable). Seal requires C.0.5 / C.1 / C.3 / C.4;
C.2 is minimal; C.5b is out of scope (→ L.D).

**One decision gates C.3 and must be settled before it executes** — see *Open Decisions*.

---

## Sprint C.0.5: Registration reachability

**Friction reference:** `friction-260811-01` (OPEN — three instances, escalated from incidents;
this sprint is its phase home per Architect ruling 2026-08-11)

**Predecessor assumptions:**
- None — independent of every other sprint in this batch. Should land **first**, because it is
  the check every later sprint's new registration is measured by.

**Risk level:** 🟢 LOW (test-only; no production code path touched)

### Objective
Assert that every component this repo *names* is a component the runtime can actually *reach* —
across both registration surfaces, in one test module.

### Design notes (audit-derived)
- Existing coverage is 47 lines over **4 hardcoded skills**; 17 skills exist, so 13 are
  uncovered — audit ref: Q9, `tests/test_mcp_tool_registration.py:28,47-51`.
- **Zero** tests validate `.claude/agents/*.md`. `test_architecture_dataflow.py:136` globs the
  directory for diagram rendering but asserts nothing about parseability or required keys — this
  is the exact gap instance 3 fell through — audit ref: Q9.
- The friction's own prescription is **one** assertion covering both surfaces, not two, so that
  instance 4 cannot arrive through a third door — `friction-260811.md:48-62`.
- Deliberate design choice: keep an **explicit** skill→tool map rather than regex-extracting tool
  names from skill prose. A regex would false-positive on historical mentions and on names a skill
  legitimately forbids (`semantic_vault_search`, DEBT-019). The map is made safe by a
  **completeness** assertion — every skill directory must appear in it — so a new skill cannot be
  silently uncovered, which is the actual failure mode.

### Task scope
1. Rename `tests/test_mcp_tool_registration.py` → `tests/test_registration.py`; keep both
   existing `analyze_paper_data` regressions verbatim (~0 net lines).
2. Add `test_every_skill_is_covered_by_the_map` — glob `.claude/skills/*/SKILL.md`, assert each
   directory name is a key in `_SKILL_REQUIRED_TOOLS` (value may be `[]` for skills that call no
   MCP tool) (`tests/test_registration.py`, ~12 lines).
3. Populate the map for all 17 skills; `[]` for the 6 lens skills + persona/observe/discipline/
   taste/veto/commit-style (~15 lines of data).
4. Add `test_every_agent_definition_parses` — for each `.claude/agents/*.md`: frontmatter fence
   opens at byte 0, YAML parses, required keys `name` / `description` / `tools` present, `name`
   matches the filename stem (~20 lines).
5. Add `test_agents_named_by_skills_exist` — scan `SKILL.md` bodies for `chimera-*` agent-type
   references; assert each resolves to a file in `.claude/agents/` (~15 lines).

### Acceptance
- `pytest tests/test_registration.py -q` green — verifiable via the venv pytest.
- Negative control (run manually, not committed): renaming any `.claude/agents/*.md` file, or
  prepending a byte before its frontmatter fence, makes task 4 or 5 **fail**. A check that cannot
  be made to fail is the advisory rigor this sprint exists to remove.
- All 17 skill directories present as map keys; all 8 agent files parse.

### Red lines
- ❌ No production code touched — this sprint is `tests/` only.
- ❌ No regex-inference of tool names from skill prose (false-positive fragility; see design notes).
- ❌ The two `analyze_paper_data` regressions survive verbatim — they encode instance 2.
- ❌ No opportunistic refactoring.

### Output locations
- Tests: `tests/test_registration.py` (renamed from `test_mcp_tool_registration.py`)
- Docs: `friction-260811-01` status flip deferred to seal.

---

## Sprint C.1: K-node claims → W1 batch offer

**Friction reference:** `phase-L.C.md` VISION — route 3 ("review [V] claims, batch-promote")
currently costs one full skill re-invocation per claim.

**Predecessor assumptions:**
- None in this batch. Assumes L.B.4's `w1_offer` exists as report prose — confirmed, audit Q1.

**Risk level:** 🟡 MED (skill-file change; no Python; the identity fix is behavioural)

### Objective
Turn the existing W1 offer from retyped prose into a single actionable batch that runs N claims
through W1 without N context switches.

### Design notes (audit-derived)
- The offer exists but is **prose**: 1-3 candidates the Architect retypes into a separate
  invocation. No queue, no handle, no payload — audit ref: Q1,
  `chimera-deep-extract/SKILL.md:62-68`.
- W1 is **strictly one claim per run**, and the N-boundary exists nowhere — not in code, not in
  prose — audit ref: Q2, `chimera-w1-verify/SKILL.md:26-58`.
- **Latent defect this sprint must fix, not inherit.** `identity` is currently "the paper's arXiv
  id when the claim is about one paper" (`chimera-w1-verify/SKILL.md:35-36`), and `write_result`
  defaults to `mode="supersede"`. N claims verified against the *same* paper therefore collide on
  one identity and **silently overwrite each other** — the second verdict destroys the first.
  Batch mode makes this the common case rather than a corner case. Identity must become
  `<arxiv_id>__<claim_slug>` when a batch is running.
- Efficiency available for free: classify + `load_criteria` are per-*paper*, not per-*claim*.
  A batch over one paper does them once.

### Task scope
1. `chimera-deep-extract/SKILL.md` step 7 — emit the offer as an enumerated list where each entry
   carries `{claim_text, cited_ref}` already resolved, plus the exact batch invocation line to run
   (~10 lines).
2. `chimera-w1-verify/SKILL.md` — add a batch entry mode: accept a list of `{claim_text, cited_ref}`;
   classify + `load_criteria` **once per distinct paper**; run step 5 (verifier subagent) per claim;
   write one artifact per claim (~20 lines).
3. `chimera-w1-verify/SKILL.md` step 1 — amend the identity rule to `<arxiv_id>__<claim_slug>`
   whenever more than one claim targets a paper, with a one-line note on why (supersede collision)
   (~5 lines).
4. Report shape: one table, one row per claim — verdict, quote count, Harness path (~5 lines).

### Acceptance
- A real extract (e.g. PyraVid `2605.17065`, 3-5 claims) produces an offer whose batch line runs
  all N without the Architect retyping a claim.
- N distinct artifacts land in `<vault>/Harness/`; **none overwrites another** — verified by
  listing the directory and confirming N files, which is the direct regression for the identity
  defect.
- Each verdict still carries a verbatim quote + location (phase-L red line, unchanged).

### Red lines
- ❌ Judgment stays in `chimera-verbatim-verifier`, one claim per spawn — batching is orchestration,
  never a widened judgment scope. Do not pass N claims into one verifier.
- ❌ The batch never auto-runs. It is offered; the Architect triggers it (I0.1).
- ❌ No new claims minted at offer time — the offer draws only on `KNodeExtraction.claims`.
- ❌ No MCP tool added or changed (`.mcp.json` stays two servers).
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-w1-verify/SKILL.md`, `.claude/skills/chimera-deep-extract/SKILL.md`
- Tests: none (skill prose; verified live per acceptance)

---

## Sprint C.2: W2 recommendation → extract

**Anticipatory justification:** W2's artifact form is explicitly uncertain (`INVARIANTS.md`
non-invariant list: "the form of a W2 breadth map as a persistent artifact" carries **no
protection**). This sprint buys the one thing that survives W2's reshaping — the handoff — and
deliberately buys nothing else.

**Predecessor assumptions:**
- None. Independent and thin by design.

**Risk level:** 🟢 LOW (one skill file, handoff prose only)

### Objective
Make a W2 promote-candidate directly actionable as an extract, carrying its gap sentence as
context, without depending on the map existing as a persistent artifact.

### Design notes (audit-derived)
- `promote-candidate: yes|no` + a ≤12-word reason is **already emitted per paper block** by
  `chimera-breadth-reducer.md:18`. It is plain text inside a keyed block — not a map structure —
  so an interface reading it survives whether W2 outputs a map or a query result. This is the
  whole reason C.2 can stay thin — audit ref: Q3.
- Thinnest extract entry is `ingest_paper(arxiv_id)` → markdown path; makes no LLM call and writes
  no node — `single_paper_ingest.py:66`, `chimera-papers/server.py:111`. Then `chimera-deep-extract`.
- DEBT-020 (no reference parser) and DEBT-021 (BFS caps enforced in prose) bound W2 upstream:
  C.2 must not assume a crawl produced the candidate.

### Task scope
1. `chimera-w2-map/SKILL.md` — after the merge step, list the `promote-candidate: yes` papers as
   an actionable handoff: for each, the `ingest_paper(<id>)` → `chimera-deep-extract <id>` line
   with its gap sentence quoted as the extract's context (~12 lines).

### Acceptance
- A real W2 run surfaces its promote-candidates as runnable lines; running one reaches a staged
  `deep_read` node with the gap sentence visible in the extract's context.
- The handoff text references **no** map path and **no** block offset — it works from a candidate
  handed over in conversation, which is the test that it survives W2's reshaping.

### Red lines
- ❌ No map parsing, no candidate ranking, no persistent-map dependency. C.2 is an interface, not
  a workflow (phase red line; `phase-L.C.md` D2).
- ❌ No auto-ingest. W2 nominates; the Architect promotes (`phase-L.md` W2 design decision).
- ❌ No new MCP tool.
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-w2-map/SKILL.md`

---

## Sprint C.3: W1 verdict → staged support edge ⚠ ONTOLOGY-GATED

**Friction reference:** `phase-L.C.md` Mission — "proof-graph normal form: every committed node's
support chain is traceable."

**Predecessor assumptions:**
- **Open Decision 1 resolved** (extend `evidence_base` to K). If the Architect rules otherwise,
  this sprint is re-planned, not adapted — re-plan trigger.
- Independent of C.1/C.2/C.4 otherwise.

**Risk level:** 🟡 MED (≈15 lines of Python + one ontology doc amendment + tests)

### Objective
Make promoting a W1 verdict stage a correctly-typed, correctly-directed support-edge patch, so the
Architect applies an edge instead of hand-writing YAML.

### Design notes (audit-derived)
- **`depends_on` is not the edge and has not been since Phase O.** Renamed to `derives_from`
  (`NODE_ONTOLOGY.md:88,98`), retired by canonical r2, absent from I2.2's nine. It survives only as
  `write_result`'s parameter, which `ENFORCEMENT_DEBT` D-4 pins to a **coordinated rename with
  Phase K.1** — audit ref: Q4, cross-finding 1. **This sprint does not rename it.**
- The mechanism already exists and is already human-gated: `link_nodes` stages a patch,
  `apply_link_patch` applies it — `staging_service.py:208-256`, `:258-302`. C.3 automates the
  *staging*; the apply stays the Architect's human-time commit (I0.1) — cross-reference 1,
  `phase-L.C.md` D7.
- Patch validation is on the **FROM** node's declared type only (`staging_service.py:279-285`), so
  a K node may point at a Harness artifact stem once the edge is legal for K. The reverse is not
  possible: harness artifacts carry no `_TYPE_EDGES` entry and are rejected as patch *targets* —
  cross-reference 2.
- Legal K edges today are `derives_from` / `supersedes` / `contradicts` (`staging_service.py:13-18`).
  `evidence_base` — the semantically correct edge — is I-only in both code and canonical
  (`NODE_ONTOLOGY.md:50,61-64`). Hence the gate.

### Task scope
1. `docs/ARCHITECTURE/NODE_ONTOLOGY.md` — Tier-2 amendment per I2.2: extend `evidence_base` to K,
   with the justification recorded against I0.2 (support-bearing edges stay structural and
   traversable) and I1.3 (support chains traceable to Tier-1 evidence) (~10 lines).
2. `mcp-servers/chimera-papers/staging_service.py` — `_TYPE_EDGES["knowledge"]` gains
   `"evidence_base": []` (1 line).
3. `.claude/skills/chimera-w1-verify/SKILL.md` — new step 6.5: when the verified claim lives in a
   vault K node **and** the verdict is `[V]`, call `link_nodes(from_node=<K node>,
   to_node=<verdict stem>, edge_type="evidence_base")`; report the staged patch path and that the
   Architect applies it (~12 lines).
4. `tests/test_link_tools.py` — regression: `evidence_base` is accepted for a knowledge node and
   still refused for a type that does not carry it (~15 lines).

### Acceptance
- Promote a real `[V]` verdict → a link patch appears in `docs/staging/`, naming the K node as
  `from`, the verdict stem as `to`, edge `evidence_base`.
- `apply_link_patch` on it writes the edge; the node's body and every other frontmatter line stay
  byte-identical (the existing guarantee, `staging_service.py:262-263`).
- `pytest tests/test_link_tools.py -q` green.
- No `depends_on` appears anywhere in the change.

### Red lines
- ❌ **Do not rename `write_result`'s `depends_on` parameter.** It is a live MCP signature that
  Phase K reads; D-4 pins the rename to K.1 as a coordinated change.
- ❌ Nothing auto-**applies** a patch. Staging is machine-time; applying is human-time (I0.1).
- ❌ `[P]` and `[U]` verdicts stage no support edge — a weak tag is not support (I1.3: "[P]/[U]
  have no computational value by design").
- ❌ No widening of `_TYPE_EDGES` beyond the one gated edge. `collides_with` / `informed_by`
  (D-3) are **not** in this sprint's scope.
- ❌ No opportunistic refactoring.

### Output locations
- Code: `mcp-servers/chimera-papers/staging_service.py`
- Skills: `.claude/skills/chimera-w1-verify/SKILL.md`
- Docs: `docs/ARCHITECTURE/NODE_ONTOLOGY.md`
- Tests: `tests/test_link_tools.py`

---

## Sprint C.4: `informed_by` for hand-authored T/I/D

**Friction reference:** I0.5 mandates `informed_by` as the provenance record for AI-informed
judgment nodes; `ENFORCEMENT_DEBT` D-3 records that the invariant currently has **no mechanism at
all**.

**Predecessor assumptions:**
- None. Independent.

**Risk level:** 🟢 LOW (three template lines + two skill report blocks; no writer, no Python)

### Objective
Give `informed_by` a real mechanism on the only surface where T/I/D nodes are actually authored —
the Architect's hands — by making the field present in the template and the value paste-ready.

### Design notes (audit-derived)
- **The original C.4 was unbuildable.** "Authoring auto-fills `informed_by`" presumes a writer;
  commit `2b72978` removed every T/I/D authoring path at two enforced layers with three
  regressions — audit ref: Q6, cross-finding 3, `staging_service.py:82-96`,
  `chimera-vault/server.py:171,182-186`, `tests/test_ascend_node.py:70-81`.
- **Fixing D-3 would not help C.4.** Adding `informed_by` to `_TYPE_EDGES` adds a key to dicts used
  only by writers that reject T/I/D outright. D-3 is real but orthogonal; do not conflate them.
- `NODE_ONTOLOGY.md:188-191` already states the correct resolution: hand-typed frontmatter "is the
  correct place for it anyway" on a hand-authored node. This sprint makes that ergonomic, not
  automatic.
- `prompts/obsidian_tpl/Tpl_thought.md:8-12` carries `graph_edges` with four keys and no
  `informed_by`. Repo templates are the source; the vault copies are **user-synced** (CLAUDE.md) —
  this sprint edits the repo only and the seal notes the sync as the Architect's action.

### Task scope
1. `prompts/obsidian_tpl/Tpl_thought.md`, `Tpl_insight.md`, `Tpl_decision.md` — add
   `informed_by: []` to `graph_edges` (1 line each).
2. `.claude/skills/chimera-deep-extract/SKILL.md` — the completion report emits a paste-ready
   block: `informed_by: ["[[<staged node stem>]]"]`, labelled as "paste into a T/I/D node you
   author from this" (~6 lines).
3. `.claude/skills/chimera-w2-map/SKILL.md` — same, naming the map artifact stem (~6 lines).
4. `docs/ARCHITECTURE/ENFORCEMENT_DEBT.md` — amend D-3's gap text to record that the
   `_TYPE_EDGES` remedy is **inert for `informed_by`** given no writer accepts T/I/D, and that the
   live mechanism is template + paste (~4 lines). *(Compliance record correction, not a canonical
   edit — the file's own contract permits re-verification.)*

### Acceptance
- A real authoring session: the Architect creates a T node from the template with the field
  present, pastes the emitted block, and amends freely — verified by the resulting node carrying
  `informed_by` without any tool having written the node.
- `rg "informed_by" prompts/obsidian_tpl/` returns all three templates.

### Red lines
- ❌ **No tool writes, stages, pre-fills, or scaffolds a T/I/D node body** (I0.5). If a sprint task
  starts to look like "just write the frontmatter for them," it has failed.
- ❌ `informed_by` is **never** support-bearing — it must not appear in any monotonicity or
  support-chain computation (I2.2, `NODE_ONTOLOGY.md:54-57`).
- ❌ Do not edit the Obsidian vault's `templates/` copies — repo sources only (CLAUDE.md).
- ❌ Do not "fix" D-3 by widening `_TYPE_EDGES` here — out of scope, and inert (design notes).
- ❌ No opportunistic refactoring.

### Output locations
- Templates: `prompts/obsidian_tpl/Tpl_{thought,insight,decision}.md`
- Skills: `.claude/skills/chimera-deep-extract/SKILL.md`, `.claude/skills/chimera-w2-map/SKILL.md`
- Docs: `docs/ARCHITECTURE/ENFORCEMENT_DEBT.md` (D-3 row)

---

## Sprint C.5a: Stream-mode W1 — queue + background

**Friction reference:** `phase-L.C.md` VISION — "a claim spotted mid-read wants immediate
verification; the verdict shapes the rest of the read."

**Predecessor assumptions:**
- **C.1 complete** — C.5a backgrounds the loop C.1 made batch-capable. Re-plan trigger if C.1 slips.
- **Probe passes** (task 1). If it fails, C.5a is abandoned to L.D and the phase seals on
  C.0.5/C.1/C.3/C.4, which the phase doc already permits.

**Risk level:** 🔴 HIGH — requires explicit per-sprint approval before execution

### Objective
Let the Architect queue a claim mid-read and receive its verdict by notification, without blocking
the read.

### Design notes (audit-derived)
- **The blocker is structural, not sizing** — cross-finding 6. W1's judgment must run in a
  subagent; MCP cannot spawn subagents (`phase-L.md:166-169`); therefore `TaskService` — the repo's
  only queue — can **never** host a backgrounded W1, whatever budget is spent on it. Any plan that
  routes C.5a through `TaskService` is planning against a wall.
- The substrate that *can* is the harness's **native background Task**, verified empirically
  during the C.0 audit (five background scouts ran detached and returned by completion
  notification) — audit ref: Q7.
- Consequence: the risk is **dependency on harness behaviour outside this repo**, which nothing in
  `tests/` can pin. Hence the probe-first structure and the 🔴.

### Task scope
1. **Probe first, build second.** Empirically confirm, and record in the sprint file: (a) a
   background subagent can call `chimera-vault` MCP tools (`load_criteria`, `write_result`);
   (b) it can spawn its own judgment sub-subagent, or alternatively perform the verbatim check
   itself under isolation; (c) the completion notification carries enough to identify which queued
   claim finished. **If (a) or (b) fails, stop and defer to L.D** (~probe only, no code).
2. `.claude/skills/chimera-w1-verify/SKILL.md` — a queue mode: spawn the W1 run as a background
   task, return the handle immediately, report the verdict on notification (~20 lines).
3. Record the queue's identity discipline: a backgrounded claim uses the same
   `<arxiv_id>__<claim_slug>` identity as C.1, so a queued and a foreground run of the same claim
   supersede rather than duplicate (~5 lines).

### Acceptance
- Queue a claim mid-read; the session remains responsive; the verdict arrives and is attributable
  to the claim that was queued.
- The verdict artifact is indistinguishable from a foreground W1 verdict — same shape, same
  Harness path convention, same `PENDING_REVIEW`.
- Both modes coexist: the foreground path is unchanged and still works (phase red line).

### Red lines
- ❌ **Stream-mode does not replace batch.** Both W1 modes coexist (phase red line).
- ❌ Judgment stays in an isolated subagent — backgrounding must not move the verbatim check into
  the main context.
- ❌ Do not route this through `TaskService` or add a queue to an MCP server — MCP cannot spawn
  subagents, and a server-side queue would put orchestration where judgment cannot follow.
- ❌ No inline rendering of verdicts into the reading context — that is C.5b, deferred to L.D.
- ❌ No opportunistic refactoring.

### Output locations
- Skills: `.claude/skills/chimera-w1-verify/SKILL.md`
- Docs: `docs/sprints/phase-L.C/C.5a.md` records the probe result either way — a failed probe is a
  finding, not a wasted sprint.

---

## Phase-wide Red Lines

Violation in any sprint halts the batch:

- ❌ **No tool authors a T/I/D node** — no writer, no staging path, no body-filler (I0.5).
- ❌ **No route privileged.** Any change smoothing one consumption route must not add ceremony to
  another (I1.4). C.1/C.3/C.5a all serve route 3 — this is the batch's standing risk.
- ❌ **Nothing auto-commits.** Machine-time stages; human-time applies and promotes (I0.1).
- ❌ **Nothing ships unregistered** — covered by C.0.5's assertion, and the seal exercises new
  components through the **live client**, never in-process imports (`friction-260811-01`).
- ❌ **No new MCP server**; `.mcp.json` stays two. Skills orchestrate existing primitives.
- ❌ **Do not rename `write_result`'s `depends_on`** — pinned to Phase K.1 (D-4).
- ❌ **W2 consumption stays thin** — no map parsing, ranking, or persistent-map dependency.
- ❌ No opportunistic refactoring.

---

## Hard Sealing Conditions (carried from phase doc, as amended)

1. **(C.0.5)** One registry assertion covers both `@mcp.tool` names and `.claude/agents/*.md`;
   all 17 skills are map-covered and all 8 agents parse — verified by `pytest tests/test_registration.py`
   plus a manual negative control that the check can be made to fail.
2. **(C.1)** An extract's offer runs N claims in one action; N distinct Harness artifacts result
   and none overwrites another — verified live on a real extract.
3. **(C.2)** A W2 promote-candidate triggers extract with its gap context, with no dependency on
   the map's persistence — verified on a real W2 run.
4. **(C.3)** Promoting a `[V]` stages a correctly-typed `evidence_base` patch against the K node;
   the Architect applies it; no manual YAML, no `depends_on` — verified by inspection.
5. **(C.4)** A T/I/D node authored by hand carries `informed_by` from template + paste, with no
   tool having written the node — verified on a real authoring session.
6. **(C.5a, deferrable)** A queued claim returns its verdict by notification without blocking;
   or the probe's failure is recorded and C.5a defers to L.D.
7. **(VISION gate — Architect-assessed)** Three sessions — pure observation / AI-assisted / batch
   promote — run with equal friction. **Reported honestly per cross-finding 4:** I1.4 has no
   mechanical verifier (`ENFORCEMENT_DEBT` D-5). The seal must either record a per-route step count
   as its observable, or state plainly that I1.4 ships as CONVENTION. It must not report this
   condition green in a way that implies a check ran.

---

## Open Decisions (block execution of the named sprint)

**Decision 1 — C.3's edge. Extend `evidence_base` to K nodes?**
No legal K edge expresses "this claim is supported by this verdict"; `evidence_base` is the right
meaning and is I-only. I2.1/I2.2 are Tier 2 and explicitly mutable ("edges may be added or merged"),
documented in `NODE_ONTOLOGY.md` — so extending it is a legal evolution, not a breach.
*Recommended: yes.* The alternative — leaving W1 verdicts unlinkable to the nodes they verify —
would make "proof-graph normal form," this phase's own Mission, unreachable.
**Blocks:** C.3.

**Decision 2 — `apply_link_patch` has no tier guard. Is that in or out of I1.2's scope?**
Cross-finding 2: `ascend_node` is the sole *creator* of committed nodes, but `apply_link_patch`
*mutates* committed nodes with no tier or status check, and is a registered MCP tool. This is the
same shape as the settled D-6 (which resolved K-vs-T/I/D and left create-vs-mutate untouched), and
L.B's seal asserted the sole-writer property flatly. C.3 would drive this path.
*Not for me to rule — surfaced per CLAUDE.md.* Two honest readings: (a) out of scope — I1.2 governs
*promotion*, and the stage→review→apply split already supplies the human gate, in which case
`ENFORCEMENT_DEBT` should record the narrower reading explicitly; (b) in scope — in which case a
tier check belongs on `apply_link_patch` and that is a sprint, in this phase or K.
**Blocks:** nothing outright — C.3 can proceed under reading (a) — but the answer determines
whether an extra sprint is owed.

---

## Approval

User approves whole sequence or rejects whole sequence.

Upon approval, hand off to `chimera-code-taste` with:
> "Execute batch for Phase L.C per `docs/plans/Phase-L.C-batch.md`."

C.5a additionally requires explicit per-sprint approval at its turn (🔴), and its probe may end it.

---

*Generated by chimera-sprint-discipline batch_planning mode.*
