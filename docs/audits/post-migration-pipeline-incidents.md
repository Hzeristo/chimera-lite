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

*Audit only — no code changed. Fix sprint follows.*
