# Phase Q Re-Audit — new sprint sequence (Disciplined Knowledge Extraction)

**Scope:** Re-derive the audit Q-list against the **rewritten** Phase Q (commit `4d0295c`: extract_paper →
K nodes + grounded edges, ARA *discipline* not *format*). The `docs/audits/Q.0.md` **substrate map still
holds** (ingest_paper, staging, grounding tools, `generate_structured_data`, seed-exclusion gap, two write
paths) — this re-audit adds the **sprint-specific** questions for the new Q.1–Q.4 and the two evidence
deltas gathered for them. Read-only; the one write is this report.
**Date:** 2026-07-09
**Evidence base:** `Q.0.md` + `mcp-architecture-review.md` + `ara-repo-structure.md` (standing) + two new
scouts: the structured-LLM path (chimera-papers) and real K-node shape (vault).

---

## Findings (new sprints)

| Q# | Sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| Q1.1 | Q.1 | Reuse pattern for a new `response_model`? | Add `KClaimExtraction(BaseModel)` to `core/schemas.py` with `ConfigDict(extra="forbid")`; call `generate_structured_data(system_prompt, user_prompt, response_model=…)` (Pattern A, like `FilterService`). Temp fixed 0.01, tenacity 3-retry, `model_validate_json`. | `schemas.py:69`, `openai_compatible_client.py:163`, `filter_service.py:26-49` | Low |
| Q1.2 | Q.1 | What fields capture ARA claim-discipline? | ARA's claim schema minus reproduction: `Statement` (mechanism, no numbers), `Conditions`, `Falsification`, `Sources` (grounding-by-quote), `Status`, `Tags`. `PaperAnalysisResult` already has `mechanism_summary` / `critical_flaws` / `ablation_findings` to draw on. | `ara-repo-structure.md` Q1; `schemas.py:74-139` | Low |
| Q1.3 | Q.1 | Can provenance + `no_prior_match` be stored on a staged node? | **No, as-is.** `create_staging_node` emits *fixed* frontmatter (`type/status/title/created_at/tags/graph_edges`) — no passthrough for provenance tags or a `grounded:` field. Needs extension. | `staging_service.py:80-92`; `mcp-architecture-review.md` Q3; `Q.0.md` #3 | **High** |
| Q2.1 | Q.2 | What does `extract_paper` reuse? | `single_paper_ingest` flow (fetch/MinerU/PaperLoader) → **new** grounding step → `generate_structured_data(KClaimExtraction)` → `StagingService`. In-process, poll model, summary-string isolation. | `Q.0.md` Q0.2; `single_paper_ingest.py:60-94` | Low |
| Q2.2 | Q.2 | How does Grounding find prior nodes, and what licenses a `derives_from` edge? | Seeds via `query_graph`/`rg` (string-only returns; seed scan excludes only `.obsidian`). **"Confirmed match" is undefined** — topic-match ≠ a real `derives_from`. Natural definition: the paper's `related_work`/references resolve to an existing vault K node (arxiv-id/title). See §Decisions D3. | `Q.0.md` Q1.1/Q1.2; `vault_read_adapter.py:496` | **High** |
| Q2.3 | Q.2 | New staged K node, or patch the existing one? | Every paper **already has** a K node (392 exist). `extract_paper` (per Mission) stages a **new** node → duplicate/supersede tension; `create_staging_node` writes new files, not edge-patches. See §Decisions D1. | Scout-2; `staging_service.py:61-93` | **High** |
| Q3.1 | Q.3 | Do ≥5 K nodes exist, and what shape? | **392** K nodes — but in **THREE schema generations**: **A** "BB Channel" (~370: no `graph_edges`, no `arxiv_id`, `score:"9/10"` string), **B** "Anatomist" (18: `arxiv_id`+`source_md`, no edges), **C** template-conformant (13: full keys + **empty** `graph_edges` scaffold). Test fixtures must cover all 3 + duplicate-migration cases. | Scout-2 | Med |
| Q3.2 | Q.3/Q.4 | Which K nodes have reusable `source_md` (no MinerU)? | Only **Schema C (13)** — valid `chimera-lite/papers/md_papers/` path. Schema A: **no** `source_md`. Schema B: **stale** path (`crucible_core/…`, likely gone). | Scout-2 | Med |
| Q4.1 | Q.4 | Are there 20 clean backfillable nodes? | **No — only 13.** 13 Schema-C nodes have a `graph_edges` block + reusable markdown; the "20" target forces ≥7 Schema-A/B nodes that lack the block AND lack/have-stale `source_md` → MinerU re-conversion. See §Decisions D2. | Scout-2 | **High** |
| Q4.2 | Q.4 | Populated K edges today? | **Zero.** 379 K nodes have no `graph_edges` block; 13 have empty scaffolds. The only real typed edges in the vault are **T/I → K** (authored from the Thought side). So HSC-2 grounding has 392 K nodes to match *against*, but no K→K precedent to copy. | Scout-2; `[[vault-graph-edges-empty]]` | Med |

