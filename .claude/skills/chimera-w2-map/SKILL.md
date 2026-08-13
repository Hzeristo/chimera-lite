---
name: chimera-w2-map
description: Run W2 — Breadth Mapping (Phase L research harness). Activate when the Architect wants a survey / breadth map built from seed papers — "map the field around these papers", "run W2 on <seeds>", "what's the landscape near <topic>?", or when building the survey material a semi-proposal needs (30-60 papers reduced to gaps + numbers across subfields). Orchestrates seed resolution → bounded reference expansion → per-paper classify + criteria-load + reduce (one gap sentence + one performance number) → merge into a classified, subfield-grouped map written to the vault Harness folder. Judgment is Claude-in-subagent, never deepseek. RECON + NOMINATION — W2 nominates promote-candidates; the Architect promotes. Explicitly invoked, not ambient.
---

# W2 — Breadth Mapping

<expected_model>
**Run this orchestration loop at Sonnet.** W2's loop is scheduling + assembly — bounded-BFS frontier
planning, wave batching, keyed-block collection, merge, report. It is the longest-lived context in
the harness (resident across up to `max_papers` papers × 2 worker spawns), which is exactly why it
must not sit at Opus. Every per-paper *judgment* is delegated to **pinned-Sonnet** workers
(`chimera-paper-classifier`, `chimera-breadth-reducer`); the loop carries none. Running it at Opus
is dev-time overspend (`docs/audits/model-routing-gaps.md`, gap #1).

If the session model is Opus, follow the recommendation procedure (detect → inform → wait, never
auto-switch): see ../_shared/expected_model.md. The pinned workers stay Sonnet regardless of the
session model.
</expected_model>

You (the main agent) **orchestrate**; each paper's judgment happens in **isolated subagents** (the
paper text stays in the worker). W2 REUSES W1's classify → load-criteria subroutine, adds a lighter
RECON reduction (gap + number), and MERGES the result into a living map — it never regenerates it.

## The loop

1. **Normalize the seed set + identity.** Seeds are ≥3 papers (arXiv ids and/or vault K-nodes).
   Compute `identity` = a stable topic / seed-set slug (e.g. `topic:agentic-memory`, or a
   deterministic slug of the sorted seed ids) so a re-run MERGES the same map, never duplicates it.

2. **Bounded reference expansion (cheap-first — D5).** Build the frontier from the seeds plus their
   cheaply-available references — bare arXiv ids already in the vault or supplied by the Architect.
   The reference PARSER is a deferred increment; do NOT crawl the open web. Apply the HARD caps with
   the exact semantics of `mcp-servers/chimera-papers/w2_breadth.py::plan_expansion` (the tested
   reference spec): seeds are depth 0; expand a node only while `depth < max_depth`; a paper reached
   twice (cycle / diamond) is visited once. **Default caps: `max_depth=1`, `max_papers=24`.** Never
   exceed them — bounded BFS is a red line.

3. **Per paper (parallelisable across subagents):**
   a. **Classify** — spawn `chimera-paper-classifier` → `{type, field}`.
   b. **Load criteria** — `load_criteria(type, field, role="paper-critic")` (domain taste for the reduction).
   c. **Reduce** — spawn `chimera-breadth-reducer` with the paper's markdown path + `{type, field}` +
      the composed criteria → ONE keyed block (`<!-- w2:paper=<id> -->` + gap sentence + performance
      number + promote-candidate). RECON ONLY — no interpretive conclusion (Phase K frames later).
   A paper that cannot be resolved is recorded as a block with `number: —` and a note — never dropped.

4. **Assemble the classified map.** Group the blocks by `field` into subfield sections. Every paper
   must carry a gap + a number (HSC #4). Render each subfield as a heading with its keyed paper
   blocks beneath. Breadth target: ≥3 subfields — but a narrower span is a **warning, not a
   failure**. When the map spans fewer than 3 subfields, emit this line in the map body and in the
   report, then continue normally:

   > Note: single-subfield map — broaden seeds for production use.

   (A tight seed set from one field family legitimately spans 1–2 subfields; failing the run there
   would block small fixture-scoped runs for no fidelity gain — L.B.6 F7.)

5. **Write (MERGE, not supersede).** `write_result(kind="w2_breadth_map", identity=<identity>,
   title=<topic>, body=<the subfield-grouped keyed blocks>, mode="merge")`. Merge PRESERVES the
   Architect's in-Obsidian annotations and ADDS new papers — the map lives; it is not regenerated.

6. **Hand off the nominees.** For each block whose `promote-candidate` is `yes`, emit one runnable
   handoff, in map order — **not ranked**, because ranking is a judgment W2 has no basis for and the
   Architect already has the gap sentences in front of them:

   ```
   <id> — <title>
       gap: "<the block's gap sentence, verbatim>"
       run: ingest_paper("<id>")            # only if not yet converted
            chimera-deep-extract on <id>    # resolves markdown via get_paper_markdown
   ```

   The gap sentence is quoted verbatim and is the point of the handoff: it is the context the
   extract should be read against, and re-typing or paraphrasing it is the manual transcription this
   phase measures (D1).

   **Build each line from the block you already hold — never by re-reading the map.** No map path,
   no block offset, no re-parse. That is not an optimization: W2's artifact form carries no
   protection and is reshaped in L.D, so a handoff that depends on the map's structure dies with it,
   while one built from a candidate in hand survives. The same handoff works when the Architect
   simply names a promote-candidate in conversation and no map exists at all.

   `ingest_paper` is refused while a long arXiv/pipeline job holds the GPU — if that happens, report
   it and leave the handoff standing; it is a timing conflict, not a failed nomination.

7. **Report.** The classified map, the handoff lines from step 6, and the Harness path.
   W2 nominates; the Architect promotes.

## Red lines

- ❌ **Bounded BFS.** Hard `max_depth` + `max_papers`; no unbounded / open-web crawl (D5 cheap-first).
  The caps' semantics are fixed by `w2_breadth.plan_expansion` — follow them exactly.
- ❌ **RECON, not interpretation.** Each row records number + verbatim + gap; NO single-framing
  conclusion. Interpretation is Phase K Gate 2 — baking a frame here reintroduces the bias K removes
  (the W2 forward-compat constraint K.0 checks).
- ❌ **MERGE, never clobber.** `mode="merge"` — a re-run preserves human annotations and adds papers.
  Never `supersede` a breadth map; that destroys the Architect's curation.
- ❌ **Judgment in Claude subagents, never deepseek.** Classify + reduce are forked Task subagents;
  the paper text stays in the worker (isolation).
- ❌ **W2 nominates; the Architect promotes.** No auto-ingest of promote-candidates, no auto-K-node.
  Step 6 emits lines the Architect *runs* — never run them yourself, not even for a single obvious
  candidate, and never chain straight into `chimera-deep-extract` (I0.1).
- ❌ **The handoff is an interface, not a workflow.** No ranking, no scoring, no filtering of
  nominees, and no dependency on the map's persistence or structure — build each line from the block
  in hand. A handoff that must parse the map cannot survive W2's reshaping in L.D.
