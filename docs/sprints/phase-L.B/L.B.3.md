# Modification Summary: L.B.3

**Phase:** L.B — Consolidation
**Sprint:** L.B.3 — `ascend_node` MCP tool + unified write path 🔴
**Batch position:** 4 of 7 (parallel-eligible with L.B.2 after L.B.1)
**Date:** 2026-07-21
**Executed by:** Sonnet subagent (`chimera-sprint-executor`); design authored + reviewed + committed by main session (Opus). Verification independently re-run via `chimera-verify-runner` (Haiku).

## Objective
Make `ascend_node` the SOLE code path that writes into the committed `Knowledge/` tier: validate
`chimera_tier == "deep_read"`, set `status: active`, write to `<vault>/Knowledge/`, unlink any
superseded prior. Make the guarantee STRUCTURAL via a `promote_node` guard (per plan PATCH 2).

## Files touched
| Path | Change |
|---|---|
| `staging_service.py` | Extract `_promote_write` (shared: status→active + write to `_TYPE_DEST[type]` + `_unlink_superseded`); `promote_node` guards `chimera_tier=='deep_read'` (raises, cites `ascend_node`); new `ascend_node` validates `deep_read` then delegates to `_promote_write` |
| `mcp-servers/chimera-vault/server.py` | New thin `ascend_node` `@mcp.tool` (lazy-import dispatcher; WHEN/WHAT/CONTRAST docstring) |
| `tests/test_ascend_node.py` | new — deep_read ascends to `Knowledge/`; scout/synthesis/untiered refused; `promote_node` refuses deep_read; `promote_node` still works for T/I/D |
| `tests/test_extract_paper.py` | **unchanged** — see note |

## Key design facts / decisions
- **Grounding verification DEFERRED to DEBT-018** (note 2 / reconciliation #6): `ascend_node` does NOT substring-verify grounding quotes. Cited in the service docstring + a comment at the deferred check. Human staging-review remains the check; the tier gate is the structural backstop.
- **The guard is TIER-keyed** (`chimera_tier=='deep_read'`), per plan PATCH 2 — not type-keyed. Consequence: the sole-writer guarantee is **airtight for `deep_read`** (the only tier real flows send to `Knowledge/`), but an *untiered* `knowledge` staging node would still promote to `Knowledge/` via `promote_node`. No such node arises in the pipeline (`extract` sets `deep_read`; `create_node` makes only T/I/D); it exists only as a synthetic fixture in `test_promote_unlinks_superseded`. If a type-airtight guarantee is later wanted, extend the guard to cover untiered/scout `knowledge` — a change from PATCH 2's explicit spec, so NOT done here.
- **F5 correction realized:** audit F5 claimed "no writer targets `Knowledge/`", but `promote_node` (via `_TYPE_DEST['knowledge']='Knowledge'`) could. The tier guard closes that for `deep_read`. (Plan recon #5 already updated in the prior commit.)
- **`test_extract_paper.py` unaffected (executor-verified):** its only `promote_node` call (`test_promote_unlinks_superseded:247`) builds a `knowledge` staging node with NO `chimera_tier` (K is never defaulted — L.B.1), so `fm.get('chimera_tier') != 'deep_read'` and `promote_node` proceeds unchanged. Not part of the `extract_single_paper` flow. No edit needed.
- **Reuse, no new supersede logic:** `_promote_write` reuses `_unlink_superseded` + `_TYPE_DEST` verbatim; non-`deep_read` promotion output is byte-identical to before.

## Verification (independently re-run in main session)
| Check | Status | Output |
|---|---|---|
| ruff | clean | exit 0 — "All checks passed!" |
| pytest (env-artifact deselected) | 124 passed | exit 0 — `124 passed, 1 deselected in 2.05s` |

## Red Line Status
| Red Line | Status |
|---|---|
| `ascend_node` sole writer of `Knowledge/` — code-enforced | ✓ (for `deep_read`; via `promote_node` guard) |
| Only `deep_read` ascends; scout/synthesis/untiered refused | ✓ (`test_ascend_node_refuses_non_deep_read_tier`) |
| Reuse Phase-Q supersede/promote — no new supersede logic | ✓ (`_unlink_superseded` reused) |
| Thin adapter — logic in `staging_service.py`, not `server.py` | ✓ |
| Grounding deferred to DEBT-018, not substring-verified | ✓ |
| No opportunistic refactoring beyond `_promote_write` extraction | ✓ |

## Acceptance
- ✅ HSC #3 (for the real pipeline): `ascend_node` promotes a `deep_read` node to `Knowledge/`; non-`deep_read` refused; `promote_node` on a `deep_read` node raises rather than writing (structural). Untiered-knowledge caveat documented above.
- ✅ Scout cards still land in `inbox/` (untouched) and are not auto-promoted.

**Seal:** L.B.3 complete.