---

## Notable cross-findings (flag, don't fix)

1. **Backfill-20 exceeds the 13 clean-reusable nodes (High).** Only 13 Schema-C K nodes have both a
   `graph_edges` block and a valid `source_md`. Backfilling 20 forces ≥7 Schema-A/B nodes that need the
   block added *and* a MinerU re-conversion (no/stale markdown) — which defeats "reuse existing markdown."
2. **`extract_paper` stages a NEW K node, but the paper already has one (High).** Interacts with the
   3-schema migration (re-ingest already produces Schema C, e.g. `Memp` C vs `Memp v2` A). Backfill is
   really *enriching/replacing* existing nodes — but `create_staging_node` writes new files, and edge-
   patching an existing node is `link_nodes`/`apply_link_patch` territory. The two are different tools.
3. **`create_staging_node` fixed frontmatter blocks HSC-2/HSC-3 (High).** No slot for provenance tags or
   `grounded: no_prior_match` — Q.1/Q.2 must extend it (or add a K-specific staging writer).
4. **"Confirmed grounding match" undefined → K→K fabrication risk (High).** The memory
   (`[[vault-graph-edges-empty]]`) explicitly warns against inventing K→K edges. Topic/keyword match is
   not confirmation; citation-resolution is (D3).
5. **The structured-LLM reuse is clean (positive).** New model in `schemas.py`, Pattern-A
   `generate_structured_data`; the async twin + `asyncio.gather` (OpticsService) is the batch template for
   Q.4. Backfill needs **no MinerU** for Schema-C nodes (reuse `source_md`).

---

## Design decisions required before batch-planning (stop-and-decide — the Architect's)

Batch-planning over these would be guessing. My recommendation on each in **bold**:

- **D1 — `extract_paper` semantics on an already-ingested paper.** (a) stage a **new** Schema-C K node that
  **supersedes** the old one (upgrades content → mechanism-claims + adds grounded edges + provenance), or
  (b) **patch** edges onto the existing node (`apply_link_patch`-style, keeps old content). **→ Recommend
  (a):** one path for new-paper and backfill; the old node is superseded on promotion. Cleaner than two tools.
- **D2 — Q.4 backfill target.** Keep **20** (needs ≥7 non-C nodes → MinerU re-convert + block-add) or scope
  to the **13 clean Schema-C nodes** (reuse `source_md`, just extract+ground). **→ Recommend 13** for the
  seal (HSC: "≥1 grounded edge or explicit `no_prior_match` on each of the 13"); treat the ~379-node
  schema migration as a separate later effort, not a Phase-Q blocker.
- **D3 — What licenses a `derives_from` edge ("confirmed match").** **→ Recommend citation-resolution:** an
  edge is proposed only when the paper's `related_work`/references resolve to an existing vault K node
  (by arxiv-id/title), tagged `ai-suggested`; the **human review is the confirmation**. Fabrication-safe.
- **D4 — Extend `create_staging_node` for provenance + `no_prior_match`.** **→ Recommend:** add an optional
  metadata passthrough to `create_staging_node` (small, backward-compatible) rather than a parallel writer.

---

## Audit complete
- 10 questions answered (file:line-anchored); substrate from `Q.0.md` reused, not re-run.
- 5 notable cross-findings (4 High), **4 design decisions** for the Architect.
- **Suggested next:** settle D1–D4 (accept the recommendations or adjust), then `batch_planning` →
  `docs/plans/Phase-Q-batch.md`. The plan is one confirmation away.

---

*Generated by chimera-sprint-discipline phase_audit mode (re-run for the rewritten sprints).*
