# Phase L.C — Colligo: Candidate Consumption Paths

**Status:** Active (opened 2026-08-12)
**Predecessor:** Phase L.B (Integratio)
**Etymology:** Latin *colligō* — to bind together, to infer. Whewell's term for
the cognitive moment scattered observations bind into a principle. Here: binding
candidate material (W1/extract outputs) into committed artifacts (K/T/I nodes).
**Audit:** `docs/audits/L.C.0.md` · **Sprint detail:** `docs/plans/Phase-L.C-batch.md`

**Driving frictions:**
- Research is not batch — a claim spotted mid-read wants verification now, and the verdict
  shapes the rest of the read.
- Route friction is unequal and unmeasured. I1.4 is one of eight canonical invariants with no
  mechanical verifier (`ENFORCEMENT_DEBT` D-5), so the phase named for it could seal on an
  impression.
- `friction-260811-01` (OPEN) — "registered" is an untested surface; three instances, no phase
  home. Every L.C sprint ships a registered thing.

---

## VISION

Research is not batch. A claim spotted mid-read wants immediate verification;
the verdict shapes the rest of the read. Phase L built the generators; L.C builds
the glue that makes their outputs immediately consumable — no context switch, no
manual wiring, no route privileged over another.

Three consumption routes, equal friction:
1. Read a paper yourself, write a T-node — zero AI (pure observation)
2. Read AI summaries + original, write T/I informed by both — AI-assisted
3. Review [V] claims, batch-promote — AI-driven, human-curated

None should feel against the grain. L2 is augmentation, not replacement.

---

## The obstacle

Routes 1 and 2 terminate **in Obsidian**. Route 3 terminates **in the vault via MCP**.

Claude Code has no reach into Obsidian: no hook fires when a note is opened, no event announces
that a T-node was written. Route 3 is fully instrumented; the other two are not reachable at all.

This is structural, and it is the phase's centre of difficulty. It also means I1.4 cannot be
satisfied by making route 3 frictionless — that maximises the imbalance. The vault filesystem is
the one surface both sides share: Claude cannot watch Obsidian, but it can read what Obsidian
wrote. That is where the bridge goes.

---

## Mission

Bind candidate material to committed artifacts by wiring the harness's existing affordances to
Chimera's invariants, and make "equal friction" a **measured** property rather than an assessed
impression. Establish proof-graph normal form: every committed node's support chain is traceable
(strong `[V]`, or documented-weak `[P]`/`[U]`).

Constraints:
1. **Judgment bodies are Architect-authored.** No tool writes or creates a T/I/D node. AI may
   inform; provenance records `informed_by`, never `derives_from` (I0.5).
2. **W2 consumption stays thin.** W2's artifact form carries no protection; the link must
   survive its reshaping in L.D.
3. **Seal on real fixtures, not scale.** 3-4 real papers suffice.
4. **Measure before smoothing.** No friction-changing sprint lands before the instrument exists.

---

## Sprint Sequence

| Sprint | Risk | One-line goal | Status |
|--------|------|---------------|--------|
| C.0 | — | Audit | ✅ `docs/audits/L.C.0.md` |
| C.1 | 🟢 | Friction instrument: the metric, and a baseline for all three routes + composition drift | ✅ `dc7375d` |
| C.2 | 🟢 | Registration reachability: ONE assertion over `@mcp.tool` names and `.claude/agents/*.md` | ✅ `4f980a9` |
| C.3a | 🟡 | The `promote` transition — the `PENDING_REVIEW → PROMOTED` lifecycle the spec declares and no code provided | ✅ `40508af` |
| C.3b | 🟡 | `evidence_base` extended to K, canonical and code together | ✅ `eb0f1d2` |
| C.3c | 🟡 | Route 3 collapse: pending `[V]` verdicts → one structured decision → promote, support edge staged | ✅ `aeaa860`, verified live `45d9d4a` |
| C.4a | 🟡 | Close D-3: `_TYPE_EDGES` mirrors the canonical; `informed_by` becomes emittable | ✅ `14aa957` |
| C.4b | 🟡 | Boundary bridge: `chimera-propose-links` proposes `informed_by` onto a hand-authored node | ✅ `3d550a7` |
| C.5 | 🔴 | Mid-read verification: queue a claim on a native background task; probe-first, may end at its probe | ✅ probe passed 3/3; queue mode live — agent-type binding owed to a restart (D-8) |
| C.6 | 🟢 | W2 handoff: a promote-candidate becomes a runnable extract carrying its gap sentence | ▶ ready |
| seal | — | phase_review: three routes measured, not asserted | — |

