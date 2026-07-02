# Audit — Post-migration MCP pipeline incidents (I-1, I-2, I-3)

**Date:** 2026-06-30
**Mode:** read-only + live profiling. **No fixes applied** — this is the evidence base; the
fix sprint follows.
**Scope:** the three incidents in the user's `2026-06-29` prototype. Led with I-2 (CUDA).

---

## I-2 (was HIGH — feared CPU fallback) → **VERDICT: GPU is real, cu128 is used. NOT wasted.**
### Headline
MinerU **is** GPU-accelerated on the venv's CUDA torch. The alarming nvidia-smi signal
(`D:\anaconda3\python.exe` as the compute process) is a **benign reporting artifact**, not a
CPU/wrong-torch fallback. Reclassify: the CUDA hypothesis is **refuted**; a separate
**venv-fragility (MEDIUM)** is the real finding.

### Evidence
**Q1 — invocation** (`ports/ingest/paper2md.py:33-92`): subprocess, console-script exe, GPU flag:
```
cmd = [self.cmd, "-p", <pdf>, "-o", <out>, "-m", "auto", "-d", "cuda"]
subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=1800)
```
`self.cmd = _detect_command()` → `shutil.which("mineru")` else `shutil.which("mineru",
path=str(Path(sys.executable).parent))`. It resolves a **console-script .exe**, not a python.

**Q2 — the M.5 fix** (commit `5f11b33`): changed *only how `mineru.exe` is discovered* (PATH,
then venv-sibling). It did **not** change which python runs MinerU — it never invoked python
directly; it invokes `mineru.exe`.

**Q3 — which interpreter / torch:**
- No competing `mineru` on PATH; resolved exe = `D:\MAS\chimera-lite\.venv\Scripts\mineru.EXE`.
- `.venv/pyvenv.cfg`: `home = D:\anaconda3`, `include-system-site-packages = false`. The venv
  is **built on anaconda's interpreter binary** → on Windows nvidia-smi reports the base image
  path `D:\anaconda3\python.exe`.
- **anaconda base python: `import torch` → ModuleNotFoundError** (no torch at all).
- venv python: `torch 2.11.0+cu128`, `D:\MAS\chimera-lite\.venv\Lib\site-packages\torch`.
- ∴ the torch that ran the convert can only be the venv's cu128 (anaconda has none).

**Q4 — live GPU profile** (single convert, `mineru.exe -d cuda`, 105 s, exit 0):
| metric | value |
|---|---|
| GPU util | peak **99%**, sustained 30-40% |
| VRAM | idle 1746 MiB → **6965 MiB** during convert (~+5.2 GB compute) |
| Power | 15 W idle → **74 W** peak |
| compute proc | `D:\anaconda3\python.exe` (= venv base image; see Q3) |

GPU is unambiguously used. The **30-40% sustained** util (not pinned) indicates MinerU is
partly CPU-bound (layout/preprocess stages) + per-invocation model cold-load — that is
MinerU's nature, not a misconfiguration.

### Real finding (reclassified) — MEDIUM: the venv is anaconda-based
`pyvenv.cfg home = D:\anaconda3`. The venv interpreter binary belongs to anaconda. CUDA works
today, but the toolchain is **coupled to an anaconda install** the project doesn't own — move/
remove/upgrade anaconda and the venv breaks. The nvidia-smi confusion is a symptom of this.

### Recommended (NOT applied)
- **Rebuild the venv on a standalone Python** (`uv python install` + recreate `.venv`) so it's
  independent of anaconda; this also makes nvidia-smi report the venv python (no more false alarm).
- **No fix needed for GPU correctness** — `-d cuda` + venv cu128 torch already work.
- **Perf lever (separate, deferred):** MinerU is a fresh subprocess per PDF → model cold-load
  each time (dominant cost in the 68-105 s/PDF). MinerU ships a **persistent service**
  (`mineru-api.exe` / `mineru-vllm-server.exe` were in `.venv\Scripts`; the convert stderr even
  logged `Start MinerU FastAPI Service`). A warm worker would cut per-PDF latency. Big change →
  future sprint.

---

## I-1 (user: FATAL) → **VERDICT: CONFIRMED. Silent env-override failure.**
### Finding
`.mcp.json` sets `CHIMERA_PAPERS_ROOT`; the config field is **nested** (`paper_miner.papers_root`).
With `SettingsConfigDict(env_prefix="CHIMERA_", env_nested_delimiter="__", extra="ignore")`,
`CHIMERA_PAPERS_ROOT` → top-level key `papers_root`, which is **not a field** → dropped by
`extra="ignore"`. The override silently no-ops.

