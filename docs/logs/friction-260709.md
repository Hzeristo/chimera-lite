# friction-260709-01 — Vault absent from the agentic loop (the always-active observer never fires)

**Date:** 2026-07-09
**Status:** OPEN — PARTIALLY ADDRESSED (2026-07-10, Phase Q). The explicit disciplined vault-write path now exists (`extract_paper`: distill a paper into K claims + grounded edges, on demand). But the friction's **ambient** half — the always-active observer never firing during ordinary conversation — remains OPEN; Phase Q scoped ambient-observe OUT (Scope Cut G2). Still the dominant blocker for a vault-grounded reading loop.
**Phase context:** Post-Phase-O; Phase N.B rescoped the same day (disposition A). This friction
re-prioritizes those two — it says the substrate under N.B is broken.

## What I expected
`chimera-academic-observe` is declared ALWAYS-ACTIVE: while I deep-read a paper, it should be
consulting the vault and surfacing the one materially-relevant prior node, unprompted. The whole
exocortex (Phases O + N.B) exists to be recalled *inside* my reading — not queried by hand.

## What actually happens
In real reading sessions the vault does not enter the loop. The observer effectively never fires;
the loop reasons about the paper with the vault sitting inert beside it. I query it by hand or not
at all. The exocortex is a library the reading loop never walks into.

## Root cause — "always-active" is a label, not a mechanism
A prompt skill cannot force a tool call. "Always-active" means its guidance is *loaded*, not
*executed* — the loop still has to *choose* to call `obsidian_graph_query` every turn, unprompted,
while its attention is on the paper. And we engineered the skill to prefer silence ("silence is the
default", "firing on every turn is the failure mode", a self-assessed relevance gate). No-forcing +
silence-bias + self-gate = structural absence. **Self-opt at the prompt level does not survive contact
with a real workflow.**

## This is the root cause; the lens misalignment is downstream
Two frustrations were filed; this one dominates. Phase N.B chased the *depth* of the recall graph and
Phase O + the disposition-A rescope tuned the *params* of the recall tool — while the loop never calls
recall at all. Retrieval quality is downstream of retrieval *happening*. Fixing the substrate (vault
structurally in the loop) is the prerequisite; the lens-deployment fix falls out of it.

## The lens corollary (downstream, not fixed here)
The lens ("lancet on one aspect") insight was right; the deployment is wrong — one-type-one-lens is a
false taxonomy (real papers are hybrids), a lancet sprayed as triage is the wrong cadence for reading
many papers a day, and "tool generates a general insight → auto-fire a lens by paper-type" inverts the
real flow, where my own reading judgment should *summon* the scalpel. Once recall is live in the loop,
lenses demote from auto-fired-by-type to summoned-on-demand deep probes.

## Preferred direction (mechanism appetite)
A **forked subagent that utilizes the vault MCP methods** — isolate recall into a worker whose sole job
is to hit `obsidian_graph_query` / `vault_query` and return grounded recall, keeping the main loop's
context clean. Isolation solves the attention-competition that kills the always-active prompt. The open
design question is only the *trigger* (hook = automatic every reading turn; `/read`-style command =
explicit step 0).

## Alignment target — the ARA model (arXiv 2605.02651)
ARA (Agentic Reproducibility Assessment, Riehl et al., 2026) reads a paper by extracting a *directed
workflow graph* (sources → methods → experiments → outputs) and scoring reconstructability — **reading
as structured graph extraction**, shown robust across models / temperatures / domains, built for scale.
Three fits for my workflow: (1) it matches high-volume triage, not a boutique per-type audit; (2) the
extracted per-paper graph is exactly the structure that would *deepen* the wide-and-shallow vault graph
as a byproduct (it addresses `[[vault-graph-edges-empty]]` at the write path); (3) it demotes the lens
to an optional deep probe fired only when the structural read flags something. The reading loop should
extract structure, ground it against the vault, and leave the vault deeper than it found it.

## Scope guard
This is a friction signal, not a phase. The phase that resolves it is the Architect's to author
(cf. `f6561e8`). Recorded to fix the priority order: **#2 (vault-in-loop) before #1 (lens redeployment).**
