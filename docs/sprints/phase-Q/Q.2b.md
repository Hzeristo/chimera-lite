# Modification Summary: Q.2b

**Phase:** Q
**Sprint:** Q.2b — `extract_paper` disciplined extraction (the 🔴 sprint)
**Batch position:** 4 of 6
**Date:** 2026-07-09
**Executed by:** main Opus session (🔴 — not delegated; gated + approved by the Architect).

---

## Files touched

| Path | Notes |
|---|---|
| `mcp-servers/chimera-papers/single_paper_extract.py` | NEW — orchestration: reuse `source_md` → `_extract_claims` (LLM) → `resolve_citations` → stage K node (supersedes old) |
| `prompts/chimera_sys/extract_claims.j2` | NEW — mechanism-claim extractor system prompt (name-deletion, grounding-by-quote, no I/T/D, leave edges empty) |
| `prompts/tasks/extract_task.j2` | NEW — user prompt (inject schema + paper) |
| `mcp-servers/chimera-papers/miner_tools.py` | `extract_paper` delegate (`asyncio.to_thread`, error-string handling) |
| `mcp-servers/chimera-papers/server.py` | new `@mcp.tool extract_paper` (thin: lock-check → delegate) |
| `mcp-servers/chimera-papers/staging_service.py` | `promote_node` supersede-unlink guard + `_unlink_superseded` (D1) |
| `tests/test_extract_paper.py` | NEW — 7 tests (grounded edge, no_prior_match, backup-exclusion, supersede edge, promote-unlink, helpers) |

---

## Verification

| Check | Status | Output |
|---|---|---|
| ruff | clean | exit 0 — "All checks passed!" |
| pytest (`test_extract_paper.py`) | 7/7 | exit 0 |
| pytest (surface: extract + staging + grounding + schema) | 38/38 | exit 0 |
| server smoke (`import server, miner_tools`) | loads | `extract_paper` registered on both — the mcp-taste "loads under the server" check |

---

## Rule Conformance Self-Check

| Rule | Status | Evidence |
|---|---|---|
| DDD layering | ✓ | `single_paper_extract` (orchestration) → `grounding` / `StagingService` / `PromptManager` / `core.schemas`; one direction |
| exception_handling | ✓ | `miner_tools.extract_paper` catches `FileNotFoundError` / `Exception` → error string; `_extract_claims` raises (no degraded node); no bare `BaseException` |
| logging_format | ✓ | `[Extract]`-prefixed info log |
| thin adapter | ✓ | `server.py` tool body = lock-check + delegate; domain logic in `single_paper_extract`; `server.py` ~145 lines (< 200) |
| no_opportunistic_refactor | ✓ | only the 7 listed files; `ingest_paper` / `create_staging_node` untouched |

---

## Red Line Status

| Red Line (batch plan) | Status | Verification |
|---|---|---|
| No I/T/D node from extraction (HSC 4) | Held | `extract_single_paper` only writes `type="knowledge"`; test asserts exactly ONE staged file |
| No fabricated edge; `no_prior_match` when none | Held | edges come only from `resolve_citations`; `test_extract_no_prior_match` + `test_extract_excludes_migration_backup` |
| Staging-only; never auto-promote | Held | writes via `create_staging_node` to `docs/staging/`; the live vault is untouched (promotion is separate) |
| No new MCP server / dependency; `.mcp.json` stays 2 | Held | `extract_paper` is a new `@mcp.tool` on existing `chimera-papers`; reuses MinerU-free path, `generate_structured_data`, `StagingService`, `grounding`; no new import deps |
| 不进行机会主义重构 | Held | 7 files only |

---

## Acceptance Criteria

| Criterion (batch plan Q.2b) | Status | Evidence |
|---|---|---|
| stages ONE K node with mechanism claims, ≥0 grounded edges (or `no_prior_match`), `provenance: ai-suggested`, NO I/T/D | Met | `test_extract_grounded_edge` / `test_extract_no_prior_match` |
| tool returns a summary string; staging shows the node; live vault untouched until promotion | Met | delegate returns `[✔] Staged K node …`; staged file asserted; no vault write |
| `server.py` stays a thin dispatcher | Met | tool body is lock-check + delegate |

---

## Notes

- **Supersede (D1):** the staged node records `supersedes: [[old-stem]]` when a prior node for the paper
  exists; `promote_node` unlinks the superseded node on promotion (`_unlink_superseded`). Tested.
- **`title = paper_id`** (bare id) for the staged node — the old moniker is dropped. Minor; the reviewer
  can rename at promotion. Follow-up: carry a moniker if desired.
- **`KClaimExtraction.proposed_edges` is filled by the LLM but IGNORED** — edges are minted by grounding
  (D3), not the LLM (which cannot know vault stems). The prompt tells the LLM to leave it empty; the
  pipeline uses `resolve_citations`. Flagged for phase_review (the field is a future affordance).
- **New-paper fetch+MinerU is a stub** — `_resolve_markdown` raises if no converted markdown exists.
  Backfill (Q.4) reuses `source_md`, so this is not on the seal path; a later extension.
- **Mechanism-vs-recipe discipline** lives in the extraction prompt (`extract_claims.j2`) + is validated on
  real LLM output (Q.3/Q.4), not structurally — consistent with the Q.1a re-scope.

---

## Commit Status

- [x] Committed

```
feat(crucible): Q.2b — extract_paper disciplined extraction (K node + grounded edges)
```

---

**Sprint result: Pass.** Next: Q.3 (🟢 discipline test / A-B-C fixtures) then Q.4 (🟡 live backfill of the 13).

---

*Generated by chimera-code-taste batch_execution mode, per-sprint summary.*
