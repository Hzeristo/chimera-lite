# MCP Rules

The enforceable rules behind `core_principles` (SKILL.md). Each rule is a bare **Statement**
followed by a Bad/Good pair. Every example is a **real** Phase M / M.5 incident (see
`docs/audits/post-migration-pipeline-incidents.md` and `docs/incidents/`), not invented.
Proof procedures and symptom→fix anti-patterns live in `verification.md`.

## interpreter_resolution
**Statement:** A subprocess that must run in the project's venv resolves its executable from `sys.executable`'s directory, never a bare PATH lookup. An MCP server inherits the *launcher's* PATH (Claude Code / anaconda / system), not your activated-venv PATH — so `which` finds the wrong python (wrong torch) or nothing.

*(Incident: `2026-06-30-mineru-not-on-path.md`. The pipeline crashed `MinerU is not installed or not in PATH` — mineru.exe sits in `.venv\Scripts` right next to the interpreter running the server, but that dir is only on PATH under shell activation.)*

**Bad:**
```python
def _detect_command(self) -> str:
    if shutil.which("mineru"):          # server PATH ≠ venv PATH → miss, or a stray system exe
        return "mineru"
    raise MineruNotInstalledError("MinerU is not installed or not in PATH.")
```

**Good:**
```python
def _detect_command(self) -> str:
    found = shutil.which("mineru")
    if found:
        return found
    # the server always runs on the venv interpreter; mineru.exe ships beside it
    sibling = shutil.which("mineru", path=str(Path(sys.executable).parent))
    if sibling:
        return sibling
    raise MineruNotInstalledError("MinerU is not installed or not in PATH.")
```

## env_var_binding
**Statement:** An env var set in `.mcp.json` binds to a config field only if its name matches the settings model's nesting. With pydantic `env_nested_delimiter="__"` + `extra="ignore"`, a flat `CHIMERA_PAPERS_ROOT` resolves to a top-level key that is **not a field** → silently dropped. It "works" only because default == intended — a landmine for any host where they differ. Prove the binding with a NON-DEFAULT value (see `verification.md`).

*(Incident I-1, `post-migration-pipeline-incidents.md`. User flagged FATAL; audit confirmed the silent no-op.)*

**Bad:**
```jsonc
// .mcp.json — flat name, silently ignored by extra="ignore"
"env": { "CHIMERA_PAPERS_ROOT": "D:\\data\\papers" }
// → maps to top-level `papers_root`, not a field; real field is paper_miner.papers_root
```

**Good:**
```jsonc
// nested name matches env_nested_delimiter="__"
"env": { "CHIMERA_PAPER_MINER__PAPERS_ROOT": "D:\\data\\papers" }
```
```python
# OR fold every flat CHIMERA_<KEY> into paper_miner in config (the robust fix, commit 79bfc07)
def _read_paper_miner_env_overrides() -> dict:
    return {k: os.environ[f"CHIMERA_{k.upper()}"] for k in _PAPER_MINER_KEYS
            if f"CHIMERA_{k.upper()}" in os.environ}
```

## progress_observability
**Statement:** A long child's per-page progress (a tqdm bar) is invisible through the server: a non-TTY pipe doesn't render tqdm, and `capture_output` discards the stream on clean success anyway. Don't fight the pipe for per-page granularity — have the *parent* emit periodic **stage-level** log lines to stderr, and accept the loss of per-page detail.

*(Incident I-3, `post-migration-pipeline-incidents.md` + `2026-06-30-pipeline-observability.md`. Stage-level timeline is adequate; per-page tqdm was deferred, not chased.)*

**Bad:**
```python
# rely on MinerU's tqdm bar for progress; capture_output discards it on success → zero signal
subprocess.run(cmd, capture_output=True)   # user sees nothing until (or unless) it fails
```

