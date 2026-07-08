# friction-260708-01 — Manual typed-edge filling after writing thought body

**Date:** 2026-07-08
**Status:** OPEN
**Phase context:** Phase O (write surface) sealing

## What I wanted to do
Write a thought node's body (the research content), then have the typed
graph_edges (derives_from / contradicts / synthesizes) filled automatically
from the relationships I already stated in the prose.

## What I actually did
Wrote the body, then manually lifted "Triggered By: [[X]]" prose links into
derives_from frontmatter by hand (for mix-arch + pitfalls nodes). Tedious,
mechanical, and exactly the metadata work I instinctively want to hand off
to Claude Code.

## The division-of-labor insight
Body = research judgment (only I can write it).
graph_edges = structuring relationships ALREADY STATED in the body
  (mechanical extraction + type assignment — the machine can do it).
Hand-filling typed edges is human labor spent on a machine task.

## Root cause
create_node / link_nodes take typed edges only as an explicit param.
Nothing reads the body's stated relationships and proposes typed edges.
The bridge from "prose I wrote" → "typed frontmatter" is manual.

## Ideal
After I write a thought body, Claude reads it, infers edge types from what
the prose SAYS ("derives from X", "contradicts Y"), and stages the typed
edges via the existing review flow. I review + approve. I never hand-fill
frontmatter again.

## NOT the same as Phase O's out-of-scope "AI infers edges"
Phase O deferred AUTONOMOUS bulk edge inference (scan 250 papers, invent a
graph — high hallucination risk). THIS is different:
  - USER-TRIGGERED (I just wrote this one node)
  - SINGLE-NODE (not bulk)
  - REVIEW-GATED (staging → I approve)
  - GROUNDED IN MY PROSE (Claude types what I already stated, not free invention)
Different risk profile. Justifies bringing "AI infers edges" from
"Phase P+ if ever" to "Phase P, friction-driven".
