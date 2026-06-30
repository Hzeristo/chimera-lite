# Incident — miner pipeline: invisible failures + apparent serial execution

**Date:** 2026-06-30
**Surfaced by:** M.5 Test 2 friction — user reported: (1) no output to the MCP shell,
(2) running bugs invisible to the user, (3) "pseudo concurrency: serial for most times."
**Severity:** High (pipeline unobservable → undebuggable) / Fix difficulty: minor.
**Mode:** semi-sprint, fire-at-will audit (no batch plan, no sprint docs) — user-directed.

## Audit (fire-at-will — started with zero knowledge of the bug)
Traced the full daily-pipeline data path:
- `download_pdfs_to_queue` (`arxiv_fetch.py:289`) — streams each PDF onto `pdf_queue` via
  `asyncio.as_completed`, blocking fetch offloaded with `asyncio.to_thread`. **Concurrent.**
- `convert_queue_worker` (`mineru_pipeline.py:251`) — single worker, MinerU subprocess via
  `asyncio.to_thread`. Single worker is **intentional** (RTX 5060 8GB; two concurrent MinerU
  → OOM).
- `filter_queue_worker` (`batch_filter_workflow.py:202-212`) — 3 workers; **every** blocking
  call (load / LLM evaluate / vault write / route) wrapped in `asyncio.to_thread`.

**Finding: the asyncio concurrency is correct.** There is no event-loop-blocking serializer.

## Root cause (one cause, three symptoms)
**Neither MCP server configured logging.** MCP stdio servers cannot log to stdout (it is the
JSON-RPC channel); logs must go to **stderr**. With no handler, Python's lastResort emits
only WARNING+ and all `[Service]/[Ingest]/[Arxiv]` INFO progress vanished. Combined with the
per-item `except Exception: logger.error(...)` in the convert/filter workers, **partial
failures were swallowed silently** (a run could "complete" with 0 conversions and no visible
error).

- **#1 no stdout output** → correct (must not use stdout); the real gap was no stderr handler.
- **#2 invisible bug** → handler-less logger + per-item catch-and-continue.
- **#3 pseudo-serial** → with the MinerU-PATH bug (`2026-06-30-mineru-not-on-path.md`) convert
  produced nothing, and with zero logs the working overlap was invisible → *read* as serial.
  The single-GPU convert is the intentional bottleneck, not a concurrency defect.

## Fix (observability, not re-architecting)
- `chimera-papers/server.py` + `chimera-vault/server.py`: `logging.basicConfig(level=INFO,
  stream=sys.stderr, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")`.
  **stderr only** — verified app logs do NOT leak to stdout (probe: stdout marker count 0,
  stderr 1), so the JSON-RPC channel stays clean.
- `task_service.run_task`: `logger.exception(...)` before `emit_failed` — full traceback to
  stderr on any background-task crash (the task JSON only keeps the message).

## Verification
- ruff 0; pytest 15 passed / 1 skipped.
- Stderr-routing probe: a `logging.info` marker appears in stderr, never in stdout.
- Both servers start clean with the handler installed.

## NOT changed (deliberate — would break a red line or is design-inherent)
- Convert stays a single GPU worker (OOM red line). #3 is not "fixed" because it is not a
  bug; the concurrency is correct and now **observable**.

## Open follow-up (deferred — real perf lever, big change)
MinerU is invoked as a fresh subprocess per PDF (`paper2md.py`), reloading models each time —
the dominant per-PDF cost. A persistent MinerU worker/daemon would cut it, but that is a
design change, not an incident fix. Worth a friction entry if throughput matters.
