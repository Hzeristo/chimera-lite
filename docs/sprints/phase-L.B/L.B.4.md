# Modification Summary: L.B.4

**Phase:** L.B — Consolidation
**Sprint:** L.B.4 — K-node lifecycle integration 🟡
**Batch position:** 6 of 7 (parallel-eligible with L.B.5; both require L.B.1 + L.B.3 sealed)
**Date:** 2026-07-21
**Executed by:** code half (`vault_query.py` + test) by Sonnet subagent (`chimera-sprint-executor`); skill-edit half (`chimera-deep-extract` `w1_offer`) + review + commit by main session (Opus).
**Commit:** `14c20a6`

---

## Objective

Close the deep-read arc without auto-running W1: the `chimera-deep-extract` skill surfaces a
`w1_offer` hint on completion (drawn from the claims its subagent already produced), and
`vault_query` returns `chimera_tier` in each row so a caller can filter deep_read vs scout.

---

## Files touched

| Path | Change |
|---|---|
| `.claude/skills/chimera-deep-extract/SKILL.md` | Added step 7: surface a `w1_offer` hint from `KNodeExtraction.claims` (1-3 verbatim-checkable, load-bearing, contestable claims, each paired with its cited source) phrased as a candidate for `chimera-w1-verify`. OFFER only — never auto-runs W1, never mints new claims, empty-claims path offers nothing. Flipped the former "❌ No `w1_offer` step here (out of scope)" red line into the new "hint only, never auto-run, never a new claim" red line. |
| `mcp-servers/chimera-vault/vault_query.py` | Emit `chimera_tier` in each result row's excerpt: `type=…  tier=…  status=…` (falls back to `?` like the other two fields). Thin return-field addition — no new query/filter logic. |
| `tests/test_lifecycle_integration.py` | **New** — asserts a `vault_query` result row carries `chimera_tier`. Fixture writes frontmatter via `write_bytes` with explicit `\n` (Windows `Path.write_text` translates `\n → \r\n`, which breaks the `^…$` line anchors in `vault_query`'s ripgrep pattern — a real trap for anyone extending vault-note fixtures on Windows). |

---

## Key design facts / decisions

1. **The `w1_offer` lives in the skill, not the MCP primitive.** `get_paper_markdown` (the former
   `extract_paper`) is a dumb path primitive with no claim awareness; the offer belongs in the
   skill that produced the claims (reconciliation #4 / batch plan task 1). MCP cannot spawn
   subagents (Phase Q B1), so the offer is a return-value HINT the calling agent acts on — never an
   auto-run. W1 stays explicitly invoked.

2. **The offer draws only on already-produced claims.** No new claim is minted in the offer step —
   it selects from `KNodeExtraction.claims` the subagent returned. This keeps the skill from
   becoming a second, ungrounded judgment site.

3. **`vault_query`'s tier row is where the query-tier work belongs, not L.B.1** (reconciliation #4).
   L.B.1 added the field to write paths + templates; surfacing it in query rows was deferred here to
   avoid duplicating the change across two sprints.

4. **Invented-name catch.** The skill draft initially referenced `chimera-verify-claim`; the real
   W1 skill is `chimera-w1-verify` (verified against `.claude/skills/`). Corrected before commit —
   an advisory pointing at a non-existent skill would be exactly the "advisory theater" the north
   star warns against.

---

## Verification

| Check | Status | Output |
|---|---|---|
| ruff (`vault_query.py`, `test_lifecycle_integration.py`) | clean | exit 0 — "All checks passed!" (run via `uv run --with ruff`; `.venv` lacks a ruff module — pre-existing env gap, not a sprint defect) |
| pytest (`tests/test_lifecycle_integration.py`) | 2 passed | exit 0 — `2 passed in 0.17s` |
| Pure-English (`rg \p{Han}` over the skill + code) | 0 hits | exit 1 (clean) |
| `w1_offer` step present + red line flipped | ✓ | step 7 + red line both reference `chimera-w1-verify` |

---

## Red Line Status

| Red Line | Status |
|---|---|
| `extract_paper` does NOT auto-run W1 — offer only; W1 stays explicitly invoked | ✓ — step 7 is a hint; red line restated |
| No deepseek in the offer/hint path | ✓ — no LLM call anywhere in the path |
| Thin adapter | ✓ — `vault_query` change is a return-field addition, no new logic |
| No opportunistic refactoring | ✓ — only the three files above, only for this change |

---

## Acceptance

- ✅ `chimera-deep-extract` completion surfaces a W1 offer (a hint, not an auto-run) drawn from `KNodeExtraction.claims`.
- ✅ `vault_query` rows carry `chimera_tier`; a caller can filter deep_read vs scout.

**Seal:** L.B.4 complete.