**Dependencies:** C.1 gates C.3a/b/c, C.4, C.5 — the sprints that change friction. C.3a and C.3b
both precede C.3c. C.2 and C.6 are independent. Seal requires C.1/C.2/C.3a/C.3b/C.3c/C.4.

---

## Design Decisions

**D1 — Friction is measured in Architect actions.** Per route, per committed artifact, in three
registers: **invocations**, **context switches** (crossings of the Claude Code ↔ Obsidian
boundary), and **manual transcription** (characters retyped that a machine already held).
Deliberately crude: a crude observable beats an eloquent impression, and there was none.

**D2 — The nudge is composition drift, not an action-count cap.** What I1.4 protects is
longitudinal: if promoted K nodes accumulate while hand-authored T/I nodes stop appearing, the
vault has become a record of what the pipeline found rather than of the Architect's thinking.
Measured from the vault itself. **Corollary — the design rule:** where a route is against the
grain, fix *that* route; never handicap another to restore parity.

**D3 — No tool writes a judgment *body*; a tool MAY write its *edges*.**

I0.5 reserves the body: "Judgment-type nodes (T/I/D) have Architect-authored bodies." D-7 settles
that an edge is metadata, not content. Together: a tool appending `informed_by` to a hand-authored
T-node's `graph_edges` authors no judgment. The line is the body — no tool creates a judgment
node, opens one, or writes prose into one.

This matters because **edges are format work.** Filling `informed_by` correctly means knowing the
exact key, the exact wikilink stem, and the exact list syntax — machine work, not judgment, and
not the work being done at the moment a thought is written. The route-1 datum: *"create a T node
via keyboard shortcut, fill the contents, no links."*

The vault sharpens this rather than merely confirming it. Five of six T-nodes carry
`derives_from` edges — 15 links, all to deep-read nodes — so the Architect **does** fill edges,
in a later pass. What is never filled is `informed_by`, the one key absent from the template.
**Template presence predicts edge population**, which is why C.4's deliverable is a template slot
plus a proposal, not a better way to type YAML.

The mechanism already exists — `link_nodes` stages a patch, the Architect applies it (D5). Only
the vocabulary entry is missing (`ENFORCEMENT_DEBT` D-3), which C.4 closes.

**Propose; never auto-apply.** The permitted act is a *proposal*: Claude observes a hand-authored
node left unlinked and proposes the edge it can honestly justify. The apply is an **explicit
Architect order** — not inferred from context, not defaulted on, not batched by convenience. D-7
makes the edge legal to write; it does not license the machine to decide the edge *should exist*.
Proposing is machine-time, ordering is human-time (I0.1), and the two stay visibly separate.

**Consequence recorded, not scoped:** edges are format work, humans do not do format work by hand,
and no tool was permitted to do it on the judgment side. That is a candidate root cause for the
typed graph standing empty for months (`friction-260708-01`; the Phase N.B cancellation), and a
better explanation than "the write path was missing" — the write path shipped in Phase O; its
vocabulary did not reach the judgment side.

**D4 — The support edge is `evidence_base`, extended to K.** `depends_on` was retired in Phase O
and again by canonical r2; it survives only as `write_result`'s parameter, pinned to a coordinated
rename with K.1 (`ENFORCEMENT_DEBT` D-4) — **this phase does not touch it**. Extending
`evidence_base` to K is a Tier-2 amendment under I2.2, ratified 2026-08-12 and documented in
`NODE_ONTOLOGY.md`, justified against I0.2 and I1.3.

**D5 — Staging is machine-time; applying is human-time.** `link_nodes` stages a patch;
`apply_link_patch` applies it. Sprints automate the staging only; the apply call is the commit
(I0.1). The two-call split is what makes the gate structural — a single writing tool would
collapse propose and commit into one machine act. **Known limit:** the patch is consumed on apply
(`staging_service.py:294,301`), so the gate is enforced at the moment and leaves no durable record
of having been. Edge-level provenance is impossible under D-7 by construction; any such record
belongs at the node level and to Phase K.

**D6 — C.5's substrate is the harness, not the repo.** W1's judgment must run in a subagent and
MCP cannot spawn subagents, so `TaskService` can never host a backgrounded W1 at any budget. The
mechanism that works is Claude Code's native background Task. The risk is therefore dependency on
harness behaviour no test here can pin — hence probe-first, and a sprint permitted to end at its
probe with a recorded finding.

