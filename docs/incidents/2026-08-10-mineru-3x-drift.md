# Incident — MinerU 3.x drift: an inert device flag, a dead output path, a rude timeout

**Date:** 2026-08-10
**Surfaced by:** `scripts/debug_mineru.py`, a white-box harness built to instrument the
ingest leg (device, params, artifact layout) that production only ever sees as a black box.
**Severity:** Medium — ingest was *working*, but for none of the reasons the code claimed.
Fix difficulty: minor. **Status:** all three fixed and verified (see Verification).

## Context

MinerU is pinned in `pyproject.toml` as `mineru[core]>=1.4`; the installed version is
**3.4.0**. `ports/ingest/paper2md.py` was written against the 1.x/2.x CLI and never
revisited. Three assumptions in it silently stopped being true. None produced an error —
which is why they survived. Every one of them is the same defect class: **the code
performing a decision it was no longer making**.

## Defect 1 — `-d cuda` was inert

`convert()` passed `-d cuda`, reading as a device pin. MinerU 3.x has **no `-d/--device`
flag**. Worse than being rejected, it was *accepted*: `mineru`'s click command is declared
`context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)`
(`mineru/cli/client.py:1037`), so unknown args are collected into `ctx.args` and forwarded
verbatim to the `mineru-api` worker it spawns — which is declared ignore-unknown too
(`mineru/cli/fast_api.py:1395`). The flag travelled the whole way and did nothing.

Device actually resolves in `mineru/utils/config_reader.py:105` — `MINERU_DEVICE_MODE` if
set, else torch autodetect. We were getting CUDA by autodetect luck, and a driver or torch
regression would have silently dropped ingest to CPU with no signal.

Related: the run also inherited MinerU 3.x's **default backend**, `hybrid-engine` at
`medium` effort. Not chosen — inherited.

## Defect 2 — the primary output path never matched

MinerU >= 3 nests a per-backend parse dir one level under the stem
(`mineru/cli/output_paths.py:9`):

```
<out>/<stem>/<method>/<stem>.md          backend=pipeline    (auto | txt | ocr)
<out>/<stem>/vlm/<stem>.md               backend=vlm-*
<out>/<stem>/hybrid_<method>/<stem>.md   backend=hybrid-*
```

`convert()` probed the 2.x flat path `<out>/<stem>/<stem>.md`, which **never exists on
3.x**. Two consequences:

- Every successful convert limped through the `rglob("*.md")` fallback. Ingest worked, but
  the insurance path had quietly become the only path.
- The same flat probe was the exists-check at the top of `convert()`. Since it never hit,
  **conversion was never idempotent** — a re-run reconverted the PDF from scratch, minutes
  of GPU time, every time. Nobody noticed because `PaperLoader.extract_and_clean` has its
  own skip on the *clean* file downstream.

## Defect 3 — the 600s timeout could not clean up after itself

`subprocess.run(timeout=600)` had two problems. The budget was set in
`2026-07-02-mineru-hang-in-mcp-server.md` on the observation that "real converts run ~5
min" — measured against MinerU 2.x. Measured now: hybrid/medium is ~37s for a short paper,
but hybrid/high is **246s** for the same one, and effort scales with page count, so 600s
was one long paper away from killing healthy work.

The mechanism was worse than the number. `mineru` spawns a `mineru-api` uvicorn worker as
a **grandchild**. `run()`'s timeout calls `Popen.kill()` — TerminateProcess on the direct
child only. The worker survives, holding ~4 GB of VRAM (measured), and the next convert
contends with a ghost.

## Fixes (all in `ports/ingest/paper2md.py`)

1. **Device.** Dropped `-d cuda`. `MINERU_DEVICE_MODE` is set in the child's environment
   from `MINERU_DEVICE` (default `"cuda"`, override via `CHIMERA_MINERU_DEVICE`), using
   `setdefault` so an operator-set value wins. The pin is now load-bearing.
2. **Output path.** New `_resolve_output_markdown(target_dir, stem)` probes the nested
   parse dir first, then the 2.x flat path, then a recursive scan as a true last resort.
   Used for BOTH the post-convert lookup and the exists-check, which restores idempotence.
3. **Timeout.** The deadline moved into the child, where cleanup lives:
   `MINERU_TASK_RESULT_TIMEOUT_SECONDS=1200` and
   `MINERU_LOCAL_API_STARTUP_TIMEOUT_SECONDS=300` are passed via env, so MinerU aborts
   through its own `finally` — stopping its API worker and removing its temp dir — and
   exits non-zero. Our `wait()` is now only a **backstop** at budget + 120s, and on expiry
   `_stop_child_gracefully()` escalates: Ctrl-Break to the process group (we already own
   one via `CREATE_NEW_PROCESS_GROUP`), 30s grace, then `taskkill /F /T` for the tree. No
   new dependency.