### Empirical proof (fresh config objects)
| env var set | resulting `papers_root` |
|---|---|
| `CHIMERA_PAPERS_ROOT=D:\PROBE_FLAT\papers` | `D:\MAS\chimera-lite\papers` (**ignored** → default) |
| `CHIMERA_PAPER_MINER__PAPERS_ROOT=D:\PROBE_NESTED\papers` | `D:\PROBE_NESTED\papers` (**works**) |
| (none) | `D:\MAS\chimera-lite\papers` (project_root/papers default) |

Works today **only** because default == intended. Any host where default ≠ intended → papers
land at the wrong path, silently. The user's "NOT harmless, FATAL" is correct.

### Recommended (NOT applied) — pick one
- **A (minimal):** `.mcp.json` → `CHIMERA_PAPER_MINER__PAPERS_ROOT` (the correct nested name).
- **B (robust):** make the flat name a first-class alias — add a top-level `papers_root` field
  with `validation_alias`, or extend `_merge_paper_miner_flat_keys` to also read it from env so
  `CHIMERA_PAPERS_ROOT` maps. (B is friendlier; A is one line.)

Config refs: `core/config.py` `SettingsConfigDict` (env_prefix/nested_delimiter/extra=ignore);
field `paper_miner: PaperMinerSettings | None`; `PaperMinerSettings.papers_root: Path | None`.

---

## I-3 (LOW) → **VERDICT: CONFIRMED. Structural, not just non-TTY.**
### Finding
`paper2md.py:84-93` uses `subprocess.run(..., capture_output=True)`. MinerU's stdout/stderr
(including the per-page tqdm bar) is **fully buffered until exit**, and on clean success
(`line 93`) the captured streams are **discarded** — `_log_mineru_streams` runs only on
failure paths (timeout / non-zero exit / exit-0-but-no-md). So per-page progress is invisible
regardless of TTY. **Stage-level** timeline IS visible (the observability fix,
`2026-06-30-pipeline-observability.md`).

### Recommended (NOT applied)
- **Accept stage-level, defer per-page** (lowest cost) — current behavior is adequate.
- If wanted later: switch convert to `Popen` + line-stream stderr → `logger.info` (tqdm to a
  non-TTY pipe emits newline-terminated lines, which log as periodic progress). Costs the
  buffered error-capture ergonomics; only worth it if per-page granularity is needed.

---

## I-4 (HIGH / Critical — silent data loss) → **MinerU `capture_output` pipe deadlock**
Found in the M.5 Test-2 re-run (after I-2), by a chimera-lite session. Detailed record:
`docs/incidents/2026-07-01-mineru-capture-deadlock.md`.

### Symptom
`daily_paper_pipeline` ran **90 min** (= 3 × 1800s), reported `completed / progress=1.0`,
`new_pdfs=3 ingested=0 errors=0` — a **hollow success**: three PDFs downloaded, zero markdown,
zero ingested, **no error signal**. Live `mineru.exe` sat at 0 CPU / 5 MB — blocked, not computing.

### Root cause
`MineruClient.convert` used `subprocess.run(cmd, capture_output=True, timeout=1800)`. MinerU 2.x
spawns a chatty **uvicorn** worker (tqdm bars, access logs, model-load lines). `capture_output`
funnels it into fixed-size (~64 KB) OS pipes that `subprocess.run` does **not** drain until the
child exits → pipe fills → child **blocks on write** → deadlock until the 1800s timeout. The
convert worker then swallows the `TimeoutExpired` as a per-PDF *skip* (neither ingest nor error)
→ silent data loss disguised as clean completion.

### Fix (applied)
Drop `capture_output`; redirect the child to a `tempfile.NamedTemporaryFile`
(`stdout=logf, stderr=subprocess.STDOUT`) — an **unbounded sink**, so no deadlock — then read
the file back for diagnostics (`_log_mineru_streams`, "exit 0 but no .md" path) and unlink it.
Windows-safe (file closed before read-back). Timeout / non-zero-exit / OSError branches preserved.

### MCP-critical rule (carry forward)
In an **stdio-transport** MCP server, **never** redirect a child subprocess to `sys.stdout` —
stdout carries the JSON-RPC protocol; child chatter would corrupt the wire. Only `sys.stderr`
(safe) or a **temp file** (safe + retains capturable diagnostics) are acceptable. The temp file
was chosen over `stdout=sys.stderr` because the latter makes `proc.stdout` `None`, forfeiting the
diagnostics the failure paths need.

### Proof (from the incident)
Same exe / PDF / GPU, only the sink changed: `capture_output` → 1800s hang, `ingested=0`;
file-redirect → **rc=0 in 331s**, produced a 0.142 MB `.md`.

### Follow-up — swallow-as-skip → **fixed as I-5 below.**

## I-5 (HIGH — silent data loss) → **convert failures swallowed-as-skip → hollow success**
The I-4 follow-up, fixed. Detailed record: `docs/incidents/2026-07-01-convert-swallow-as-skip.md`.

