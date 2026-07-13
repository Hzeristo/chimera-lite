# friction-260710-01 — ingest_paper triage prompt is low-quality and untunable

**Date:** 2026-07-10
**Status:** OPEN
**Phase context:** Phase Q functionally sealed; Phase R planning.

## What I wanted
When `ingest_paper` auto-triages a paper, it should produce a *useful* score / moniker / verdict —
especially a *meaningful* short moniker (the paper's shorthand codename), not filler like "Paper A".

## What I actually got
Across the backfilled papers the monikers were generic and information-free ("MemoryTransfer", "AutoMem").
Scores clustered at 7–8 with no discrimination. Verdicts looked near-random (papers marked `must_read` that
should be `skim`, and vice versa).

## Root cause
The triage prompt is buried inside `single_paper_ingest.py` (via `FilterService` → `reviewer_zero.j2` /
`filter_task.j2`) — I cannot see it or tune it in the flow. And the prompt itself is likely generic: it
reads the abstract, not the method.

## Why this matters
After every ingest I still have to re-judge "is this actually a must-read?" by hand. The triage output does
no filtering work — it is decoration, not a signal.

## Ideal
The triage prompt is exposed (e.g. `prompts/triage.j2`, or a `.claude/skills/triage-paper` skill) so I can
edit the judgement criteria (for example: "if this is a memory-benchmark paper, auto `must_read`").

---

# friction-260710-02 — Phase Q output violated the founding vision (spec drift)

**Date:** 2026-07-10
**Status:** RESOLVED (2026-07-13, Phase Q re-seal) — was OPEN / reopened Phase Q. The output shape was
rebuilt (synthesis + lens + attack + claims-as-floor, then the motivation/results arc) and validated
end-to-end on a real paper (STALE, arXiv 2605.06527). See `docs/sprints/phase-Q/phase-reseal.md`.
**Phase context:** Phase Q functionally sealed 2026-07-10, then reopened the same day on this friction.

## What I wanted
`extract_paper` to deliver the founding workflow — a **general synthesis → apply the right lens →
human-readable summary + critique**: a node I actually want to read.

## What I actually got
Atomic-claims extraction. Each node is a machine-structured list of 1–5 mechanism claims — a claim graph
for an agent, not a synthesis for a researcher.

## Root cause — spec drift
The ARA correction (`mode='ara'` → Option B) correctly rejected ARA-**format** reconstruction, but
**overcorrected** into atomic-claims extraction — dropping the founding "synthesis → lens → summary"
workflow. **ARA's "claim-as-mechanism" discipline is a QUALITY BAR for statements, NOT an OUTPUT SHAPE.**
It was misapplied as the whole output.

## Why this matters
The founding VISION (recorded in `phase-Q.md`) is "a tool I actually want to use for daily research." An
atomic claim graph is not that — it is a builder's artifact, not a reader's synthesis. The spec drifted
away from the vision while chasing correctness against the *previous* spec.

## Caught by
The **staging gate** — human review rejected the atomic-dump nodes before any reached the vault. The gate
worked exactly as designed: nothing bad was promoted. (This validates the "never auto-promote" red line.)

## Lesson
Every spec rewrite must re-check against the **FOUNDING VISION**, not merely against the
immediately-preceding spec. A chain of locally-correct corrections can still walk away from the goal.

## Ideal / rebuild direction
Rebuild `extract_paper`'s **output shape**: a human-readable synthesis (contribution → mechanism → critique),
with the ARA claim-discipline applied as a *quality bar on the prose* (mechanism-level, grounded, honest),
NOT as the emitted structure. Keep the citation-grounded edges — those were correct. Re-anchor on the VISION
before re-implementing.

---

# friction-260710-03 — Lens logic was single-address; server extraction risked a second copy

**Date:** 2026-07-10
**Status:** RESOLVED (design decision, Phase Q rebuild — A-refined).
**Phase context:** Phase Q reopened on `friction-260710-02`; the rebuilt node carries a Lens Critique
section, so the lens methodology now has to reach the server-side `extract_paper` LLM call as well as the
interactive Claude-Code lens skills.

## What I wanted
The lens methodology available to BOTH consumers — the server extraction call AND the six interactive
`chimera-lens-*` skills — without the two drifting apart.

## The trap (A-naive)
The obvious move — copy each lens's method into the server prompt (`extract_node.j2`) — creates a SECOND
source of truth. Lens logic would then live in two places (`.claude/skills/chimera-lens-*/SKILL.md` and the
server prompt) that inevitably drift. That is the SAME friction the rebuild exists to fix (buried,
non-single-source prompt) — made worse by duplication.

## Resolution (A-refined — one canonical source)
One canonical definition per lens: `prompts/lenses/<name>.md` (function-based trigger + analysis method),
plain markdown, externally editable. Both consumers read it:
- **server:** `extract_node.j2` includes the canonical lens files; the extraction call selects ONE by paper
  FUNCTION (per G1: function, not content type).
- **interactive:** the six `chimera-lens-*/SKILL.md` bodies are thinned to a one-line pointer
  (`Apply the lens methodology in prompts/lenses/<name>.md`), keeping only their `description` frontmatter
  for auto-selection.

Zero drift; one home; externally tunable. (This touches Phase N.A sealed deliverables — flagged for
explicit sign-off before editing.)

## Same principle, applied to friction-260710-01
The buried triage prompt (`single_paper_ingest.py` → `reviewer_zero.j2` / `filter_task.j2`) moves to an
external `prompts/triage.j2` for the same reason — one editable home per prompt.

## Lesson
**Every prompt is an externally-editable file with ONE source of truth.** Never inline prompt logic in code,
and never duplicate it across consumers — give it one canonical file and have each consumer read that file.
