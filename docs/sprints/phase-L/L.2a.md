# Sprint L.2a — `fetch_paper` + `convert_pdf_to_md` primitives

**Phase:** L (Locus) · **Risk:** 🟡 MED · **Date:** 2026-07-16
**Plan:** `docs/plans/Phase-L-batch.md` · **Audit:** `docs/audits/L.0.md` (D1/D2)
**Executed by:** Sonnet subagent (edits) + Opus main session (review + commit).

## What was built
- `_fetch_pdf(arxiv_id, settings)` in `miner_tools.py` — shared download primitive wrapping
  `single_paper_ingest._fetch_arxiv_pdf` (lazy import, run in a worker thread).
- `fetch_paper(arxiv_id, settings=None)` delegate — bare PDF download, writes NO node; returns the path.
- `convert_pdf_to_md(pdf_path=None, arxiv_id=None, settings=None)` delegate — standalone
  `MineruClient.convert` wrapper; fetches first (via `_fetch_pdf`) when only `arxiv_id` is given; writes NO node.
- Thin `@mcp.tool` wrappers for both in `chimera-papers/server.py`, gated by the same
  `_start_lock` + `has_active_long_task` busy-check as `ingest_paper`; WHEN/WHAT docstrings contrasting
  with `ingest_paper`.
- `tests/test_fetch_convert_primitives.py` — 7 tests, network + GPU mocked; an autouse fixture patches
  `VaultNoteWriter.write_knowledge_node` + `StagingService.create_staging_node` to RAISE — a behavioral
  proof of "no vault node written."

## Verification
- pytest `tests/test_fetch_convert_primitives.py`: **7 passed**, exit **0**. Full suite: **92 passed** (no regressions).
- `uvx ruff check`: clean, exit **0**.
- **Decision: PASS** (0/0).

## Red-line check
- ✅ Neither tool writes a vault node (behaviorally proven by the forbid-writes fixture).
- ✅ Reuses `_fetch_arxiv_pdf` + `MineruClient.convert` — no reimplementation, no new dependency.
- ✅ Thin adapter — delegates in `miner_tools.py`; `server.py` bodies are lock-gated dispatchers.
- ✅ No opportunistic refactoring (`ingest_single_paper`'s node-writing path untouched).

## Notes
- Delegates take an injectable `settings: ChimeraConfig | None` (DI for testability), matching the
  ingest/extract pattern.
- The retired Phase R's R.1 (`convert_pdf_to_md`) is delivered here as the thin wrapper the L.0 audit
  (D2) predicted — new logic ≈ 0, it wraps the already-live `MineruClient.convert`.

**Delivers:** W1/W2 input primitives (fetch + convert). **Next:** L.2b (🔴 `write_result`) — HALTED for approval + open decision #9.
