# Phase L.C — Colligo: Candidate Consumption Paths

**Status:** Queued (after Phase L.B seal)
**Predecessor:** Phase L.B (Integratio)
**Etymology:** Latin *colligō* — to bind together, to infer. Whewell's term for
the cognitive moment scattered observations bind into a principle. Here: binding
candidate material (W1/extract outputs) into committed artifacts (K/T/I nodes).

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

## Mission

Bind candidate material to committed artifacts with zero manual wiring and equal
support for all three routes. Establish proof-graph normal form: every committed
node's support chain is traceable (strong [V] or documented-weak [P]/[U]); no
candidate orphaned beyond a review threshold.

Three constraints from architectural reconciliation:
1. **T-nodes are observations, not AI audits.** Authorship is the Architect's.
   AI outputs may inform; provenance records `informed_by`, never `derives_from`.
2. **W2 consumption stays thin.** W2 may become an incremental gap-finder or merge
   into field-ingestion (Phase L.D). L.C does NOT build thick W2-consumption paths.
   The W2→extract link is interface-only, agnostic to map-vs-query.
3. **Seal on real fixtures, not scale.** 3-4 real papers suffice. 20+ papers /
   3+ subfields is future work.

---

## Sprint Sequence

| Sprint | Risk | One-line goal |
|--------|------|---------------|
| C.0 | — | Audit: current handoff gaps (K→W1, extract→W1, provenance automation surface); confirm W2's uncertain future to scope C.2 minimally |
| C.1 | 🟡 | K-node claims → W1 batch offer: extract completion surfaces "verify these N claims" one-click |
| C.2 | 🟢 | W2 recommendation → extract: thin interface only — "a paper recommendation triggers extract," agnostic to map-vs-query. Minimal by design (W2 may die) |
| C.3 | 🟡 | W1 verdict → depends_on auto-edge: promote writes the edge, no hand-editing |
| C.4 | 🟡 | Informed_by provenance: authoring T/I while viewing AI material auto-records `informed_by` (not `derives_from`) |
| C.5 | 🔴 | Stream-mode W1: queue + background + inline verdict. Heavy; defer to L.D if over one sprint |
| seal | — | phase_review: three consumption routes run on real fixtures with equal friction |

**Dependencies:** C.0 precedes all. C.1/C.3/C.4 parallel-eligible after C.0.
C.2 is thin, independent. C.5 depends on C.1+C.3. Seal requires C.1/C.3/C.4;
C.2 is minimal; C.5 may defer to L.D.

---

## Cross-Sprint Red Lines

- ❌ **T/I nodes are Architect-authored.** No "W2 map → T-node" auto-conversion.
  Provenance records `informed_by` at most. Authorship is non-transferable.
- ❌ **W2 consumption stays thin.** C.2 is an interface, not a workflow. Do not
  build map-parsing, candidate-ranking, or persistent-map logic — W2's artifact
  form is uncertain (Phase L.D). The link survives whether W2 outputs a map or a
  query result.
- ❌ **No privileging of routes.** Any feature smoothing one route must not add
  ceremony to the others.
- ❌ **Provenance is structural.** Auto-edges (C.3) and informed_by (C.4) live in
  frontmatter, not comments.
- ❌ **Stream-mode does not replace batch.** Both W1 modes coexist (C.5).
- ❌ **No new MCP server.** Skills orchestrate existing primitives.
- ❌ No opportunistic refactoring.

---

## Hard Sealing Conditions

1. **(C.1)** extract completion surfaces "verify N claims" one-click; triggering
   queues all N to W1. Verified on a real extract (e.g., PyraVid, 3-5 claims).

2. **(C.2)** A W2 paper recommendation (map entry OR query result — interface
   handles both) triggers extract with the gap-context carried into metadata.
   Thin: no persistent-map dependency. Verified on a real W2 run.

3. **(C.3)** Promoting a W1 verdict writes the `depends_on` edge in the target's
   frontmatter automatically. No manual YAML. Verified: promote a [V], inspect edge.

4. **(C.4)** Authoring a T/I node while viewing a W2 map or extract K-node
   auto-fills `informed_by`. Architect may amend. Verified on a real authoring session.

5. **(C.5 — deferrable)** Queue a claim mid-read; W1 runs background; verdict
   appears inline without blocking. If heavier than one sprint, defer to L.D;
   seal on C.1/C.3/C.4.

6. **(VISION gate — Architect-assessed)** Three sessions — pure observation /
   AI-assisted / batch promote — run with equal friction and honest provenance.
   No route against the grain.

---

## Design Decisions

**D1 — Informed_by, not derives_from.** T/I authored while viewing AI material
carry `informed_by` (context, not derivation). `derives_from` is reserved for
machine-synthesized edges. Human observation informed by a tool is not derivation.

**D2 — W2 consumption is interface-only (thinning decision).** C.2 does not parse
maps or rank candidates. It exposes one action — "recommend this paper → extract"
— that works whether the recommendation is a persistent map entry or a fresh query
result. W2's artifact may die in L.D; C.2 must not depend on its form. This is the
primary thinning: no thick investment in a possibly-dying node.

**D3 — Auto-wiring is heuristic with override.** C.3/C.4 use recency/open-pane/
explicit-action heuristics. The Architect always amends. Defaults, not locks.

**D4 — Equal-friction principle.** Every operation tested against: "does this
smooth route X while taxing route Y?" If yes, redesign. L2 augments; it does not
nudge toward AI-dependence or away from it.

**D5 — Stream-mode async, splittable.** C.5 queues claims, returns verdicts async.
If complex, splits: C.5a (queue+background) seals; C.5b (inline display) defers.
Batch-offer (C.1) + auto-edge (C.3) already unlock route 3; stream is enhancement.

---

## Out of Scope

- W2 role change itself (Phase L.D). L.C prepares the interface; L.D reshapes W2.
- Deep Obsidian integration beyond command-palette + frontmatter (Phase S+).
- 20-paper breadth regime.
- Novelty three-state operationalization (Phase H/K).
- Multi-user, deployment.

---

## Notes

C.2 is deliberately 🟢 (low-risk, thin). The temptation is to build rich W2-map
consumption — resist it. W2's artifact form is uncertain (Phase L.D may replace
maps with incremental queries or merge W2 into field-ingestion). Any thick
W2-consumption logic built now is work thrown away when W2 reshapes. The interface
("a recommendation triggers extract") is all that survives the transition.

C.5 weight: stream-mode W1 needs Task backgrounding + async verdict return + queue
management. Estimate 2-3 sprints if full. Recommend attempting in L.C; if blocked,
seal on C.1/C.3/C.4 and defer C.5 to L.D. Route 3 is already unlocked by C.1+C.3.

The T-node-authorship clarification (D1) corrects a prior ST error: T-nodes were
briefly framed as "W2 audit reports." They are observations, possibly AI-informed,
authored by the Architect. This is load-bearing for human-time supremacy.
