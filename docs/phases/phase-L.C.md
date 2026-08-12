# Phase L.C — Colligo: Candidate Consumption Paths

**Status:** Queued (after Phase L.B seal)
**Predecessor:** Phase L.B (Integratio)
**Etymology:** Latin *colligō* — to bind together, to infer. Whewell's term for
the cognitive moment scattered observations bind into a principle. Here: binding
candidate material (W1/extract outputs) into committed artifacts (K/T/I nodes).
**Audit:** `docs/audits/L.C.0.md` (C.0, complete). Sprint detail belongs in the batch plan,
not here.

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
1. **T/I/D nodes are Architect-authored.** AI may inform; provenance records `informed_by`,
   never `derives_from`. Authorship is non-transferable (I0.5).
2. **W2 consumption stays thin.** W2's artifact form carries no protection; the link must
   survive its reshaping in L.D.
3. **Seal on real fixtures, not scale.** 3-4 real papers suffice.
4. **Measure before smoothing.** No friction-changing sprint lands before the instrument exists.

---

## Sprint Sequence

| Sprint | Risk | One-line goal |
|--------|------|---------------|
| C.0 | — | ✅ Complete — `docs/audits/L.C.0.md` |
| C.1 | 🟢 | Friction instrument: define the metric, baseline all three routes + composition drift |
| C.2 | 🟢 | Registration reachability: ONE assertion over `@mcp.tool` names and `.claude/agents/*.md`. Homes `friction-260811-01` |
| C.3a | 🟡 | The `promote` transition: implement the `PENDING_REVIEW → PROMOTED` lifecycle the artifact spec declares and no code has ever provided |
| C.3b | 🟡 | `evidence_base` extended to K, canonical and code together (D4) |
| C.3c | 🟡 | Route 3 collapse: pending `[V]` verdicts → one structured decision → promote; the `evidence_base` patch is staged, not hand-written |
| C.4 | 🟡 | Boundary bridge: close D-3 (`informed_by` / `collides_with` emittable), then stage an `informed_by` patch onto a hand-authored T/I/D node. The tool writes the edge, never the body |
| C.5 | 🟡 | Mid-read verification: queue a claim on a native background task, verdict returns by notification. Probe-first; may end at its probe |
| C.6 | 🟢 | W2 handoff: a promote-candidate becomes a runnable extract carrying its gap sentence. Interface only |
| seal | — | phase_review: three routes measured, not asserted |

**Dependencies:** C.1 gates C.3a/b/c, C.4, C.5 — the sprints that change friction. C.3a and C.3b
both precede C.3c and are parallel-eligible with each other. C.2 and C.6 are independent. Seal
requires C.1/C.2/C.3a/C.3b/C.3c/C.4. Sprint detail: `docs/plans/Phase-L.C-batch.md`.

---

## Design Decisions

**D1 — Friction is measured in Architect actions.** Per route, per committed artifact, in three
registers: **invocations**, **context switches** (crossings of the Claude Code ↔ Obsidian
boundary), and **manual transcription** (characters retyped that a machine already held).
Deliberately crude: a crude observable beats an eloquent impression, and today there is none.

**D2 — The nudge is composition drift, not an action-count cap.** What I1.4 protects is
longitudinal: if promoted K nodes accumulate while hand-authored T/I nodes stop appearing, the
vault has become a record of what the pipeline found rather than of the Architect's thinking.
Measured from the vault itself (`vault_query` by type and `chimera_tier`). **Corollary — the
design rule:** where a route is against the grain, fix *that* route; never handicap another to
restore parity.

**D3 — No tool writes a judgment *body*; a tool MAY write its *edges*.** *(Revised 2026-08-12 —
supersedes "informed_by is offered, never written.")*

I0.5 reserves the **body**: "Judgment-type nodes (T/I/D) have Architect-authored bodies." D-7
settled that an **edge is metadata, not content**. Together: a tool that appends `informed_by` to
a hand-authored T-node's `graph_edges` authors no judgment and violates nothing. The earlier
reading — that no tool may touch a T/I/D node at all — over-extended I0.5 from bodies to whole
files.

This matters because **edges are format work.** Filling `informed_by` correctly means knowing the
exact key, the exact wikilink stem, and the exact list syntax. That is machine work, not judgment,
and the Architect does not do it: the route-1 datum is *"create the node via keyboard shortcut,
fill the contents, **no links**,"* and `informed_by` is **skipped entirely**. All six vault T-nodes
carry empty edge lists.

So the mechanism is the one that already exists — `link_nodes` stages a patch, the Architect
applies it (D5) — and the only thing missing is the vocabulary entry (`ENFORCEMENT_DEBT` D-3).
The tool never opens the body.

**Propose; never auto-apply (Architect, 2026-08-12).** The permitted act is a *proposal*: Claude
observes a hand-authored node that is unlinked, and proposes the `informed_by` edge it can
honestly justify. The apply is an **explicit Architect order** — not inferred from context, not
defaulted on, not batched by convenience. Legality here rests on the edge being metadata (D-7);
it does **not** license the machine to decide *that* the edge should exist. Proposing is
machine-time, ordering is human-time (I0.1), and the two must stay visibly separate.

