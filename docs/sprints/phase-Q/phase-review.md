# Phase Review Verdict: Phase Q — Disciplined Knowledge Extraction

**Audit reference:** `docs/audits/Q.0.md` + `docs/audits/Q.0-reaudit.md` (2026-07-09)
**Batch plan reference:** `docs/plans/Phase-Q-batch.md` (approved 2026-07-09)
**Sprints in batch:** Q.1a, Q.1b, Q.2a, Q.2b, Q.3, Q.4 (6 of 6)
**Batch history source:** `docs/sprints/phase-Q/*.md` (per-sprint records, written at each commit)
**Date:** 2026-07-10

---

## Per-Sprint Verdicts

| Sprint | Status | Evidence | Action |
|---|---|---|---|
| Q.1a — `KClaimExtraction` model | Pass | `core/schemas.py` (`ca079ca`); 12 tests, ruff clean | - |
| Q.1b — `create_staging_node` metadata | Pass | `staging_service.py` (`8223814`); 2 tests + 12-test staging regression | - |
| Q.2a — citation-resolution grounding | Pass | `grounding.py` (`afb3969`); 7 tests; excludes `.migration_backup`/`templates` | - |
| Q.2b — `extract_paper` 🔴 | Pass | `single_paper_extract.py` + tool wiring + `promote_node` supersede (`7736ec6`); 7 tests; server loads with tool | - |
| Q.3 — A/B/C schema fixtures | Pass | `test_extract_schemas.py` (`343d8f5`); 4 tests | - |
| Q.4 — live backfill (8/13) | Pass (Accepted Partial) | `b4b9378`; 8/8 staged, 21 grounded edges, 3 `no_prior_match` | 5 deferred → `Q.seal.1` + `DEBT-016` |

---

## Phase-Wide Red Lines

| Red Line | Status | Verification |
|---|---|---|
| Zero I/T/D nodes from extraction (HSC 4) | Held | `single_paper_extract.py:189` writes `type="knowledge"` only; staging held exactly 8 K nodes after backfill |
| No fabricated edges — citation-resolution only | Held | `grounding.py` matches resolved arxiv-ids only; backfill: 5 grounded / 3 honest `no_prior_match` |
| Staging → review → never auto-promote | Held | no `VaultNoteWriter` / `write_knowledge_node` / `promote_node` in extract (grep = none); all 8 nodes `PENDING_REVIEW` in `docs/staging/` |
| No new MCP server / no new dependency; `.mcp.json` stays 2 | Held | `git diff 4d0295c..HEAD -- pyproject.toml .mcp.json` = empty; `.mcp.json` = `chimera-papers` + `chimera-vault` |
| Thin adapter | Held | `chimera-papers/server.py` tool body = lock-check + delegate; domain logic in `single_paper_extract.py` |
| Backward-compatible staging | Held | `create_staging_node(metadata=None)` byte-identical (Q.1b key-set test) |

---

## Hard Sealing Conditions

| Condition | Status | Verification |
|---|---|---|
| HSC 1 — mechanism-level claims (name-deletion) | Pass | prompt-enforced (`extract_claims.j2`); live backfill spot-check (`2602.01869`): mechanism statements, numbers in `Sources` quotes, not statements |
| HSC 2 — grounded edges only / `no_prior_match` when none | Pass | all 8 backfill nodes are `citation_resolved` (21 edges) or `no_prior_match`; zero fabrication |
| HSC 3 — provenance on every field | Pass | every staged node carries `provenance: ai-suggested` + `grounded:` |
| HSC 4 — zero I/T/D from extraction | Pass | `type="knowledge"` only; staging holds 8 K nodes |

---

## Driving Friction Resolution

| Friction | Original | Current | Evidence |
|---|---|---|---|
| `friction-260708-01` — manual typed-edge filling | OPEN | **RESOLVED** | `extract_paper` auto-proposes typed `derives_from` edges from citations (review-gated); the Q.4 backfill minted 21 real edges. Edge-filling is no longer hand labor. |
| `friction-260709-01` — vault absent from the agentic loop | OPEN | **PARTIAL (stays OPEN)** | A disciplined, explicit vault-write path (`extract_paper`) now exists — the operator can populate the graph on demand. But the **ambient** half (the always-active observer never firing during conversation) is explicitly scoped OUT of Phase Q (Scope Cut G2) and remains open. |

---

## Sealing Decision

⚠️ **Functionally Sealed.** All 6 sprints Pass; all 4 Hard Sealing Conditions Pass; every phase-wide red
line Held. `friction-260708-01` resolved; `friction-260709-01` partially addressed (explicit extraction
built; ambient-observe deferred by design). One Accepted Partial (`Q.seal.1` — 8/13 backfilled) and one
Technical Debt (`DEBT-016` — the 5 missing-markdown papers) filed. Phase moves forward; the gap is tracked.

**What Phase Q delivered:** `extract_paper` — a disciplined, staging-only extraction tool that distills a
paper into mechanism-level Knowledge claims (ARA *discipline*, not *format*) plus citation-grounded K→K
edges, superseding the paper's prior node on promotion, writing no Insight/Thought/Decision and fabricating
no edge. The live backfill produced the **first populated typed edges the vault has ever carried** (21
`derives_from`, all resolved citations), staged for the Architect's review.

---

## State File Updates

### Auto-applied (phase_review authority)
- `docs/ACCEPTED_PARTIALS.md` — appended **Q.seal.1** (8/13 backfill; 5 deferred, `source_md` missing) +
  **Q.seal.2** (design re-scopes: name-deletion prompt-enforced not schema-enforced; `contradicts` out of
  grounding scope; `title=paper_id`, LLM `proposed_edges` ignored, new-paper fetch+MinerU stubbed).
- `docs/TECHNICAL_DEBT.md` — appended **DEBT-016** (5 Schema-C papers un-backfilled: `source_md` markdown
  absent; fix by re-ingest or by `_resolve_markdown` reading each node's own `source_md` frontmatter).
- Friction — `friction-260708-01` OPEN → RESOLVED; `friction-260709-01` annotated PARTIAL (stays OPEN).

### Applied — transcribing the Architect's dictated seal (this seal was user-requested)
- `docs/ROADMAP.md` — Phase Q → Functionally Sealed; Active → none.

---

## Audit-to-Implementation Trace

| Audit finding (Q.0-reaudit) | Outcome |
|---|---|
| #1 B1↔R1 substrate tension | Resolved (D1/D2 decisions) → extend `ingest_paper`; `extract_paper` built |
| #2 backfill-20 > 13 clean nodes | Scoped to Schema-C (D2); reality was 8/13 with markdown → `Q.seal.1` + `DEBT-016` |
| #3 `create_staging_node` fixed frontmatter | Fixed by Q.1b metadata passthrough |
| #4 "confirmed match" undefined → fabrication risk | Fixed by Q.2a citation-resolution (D3); 0 fabricated edges in backfill |

---

*Generated by chimera-sprint-discipline phase_review mode.*
