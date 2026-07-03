# Incident — MinerU convert hangs ONLY when spawned by the headless MCP server

**Date:** 2026-07-02
**Surfaced by:** M.5 E2E smoke, Test 2 re-run, after the capture_output fix
(`2026-07-01-mineru-capture-deadlock.md`).
**Severity:** Critical (pipeline still ingests 0) / Fix difficulty: minor (spawn flags) —
but root-caused only after a long investigation.
**Status:** fixed and **VERIFIED** — see Verification below.

## Symptom
After the capture_output→temp-file fix, `daily_paper_pipeline` STILL hung: stuck at
progress 0.2 "Converting…" for ~30 min/PDF (3 PDFs → ~90 min), producing a hollow
`completed / ingested=0`. The patched temp-file path WAS running (three 0-byte
`*.mineru.log` temp files, ~30 min apart) — but MinerU wrote nothing. The live `mineru.exe`
sat at **5 MB RSS / 0 CPU**: frozen at interpreter startup, before any imports or output.

## Investigation — what it was NOT (all reproduced clean, standalone)
The capture_output theory was disproven (file sink still hung in-server). A confounded
"proof" earlier (file sink + console) had credited the wrong variable. Systematic isolation,
one variable at a time, in the scratchpad — **every** standalone launch converted a 48-page
PDF in ~40s and wrote a `.md`:

1. `capture_output=True` pipe-buffer deadlock — **not it** (file sink also hangs in-server).
2. stdin inheritance — **not it** (`stdin=PIPE` held-open AND `stdin=DEVNULL` both worked).
3. Missing console — **not it** (console-less `pythonw` launch worked).
4. Proxy / HuggingFace network — **not it** (proxy stripped ± `HF_HUB_OFFLINE` both worked).
5. Server environment — **not it** (read the live server's PEB env; proxy/USERPROFILE/TEMP/
   CUDA_PATH all match the working shell).
6. asyncio `to_thread` + Proactor loop spawn path — **not it** (exact replication worked).
7. Import side-effects (torch CUDA ctx, full `miner_tools`/mineru stack loaded) — **not it**.
8. "Two server processes" — **red herring**: the venv `python.exe` is a uv trampoline that
   re-execs the uv base CPython; one logical server.

## Root cause (leading, matches all evidence)
`mineru.exe` is a **console-subsystem** executable that internally spawns a uvicorn worker.
The chimera-papers MCP server is launched by Claude Code as a **headless** child (no
inheritable console). A console app spawned from a console-less process triggers Windows
console auto-allocation for the child; in this detached context that startup blocks — hence
5 MB / 0 CPU / zero output, frozen before user code. Every standalone launch had a console
(shell) or a clean GUI-subsystem parent, so none reproduced it. This is the classic
"runs from a shell, hangs when spawned by a service/server" Windows pattern.

## Fix (applied, `ports/ingest/paper2md.py`)
Spawn MinerU isolated from the headless parent's process context:
- `creationflags = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP` — its own clean console +
  process group (no inherited console state / Ctrl-event group).
- `stdin = subprocess.DEVNULL` — never inherit the MCP JSON-RPC stdin pipe.
- Output still to a temp file (retains the prior deadlock fix).
- `timeout` 1800 → **600s** — real converts run ~5 min; tighter ceiling fails a genuine hang
  in 10 min instead of 30 during iteration. Revisit if very large PDFs legitimately exceed it.

Regression-checked standalone: with all three changes MinerU still converts (rc=0, 32s,
`.md` produced, flags `0x8000200`). `py_compile` green.

## Verification (DONE)
The bug only manifests under a Claude-Code-launched (headless) server, so verification drove
the **real** `server.py` the same way: a scratch MCP stdio client launched it with
`CREATE_NO_WINDOW` + bound stdin/stdout pipes + real env, spoke MCP, ran
`daily_paper_pipeline`, and polled. Result:

```
0% Fetching -> 20% Converting -> completed  (~3 min total)
new_pdfs=3 ingested=3 convert_failed=0 batch_total=3 must_read=0 skim=1 reject=2 errors=0
```

Progress climbed past 0.2 (the old wall), all 3 PDFs converted (`convert_failed=0`), and
`ingested=3`. Non-confounded: identical headless launch context that previously produced the
0-byte temp files; only `paper2md.py` changed. **Fix confirmed.**

Note: a *live* Claude Code session whose chimera-papers server started before this patch must
`/mcp` reconnect to load it. Do NOT `/mcp` reconnect mid-run (orphans the task — separate
liveness gap).

## Follow-ups (deferred)
- **Swallow-as-skip still masks failure** (from the prior incident): a convert timeout/error
  should increment `errors`, not vanish into `ingested=0 errors=0 completed`. Highest-value
  remaining fix — it's what turned every hang into a silent "success".
- If the console-allocation theory is ever disproven by a future hang, the next suspect is
  handle inheritance from the FastMCP stdio transport (bInheritHandles=TRUE passing the
  server's inheritable pipe handles to the child).
