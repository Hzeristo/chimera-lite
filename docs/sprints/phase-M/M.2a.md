# Sprint M.2a — arXiv miner + TaskService + server concurrency lock

**Status:** ✅ Complete (live arXiv fetch deferred to M.5 — network)
**Commit:** {filled at commit}
**Risk:** 🔴 HIGH — executed under per-sprint approval ("Proceed to M.2", 2026-06-28).
**Plan ref:** `docs/plans/Phase-M-batch.md` → Sprint M.2a
**Audit ref:** `docs/audits/M.0.md` Q3/Q4 + cross-finding #4

## Objective
Wire `arxiv_miner` + `check_task_status` to `TaskService` (poll model) and add the
net-new server-held concurrency lock.

## What was done
- Authored `miner_tools.py` (`arxiv_miner`, `check_task_status`) — flat imports, `str`
  returns. `check_task_status` flattens a completed `ToolOutput` JSON to `.text` (MCP has
  no structured channel).
- **Concurrency lock (cross-finding #4 — the sanctioned thin-adapter exception):**
  - `TaskService.has_active_long_task()` — disk-truth query: any `arxiv_fetch`/
    `daily_pipeline` task still PENDING/RUNNING. (~12 lines.)
  - `server.py`: an `asyncio.Lock` serializes the check-and-start; a second long-running
    start while one is active returns `[Busy] …`. (~10 lines.)
- Import rewrites `src.crucible.*` → flat across the arXiv runtime chain:
  `task_service.py` (schemas/platform; llm.base is TYPE_CHECKING-only),
  `fetch_arxiv_workflow.py`, `ports/arxiv/arxiv_fetch.py`, `ports/arxiv/__init__.py`.
- `daily_paper_pipeline` left as a single NOT-WIRED sentinel for M.2b (the lock guard is
  already in place for it).

## Verification (real exit codes)
- ruff: **0** — All checks passed.
- pytest (`tests/`): **0** — 12 passed, 1 skipped.
  - `task_id` matches `^[0-9a-f]{8}$`; `has_active_long_task()` transitions
    PENDING→busy→COMPLETED→free; non-long task does not block; `check_task_status`
    flattens ToolOutput / handles unknown id; `arxiv_miner` returns a task_id (fetch mocked).
- import smoke: `import server, miner_tools, fetch_arxiv_workflow` + `ArxivFetcher` OK.
- `grep "from src." ` over M.2a files → **0**.

## HSC status (sealing condition 2, part A)
- `arxiv_miner` → immediate 8-hex `task_id`: ✅ (test).
- `check_task_status` poll → result: ✅ (test, mocked completion).
- Second long-running start rejected (lock): ✅ (guard verified via `has_active_long_task`).
- **Live arXiv fetch returning real papers: ⏸ deferred to M.5** (needs network; the tool's
  immediate return + background scheduling are verified, fetch body mocked in tests).

## Accepted deviations / notes
1. **+1 dependency `requests`** — `arxiv_fetch.py`'s existing footprint; passes
   `chimera-dependency-veto` (ubiquitous HTTP lib).
2. **Lock split across layers:** the *query* (`has_active_long_task`) lives in TaskService;
   the *decision* (reject + serialize) lives in the server. This is the declared net-new
   logic; TaskService gains only a read-only accessor, not pipeline logic.
3. Stale-task edge: a task left RUNNING on disk after a crash would read as "busy" until
   cleared. Acceptable for single-user; noted for M.4/operational follow-up.

## Predecessor handoff to M.2b
- `miner_tools.py` exists; M.2b adds `daily_paper_pipeline` + `_run_daily_with_progress`
  and removes the `_PIPELINE_NOT_WIRED` sentinel, wiring it under the existing lock guard.
- The arXiv chain imports flat; M.2b rewrites the filter/ingest/notify chain.
