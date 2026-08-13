# Phase Review Verdict (RE-SEAL): Phase Q — Disciplined Knowledge Extraction

**Supersedes:** `docs/sprints/phase-Q/phase-review.md` (the 2026-07-10 functional seal of the
atomic-claims build, reopened same day on `friction-260710-02`).
**Rebuild record:** `docs/sprints/phase-Q/Q.R-rebuild.md` (+ its 2026-07-13 addendum).
**Audit reference:** `docs/audits/Q.0.md` + `docs/audits/Q.0-reaudit.md`
**Batch plan reference:** `docs/plans/Phase-Q-batch.md`
**Sprints in batch:** Q.1a, Q.1b, Q.2a, Q.2b, Q.3, Q.4, **Q.R (reopen rebuild)**
**Batch history source:** `docs/sprints/phase-Q/*.md`
**Date:** 2026-07-13

---

## Per-Sprint Verdicts

| Sprint | Status | Evidence | Action |
|---|---|---|---|
| Q.1a / Q.1b (schema + staging metadata) | Pass | Superseded by Q.R's `KNodeExtraction`; structural contract green — `tests/test_knode_schema.py` (12) | - |
| Q.2a (grounding = citation resolution) | Pass | Unchanged; `tests/test_grounding.py` + `tests/test_extract_schemas.py` green | - |
| Q.2b (extract orchestration) | Pass | Rebuilt in Q.R (schema/prompt/renderer); `tests/test_extract_paper.py` (9) green; validated live on STALE | - |
| Q.3 (grounding across A/B/C schemas) | Pass | `tests/test_extract_schemas.py` green | - |
| Q.4 (backfill) | Accepted Partial | Old 8/13 atomic-shape backfill CLEARED (wrong shape); corpus re-backfill deferred | Q.reseal.1 |
| **Q.R (output-shape rebuild)** | Pass | `friction-260710-02` resolved; full arc + hybrid lenses + clean render validated live (STALE, `docs/staging/20260713_035258-…`) | - |

---

## Phase-Wide Red Lines

| Red Line | Status | Verification |
|---|---|---|
| Paper markdown must NOT reach the calling agent's context | **Held** | `miner_tools.py:137` — `extract_paper` returns only `"[✔] Staged K node … {out_path}"`; never body/raw_text |
| No probabilistic prompts for CONTROL FLOW (grounding→extraction→staging hard-coded) | **Held** | `single_paper_extract.py` `extract_single_paper` — the three steps run unconditionally; the schema-constrained LLM call is content-only |
| Do NOT overwrite existing K/T/I/D schemas | **Held** | `single_paper_extract.py:273` — extraction writes `type="knowledge"` ONLY; Grep for insight/thought/decision type-writes → 0 |

---

## Hard Sealing Conditions

| Condition | Status | Verification |
|---|---|---|
| HSC 1 — mechanism-level claims (name-deletion) | Pass | Live STALE C01 "Implicit conflict resolution requires write-side state invalidation…" survives name-deletion; prompt enforces (`extract_node.j2`) |
| HSC 2 — grounded edges only, zero fabrication (no_prior_match valid) | Pass | Live STALE `derives_from: []` + `grounded: no_prior_match`; edges only via `grounding.py` citation resolution; `test_extract_schemas`/`test_grounding` green |
| HSC 3 — provenance on every AI field | Pass | Live node `provenance: ai-suggested`; every claim carries grounded `sources` (`ClaimSource{quote,location}`) |
| HSC 4 — zero I/T/D from extraction | Pass | `type="knowledge"` only (source-verified); `test_knode_schema::test_no_model_admits_an_itd_field`; single staged file per run |

---

## Driving Friction Resolution

| Friction | Original Status | Current Status | Evidence |
|---|---|---|---|
| `friction-260710-02` (output-shape drift — the reopen driver) | OPEN | **RESOLVED** | Q.R rebuild; reader's-node arc validated live on STALE |
| `friction-260710-03` (lens single-source) | OPEN | RESOLVED (at fix) | 6 canonical `prompts/lenses/*.md` read by both consumers |
| `friction-260713-01` (motivation/results arc) | OPEN | RESOLVED (at fix) | `PaperSynthesis` + motivation/results; live arc complete |
| `friction-260709-01` (vault-in-loop / lens deployment) | PARTIAL | PARTIAL | Lens-hybrid corollary now addressed (function-triggered 1-2 lenses); the AMBIENT half remains OPEN |
| `friction-260710-01` (ingest triage tunability) | OPEN | OPEN | Not a Phase Q deliverable; the triage prompt is already external — the real ask (tunable criteria) is unaddressed |

---

## Sealing Decision

⚠️ **Functionally Sealed** (2026-07-13). All HSC Pass; all three red lines Held; the reopen driver
(`friction-260710-02`) and the two follow-on frictions resolved and validated live end-to-end on a
real paper (STALE, arXiv 2605.06527). Accepted Partials: Q.reseal.1/2/3. Technical Debt filed:
**DEBT-017** (re-extraction supersede idempotency); pre-existing **DEBT-016** (5 missing-markdown
papers) remains open. The disciplined-extraction ENGINE is sealed; corpus re-backfill is deferred
operational work, not a code blocker.

---

## Live Validation (STALE, arXiv 2605.06527)

The rebuilt `extract_paper`, run end-to-end via the reconnected MCP server, produced a staged K node
demonstrating every phase goal at once:
- Full reading arc: **Motivation** (grounded) → **BB Analysis** (contribution) → **Mechanism** (bold
  bulleted) → **Core Algorithm Steps** (clean, no double markers) → **Results** (grounded headline
  numbers — the home for the numbers the claims strip) → `[My Critique]` hook.
- **Hybrid lenses fired correctly**: Forensic Leakage Audit (benchmark integrity) + State Collision
  Stress Test (mechanism depth — surfaced the unmeasured inertia threshold the single-lens run missed).
- **Attack Vectors** (clean single 💥) + ARA-disciplined **Mechanism Claims** (quote-grounded).
- Plumbing: `supersedes [[2605.06527-CUPMEM]]`, honest `no_prior_match`, staged `PENDING_REVIEW`
  (never auto-promoted — the review gate held throughout the reopen).

---

## Audit-to-Implementation Trace

| Audit / reopen finding | Outcome |
|---|---|
| Q.0 disciplined extraction (K + grounded edges, no I/T/D) | Delivered (Q.2a/Q.2b/Q.3), preserved through the rebuild |
| `friction-260710-02`: discipline is a quality bar, not the output shape | Addressed by Q.R (synthesis + lens + attack + claims-as-floor) |
| `friction-260710-03`: single-source lens logic | Addressed (`prompts/lenses/*.md`) |
| `friction-260713-01`: reading arc missing motivation + results | Addressed (PaperSynthesis) |
| Hybrid-paper lens deployment (`friction-260709-01` corollary) | Addressed (1-2 function-triggered lenses); ambient half deferred |

---

*Generated by chimera-sprint-discipline phase_review mode (re-seal).*