**Good:**
```python
# parent emits a coarse, always-visible stage line to stderr around each unit of work
logger.info("[ingest] converting %s (%d/%d)", pdf.name, i, n)   # goes to stderr, not the JSON-RPC wire
clean_md = client.convert(pdf)
logger.info("[ingest] done %s -> %s", pdf.name, clean_md.name)
```

## child_output_sink
**Statement:** A subprocess whose child is chatty must not use `capture_output=True`: it funnels stdout/stderr into fixed ~64 KB OS pipes that `subprocess.run` does not drain until the child exits → the child blocks on a full pipe → deadlock. Redirect to a temp file (unbounded, and readable back for diagnostics) or `sys.stderr`. In an **stdio-transport** MCP server, **never** redirect a child to `sys.stdout` — stdout carries JSON-RPC; child bytes corrupt the wire.

*(Incident I-4, `2026-07-01-mineru-capture-deadlock.md`. MinerU spawns a chatty uvicorn worker; `capture_output` deadlocked it for the full 1800s timeout → 90-min "hollow success" `ingested=0 errors=0`. Same-exe/PDF/GPU: capture_output → hang; temp-file sink → rc=0 in 331s.)*

**Bad:**
```python
proc = subprocess.run(cmd, check=True, capture_output=True, timeout=1800)  # pipe fills → deadlock
```

**Good:**
```python
with tempfile.NamedTemporaryFile(suffix=".mineru.log", delete=False) as tmp:
    log_path = Path(tmp.name)
with log_path.open("w", encoding="utf-8", errors="replace") as logf:
    subprocess.run(cmd, check=True, stdout=logf, stderr=subprocess.STDOUT, timeout=600)
mineru_output = log_path.read_text(encoding="utf-8", errors="replace")  # diagnostics retained
log_path.unlink(missing_ok=True)
# NEVER stdout=sys.stdout here — this server speaks JSON-RPC on stdout.
```

## headless_spawn_isolation
**Statement:** A console-subsystem child (e.g. `mineru.exe`) spawned by a **headless** MCP server (launched by Claude Code with no inheritable console) hangs at interpreter startup on Windows — 5 MB RSS, 0 CPU, zero output — until timeout. Isolate it from the parent's process context: `creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP` and `stdin=subprocess.DEVNULL`. This never reproduces from a shell (the shell has a console), so it must be verified against the real server (see `verification.md`).

*(Incident: `2026-07-02-mineru-hang-in-mcp-server.md`. Nine standalone reproductions all converted cleanly; only the Claude-Code-launched server hung. Fix verified by driving the real headless server → `ingested=3`.)*

**Bad:**
```python
# fine from any shell; hangs at startup when the parent is a console-less MCP server
subprocess.run(cmd, check=True, stdout=logf, stderr=subprocess.STDOUT, timeout=600)
```

**Good:**
```python
_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
subprocess.run(
    cmd, check=True,
    stdin=subprocess.DEVNULL,        # never inherit the MCP JSON-RPC stdin pipe
    stdout=logf, stderr=subprocess.STDOUT,
    timeout=600, creationflags=_flags,  # own clean console + process group
)
```

## asset_migration
**Statement:** Domain code carries its *logic* across a migration; it does **not** carry its *assets* — prompt files, Jinja templates, config files. Every import can succeed while a filesystem asset the code resolves at runtime is missing. Verify each referenced asset is present and path-resolved before smoke, not at the first tool call.

*(Incident: `2026-06-30-missing-prompts-tree.md`. Ported code + modules but not the `prompts/` tree; `PromptManager` resolved `<repo-root>/prompts/` → `FileNotFoundError` at runtime, invisible to the import-surface audit.)*

**Bad:**
```text
Migrate paper2md + services + config; run smoke. First daily_paper_pipeline call dies at
PromptManager.__init__ → "Template directory not found: <repo>/prompts". The tree was never copied.
```

**Good:**
```python
# pre-smoke asset check — prove every referenced asset resolves from the new repo root
assert (REPO_ROOT / "prompts").is_dir()
for tpl in ("tasks/filter_task.j2", "chimera_sys/reviewer_zero.j2"):
    assert (REPO_ROOT / "prompts" / tpl).exists(), tpl
```

