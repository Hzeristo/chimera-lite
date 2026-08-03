# Incident — `analyze_paper_data` shipped unregistered; `chimera-triage-paper` Path 1 could not run

**Date:** 2026-08-03
**Surfaced by:** the post-merge live re-run of the L.B.6 five-path e2e (operator-directed, before
the Phase L.B seal). Invoking `chimera-triage-paper` on `2602.01869` hit step 1 —
`analyze_paper_data(paper_id)` — and the tool was absent from the live `chimera-papers` registry.
**Severity:** Medium (a shipped skill's entry step is unreachable; no data loss, no wrong output) /
Fix difficulty: minor (one thin `@mcp.tool` registration + its delegate).
**Status:** fixed; test-verified + direct-call verified. Live MCP reachability requires a server
restart (see Verification).

## Symptom
`chimera-triage-paper` SKILL.md step 1 instructs the orchestrator to call
`analyze_paper_data(paper_id)` → `{markdown_path, metadata}`. No such tool exists in the live
registry — `chimera-papers` exposed nine tools (`arxiv_miner`, `daily_paper_pipeline`,
`ingest_paper`, `fetch_paper`, `convert_pdf_to_md`, `get_paper_markdown`, `stage_deep_read_node`,
`write_scout_card`, `check_task_status`) and `analyze_paper_data` was not among them. Path 1 of the
four-path model therefore could not run at all through its intended L.B.2 flow.

## Root cause
L.B.2 built the primitive but never exposed it. `filter_service.analyze_paper_data`
(`mcp-servers/chimera-papers/filter_service.py:24`) was written, documented, and unit-tested — and
the `@mcp.tool` registration in `mcp-servers/chimera-papers/server.py` was never added. The sprint
record `docs/sprints/phase-L.B/L.B.2.md:39` asserts the skill "orchestrates `analyze_paper_data` →
… → `write_scout_card`", a wiring that did not exist.

**Why the tests missed it.** `tests/test_filter_service.py` imports the function directly and
asserts its behaviour (path, metadata, `FileNotFoundError`). Every assertion passed. The tests
proved the primitive *worked*; nothing proved it was *reachable*. A domain function and a
registered tool are different artifacts, and only the former had coverage.

**Why L.B.6 missed it.** L.B.6 exercised Path 1 as `ingest_paper 2605.06527` — the pre-L.B.2 flow
that predates the externalized-triage split — so the new skill's entry step was never executed. Its
Finding 1 (registry staleness against an unmerged worktree) masked the gap further: the scout card's
missing `chimera_tier` was attributed wholly to the stale registry.

## Fix
Register the primitive; change nothing about the (correct) domain code.

- `mcp-servers/chimera-papers/miner_tools.py` — new `analyze_paper_data(paper_id) -> str`
  delegate, mirroring its sibling `get_paper_markdown`: strip/guard the id, **lazy-import**
  `filter_service` (keeps the config/vault chain out of module load), run the sync primitive in
  `asyncio.to_thread` (it does real file I/O via `PaperLoader`), return the payload as JSON.
  Errors follow the module convention — `[Tool Error]: …` for a bad argument, `[Extract Error] …`
  for an unconverted paper. Added `import json`.
- `mcp-servers/chimera-papers/server.py` — thin `@mcp.tool() analyze_paper_data` with a
  WHEN/WHAT/CONTRAST docstring; the body is one delegation line (thin-adapter rule).
- `tests/test_mcp_tool_registration.py` (new) — the regression, written against the defect *class*
  rather than the single instance: it parses both `server.py` files for `@mcp.tool()`-decorated
  names and asserts that every primitive each Phase-L / L.B skill orchestrates is registered
  (`chimera-triage-paper`, `chimera-deep-extract`, `chimera-w1-verify`, `chimera-w2-map`). Parsing,
  not importing — the servers instantiate FastMCP and pull a heavy chain at module load.

Return shape is a JSON **string**, matching every other tool in the module (`-> str`), so the
error-string convention stays uniform rather than becoming a `dict | str` union.

## Verification
- `pytest tests/test_mcp_tool_registration.py tests/test_filter_service.py` → **10 passed**.
- Full suite `pytest tests/` → **157 passed, 0 failed**.
- Direct domain call (mcp-taste rule 8 — direct before transport):
  `miner_tools.analyze_paper_data("2602.01869")` returns the real markdown path plus resolved
  metadata (7 authors, year 2026); the empty-id and unconverted-paper guards return their
  conventional error strings.
- ruff: the 9 findings on the touched files (7×`BLE001`, `I001`, `RUF100`) are **pre-existing** —
  proven by running the same ruff build against `git show HEAD:` copies of both files, which
  produces the identical 9. This change adds zero new findings.
- **Live MCP reachability requires a server restart.** The running `chimera-papers` process loaded
  `server.py` at startup, so the new tool is not in the current session's registry until the MCP
  servers reconnect. Same mechanism as L.B.6 Finding 1, different cause (fresh registration rather
  than a stale checkout).

## Lesson
A unit test on a domain function does not test an MCP tool. The registration is a separate
artifact with a separate failure mode, and "the function is tested" reads as coverage while the
seam is bare. This is the repo's own north star in miniature — a test that proves the primitive but
not its reachability is advisory rigor: it reports safety it does not deliver. The regression test
is deliberately written over the whole skill→tool surface, so the next unwired primitive fails a
test instead of failing an operator mid-e2e.

## Follow-up (deferred, not a blocker)
`docs/sprints/phase-L.B/L.B.2.md:39` records a wiring that was not delivered. Correcting that
record — and deciding whether the gap changes L.B.2's verdict — belongs to the Phase L.B
phase_review, which is currently halted pending vault node population.
