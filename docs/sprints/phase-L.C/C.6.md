# Sprint C.6 — W2 handoff: a promote-candidate becomes a runnable extract

**Phase:** L.C (Colligo) · **Risk:** 🟢 LOW · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Executed by:** Opus main session (one skill file).
**Outcome:** ✅ Pass — verified end-to-end on a real vault fixture, with the map deliberately
withheld from the executor.

## What was built

`.claude/skills/chimera-w2-map/SKILL.md` — a step 6 between the merge and the report. For each
block whose `promote-candidate` is `yes`, one runnable handoff carrying the id, the **verbatim** gap
sentence, and the two commands. The report step now includes those lines.

Two red lines added: step 6 emits lines the Architect *runs* (never chain straight into
`chimera-deep-extract`), and the handoff is an interface — no ranking, no scoring, no filtering, no
dependency on the map's persistence or structure.

## The design decision that is the whole sprint

**Build each handoff from the block already in hand; never by re-reading the map.**

This looks like an optimization and is not. W2's artifact form carries **no protection**
(`INVARIANTS.md` non-invariant list) and is reshaped in L.D. A handoff that parses the map dies with
the map; a handoff assembled from a candidate in hand survives, and works identically when the
Architect just names a promote-candidate in conversation with no map involved at all. That is why
the acceptance test hands the executor an id and a gap sentence and **nothing else** — the test is
not "does a line get printed", it is "does the line stand up with its map removed."

**No ranking, deliberately.** Ordering nominees would require W2 to judge which gap matters most,
which is the Architect's axis and not a recon worker's. The gap sentences are already in front of
them; a rank would add a machine opinion wearing the costume of a sort order.

## Acceptance run

Fixture: the real vault map `w2_breadth_map__topic_streaming-video-memory.md` — 4 papers, all
`promote-candidate: yes`. FluxMem (2603.02096) was excluded on inspection because it **already has a
committed K node**, and re-extracting it would have manufactured a duplicate rather than tested
anything. Ran on MemDreamer (2606.07512), which has none.

All four candidates were already converted, so the `# only if not yet converted` branch is the live
one and `ingest_paper` was correctly skipped — the handoff's cheap-first clause earning itself on
the first real fixture.

**Result: pass.** The executor was given the id and the gap sentence and nothing else, and reported
needing nothing further. `get_paper_markdown` resolved the path directly; classify →
`load_criteria(method, streaming-video-memory, paper-critic)` → isolated `chimera-deep-extractor`
→ `stage_deep_read_node` produced
`docs/staging/20260812_194056-MEMDREAMER_….md` at `chimera_tier: deep_read`,
`status: PENDING_REVIEW`, `provenance: ai-suggested`, with 4 citation-grounded `derives_from` edges
and 5 ARA claims (1 supported, 4 hypothesis). Verified by reading the file, not from the report.

**The gap did real work, not decorative work.** It was carried into the extractor's prompt verbatim
as READING CONTEXT, and the output is demonstrably responsive: the extractor selected the Forensic
Leakage and Agentic Illusion lenses *because* of the gap's compute-confound concern, and its
strongest claim builds exactly the falsification test the gap asked for — re-run `Full Memory
Context` and `Agentic Search Only` under a matched call budget and token cap, and see whether the
11.8-point gap survives compute parity. It also caught a numeric contradiction the gap did not
predict: §4.3's prose narrates 76.9 vs 78.2 for two conditions Table 11 lists as 78.9 and 80.2.

Incidental confirmation of earlier sprints: the staged node's `graph_edges` carries
`evidence_base: []` (C.3b) and `collides_with: []` (C.4a), and correctly carries **no**
`informed_by` — C.4a's T/I/D-only scoping holding in a live artifact.

## Known limit — the handoff's context is transient

The gap oriented the extraction and then vanished. The staged node's `**Motivation (the gap):**`
section is the *paper's own* framing; nothing in the artifact records that it was read against a W2
handoff gap, and the phrases most distinctive to that gap ("horizon sweep", "out-of-context
distractor probe") appear nowhere in it. A later reader cannot tell this extract was oriented at
all.

**Not fixed here, deliberately.** Recording it would mean writing provenance into the staged node —
which is `stage_deep_read_node`'s shape, not this skill's, and is the same node-level-provenance
problem D5 deferred to Phase K. Fixing it inside C.6 would breach the phase's own "W2 consumption
stays thin" red line to solve a problem that already has a home.

## Acceptance

- [x] A real promote-candidate yields a runnable handoff line
- [x] Running one reaches a staged `deep_read` node — verified by reading the staged file
- [x] The gap sentence is in the extraction's context, not merely echoed in a report — verified by
      the extractor's quoted prompt **and** by the output being responsive to it
- [x] The handoff needed **no** map path and **no** block offset — verified by withholding both and
      instructing the executor to report failure rather than go looking

## Red lines

Held. No map parsing, no ranking, no persistent-map dependency; no auto-ingest and no auto-chain
into extract (W2 nominates, the Architect promotes — I0.1); no new MCP tool; the staged node stays
in `docs/staging/` for Architect review (I1.2), and nothing was ascended.