## venv_independence
**Statement:** The project venv is built on a standalone (uv-managed) interpreter, never the base anaconda/system python. A venv whose `pyvenv.cfg` `home` points at anaconda is hostage to it — move/upgrade/remove anaconda and the whole toolchain breaks; nvidia-smi even misreports the base-image path as the compute process.

*(Incident I-2 reclassified + DEBT-010, `post-migration-pipeline-incidents.md`. Rebuilt on uv CPython 3.13; `uv sync` re-pulled `torch 2.11.0+cu128`.)*

**Bad:**
```ini
# .venv/pyvenv.cfg — the interpreter binary belongs to anaconda
home = D:\anaconda3
include-system-site-packages = false
```

**Good:**
```ini
# .venv/pyvenv.cfg — standalone uv-managed interpreter, project owns its toolchain
home = C:\Users\<you>\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none
```

## direct_before_transport
**Statement:** Verify a tool's domain function by a **direct python call** before testing it through the MCP transport. If the direct call passes and only the transport fails, the bug is in the seam (interpreter / env / console / stdio / handles), not your logic. Bisect the layer; do not rewrite correct code.

*(The M.5 debugging arc: MinerU convert worked from every shell and every direct call; the hang lived only in the transport-hosted server. Rewriting `convert` would have been wasted — the fix was three spawn flags.)*

**Bad:**
```text
"daily_paper_pipeline hangs" → start editing convert()'s parsing / retry / GPU logic.
(The logic was never the problem; the same code runs fine directly.)
```

**Good:**
```bash
# 1) direct — is the domain logic sound?
.venv/Scripts/python.exe -c "from ports.ingest.paper2md import MineruClient; \
    MineruClient(output_root=OUT).convert(PDF)"        # passes → logic is fine
# 2) transport — drive the real server headless (see verification.md). Fails here only
#    ⇒ the bug is the MCP seam. Fix the spawn/env/interpreter, not convert().
```

## thin_adapter
**Statement:** The MCP server module is a thin adapter (<200 lines): it declares tool contracts (names, args, docstrings) and delegates to the service/port layer. Business logic never lives in `server.py`. The single sanctioned exception is the concurrency guard — the check-and-start lock that rejects a second long task (Phase M red line).

*(chimera-papers `server.py` is 94 lines: three `@mcp.tool`s that delegate to `miner_tools`, plus `_start_lock` + `has_active_long_task`.)*

**Bad:**
```python
@mcp.tool()
async def daily_paper_pipeline(...) -> str:
    records = await fetch_arxiv(...)          # orchestration inlined in the adapter
    for pdf in await download(records): ...
    md = convert(pdf); route(filter(md)); ...
```

**Good:**
```python
@mcp.tool()
async def daily_paper_pipeline(...) -> str:
    async with _start_lock:                    # the ONE allowed bit of server logic
        if get_task_service().has_active_long_task():
            return _busy_message()
        return await miner_tools.daily_paper_pipeline(...)   # delegate; logic lives in the service
```

## heavy_deps_lazy_optional
**Statement:** Heavy or optional dependencies (torch, MinerU) import **inside** the function that needs them and raise a clear NotInstalled error — so the server module imports and its lighter tools work without the multi-GB stack present. A top-level `import torch` makes the whole server fail to load when the stack is absent, taking every unrelated tool down with it.

*(chimera-papers tool bodies lazy-import their domain stack; `MineruNotInstalledError` is the clear signal. Smoke passes on lighter stages without forcing the ML install.)*

**Bad:**
```python
# server.py / tool module top level
import torch
import mineru                      # absent stack ⇒ the entire MCP server fails to import
```

**Good:**
```python
def convert(self, pdf_path: Path) -> Path:
    # heavy stack touched only on the path that needs it
    self.cmd = self._detect_command()   # raises MineruNotInstalledError with a clear message
    ...
```
