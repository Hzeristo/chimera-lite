# Incident 2026-07-13 — extract_paper / ingest_paper block silently for minutes

**Severity:** UX (no data loss). **Status:** fixed and live-verified 2026-07-13 — the operator
confirmed the stage labels render below the tool-call line during `extract_paper` / `ingest_paper`.

## Symptom
`extract_paper` (and `ingest_paper`) block for minutes — a long LLM call, and for ingest a MinerU
GPU convert — with **no progress feedback**: the client shows only a spinner. There is no way to tell
whether the tool is working, stuck, or how far along it is.

## Root cause
The single-shot tools were written as plain async functions that ran the whole domain call in one
`asyncio.to_thread(...)` and returned only at the end — no progress emission. The poll-model tools
(`arxiv_miner`, `daily_paper_pipeline`) correctly return a `task_id` and stream stage events through
`TaskService`; the single-shot tools were left silent. MCP supports `notifications/progress`, and
FastMCP exposes `ctx.report_progress(progress, total, message)` — it was simply never called.

## Fix
Emit MCP progress notifications at stage boundaries.

- **Domain layer stays ctx-free.** `extract_single_paper` / `ingest_single_paper` became `async`
  and take an optional `progress: Callable[[float, str], Awaitable[None]] | None = None`. The
  blocking sub-steps run in `asyncio.to_thread(...)` so the event loop stays free while each stage
  label is flushed *before* the long wait. `progress=None` is fully supported (pytest injects None).
- **MCP wrapper adapts ctx.** `server.py` tools take `ctx: Context` (injected by FastMCP, excluded
  from the client schema) and pass a `_reporter(ctx)` callback that calls `ctx.report_progress`.
  The call is best-effort (guarded) — a notification failure never aborts the tool.
- **Rule #4 fallback (chimera-mcp-taste).** Each stage is ALSO logged to stderr, so a no-ctx /
  captured run is never silent.

### Stage breakdown
- `extract_paper`: 0.0 Resolving markdown → 0.25 Grounding citations → 0.5 Extracting structure
  (LLM) → 0.85 Staging node → 1.0 Done.
- `ingest_paper`: 0.0 Fetching arXiv PDF → 0.15 Converting PDF (MinerU) → 0.7 Triaging (LLM) →
  0.9 Writing node → 1.0 Done.

### Files
- `server.py` — `ctx: Context` on `extract_paper`/`ingest_paper` + `_reporter(ctx)` adapter.
- `miner_tools.py` — thread `progress` through; `await` the now-async domain fns (drop the outer
  `to_thread`).
- `single_paper_extract.py` / `single_paper_ingest.py` — async + `progress` + per-stage `to_thread`.
- `tests/test_extract_paper.py` — the 4 extract tests are `async`/`await`; new
  `test_extract_reports_progress` asserts the boundaries `[0.0, 0.25, 0.5, 0.85, 1.0]`.

## Scope
- `extract_paper`: **yes** (primary — long LLM). `ingest_paper`: **yes** (MinerU + triage LLM).
- `arxiv_miner` / `daily_paper_pipeline`: **unchanged** — the poll model (`task_id` + `check_task_status`)
  is the right pattern for those and was not touched.

## Verify
- `pytest` — 77 passed (incl. progress-boundary test; `progress=None` exercised by the other extract
  tests). `ruff check` clean. All four modules `py_compile`. `server.mcp.list_tools()` shows `ctx`
  excluded from both schemas (`extract_paper -> [paper_id]`, `ingest_paper -> [arxiv_id, pdf_path]`).
- **Live (pending reconnect):** call `extract_paper` in Claude Code and confirm the stage labels
  ("Grounding citations…", "Extracting structure…") appear below the tool-call line during execution,
  not just a spinner.
