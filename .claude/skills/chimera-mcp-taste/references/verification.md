# Verification — how to PROVE each MCP-layer claim

MCP-layer bugs are invisible to code reading and to "it ran once." Each rule below has a
check that makes the difference **observable**. Do the check; don't argue from the source.
The anti-patterns at the end are symptom→fix (no code), for fast recognition.

## Why proof, not inference
Audit I-2 nearly shipped a wrong verdict ("CUDA wasted, CPU fallback") from three-way
reasoning off the code + an nvidia-smi *path* string. One live measurement flipped it:

| check | idle | during convert | verdict |
|---|---|---|---|
| `nvidia-smi` VRAM | 1746 MiB | **6965 MiB** (+5.2 GB) | GPU is real |
| power | 15 W | **74 W** | compute, not idle |
| util | 12% | peak **99%** | genuine load |

The compute-process path (`anaconda\python.exe`) was a benign artifact of a base-coupled
venv — a *different* real bug (venv_independence), not the one inferred. Measurement > inference.

## interpreter_resolution + venv_independence → nvidia-smi during a real convert
Run one convert and watch the GPU. A VRAM jump + a compute process named after the **venv**
interpreter proves both that the right torch ran and that the venv is independent. A flat
"it completed" proves neither.
```bash
# terminal A: drive one convert on the venv interpreter
.venv/Scripts/python.exe -c "from ports.ingest.paper2md import MineruClient; \
    MineruClient(output_root=OUT).convert(PDF)"
# terminal B: sample the GPU while it runs
nvidia-smi --query-gpu=memory.used,power.draw,utilization.gpu --format=csv -l 2
```
Also confirm the interpreter binary directly: `python -c "import torch, sys; \
print(sys.executable); print(torch.__version__, torch.cuda.is_available())"` — the venv
python must import cu128 torch; the base interpreter should NOT have torch at all.

## env_var_binding → construct a fresh config with a NON-DEFAULT value
Never test env binding with the value that equals the default — that hides the no-op. Set the
var to a path that could not be the default and assert the field moved there.
```python
import os
os.environ["CHIMERA_PAPERS_ROOT"] = r"D:\PROBE_FLAT\papers"      # deliberately non-default
cfg = load_config()                                              # fresh object
assert cfg.paper_miner.papers_root == Path(r"D:\PROBE_FLAT\papers"), cfg.paper_miner.papers_root
# The real probe (I-1): flat name → still the default (IGNORED); CHIMERA_PAPER_MINER__PAPERS_ROOT → moves.
```

## child_output_sink + headless_spawn_isolation → drive the REAL server headless
These reproduce only under a Claude-Code-launched (console-less, stdio) server. A shell run
will *not* reproduce the hang or the stdout corruption — so verify against the real thing:
launch `server.py` the way the host does and speak MCP to it.
```python
# minimal MCP stdio client: launch server headless, run the tool, poll
proc = subprocess.Popen([VENV_PY, SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=open("server_stderr.log", "w"), cwd=SERVER_DIR, env=env,
                        creationflags=0x08000000)     # CREATE_NO_WINDOW = truly headless
# send: initialize → notifications/initialized → tools/call daily_paper_pipeline → poll check_task_status
# PASS = progress climbs past the convert stage AND the completion reports ingested>0.
```
Signatures to watch for: a `mineru.exe` at **0 CPU / ~5 MB** (headless-spawn hang);
a 0-byte child log file while "converting" (output sink not reaching disk); JSON-RPC parse
errors on the client (a child wrote to `sys.stdout`).

## direct_before_transport → bisect the layer, then fix the seam
1. **Direct:** call the domain function in-process (`MineruClient(...).convert(pdf)`). Passes →
   the logic is sound; stop editing it.
2. **Transport:** drive the headless server (above). Fails only here → the bug is the MCP seam.
3. Fix the seam (interpreter / env / creationflags / stdin / output sink), re-run the headless
   check, confirm `ingested>0`. Then, if a live Claude Code session hosts the server, it must
   `/mcp` reconnect to load the patched module (do not reconnect mid-run — it orphans the task).

## thin_adapter + heavy_deps_lazy_optional → import and line-count checks
- **Server imports without the heavy stack:** in an env where torch/MinerU are absent,
  `python -c "import server"` must succeed; only calling the ML tool may fail (with the clear
  NotInstalled error). A failing import means a heavy dep leaked to module top.
- **Adapter stays thin:** `wc -l server.py` < 200, and a grep for orchestration keywords
  (fetch/convert/route loops) in `server.py` returns nothing but the concurrency guard.

---

## Anti-patterns (symptom → fix)

- **"Works in my shell, not as a tool."** → Don't touch the domain logic. Run direct-before-transport;
  the bug is the seam (PATH / console / stdio / env).
- **Tool hangs at ~0 CPU / tiny RSS, no output.** → Console-subsystem child from a headless server.
  Add `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP` + `stdin=DEVNULL`.
- **Long run, then `completed` with `ingested=0 errors=0`.** → Chatty child + `capture_output` deadlock,
  or swallow-as-skip. Move to a temp-file sink AND make a 0-of-N result raise, not "complete".
- **Client shows JSON-RPC parse errors during a tool call.** → A child wrote to `sys.stdout`. Redirect
  child output to a temp file or `sys.stderr`; stdout is the protocol wire.
- **"The env override works" (but only on this machine).** → Default == intended masking a dropped var.
  Re-test with a non-default value; check the nested name and `extra="ignore"`.
- **`import torch` at server module top; whole server won't load on a light host.** → Lazy-import inside
  the tool body; raise a clear NotInstalled error.
- **nvidia-smi shows a surprising python path.** → Don't conclude "wrong torch." Measure VRAM/power/util;
  the path may be a base-coupled-venv artifact (fix the venv, not the GPU flag).
- **Asset not found at runtime (prompt/template/config).** → Migrated code without its assets. Verify every
  referenced asset is present and path-resolved before smoke (see `2026-06-30-missing-prompts-tree.md`).
