# friction-260813-01 — K-node claims restate one idea across four fields

**Name:** one idea, four fields
**Date:** 2026-08-13
**Status:** OPEN — diagnosed and measured; the fix belongs to Phase L.D (extraction reshape)
**Phase context:** L.C functionally sealed; L.D design discussion, arising from a question about
whether K-node claims carry useless rationale.

## What I wanted

To read a K node's mechanism claims and get, per claim, the mechanism and the test that would
disprove it — the two things that make a claim reusable in future research.

## What I actually got

Each claim states its central point up to four times at different compression levels. Measured on
`Knowledge/2606.07512-MEMDREAMER.md` (5 claims, the node's largest section at 67 lines of 203):

| field | per claim | assessment |
|---|---|---|
| `statement` | ~59 w | earns it — carries the mechanism. A trailing inference clause duplicates the status note |
| `falsification` | ~50 w | **the most valuable field in the node.** C03's carries both branches and a numeric threshold |
| `sources` | ~33 w | verbatim quote; incompressible without breaking grounding |
| `title` | **21 w avg** (17–24) | the schema says "*a short* mechanism-level title" and enforces nothing. These are full sentences duplicating `statement` |
| `status_note` | ~32 w, in **4 of 5** | restates `flags` plus `statement`'s inference clause |
| `tags` | 4 w | written into the **body**, so `search_vault_attribute` (frontmatter-only) cannot read them |

Worked example — C03 says "the ablation is missing" four times:

1. **title:** "…making a genuine bottleneck read as false robustness"
2. **statement**, final clause: "…equally consistent with 'the template is the bottleneck' as with
   'the system tolerates perceptual error'"
3. **status_note:** "…asserted from the swap-insensitivity number without an ablation that
   separates schema-absorption from genuine robustness"
4. **flags:** `no_ablation`

## Root cause

**A specification defect, not a prose defect.** `ExtractedClaim` gives every field an independent
description in `core/schemas.py:304-315`, and **none of them says "do not restate the others."**
The extractor is not padding — it is answering four prompts about one idea, obediently, four times.
It will do so again on every paper extracted until the schema stops asking.

Two contributing gaps:
- **No length discipline.** `title`, `statement`, `falsification` and `status_note` carry no
  `max_length`, so output length is whatever the model feels like. The file already uses the
  pattern elsewhere (`short_moniker: max_length=64`).
- **`status_note` is already optional in practice.** C05 carries the bare word `hypothesis` with no
  justification and reads perfectly — the natural experiment for dropping the field was already run
  inside the same node, and nobody noticed because no node had ever been measured.

## Why it matters beyond tidiness

One K node is **203 lines / ~4.4K tokens**. The vault has 3 nodes, so nothing hurts yet; at 30, a
question spanning five papers costs ~30K tokens of reading before any thinking happens. This is the
"context is the load" problem arriving inside the vault rather than in `docs/`.

The arithmetic also decides an open design question: dropping `status_note` (~128 w) and capping
titles to ~8 words (~65 w) recovers roughly **190 words, ~20% of the claims section** — about what a
`{kind, statement, what_would_fill_it}` gap object costs across a node. **The compression pays for
the gaps**, so the node absorbs a new capability at flat size.

## Ideal

- `title` capped short (the schema already asks for it; enforce it) and explicitly scoped as an
  index label, not a sentence.
- `status_note` dropped, or capped hard and marked genuinely optional — `flags` plus `falsification`
  already carry its content.
- Field descriptions state their division of labour, so no field restates another.
- `tags` either promoted to frontmatter (where `search_vault_attribute` can reach them) or removed.
  A tag nothing can query is decoration.

## Scope guard

**Do not cap `falsification`.** Fifty words naming the measurement that would disprove the claim,
with the threshold written in, is the only content in the node that could ever cost the paper
anything. Trimming it would read as discipline and would be the most expensive cut available — the
Theater's exact shape (`PHILOSOPHY.md` §3).
