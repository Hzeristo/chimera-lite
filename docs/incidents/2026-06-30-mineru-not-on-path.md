# Incident — daily_paper_pipeline crash: MinerU not on PATH

**Date:** 2026-06-30
**Surfaced by:** M.5 E2E smoke, Test 2 (`docs/audits/M.5-e2e-smoke.md`) — re-run after the
`prompts/` tree port (incident `2026-06-30-missing-prompts-tree.md`).
**Severity:** Critical (pipeline unrunnable) / Fix difficulty: minor (one-line adapter fallback).

## Symptom
`daily_paper_pipeline` (task `d0238ffa`) started, cleared arXiv fetch, prompt loading, and
the LLM filter, then the background task died at the PDF→Markdown convert stage with
`MinerU is not installed or not in PATH.`

## Root cause
`mineru.exe` **is** installed — it lives in `.venv\Scripts\` (package `mineru`, importable).
The fault is PATH resolution: `.mcp.json` launches the papers server by invoking
`.venv\Scripts\python.exe` **directly**, not through venv *activation*. Running the
interpreter directly does not put `.venv\Scripts\` on the process PATH, so
`MineruClient._detect_command` (`ports/ingest/paper2md.py`) — which relied solely on
`shutil.which("mineru")` — found nothing, even though the exe sits beside the very
interpreter running the server. The earlier "ran end-to-end" note was from an
activated-venv shell; a plain `/mcp` reconnect loses that PATH.

This is the failure the prompts-tree incident predicted as "genuine runtime," but it is
actually a **construction/discovery gap**, not a model-load or live-call failure.

## Fix
`paper2md.py` — `_detect_command` now falls back to the interpreter's sibling dir before
raising:
```python
found = shutil.which("mineru")
if found:
    return found
sibling = shutil.which("mineru", path=str(Path(sys.executable).parent))
if sibling:
    return sibling
raise MineruNotInstalledError(...)
```
Encodes the real invariant — the server always runs on the venv interpreter, and `mineru`
ships beside it — so discovery survives any launch context (direct exec, activation, shell).
`import sys` added. `shutil.which(..., path=...)` handles the Windows `.exe`/PATHEXT
resolution, so no manual extension handling. No `.mcp.json` change needed.

## Verification
- Under the venv interpreter:
  `shutil.which('mineru') or shutil.which('mineru', path=str(Path(sys.executable).parent))`
  → `D:\MAS\chimera-lite\.venv\Scripts\mineru.EXE`.
- **Requires an MCP reconnect** to take effect: the running server's PATH/import state is
  frozen at launch, so the live pipeline re-run must follow a `/mcp` reconnect.

## Notes / non-issues
- Chosen over the `.mcp.json` PATH-injection alternative (fragile: must hardcode/compose
  PATH, fixes only one launch path). Code fallback is launch-context-agnostic.

## Open follow-up (deferred)
The same direct-interpreter launch means **any** other console-script entry point the
pipeline shells out to would hit this. `mineru` was the only one; if more appear, prefer a
shared helper that resolves console scripts against `sys.executable`'s dir rather than
patching each call site.
