# Sprint C.4b — The proposal path: `chimera-propose-links`

**Phase:** L.C (Colligo) · **Risk:** 🟡 MED · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` (C.4 split; C.4a closed D-3, this builds the proposal)
**Executed by:** Opus main session (skill authoring is reasoning-shaped — L.1b precedent).
**Outcome:** ✅ Pass — mechanism verified live; the semantic acceptance is the Architect's next
real authoring session.

## Design correction made during execution

The plan's task 4 read: *"on completion, propose an `informed_by` edge naming the artifact just
produced"*, attached to `chimera-deep-extract` and `chimera-w2-map`. **That is not buildable in
that place.** An edge is staged *from* the judgment node, and at extract/map completion the
judgment node does not exist yet — the Architect authors it afterwards, in Obsidian.

So the proposal is its own step, in its own skill (`chimera-propose-links`), triggered when the
node exists. The two producing skills were left alone rather than given a proposal they cannot
make.

## What was built

`.claude/skills/chimera-propose-links/SKILL.md`. Loop: resolve the judgment node → refuse anything
that is not T/I/D → read its existing `informed_by` → assemble candidates **from this session
only** → render one row per candidate with a mandatory `consulted:` reason → one
`AskUserQuestion` multi-select, no default → `link_nodes(edge_type="informed_by")` per ordered
candidate → report the staged paths and stop.

The `consulted:` line is the load-bearing part. A proposal the Architect cannot check is one they
can only rubber-stamp, and rubber-stamped provenance is the advisory-rigor failure this repo
exists to refuse.

## Constraints verified in code, not assumed

- **`link_nodes` resolves both endpoints against the vault root only**
  (`vault_read_adapter.py:417`). A **staged** `deep_read` node in `docs/staging/` therefore cannot
  be an `informed_by` target — it becomes linkable only after `ascend_node`. The skill states this
  rather than letting it fail at stage time.
- **The arXiv-id mis-resolution risk did not materialise.** `resolve_note_path` tries an arXiv-id
  match *first* (`:413-416`), and a stem like `w1_verdict__2606.16353` contains one, so it could
  have resolved to a paper PDF instead of the Harness artifact. Probed live: it resolved to
  `Harness\w1_verdict__2606.16353.md`. Correct — and now checked rather than hoped.

## Live mechanism probe

`link_nodes("Thought-visual memory substrates" → "w1_verdict__2606.16353", "informed_by")` staged a
patch carrying `from_type: thought`, `edge_type: informed_by`, and both paths resolved. Before
C.4a this call would have raised `Invalid edge 'informed_by' for node type 'thought'`.

**The patch was deleted immediately and asserts nothing.** This session was a build session, not a
research session: that T-node was not authored while consulting that verdict, so staging the edge
as a real proposal would have fabricated exactly what the skill's own red line forbids. Recorded
as a mechanism probe, not a provenance claim. Vault node confirmed untouched; `docs/staging/` empty
afterwards — which also demonstrates the propose/apply separation holds.

## The measurement error this sprint corrected

C.1's baseline claimed **all six T-nodes carry empty `graph_edges`**. False. Measured:

| `derives_from` | `informed_by` |
|---|---|
| **5 of 6 nodes populated, 15 links total**, every one to a deep-read node | **0 of 6** — the key is absent from the template |

The Architect *does* fill edges by hand, in a later pass; "no links" described the authoring
moment, not the final state. The corrected reading is stronger than the original claim: the edge
type present in `Tpl_thought.md` was populated 15 times and the edge type missing from it zero
times. **Template presence predicts edge population.**

That reframes C.4a's one-line template change from housekeeping into the intervention most likely
to move the number, and makes the vault-template sync (`NODE_ONTOLOGY.md` §5 — the Architect's
own copies, which the repo must not touch) the highest-leverage remaining action in this phase.

Corrected in `docs/audits/L.C.1-friction-baseline.md` §5, `phase-L.C.md` D3, and the C.4 design
notes.

## Verification

- Full suite **239 passed**, exit 0 (238 + the new skill's map entry; architecture map regenerated
  after the skill-count guard fired again).
- C.2's registry check fired on the new skill, as it did for C.3c — caught at creation.

## Acceptance

- [x] `informed_by` is proposable and stageable onto a hand-authored judgment node
- [x] Nothing writes a body; nothing creates a node; the skill never calls `apply_link_patch`
- [x] Endpoint resolution verified live, including the mis-resolution risk
- [x] Propose/apply separation demonstrated (patch staged, then removed; vault untouched)
- [ ] **Semantic acceptance** — a node the Architect authors *while consulting* an artifact, whose
      proposal they then order applied. Owed to the next real research session; cannot be
      manufactured in a build session without fabricating provenance.

## Red lines

All held. No body written, no node created, no patch applied, `informed_by` never proposed for a
`knowledge` node, no vault-wide fishing for plausible candidates, `derives_from` never proposed in
its place, and `informed_by` remains not support-bearing.
