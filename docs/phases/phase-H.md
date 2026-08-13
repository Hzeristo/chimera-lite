# Phase H — Hypostasis: Structured Primary Evidence

**Status:** Queued (executes after Phase I; see dependency tension note)
**Sealed predecessor:** Phase I (Isostheneia) in execution order
**Alphabetical position:** M→L→K→I→H (reverse-descending, H is the substrate)

**Dependency tension note:** H is substrate to K — K's Gate 1 monotonicity
guarantees rest on W1 verdicts whose [V] tags anchor on table evidence. If H
hasn't ensured table extraction is reliable, K computes monotonicity over
potentially malformed numbers (katalepsis over akataleptic input — the precise
failure phrase-K.md:25-28exists to prevent). The execution sequence (K before H)
was chosen because K requires codex (acquisition-gated) and I requires isostheneia
research (research-gated), while H is purely engineering-gated. If the user finds
W1 [V] reliability unacceptable during K/I execution, H may be pulled forward.

**Driving frictions:**
- W1's [V] tags currently anchor on MinerU prose conversions of tables,
  which frequently malform: columns misaligned, numbers truncated, delta-vs-
  absolute context lost. Gate 1 (K.1) computes min over dependency statuses —
  a [V] anchored on a malformed table is a kataleptic label over akataleptic input.
- The Tier 1/2/3 taxonomy (TAG_SYSTEM.md, Phase K pre-req) distinguishes primary
  evidence (table entries, equation definitions) from authorial framing. Without H,
  W1 cannot reliably reach Tier 1 — all evidence collapses to prose-quality Tier 2/3.
- Paper metadata (citation count, venue, author h-index) is epistemic signal for
  weighting candidate material but is absent from K nodes and never consulted by W1.

## VISION — Why Hypostasis

┌────────────────────────────────────────────┐
│ Hypostasis (ὑπόστασις, Neoplatonist): the concrete substrate that gives     │
│ abstract logos its specific existence. A table number is the hypostasis of│
│ the claim "method X achieves Y" — the concrete realization without which    │
│ the claim is mere abstraction.                                              │
│                                │
│ MinerU produces prose. W1 verifies claims against prose. But the Tier 1     │
│ epistemic warrant the THEORETICAL_FRAMEWORK.md promises — "table entries,   │
│ equation variable definitions, arXiv metadata" — does not yet exist as      │
│ machine-readable structured data. It exists as text strings like│
│ "60.353.468.0" where three numbers lost their column context.│
│                                                                              │
│ Phase H materializes Tier 1. It makes the concrete substrate of research    │
│ claims (tables, equations, metadata) into first-class queryable objects│
│ attached to K nodes, so W1 can anchor [V] on structured evidence rather│
│ than prose approximations of evidence.│
│                                                                              │
│ Without H: K guarantees propagation of provenance, but the provenance       │
│ status itself was determined against unreliable source material.            │
│ With H: a [V] tag means what TAG_SYSTEM.md says it means — verbatim from│
│ a Tier 1 source — and K's propagation guarantee is actually load-bearing.  │
│                 H is the lowest layer of the M→L→K→I→H stack. It is built last in time│
│ but depends on nothing above it. When it ships, the stack is complete.      │
└────────────────────────────────────────────┘

## Mission

Convert paper primary evidence (tables, equations, metadata) from prose strings
into structured Tier 1 objects attached to K nodes, so W1 can anchor [V] tags
on machine-readable evidence rather than MinerU's prose conversions.

Three deliverables:
- **Table formatter:** MinerU table markdown → structured JSON{method, metric, value, context} per cell, attached to K node.
- **Equation extractor:** Eq.N → structured assertion
  {variable, definition, constraint, location}, attached to K node.
- **Metadata enrichment:** citation count (Semantic Scholar), venue, date, author
  affiliations → attached to K node frontmatter as epistemic weight signals.

## Sprint Sequence

| Sprint | Risk | One-line goal |
|---|---|---|
| H.0 | — | Audit: how MinerU actually converts tables (column alignment, number truncation, delta-vs-absolute loss); what equation parsing exists; Semantic Scholar API availability |
| H.1 |🔴 | Table formatter: MinerU table markdown → {method, metric, value, context} JSON; attached to K node as structured_tables field |
| H.2 | 🟡 | Equation extractor: identify Eq.N in markdown → {variable, definition, constraint, location}; attached to K node as structured_equations |
| H.3 | 🟡 | Metadata enrichment: arXiv API + Semantic Scholar → citation count, venue, date; fill K node frontmatter; weight signal for W1 |
| H.4 | 🔴 | W1 integration: W1 subagent queries structured_tables/equations FIRST, falls back to prose only if structured data absent; [V] definition upgraded to prefer Tier 1 structured evidence |
| seal | — | phase_review — verify on confession fixture: Table3 "+0.2" arrives as {method: similarity-merge, metric: OVBench, value: 60.3} not "60.353.4 68.0" |

**Dependencies:** H.0 precedes all. H.1/H.2/H.3 are parallel-eligible after H.0
(different files, no shared state). H.4 integrates all three into W1 and is the
seal gate. H.4 must come after TAG_SYSTEM.md is canonical (Phase K pre-req) —
W1's upgraded [V] definition must reference TAG_SYSTEM.md's Tier taxonomy.

## Cross-Sprint Red Lines

- ❌ **H does not reopen Phase Q (extract_paper).** extract_paper produces K nodes
  from paper prose (sealed). H adds structured_tables/equations/metadata asATTACHMENTS to those nodes — it does not change extraction logic.
- ❌ **Structured data is additive, not replacing.** The prose K node body remains.
  structured_tables is a new field, not a rewrite of Claims or Synthesis sections.
  W1 reads structured data FIRST if available; prose is fallback — graceful
  degradation, not hard dependency.
