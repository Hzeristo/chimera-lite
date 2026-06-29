# Sprint M.2b — Daily paper pipeline (filter / ingest / notify) + CUDA MinerU

**Status:** ✅ Complete (full live end-to-end run is the M.5 E2E smoke)
**Commit:** {filled at commit}
**Risk:** 🔴 HIGH — executed under per-sprint approval ("Install MinerU fully", 2026-06-28).
**Plan ref:** `docs/plans/Phase-M-batch.md` → Sprint M.2b
**Audit ref:** `docs/audits/M.0.md` Q6/Q7 + cross-findings #4/#5

## Objective
Wire `daily_paper_pipeline` (fetch → MinerU ingest → LLM filter → notify) and rewrite the
daily-path import chain to flat.

## What was done
- Ported `bootstrap.py` (`build_openai_client*`) — another missing module (like config), flat.
- Rewrote **14 daily-path files** `src.crucible.*` / `src.oligo.*` → flat (scripted, 5
  deterministic substitutions, verified by re-grep): `daily_chimera_service`,
  `batch_filter_workflow`, `filter_service`, `ports/ingest/*`, `ports/notify/*`,
  `ports/papers/*`, `ports/prompts/__init__`, `ports/llm/*`, `ports/vault/vault_note_writer`.
- Wired `daily_paper_pipeline` + `_run_daily_with_progress` in `miner_tools.py` — the heavy
  filter/ingest chain is **lazy-imported** inside the helper, so `miner_tools` module load
  stays light. Server tool delegates under the existing concurrency lock; `_PIPELINE_NOT_WIRED`
  removed.
- Fixed one pre-existing ruff F841 (`last_exc` dead assignment) in `openai_compatible_client.py`.

## CUDA / MinerU install (user-directed Step 0–4)
- GPU **RTX 5060 (Blackwell, sm_120)**, driver CUDA 13.1.
- pyproject: `[[tool.uv.index]] pytorch-cuda` (cu128) + `[tool.uv.sources]` torch/torchvision;
  `torch>=2.7,<3` + `mineru[core]>=1.4` with an inline dependency-veto OVERRIDE justification.
- Verified: `torch 2.11.0+cu128`, `torch.cuda.is_available()` → **True**, device **RTX 5060**.
- Documented in `CLAUDE.md` (dev env → GPU / CUDA).

## Verification (real exit codes)
- ruff: **0** — All checks passed (all M.2b files).
- pytest (`tests/`): **0** — 13 passed, 1 skipped.
  - `daily_paper_pipeline` returns a `daily_pipeline` 8-hex task_id and registers an active
    long task (heavy chain mocked).
- import smoke: `daily_chimera_service`, `batch_filter_workflow`, `filter_service`,
  `bootstrap`, `mineru_pipeline`, `telegram_notifier`, `vault_note_writer` all import — the
  full real MinerU/torch chain loads.
- `grep "from src." ` over daily-path files → **0**.

## HSC status (sealing condition 2, full)
- `daily_paper_pipeline` → task_id → poll model: ✅ wired + unit-verified.
- **Live end-to-end** (real arXiv fetch → GPU PDF→MD → LLM triage → real titles): ⏸ **M.5
  E2E smoke** — needs network, valid LLM API keys, and minutes of runtime. The install is now
  in place so M.5 can run it fully locally.

## Accepted deviations / notes
1. **Dependencies added (dependency-veto):** `torch` (cu128), `mineru[core]` (OVERRIDE —
   core capability, confined to `ports/ingest/mineru_pipeline.py`), `jinja2`, `openai`,
   `tenacity` (direct footprint of the chain). `torch>=2.7` (not the plan's `>=2.4`) is the
   first series with cu128/sm_120 wheels — required for the RTX 5060.
2. **`uv.lock` is gitignored** — the ML stack is large; reproduction is via pyproject + the
   cu128 index. Reconsider committing the lock if reproducibility becomes a concern.
3. **4 stragglers still on `src.*`** (`optics_service`, `optics_lens_registry`,
   `cli_presenter`, `single_paper_pipeline_service`) — not on the daily path; M.4 rewrites
   or deletes them.

## Predecessor handoff to M.4
- Remaining `src.*`: only the 4 stragglers above. M.4 rewrites/deletes them, deletes any
  remaining `_NOT_WIRED` / dead oligo comments (e.g. `schemas.py` docstring), and runs the
  final independence + sentinel grep (sealing conditions 4 & 5).