**D7 — Prefer invoking an affordance over building one.** Background tasks, structured
multi-select decisions, skill invocation by description, completion notification — the harness
supplies these. A sprint building a queue, a picker, or a scheduler should stop and check whether
it is rebuilding the harness. `chimera-dependency-veto`'s logic, pointed inward.

---

## Cross-Sprint Red Lines

- ❌ **No tool authors a T/I/D *body***, and no tool creates a judgment node — no writer, no
  staging path, no body-filler, no prose scaffold (I0.5). Writing an *edge* onto an existing
  hand-authored node is permitted (D3, D-7). The line is the body.
- ❌ **Nothing auto-commits, and nothing auto-applies.** Machine-time proposes and stages;
  human-time applies and promotes on an explicit order (I0.1). No skill calls `apply_link_patch`.
  An edge patch is never applied because it was obvious, recent, or the only one pending.
- ❌ **No friction-changing sprint lands before C.1.** A route whose before-state was never
  recorded cannot be shown to have kept parity.
- ❌ **No route privileged.** Where a route is against the grain, fix that route — never
  handicap another (D2).
- ❌ **Nothing ships unregistered.** Covered by C.2, and the seal exercises new components
  through the **live client** — never in-process imports (`friction-260811-01`).
- ❌ **Do not rename `write_result`'s `depends_on` parameter** — pinned to Phase K.1.
- ❌ **Do not relax a closed `Literal` to `str`** — R5a is discharged only while they stay closed.
- ❌ **W2 consumption stays thin** — no map parsing, ranking, or persistent-map dependency.
- ❌ **No new MCP server**; `.mcp.json` stays two.
- ❌ No opportunistic refactoring.

---

## Hard Sealing Conditions

1. **(C.1)** The metric is defined and all three routes carry a recorded baseline in D1's three
   registers, plus a composition-drift baseline (D2), before any friction-changing sprint runs.

2. **(C.2)** One assertion covers `@mcp.tool` names and `.claude/agents/*.md`; every skill is
   covered and every agent parses. Verified by `pytest` **plus a negative control proving the
   check can be made to fail.**

3. **(C.3a+b+c)** Pending `[V]` verdicts are reviewed and promoted in one structured decision, and
   the `evidence_base` patch is staged with correct type and direction. No manual YAML, no
   `depends_on`.

4. **(C.4)** A T/I/D node hand-authored in Obsidian and left unlinked — the observed default —
   receives a **proposed** `informed_by` edge naming what the session consulted; the Architect
   **explicitly orders** the apply and the edge lands through the staged-patch path. No tool wrote
   its body, and nothing applied without that order. Verified on a real authoring session.

5. **(C.5 — may end at its probe)** A claim queued mid-read returns its verdict without blocking,
   and both W1 modes coexist. Or the probe's failure is recorded as the sprint's finding.

6. **(C.6)** A W2 promote-candidate triggers extract with its gap context, with no dependency on
   the map's persistence.

7. **(VISION gate — Architect-assessed)** Three sessions run with seal-time friction numbers
   recorded beside the baseline, and no route reported as against the grain. If a route got worse,
   this condition does not seal green regardless of how the sessions felt. Composition drift is
   longitudinal: L.C delivers the baseline; a widening trend later is a re-opening trigger, not a
   seal blocker.

---

## Settled Questions

- **`evidence_base` extended to K** — ratified 2026-08-12 (D4); shipped in C.3b.
- **`apply_link_patch` writing committed nodes is not an I1.2 violation** — settled 2026-08-12 on
  ontological grounds: an edge is frontmatter metadata, not a first-class relation object carrying
  its own identity and provenance. Appending one does not modify the committed node's *content*,
  which is what I1.2's writer clause governs. No tier guard is owed. Recorded as `ENFORCEMENT_DEBT`
  **D-7**, with the definitional basis in `NODE_ONTOLOGY.md` §2.

---

## Out of Scope

- Inline rendering of verdicts into the reading context → Phase L.D.
- W2's role change itself → Phase L.D. L.C prepares the interface; L.D reshapes W2.
- Node-level provenance for applied edges (D5's known limit) → Phase K.
- Deep Obsidian integration beyond the vault filesystem → Phase S+.
- 20-paper breadth regime; novelty three-state operationalization (→ H/K); multi-user.
- **Phase L's own seal.** L has six sprint records and no `phase-review.md`; its VISION gate has
  never been assessed. Recorded so the parent seal is not forgotten under its children.
