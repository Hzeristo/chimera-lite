# friction-260713-01 — K node synthesis missing motivation (the gap) and results (the payoff)

**Date:** 2026-07-13
**Status:** RESOLVED (implemented 2026-07-13).
**Phase context:** Phase Q output-shape rebuild (`friction-260710-02`), reviewed live on STALE
(arXiv 2605.06527) after the hybrid-lens re-extraction.

## What I wanted
The human-readable part of a K node should match how I ACTUALLY read a paper — a complete arc:

> motivation (the gap) → contribution + insight (BB analysis) → mechanism / steps → results (did it
> work) → [Lens] → [Attack] → [Claims]

This is my reading mental model, not a reinterpretation of the paper.

## What I actually got
The rebuilt Synthesis jumped from **contribution** (BB analysis) straight through mechanism/steps into
the lens — with two arc beats missing:
1. **Motivation** — WHY the work exists, the gap it closes. The reader is dropped into the contribution
   with no problem statement.
2. **Results** — DID it work: the headline outcomes and key numbers. The node critiques the method
   before ever saying whether it succeeded.

## Root cause
The rebuild modeled the paper's *contribution and critique* (synthesis / lens / attack / claims) but
omitted the *setup* (the gap) and the *payoff* (the results). Compounding it: the ARA claims discipline
deliberately strips numbers from claim `statement`s (numbers live in `sources`), which **orphaned the
headline outcome numbers** — they had no home in the node. `results` reclaims them.

## Fix
`PaperSynthesis` gains two grounded-by-quote fields (same discipline as claims):
- `motivation`: the gap, 1-2 sentences, the problem only, grounded by a verbatim quote.
- `results`: headline outcomes WITH key numbers (not a full table), grounded by verbatim quotes — the
  HOME for the numbers the claims strip.

Render arc: **Motivation → BB Analysis (contribution) → mechanism → steps → Results →** `[My Critique]`
→ Lens → Attack → Claims. Prompt bounds: "motivation = 1-2 sentences, the gap only"; "results =
headline outcomes with key numbers, not a full table."

## Lesson
A synthesis a researcher will read must trace the FULL arc — the question (gap) and the answer (result),
not only the middle. And a discipline that strips numbers from one section (claims) must give those
numbers a home in another (results), or they vanish.
