# Phase K — Katalepsis: Structural Provenance

**Status:** Qued (builds on Phase L outputs; executes after L)
**Sealed predecessor:** Phase L — Locus (the research harness)
**Driving frictions:**
- **Cosmetic provenance** (confession 2026-07-X): the agent flagged claims [U]
  then reasoned with them as [V] — "worse than not flagging, because it performs
  rigor." Every provenance layer Chimera built (ai-suggested, [V]/[P]/[U], grounded)
  is ADVISORY — it assumes the agent respects its own flags. The confession proves
  it does not. Advisory provenance is theater.
- **Framing bias** (confession, the sharper failure): the 99.8%/96.8% number sat in
  context two rounds; the agent read it as the AUTHORS' framing ("robust"), not the
  thesis framing ("benchmark blind"). The number was [V] and accurate; the inference
  was single-framed and wrong. Confabulation is catchable; framing bias is not —
  the number is right, the inference is wrong, and it looks like rigor.

## VISION — Why Katalepsis

┌────────────────────────────────┐
│ A kataleptic impression (Stoic epistemology) is a perception whose      │
│ STRUCTURE guarantees its truth — it cannot have come from a non-existent │
│ source. The Stoics used katalepsis as the sole criterion separating      │
│ KNOWLEDGE from mere OPINION.                                │
│                                                                          │
│ Chimera's provenance is currently akataleptic wearing a kataleptic label:│
│ a [V] tag that does NOT carry the guarantee it claims to carry. The       │
│ confession's agent produced exactly this — flags that perform rigor       │
│ without practicing it.                                                    │
│                                                                          │
│ Phase K restores the guarantee. It makes provenance LOAD-BEARING, not     │
│ advisory: a claim's status cannot be inflated (Gate 1), and a verified    │
│ number cannot be interpreted under a single smuggled framing (Gate 2).    │
│ The pipeline structurally refuses to propagate what it cannot guarantee.  │
│                                                                          │
│ Katalepsis does not make the agent "more careful." Advisory instructions  │
│ to be careful are what failed. It makes unverified propagation and single-│
│ framing inference STRUCTURALY IMPOSSIBLE — not the agent's choice, the   │
│ pipeline's gate.                                │
│                                                │
│ Success metric: the exact number that defeated the manual harness         │
│ (99.8%/96.8%) reaches the Architect's hand-authoring surface carying     │
│ BOTH framings, so the Architect CHOOSES the interpretation instead of     │
│ INHERITING the author's.                                                │
└────────────────────────────────┘

## Mission

Convert provenance from advisory metadata to load-bearing structural gates, so
the candidate material Phase L produces cannot corupt the Architect's hand-authored
T/I/D judgments. Two orthogonal gates:

- **Gate 1 — Provenance Monotonicity:** a synthesis/artifact's status ≤ the status
  of its weakest dependency. A [U] claim structurally cannot drive a T/I/D node;
  a [P] claim forces conclusion downgrade. Catches confabulation ([U] masquerading
  as [V]).