### Symptom
A run converting **0 of N** PDFs reports `completed / ingested=0 errors=0` — indistinguishable
from a no-op run, no error signal. This is what hid I-4's deadlock as "success" for 90 min.

### Root cause (two layers)
1. `convert_queue_worker` (`mineru_pipeline.py:275`) caught every per-PDF convert exception,
   logged, and continued — tracked only `success_count`, so **failures were counted nowhere**.
2. `_run_pipelined_async` returned a normal summary at `ingested_count == 0`; the summary's
   `errors` field is **filter**-only (`stats.errors`) — convert failures never entered it →
   `emit_completed`.

### Fix (applied)
- `convert_queue_worker` returns `(success_count, failure_count)` (per-PDF exceptions increment
  the failure count).
- `_run_pipelined_async`: **anti-hollow-success guard** — `if new_pdfs > 0 and ingested == 0:
  raise` → task marked **FAILED**; partial failures surfaced via a new `convert_failed=<n>`
  field in the completion summary. Propagation is clean (a raise → `run_task` `emit_failed`).

### Verification
`tests/test_convert_worker.py` (2 PDFs, convert mocked to raise → worker returns `(0, 2)`,
only the sentinel queued). ruff 0, pytest 19 passed / 1 skipped. Guard exercised live at M.5 Test-2.

## Profiling appendix (reference)
- Idle GPU baseline: 12% util / 1746 MiB / 15 W (desktop graphics contexts).
- Single MinerU convert (cold): 105 s, peak 99% util, +5.2 GB VRAM, 74 W.
- 2-paper pipeline run (`2026-06-30`, PDFs cached): 218 s total; convert ~68-94 s/PDF, LLM
  filter ~52-57 s/PDF, with measured convert∥filter overlap (~20% wall-clock saved).

## Severity reassessment
| Incident | User flag | Audit verdict |
|---|---|---|
| I-2 CUDA "wasted" | HIGH | **Refuted** — GPU + cu128 work. Reclassified → MEDIUM venv-is-anaconda-based fragility. |
| I-1 env override | FATAL | **Confirmed** — silent no-op; correct name `CHIMERA_PAPER_MINER__PAPERS_ROOT`. |
| I-3 tqdm | LOW | **Confirmed** — `capture_output` buffers+discards; defer. |
| I-4 MinerU deadlock | HIGH/Critical | **Confirmed** — `capture_output` pipe deadlock → 90-min hollow success (`ingested=0 errors=0`). Same `capture_output` root as I-3, but the *fatal* half. |
| I-5 swallow-as-skip | HIGH | **Confirmed** — convert failures counted nowhere + no aggregate guard → 0-of-N converts report `completed`. The silent-failure amplifier behind I-4. |

---

## Resolution — fix sprint (2026-06-30)

| Incident | Decision | Outcome | Evidence |
|---|---|---|---|
| **I-1** env override | Option **B** (robust) | ✅ Fixed | `config.py` `_read_paper_miner_env_overrides` folds every flat `CHIMERA_<KEY>` into `paper_miner` (whole `_PAPER_MINER_KEYS` class). Verified: `CHIMERA_PAPERS_ROOT=D:\NONDEFAULT\papers` → papers_root moves there. `tests/test_config_env.py`; commit `79bfc07`. |
| **I-2** venv anaconda-coupled | **Rebuild now** | ✅ Fixed (DEBT-010 lineage closed) | `.venv` rebuilt on uv-managed CPython 3.13.13 (`pyvenv.cfg home = …\uv\python\…`, no longer `D:\anaconda3`). `uv sync` re-pulled `torch 2.11.0+cu128` + `mineru 3.4.0`. Re-verified: `torch.cuda.is_available()=True` (RTX 5060); live GPU op now shows the **uv** python as the compute process (anaconda gone). pytest 18 passed. |
| **I-3** tqdm | **Defer** | ⏸ Accepted partial | `ACCEPTED_PARTIALS.md` I-3.1 — stage-level timeline suffices. |
| **I-4** MinerU deadlock | **Fix (temp-file sink)** | ✅ Fixed | `paper2md.py` → `tempfile.NamedTemporaryFile` (unbounded, diagnostics retained). Incident `2026-07-01-mineru-capture-deadlock.md`. |
| **I-5** swallow-as-skip | **Fix (count + guard)** | ✅ Fixed | `convert_queue_worker` returns `(success, failure)`; `_run_pipelined_async` raises on 0-of-N + surfaces `convert_failed=`. `tests/test_convert_worker.py`. Incident `2026-07-01-convert-swallow-as-skip.md`. |
| perf lever (mineru-api) | Log only | 📋 Debt | `TECHNICAL_DEBT.md` DEBT-015 — future perf sprint, not an incident fix. |

*Audit + fix sprint complete.*