**Wider consequence, recorded not scoped:** edges are format work, humans do not do format work by
hand, and no tool was permitted to do it on the judgment side. That is a candidate root cause for
the typed graph being empty for months (`friction-260708-01`; the Phase N.B cancellation), and it
is a better explanation than "the write path was missing" — the write path existed since Phase O
and its vocabulary simply excluded the judgment edges.

**D4 — The support edge is `evidence_base`, extended to K.** `depends_on` was retired in Phase O
and again by canonical r2; it survives only as `write_result`'s parameter, pinned to a coordinated
rename with K.1 (`ENFORCEMENT_DEBT` D-4) — **this phase does not touch it**. Extending
`evidence_base` to K is a Tier-2 amendment under I2.2, ratified 2026-08-12, documented in
`NODE_ONTOLOGY.md`, justified against I0.2 and I1.3. C.3 carries it as its first task.

**D5 — Staging is machine-time; applying is human-time.** `link_nodes` stages a patch;
`apply_link_patch` applies it. C.3 automates the staging only; the apply call is the commit (I0.1).

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

- ❌ **No tool authors a T/I/D *body*** — no writer, no staging path, no body-filler, no prose
  scaffold, no node created by a tool (I0.5). Writing an *edge* onto an existing hand-authored
  node is explicitly permitted (D3 + D-7): metadata, not content. The line is the body.
- ❌ **No friction-changing sprint lands before C.1.** A route whose before-state was never
  recorded cannot be shown to have kept parity.
- ❌ **No route privileged.** Where a route is against the grain, fix that route — never
  handicap another (D2).
- ❌ **Nothing auto-commits, and nothing auto-applies.** Machine-time *proposes* and stages;
  human-time applies and promotes on an explicit order (I0.1). An edge patch is never applied
  because it was obvious, recent, or the only one pending.
- ❌ **Nothing ships unregistered.** Covered by C.2, and the seal exercises new components
  through the **live client** — never in-process imports (`friction-260811-01`).
- ❌ **Do not rename `write_result`'s `depends_on` parameter** — pinned to Phase K.1.
- ❌ **W2 consumption stays thin** — no map parsing, ranking, or persistent-map dependency.
- ❌ **No new MCP server**; `.mcp.json` stays two.
- ❌ No opportunistic refactoring.

---

## Hard Sealing Conditions

1. **(C.1)** The metric is defined and all three routes carry a recorded baseline in D1's three
   registers, plus a composition-drift baseline (D2), before any of C.3/C.4/C.5 executes.

2. **(C.2)** One assertion covers `@mcp.tool` names and `.claude/agents/*.md`; every skill is
   covered and every agent parses. Verified by `pytest` **plus a manual negative control that the
   check can be made to fail.**

3. **(C.3a+b+c)** Pending `[V]` verdicts are reviewed and promoted in one structured decision, and
   the `evidence_base` patch is staged automatically with correct type and direction. No manual
   YAML, no `depends_on`. Requires the `promote` transition to exist at all — it does not today
   (`result_service.py:56`), which is C.3a.

4. **(C.4)** A T/I/D node hand-authored in Obsidian and left unlinked (the observed default)
   receives a **proposed** `informed_by` edge naming what the session consulted; the Architect
   **explicitly orders** the apply and the edge lands through the staged-patch path — with **no
   tool having written its body**, and nothing applied without that order. Verified on a real
   authoring session.

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

- **`evidence_base` extended to K** — ratified 2026-08-12 (D4).
- **`apply_link_patch` writing committed nodes is NOT an I1.2 violation** — settled by the
  Architect 2026-08-12 on ontological grounds: an edge here is frontmatter metadata (a list of
  wikilink stems), not a first-class relation object carrying its own identity and provenance as
  in a KG. Appending one does not modify the committed node's **content**, which is what I1.2's
  writer clause governs. **No tier guard is owed.** Recorded in `ENFORCEMENT_DEBT` and
  `NODE_ONTOLOGY.md §2`; the L.B seal's flat "sole writer" phrasing is annotated there.

---

## Out of Scope

- Inline rendering of verdicts into the reading context → Phase L.D.
- W2's role change itself → Phase L.D. L.C prepares the interface; L.D reshapes W2.
*(`ENFORCEMENT_DEBT` D-3 was listed here as orthogonal and inert. It is neither — it is the
mechanism I0.5's provenance mandate has been missing, and C.4 closes it. See D3.)*
- Deep Obsidian integration beyond the vault filesystem → Phase S+.
- 20-paper breadth regime; novelty three-state operationalization (→ H/K); multi-user.
- **Phase L's own seal.** L has six sprint records and no `phase-review.md`; its VISION gate has
  never been assessed. Recorded so the parent seal is not forgotten under its children.
