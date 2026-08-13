# Sprint C.3a — The `promote` transition

**Phase:** L.C (Colligo) · **Risk:** 🟡 MED · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Baseline:** `docs/audits/L.C.1-friction-baseline.md` §4
**Executed by:** `chimera-sprint-executor` (pinned Sonnet). Reviewed + verified by the Opus main
session; commit owned by main.
**Outcome:** ✅ Pass

## Why

`docs/phases/phase-L.md:139-142` declares the harness-artifact lifecycle
`PENDING_REVIEW → PROMOTED | REJECTED`. No code implemented `PROMOTED`. C.1 confirmed it
empirically: all 6 artifacts in the live vault's `Harness/` sit at `PENDING_REVIEW`, and not one
has ever been promoted. Route 3 of the VISION — "review [V] claims, batch-promote" — had no
terminal operation, which is why the gap survived two phase specs unnoticed: nobody ever walked
the route to its end.

## Changes

- `result_service.py:57` — `_VALID_MODES` gains `"promote"`.
- `result_service.py:175-181` — dispatch through the existing `_transition` via an explicit
  `{"promote": "PROMOTED", "reject": "REJECTED", "mark_stale": "STALE"}` map. The mechanism
  already generalized over a target status; only the mode and its dispatch were missing.
- `chimera-vault/server.py:304` — `mode` `Literal` widened to include `"promote"`; the contract
  docstring updated in both places it describes modes.
- `tests/test_result_lifecycle.py` — new, 4 tests: promote flips the status; body and all
  non-status frontmatter stay byte-identical; a missing artifact raises; an unknown mode is still
  rejected.
- `docs/ARCHITECTURE/ARCHITECTURE.md` — regenerated (`scripts/gen_architecture_diagram.py`,
  exit 0). The only delta is a line-number shift, `result_service.py:132` → `:133`, caused by this
  sprint's docstring edit. The generated-artifact staleness test is doing its job.

## Verification

| Command | Result | Exit |
|---|---|---|
| `pytest tests/ -q -k "lifecycle or result"` | `20 passed, 213 deselected` | **0** |
| negative control — `promote` mis-wired to `"REJECTED"` | `FAILED ...::test_promote_flips_pending_review_to_promoted` · `AssertionError: assert 'REJECTED' == 'PROMOTED'` | **1** |
| negative control — restored | `4 passed` | **0** |
| full suite (after the C.3b scope repair below) | `233 passed in 6.98s` | **0** |

## Red lines

All held.

- `Literal`s **widened, never relaxed to `str`** — `ENFORCEMENT_DEBT` R5a stays discharged only
  while these remain closed sets rejected at the JSON-RPC boundary before the handler runs.
- `write_result`'s `depends_on` parameter untouched (pinned to a coordinated K.1 rename, D-4).
- Harness promotion does **not** route through `ascend_node` — different tier, different gate; no
  `chimera_tier` was added to harness artifacts.
- `promote` is reachable only via an explicit caller-supplied mode; nothing auto-promotes (I0.1).
- No opportunistic refactoring of the other modes.

## Notes

Pre-existing ruff findings on both edited files (2× `DTZ005`, plus import-order in `server.py`)
were confirmed identical against `git show HEAD:...` and left alone — not introduced here, and
out of scope.

Route 3 can now complete. Whether it completes *legibly* is C.3c's problem.
