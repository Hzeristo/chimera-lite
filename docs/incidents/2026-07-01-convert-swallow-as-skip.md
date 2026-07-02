# Incident — convert failures swallowed-as-skip → hollow success (I-5)

**Date:** 2026-07-01
**Surfaced by:** the I-4 deadlock post-mortem (`2026-07-01-mineru-capture-deadlock.md`) — the
90-min freeze reported `completed / ingested=0 errors=0`. I-4 fixed the *deadlock*; I-5 fixes the
*silent-failure amplifier* that disguised it as success.
**Severity:** HIGH (silent data loss — a total convert failure reports clean completion, no error
signal). **Audit-before-fix** per user directive.

## Symptom
A daily-pipeline run that converts **0 of N** downloaded PDFs (every MinerU convert fails)
reports `status=completed, progress=1.0, new_pdfs=N ingested=0 ... errors=0`. Indistinguishable
from a run with nothing to do. The user only discovered I-4 by manually noticing `ingested=0`.

## Root cause (two layers)
1. **Swallow (`convert_queue_worker`, `ports/ingest/mineru_pipeline.py:275`):** each per-PDF
   convert exception was caught, `logger.error`-ed, and the loop continued. The worker tracked
   only `success_count` and returned it — **failures were counted nowhere and propagated nowhere.**
2. **No aggregate guard (`_run_pipelined_async`, `daily_chimera_service.py`):** the function
   returned a normal summary even at `ingested_count == 0`, and the summary's `errors` field is
   **filter**-stage only (`stats.errors`) — convert failures never entered it. `run_task` then
   `emit_completed`s the summary → COMPLETED. Propagation is otherwise clean (no try/except
   between `_run_pipelined_async` and `run_task._run`), so a *raise* becomes `emit_failed`.

Net effect: N convert failures → `ingested=0 errors=0 completed`. Silent data loss.

## Fix
- `convert_queue_worker` now returns `(success_count, failure_count)` — per-PDF exceptions
  increment `failure_count` (still logged; no behavior change to the convert itself).
- `_run_pipelined_async`:
  - unpacks `ingested_count, convert_failures = convert_task.result()`;
  - **anti-hollow-success guard:** `if new_pdfs_count > 0 and ingested_count == 0: raise
    RuntimeError(...)` → task marked **FAILED** with a clear message (not a clean summary);
  - surfaces partial failures via a new `convert_failed=<n>` field in the completion summary.

Single caller (`daily_chimera_service.py:268/275`), so the tuple-return change is contained.

## Verification
- `tests/test_convert_worker.py`: 2 PDFs, `MineruClient.convert` monkeypatched to raise →
  worker returns `(0, 2)` and queues only the sentinel. (The counting is the enabling change.)
- ruff 0; pytest 19 passed / 1 skipped.
- Guard behavior (total convert failure → task FAILED) is exercised by the live M.5 Test-2
  re-run; the unit path is the worker's failure count.

## Notes
- Distinct from I-4: I-4 was *why* converts failed (pipe deadlock); I-5 is *why the failure was
  invisible* (swallow + no guard). Both had the same fatal fingerprint (`ingested=0 errors=0
  completed`).
- Requires an MCP reconnect to load the patched modules before the confirming re-run.