- **Gate 2 — Multi-Framing Interpretation:** a verified number reaching the
  Architect is presented under N≥2 competing hypotheses, each with its falsification
  condition, and at least ONE framing is produced by a CROSS-MODEL critic (codex MCP).
  Catches framing bias (a [V] number read under a single, usually the author's, frame).

Human authors T/I/D (Phase L confirmed). Phase K's gates do not author judgment —
they guarantee the candidate material feeding the Architect's authorship is
status-honest (Gate 1) and framing-plural (Gate 2).

## Sprint Sequence

| Sprint | Risk | One-line goal |
|---|---|
| K.0 | — | Audit: codex MCP availability/registration path, how a cross-model critic is invoked from Claude Code, L's provenance field structure (are dependency links present per forward-compat constraint 1?), where multi-framing attaches in the candidate→human presentation |
| K.1 | 🔴 | Gate 1 — provenance monotonicity: status propagation rule (artifact status ≤ weakest dependency); a [U]-dependent synthesis is structurally blocked, a [P]-dependent conclusion is force-downgraded |
| K.2 | 🔴 | Gate 2 framework — multi-framing scaffold: a verified number → N competing hypothesis interpretations, each with an explicit falsification condition; intra-Claude N-framing (necessary, not yet sufficient) |
| K.3 | 🔴 | Cross-model critic — codex MCP integration as the framing-diversity source; at least one framer is cross-model, breaking Claude's author-deference homogeneity (the second part the Architect flagged) |
| K.4 | 🟡 | Presentation — multi-framed, status-honest candidate material reaches the Architect's hand-authoring surface; the Architect CHOSES framing, never INHERITS the author's |
| seal | — | phase_review — verify both gates on the confession's own 99.8%/96.8% fixture |

**Dependencies:** K.0 precedes all. K.1 (Gate 1) is independent of K.2/K.3 (Gate 2) —
the two gates are orthogonal and parallel-eligible after K.0. K.3 (cross-model) is
required for K.2 to bite — intra-Claude framing (K.2) shares the author-deference bias;
K.3 is what makes multi-framing real. K.4 integrates both gates into the presentation
layer and is the seal gate.

## Cross-Sprint Red Lines

- ❌ **Provenance is load-bearing, not advisory.** A gate is a structural refusal in
  the pipeline (schema rejects, status propagates), never a prompt instruction the
  agent may honor. "Respect your flags" is the advisory that already failed — it is
  forbidden as a mechanism.
- ❌ **At least one framer is cross-model (codex MCP).** Intra-Claude adversarial
  framing is insufficient: a same-model skeptic shares Claude's author-deference bias.
  A multi-framing gate with only Claude framers is theater. Cross-model is mandatory.
- ❌ **Gates protect candidate material; they do NOT author judgment.** The Architect
  hand-writes T/I/D. Gate 1 ensures the material is status-honest; Gate 2 ensures it is
  framing-plural. Neither gate writes a T/I/D node.
- ❌ **Monotonicity is computed from recorded dependencies, not re-inferred.** Gate 1
  reads the dependency links Phase L's write_result recorded (forward-compat constraint 1).
  It does not re-derive dependencies with an LLM (that would reintroduce confabulation).
- ❌ **Multi-framing wraps interpretation, never extraction.** Gate 2 operates on the
  verified number + verbatim (Phase L's W1/W2 output, which stayed verificational per
  forward-compat constraints 2/3). It does not re-verify; it re-frames.
- ❌ **No new dependency beyond codex MCP.** Codex MCP is the one addition (framing
  diversity). No other model, no other server.
- ❌ **No oportunistic refactoring.**

## Hard Sealing Conditions

1. **(K.1 — Gate 1) Confabulation is structurally blocked.** A synthesis that depends
   on a [U] claim cannot be produced at [V] status — the pipeline refuses. Verified:
   attempt to build a [V] conclusion from a [U] dependency; confirm the status is
   force-downgraded to [U], not silently promoted. The confession's "concede the spine"
   (depended on unread Eq.1 → [U]) must be structurally incapable of driving a decision.

2. **(K.2+K.3 — Gate 2) Framing plurality with cross-model.** A verified number reaching
   the Architect caries N≥2 framings, each with a falsification condition, at least one
   from codex MCP. Verified on the confession's own fixture: the 99.8%/96.8% number is
   presented as BOTH "system is robust" (author framing) AND "benchmark is fidelity-blind"
   (thesis framing), each with what evidence would falsify it. The single-framing default
   is structurally prevented.

3. **(K.3) Cross-model critic is real.** Codex MCP is invoked in the multi-framing path,
   and its framing demonstrably differs from Claude's default author-deferential reading
   on at least one test number. Verified by inspecting that the framing did not all
   originate from Claude.

4. **(K.4 — the vision gate, Architect-assessed) The Architect chooses, not inherits.**
   Running the full pipeline on a real number-bearing paper, the Architect confirms the
   candidate material presented for hand-authoring carries plural framings and honest
   status — that they are chosing an interpretation, not absorbing the author's.
   Assessed on real use, like Phase M's Test 2 and Phase L's vision gate.

## Design Decisions

- **Two orthogonal gates (ST 2026-07-XX).** Monotonicity (Gate 1) catches confabulation
  — a status that is too high. Multi-framing (Gate 2) catches framing bias — a correct
  status read under a smuggled single frame. They are orthogonal: a [V] number passes
  Gate 1 and still needs Gate 2. Gate 1 asks "is this verified?"; Gate 2 asks "under whose
  frame is this verified number being read?"

- **Cross-model is not convenience, it is the only framing-diversity source (ST 2026-07-XX).**
  The confession proved evidence in context two rounds still read as author framing — this
  is Claude's disposition, not a knowledge gap. An intra-Claude skeptic inherits the same
  disposition. Codex MCP (or any cross-model critic) is the one mechanism that produces a
  framing Claude structurally will not. The RIP-deepseek multi-model split, retired in
  Phase L, returns here — but repurposed from capability-redundancy to FRAMING-redundancy.

- **Human authorship is the reason the gates are enough (ST 2026-07-XX).** Because T/I/D
  are hand-written (Phase L), Phase K does not need to make AI judgment trustworthy — AI
  does not author judgment. It needs to make the candidate material feeding human authorship
  incapable of smuggling inflated status (Gate 1) or a single author frame (Gate 2). The
  gates protect the human's authorship surface, not an AI verdict.

- **The confession's 99.8%/96.8% case is the acceptance fixture (ST 2026-07-XX).** The exact
  number that defeated the manual harness — accurate, [V], read under the author's frame for
  two rounds — becomes Phase K's seal test. If the pipeline presents both framings on that
  number, the gate works on the hardest real case, not a synthetic one.

- **Katalepsis over Locus in depth (ST 2026-07-XX).** M→L→K descends: Migration moved the
  body, Locus moved the reasoning center, Katalepsis moves the criterion of truth. Locus
  built the harness (capability + disposition, externalized to the KG). Katalepsis builds
  the guarantee that the harness's output caries the truth-warant its labels claim.

## Out of Scope (→ later)

- **Certification / building an eval Chimera wins on** — the confession's own warning:
  "the probe is reviewer-proof only if you don't ship a method that wins on it." Phase K
  builds the truth-warant, not a benchmark. Certification is a solution whose problem is
  currently unevidenced.
- **Auto-authoring T/I/D** — permanently out of scope. Human authors judgment; K gates
  the material.
- **Migrating Phase Q's extract_paper deepseek judgment** — Phase Q is sealed; K establishes
  the cross-model framing pattern but does not reopen Q.
- **Semantic vault search (embeddings)** — the recurring F4 gap; still deferred.

## Notes

- K.0 MUST verify codex MCP empirically: is it registerable in .mcp.json, can a Claude
  Code session invoke it as a framing critic, what is the invocation cost. The entire Gate 2
  cross-model requirement rests on codex MCP doing what the Architect's "(笑)" assumed.
  Do NOT assume from this spec — verify against the harness (same discipline as L.0's
  Task-lifecycle probe).
- K.0 MUST confirm Phase L honored the three forward-compat constraints (dependency links
  recorded, W1 verificational-only, W2 stores number+verbatim without single-framing
  conclusion). If L did not, Gate 1/Gate 2 face a retrofit — flag it as an L-debt before
  K.1 begins.