- ❌ **No new dependency beyond Semantic Scholar API.** Table/equation extraction
  operates on existing MinerU markdown. Semantic Scholar is a READ-ONLY API call
  per paper. No new MCP server; no new ML model.
- ❌ **Table formatter is heuristic, explicitly imperfect** (same discipline as
  clean_markdown_heuristic in Phase R). MinerU's table markdown is inconsistent;
  no formatter achieves 100%. Document coverage rate, flag failures, do not claim
  correctness. A missing table entry falls back to prose [P] or [U], not [V].
- ❌ **Equation extractor targets definitions, not proofs.** Eq.N as a theorem
  in a proof section is out of scope. Eq.N defining variables (Eq.1: x_i and x_{i+1}
  are adjacent nodes) is the target — the confession's most expensive mistake.
- ❌ **No opportunistic refactoring.**

## Hard Sealing Conditions

1. **(H.1) Table 3 arrives structured.** The confession's Table 3 (StreamForest,
   with OVBench baseline58.2, method60.3 — a +0.2 that looks decisive but is
   noise) arrives as structured JSON, not the prose string "60.353.468.0".
   W1 can now express the claim "Table 3 proves tree works" with
   source: {table_3, row: similarity-merge, col: OVBench, value: 60.3} — a
   DIFFERENT claim structure than "Table 3 shows these numbers."Verified: run W1 on that claim, confirm structured_tables is consulted.

2. **(H.2) Eq.1's adjacency constraint is structured.** The confession's
   most expensive mistake was treating StreamForest's merge as cross-time
   because Eq.1 (x_i, x_{i+1} = adjacent) was never read. After H.2,
   Eq.1 appears in structured_equations as
   {name: Eq1, constraint: x_{i+1} is x_i's temporal successor}.
   W1 querying "do adjacent nodes mean temporally adjacent?" now has
   a structured answer, not a prose-search.

3. **(H.3) Citation metadata informs W1 weight.** A claim from a paper
   with 0citations (month-old preprint) and a claim from a 400-citation
   paper should carry different epistemic weight. H.3 attaches citation_count
   to K node frontmatter; criteria/field/*.md can reference it. Verified
   by inspecting a K node and confirming the field is populated.

4. **(H.4 — the seal gate) W1's [V] anchors on structured evidence.**
   Given a claim with both structured_tables coverage and prose, W1 uses
   structured data for the verbatim quote. The Tag Tier taxonomy (T1= table
   entries) is operationalized: a table cell reference is Tier 1, a prose
   description of that table is Tier 2. Verified: W1 on Table 3 "+0.2 proves"
   cites {table_3, similarity-merge, OVBench, 60.3} not "Table 3 shows..."

## Design Decisions

- **H is the last layer but the logical first (ST2026-07-XX).** The execution
  sequence is K→I→H (latest), but the epistemological sequence is H→K→I (H
  is substrate). This inversion exists because H is purely engineering-gated
  (no codex, no external research required), while K is acquisition-gated
  (codex) and I is research-gated (isostheneia literature). If W1 [V] reliability
  proves unacceptable during K execution, H.1/H.2 may be pulled forward
  while K.2/K.3 (codex-dependent) wait.

- **Heuristic extraction with graceful degradation (ST 2026-07-XX).** Both
  H.1 (table formatter) and H.2 (equation extractor) are best-effort, not
  guaranteed. A paper with non-standard table formatting falls back to prose
  — W1 assigns [P] or [U] rather than [V], which is correct behavior: if we
  can't read the table, we can't claim verbatim Tier 1 grounding. Graceful
  degradation preserves the epistemic guarantee even when extraction fails.

- **Semantic Scholar over full arXiv scraping (ST 2026-07-XX).** Citation count
  is the primary metadata signal. Semantic Scholar's free API provides it
  per arXiv ID. Full citation graph scraping (finding WHO cited the paper)
  is W2's domain and out of Phase H scope. H.3 is a point lookup, not a
  graph operation.

- **Equation extractor targets confession's failure class (ST 2026-07-XX).**
  The most expensive confabulation in the confession (cross-time merge possible
  from adjacency constraint) was caused by not reading Eq.1's variable
  definitions — a10-word structural fact. The equation extractor prioritizes
  "variable definition" equations over "proof step" equations. A10-word
  definition costs 10 tokens; a missing definition costs a research direction.

## Out of Scope (→ later)

- **Full citation graph (who cited this paper)** — W2's domain, graph operation.
- **Figure/diagram extraction** — multimodal, Phase V (MLLM) territory.
- **Cross-paper equation alignment** (does Eq.1 in paper A correspond to Eq.3
  in paper B?) — semantic matching, requires embedding, deferred.
- **Semantic Scholar deep data** (author h-index, co-authorship network) — the
  API provides it but H.3 scopes to citation_count and venue only.
- **Reopening Phase Q's extract_paper** to use structured evidence — sealed.extract_paper still runs on prose; structured data is H's addition to the
  output artifact, not a rewrite of extraction.

## Notes

- H.0 must empirically test MinerU's table output on at least three paper types:
  a simple2-column table, a multi-column comparison table (like Table 3), and
  a table with merged cells. The formatter design depends on which failure modes
  are most common in practice.
- H.4 requires TAG_SYSTEM.md to be canonical and W1's subagent prompt to
  reference the Tier taxonomy. Verify before H.4 that TAG_SYSTEM.md section
  "Doubt-signal to tag translation" (added during lens-criteria reconciliation)
  is present and complete.
- The seal fixture is explicit: Table 3 from StreamForest (confession's own
  benchmark), with the "+0.2 that looks decisive but is noise" as the test case.
  This is the hardest real case — if H.1 parses that table correctly, it handles
  the class of failure that caused the confession.
