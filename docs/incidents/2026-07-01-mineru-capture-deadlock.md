# Incident — daily_paper_pipeline hollow success: MinerU capture_output pipe deadlock

**Date:** 2026-07-01
**Surfaced by:** M.5 E2E smoke, Test 2 re-run (`docs/audits/M.5-e2e-smoke.md`), after the
MinerU-PATH fix (`2026-06-30-mineru-not-on-path.md`).
**Severity:** Critical (silent data loss — pipeline reports success, ingests nothing) /
Fix difficulty: minor (drop `capture_output`, redirect to a file).

## Symptom
`daily_paper_pipeline` (`f46283f4`) ran **90 minutes** and reported
`completed / progress=1.0`, result `new_pdfs=3 ingested=0 ... reject=0 errors=0 telegram=no`.
Three PDFs downloaded, **zero** markdown produced, **zero** ingested — yet `errors=0` and
status `completed`. A **hollow success**: the pipeline lied that it did work. The 90 min =
exactly **3 × 1800s** (the per-PDF MinerU timeout). During the run the live `mineru.exe`
sat at **0 CPU / 5 MB** — blocked, not computing.

## Root cause
`MineruClient.convert` (`ports/ingest/paper2md.py`) ran
`subprocess.run(cmd, capture_output=True, ..., timeout=1800)`. MinerU 2.x spawns a local
**uvicorn** worker (`http://127.0.0.1:9311`) and is extremely chatty — tqdm progress bars
(`Layout Predict`, `Predict 48/48`, `OCR-det`, `Processing pages`), access logs, model-load
lines. `capture_output=True` funnels all of it into fixed-size OS pipe buffers that
`subprocess.run` does **not** drain until the child exits. On a large PDF the ~64 KB pipe
fills, the child **blocks on write**, and the whole conversion deadlocks until the 1800s
timeout kills it. The convert worker then swallows the `TimeoutExpired`→`RuntimeError` as a
per-paper skip (counted as neither ingest nor error), so the batch finishes "clean" with
`ingested=0 errors=0`. Classic `subprocess` pipe-buffer deadlock; the swallow-as-skip turned
it into silent data loss.

Yesterday's `d8b830d9` "completion" was almost certainly the same illusion (never checked
its `ingested` count).

## Proof (empirical, decisive)
Same exe / PDF / GPU / command, only the output sink changed:
- **`capture_output=True`** (pipeline): hang 1800s → timeout → no `.md`, `ingested=0`.
- **redirect to a FILE** (`scratchpad/run_mineru.py`, `mineru -p 2606.32034.pdf -o … -m auto
  -d cuda`, `stdout=file, stderr=STDOUT`): **rc=0 in 331s (~5.5 min)**, produced a 0.142 MB
  `.md`, log shows full page progress. An unbounded sink never blocks.

## Fix
`paper2md.convert` — dropped `capture_output=True`; the child now writes to a
`tempfile.NamedTemporaryFile` (`stdout=logf, stderr=subprocess.STDOUT`). The file is closed
before read-back (Windows share safety), the text is still fed to `_log_mineru_streams` for
diagnostics, and the temp file is unlinked. Timeout / non-zero-exit / OSError branches
preserved. `import tempfile` added. AST + `py_compile` green.

## Design note — the `stdout=sys.stderr` alternative (user's proposal)
`subprocess.run(..., stdout=sys.stderr, stderr=subprocess.STDOUT)` also fixes the deadlock
(unbounded fd sink) and **is MCP-safe *only* because it targets `sys.stderr`**: this server
speaks MCP over **stdio**, where **`stdout` carries the JSON-RPC protocol** — redirecting the
child to `sys.stdout` would corrupt the wire. Chose the temp-file variant instead because
`stdout=sys.stderr` makes `proc.stdout`/`proc.stderr` `None`, forfeiting the captured text
that `_log_mineru_streams` and the "exit 0 but no .md" path rely on. Temp file = deadlock-free
**and** diagnostics retained. (Precondition either way: never `sys.stdout`.)

## Follow-ups (deferred, flagged)
- **Swallow-as-skip masks failure:** a per-PDF convert timeout/error should increment
  `errors`, not vanish into `ingested=0 errors=0`. A convert that yields 0 of N papers ought
  to fail (or at least surface) the task, not report clean success.
- **Requires MCP reconnect** to load the patched `paper2md.py` before the confirming re-run.
- Same liveness-gap caveat as prior incidents: don't `/mcp` reconnect mid-run.
