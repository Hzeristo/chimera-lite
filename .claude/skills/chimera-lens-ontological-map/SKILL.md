---
name: chimera-lens-ontological-map
description: Map a survey / review / position paper as an opinionated ontology — classification axes, categories with architectural distinctions, agreed bottlenecks, open structural gaps, and the edges between concepts. Activate when deep-reading a survey, review, or position paper (no raw experiments). Judges the paper on its Architectural Metacognition, not its math: an opinionated taxonomy is high value, a lazy SOTA laundry list is low value. Consolidates taxonomy + consensus-bottlenecks + structural-gaps into ONE map with inter-concept edges.
---

# chimera-lens-ontological-map

## What this lens is for

The survey cartographer — read a map paper AS a map, not a table of contents. This lens
**consolidates three registry survey lenses into one** (batch Decision 1): `survey_taxonomy`
(`optics_lens_registry.py:130` — `classification_axes` + `core_categories` with architectural-bound
distinctions), `survey_consensus` (`optics_lens_registry.py:145` — `major_limitations` /
bottlenecks), and `survey_gaps` (`optics_lens_registry.py:157` — `future_directions` /
`technical_void`) become dimensions of ONE ontological map. The **delta** beyond a flat category
list is the **inter-concept edges** — how categories relate, subsume, or conflict.

Judgment stance (`prompts/chimera_sys/user_profile.j2:27-31`, the Survey Exception): judge on
**Architectural Metacognition**. A lazy laundry list of SOTA models → LOW VALUE. An opinionated,
architecturally grounded taxonomy that exposes real structural gaps → MUST READ.

## When it fires

Auto-select on surveys / reviews / position papers — work that lacks raw experiments. Not the
paper-analysis lenses (forensic / thermodynamic / state-collision / agentic-illusion / math).

## The map — one consolidated ontology

Produce a SINGLE map with these dimensions (not three separate survey outputs):

a. **Axes** — the abstract dimensions the authors use to structure the field (not a model
   enumeration).
b. **Categories** — each with the *architectural bound* that distinguishes it from its neighbors
   (e.g. "episodic memory as timestamped vector-JSON retrieved via Top-K" vs "external memory as a
   tool-call KV store"). Short label, dense technical distinction.
c. **Bottlenecks** — the paradigm-level flaws and hard bottlenecks the field agrees on (absorbed
   from `survey_consensus`); each dense, not a generic complaint.
d. **Gaps** — open structural voids, each pairing a direction with the specific technical reason the
   field has not closed it (absorbed from `survey_gaps`); no vague wish lists.
e. **Edges** — the inter-concept relations (subsumes / competes-with / composes-into) that turn a
   list into a map. This is the delta; do not omit it.

## Output contract

Apply the shared academic-taste contract — `../_shared/falsifiability.md`. Mechanism + Evidence +
Falsifiability, adapted for a map:

- **Consolidated map** — axes + categories + bottlenecks + gaps + edges, as ONE artifact.
- **Metacognition verdict** — opinionated taxonomy (must-read) vs laundry list (low value), with the
  reason.
- **Falsifiability** — for each claimed gap / bottleneck, the concrete architectural limit that makes
  it real (not "needs more research").

## Red lines
- ❌ ONE consolidated map — do not emit three separate survey outputs. Bottlenecks and gaps are
  dimensions of the map, not sibling reports.
- ❌ Do not produce a sterile table of contents — categories carry architectural distinctions or they
  do not belong.
- ❌ Falsifiability is mandatory (`../_shared/falsifiability.md`).
- ❌ Pure English only. No opportunistic refactor.
