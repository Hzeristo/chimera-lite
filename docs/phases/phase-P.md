# Phase P — Prose-Grounded Edge Inference

**Status:** 🌱 Queued (friction-driven 2026-07-08)
**Sealed predecessor:** Phase O — Exocortex Write Surface
**Driving friction:** `docs/logs/friction-260708.md` (friction-260708-01)

## Mission

Close the last manual step in the exocortex write path. After the user writes a thought body
(the research judgment — theirs alone), Claude reads the prose, infers the typed edges the prose
ALREADY STATES ("derives from X", "contradicts Y", "synthesizes A + B"), and stages them through
Phase O's existing review flow. The user reviews and approves. No more hand-lifting
"Triggered By: [[X]]" prose into `derives_from` frontmatter by hand.

## The division of labor (from the friction)

- **Body = research judgment** — only the user can write it.
- **graph_edges = structuring relationships already stated in the body** — mechanical extraction
  plus type assignment. A machine task the user should hand off, not do by hand.

## Explicitly NOT Phase O's deferred "AI infers edges"

Phase O's out-of-scope item was AUTONOMOUS BULK inference (scan the ~250 existing K Nodes, invent a
graph — high hallucination risk; "Phase P+ if ever"). This phase is the opposite risk profile:

| | Deferred (autonomous bulk) | Phase P (this) |
|---|---|---|
| Trigger | autonomous / batch | USER-TRIGGERED |
| Scope | ~250 papers | SINGLE node |
| Gate | none | REVIEW-GATED (staging → approve) |
| Grounding | free invention | GROUNDED IN THE USER'S OWN PROSE |

Claude types what the author already wrote; it does not invent relationships. That difference is
what promotes "AI infers edges" from "Phase P+ if ever" to a near-term, friction-driven phase.

## Sprint Sequence (sparse manifest)

| Sprint | One-line goal |
|---|---|
| P.0 | Audit: body-relationship extraction (the existing `_wikilink_targets` / `_collect_graph_links` parsing), edge-type assignment from prose cues, and reuse of the Phase O stage-a-patch flow |
| P.1 | Read a node body → propose typed edges grounded in the prose → stage them via `link_nodes` / `apply_link_patch` for review (never auto-apply) |
| P.2 | Verify: a thought body stating "derives from X / contradicts Y" → correctly-typed edges staged → user approves → zero hand-filling |

## Hard Sealing Conditions

1. Given a thought body that states N relationships, the flow stages N correctly-typed edges, each
   grounded in a sentence the body actually contains.
2. Every proposed edge goes through Phase O staging → user review (never auto-applied).
3. On a body that states NO relationships, it stages nothing (no free invention).

## Design leaning

Likely a thin addition — or a skill (like `chimera-academic-observe`) — over the sealed Phase O
tools plus the existing body-wikilink parsing. Claude does the type inference; `link_nodes` /
`apply_link_patch` do the staged write. Reuse, not new infrastructure.

## Out of Scope

- Autonomous bulk inference over the ~250 existing K Nodes — stays deferred (the high-hallucination
  version this phase is explicitly carved out from).
- Auto-APPLYING inferred edges — must stay review-gated.