Two adjacent changes, called out so they are easy to reverse:

- **Backend pinned** to `-b hybrid-engine`. Functionally a no-op today — it *is* the 3.x
  default — but it makes a future MinerU release unable to change our parse backend
  without a diff. This is the whole lesson of Defect 1.
- **CUDA-OOM hint tightened.** The L.B.6 F4 hint fired on `"cuda" in log`, which with the
  device now named in the env would have labelled nearly every failure a CUDA OOM. It now
  requires an actual OOM signature, with a separate hint for a self-aborted deadline. A
  diagnostic that mislabels is the advisory-rigor failure in miniature.

**`--effort high` was deliberately NOT adopted.** See Follow-ups.

## Error-path audit (same sitting)

Asked whether failures actually reach the operator, the chain was traced end to end:
`convert()` -> `mineru_pipeline` -> `single_paper_ingest` / `miner_tools` -> `@mcp.tool`.
Messages DO propagate — `miner_tools.ingest_paper:128` and `convert_pdf_to_md:235` return
`f"[Convert Error] {exc}"`, so the OOM and self-abort hints above reach the tool output
rather than dying in a log. Two defects found and fixed, one gap left open:

- **Fixed — "no output" was reported as "PDF not found".** `convert()` raised a bare
  `FileNotFoundError` when MinerU exited 0 having written nothing; `miner_tools.py:233`
  catches `FileNotFoundError` and renders it as `[Convert Error] PDF not found`. The
  operator was told their input was missing when the input was fine and the CONVERTER
  produced nothing — a diagnosis pointing at the wrong half of the system. Now
  `MineruOutputMissingError(RuntimeError)`, which falls through to the generic branch and
  reports the real message.
- **Fixed — a regression introduced by this very patch.** `subprocess.run()` kills the
  child when any exception escapes; `Popen` does not. The Popen refactor silently dropped
  that guarantee, so a KeyboardInterrupt or a cancelled caller would have orphaned MinerU
  and its GPU-holding worker — the exact leak fix 3 exists to prevent. Restored with an
  `except BaseException: _stop_child_gracefully(...); raise`.
- **Open — `run_pdf_ingestion` (`mineru_pipeline.py:162`) still swallows-as-skip.** It
  catches every per-PDF `Exception`, logs, continues, and returns only `success_count` —
  the exact I-5 pattern that `2026-07-01-convert-swallow-as-skip.md` fixed in
  `convert_queue_worker`. It is **dead code**: exported from `ports/ingest/__init__.py`
  and called by nothing. Left untouched deliberately — the right move is deletion, not
  repair, and that is the operator's call. Until then it is a loaded gun for whoever
  reaches for the obvious-looking batch entry point.

## Verification

- `py_compile` green; `test_convert_worker.py`, `test_fetch_convert_primitives.py`,
  `test_single_paper_ingest.py` — 15 passed. (No test asserted the argv; they monkeypatch
  `convert` wholesale, which is exactly why the drift was invisible for so long.)
- Real convert through the patched seam, driving `MineruClient` directly: returns
  `<stem>/hybrid_auto/<stem>.md` from the nested probe, and an immediate second
  `convert()` on the same PDF returns the same path in under a second — the skip-cache
  works for the first time.

## Follow-ups (deferred, deliberate)

- **`--effort high` stays off until a thin wrapper exists.** Measured cost is 6.7x
  (246.3s vs 37.0s, peak GPU 100% vs 46%) and what it buys is chart transcription: three
  `<details><summary>line|bar</summary>` blocks holding markdown tables of values a VLM
  read off figure *pixels* ("~55", "~70"). Those numbers appear nowhere in the paper's
  text, sit unmarked beside verbatim prose, and would be indistinguishable from
  paper-stated figures to anything downstream that reads the markdown for numbers (W1
  verbatim verification, W2's headline number). That is unsourced quantity entering the
  corpus wearing the costume of evidence — the exact laundering the north star forbids.
  A wrapper that strips or explicitly marks those blocks as machine-read is the
  precondition, not an optimization. `high` also *regressed* text on the sample paper
  (venue boilerplate spliced into the abstract; "original" -> "origina").
- `pyproject.toml` still declares `mineru[core]>=1.4` against an installed 3.4.0. The
  floor should move to `>=3.4,<4` so the CLI contract this module now targets is the one
  the manifest promises.
- No test covers the argv or the output-path resolution. `_resolve_output_markdown` is
  pure and trivially testable against a fake tree — worth a test so the next MinerU major
  fails loudly instead of drifting.
