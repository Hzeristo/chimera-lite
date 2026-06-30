# Sprint M.4 — Cleanup + independence verification

**Status:** ✅ Complete
**Commit:** {filled at commit}
**Risk:** 🟡 MED — mechanical; self-executed.
**Plan ref:** `docs/plans/Phase-M-batch.md` → Sprint M.4
**Audit ref:** `docs/audits/M.0.md` (sealing conditions 4 & 5)

## Objective
Rewrite the straggler imports, delete sentinels + dead refs, and prove independence.

## What was done
- **Step 1 — stragglers flattened:** `optics_service.py`, `optics_lens_registry.py`,
  `cli_presenter.py`, `single_paper_pipeline_service.py` → `src.crucible.*`/`src.oligo.*`
  rewritten to flat (same 5 substitutions). These are currently-unused domain modules
  (no MCP tool imports them), kept for potential future tools.
- **Step 2 — sentinels + dead refs:**
  - `NOT_WIRED` / `NotImplementedError`: already 0 across `mcp-servers/` (servers were
    cleaned at M.1/M.2a/M.2b).
  - Removed the retired **astrocyte** surface from `config.py` (`AstrocyteConfigBlock`
    class + field + legacy dict + comment) — safe because `extra="ignore"` now drops the
    shared config's `[astrocyte]` section. Removed the now-unused `Literal` import.
  - Removed misleading dead oligo comments in `schemas.py` (`# --- Oligo ---`,
    `migrated to oligo.core.schemas — re-exported above` blocks, docstring "Oligo").
  - Trimmed oligo/astrocyte mentions in `bootstrap.py`, `task_service.py`,
    `ports/llm/base.py`, `vault_query.py` docstrings; `platform.py`
    `chimera-oligo.service` → `chimera.service`.
- **Step 3 — independence grep (sealing conditions 4 & 5):** all pass.

## Verification (real exit codes)
- ruff (`mcp-servers tests`, full repo): **0** — All checks passed.
- pytest (`tests/`): **0** — 13 passed, 1 skipped.
- config load smoke: `get_config()` loads the shared `~/.chimera/config.toml` cleanly
  (`[oligo]` + `[astrocyte]` sections ignored); `vault_root` resolves; no `astrocyte` attr.
- **Independence grep (code, excl. `__pycache__`):**
  - `grep src.crucible` → **0**
  - `grep "from src.oligo\|import oligo"` → **0**
  - `grep -i astrocyte` → **0**
  - `grep "NOT.WIRED\|NotImplementedError"` → **0**

## Notes
- Remaining bare-word "oligo" in code is **intentional** and accurate: `config.py`
  comments describing the dropping of legacy `oligo_*` keys and tolerance of the shared
  config's `[oligo]` block (current behavior). These do not match the independence import
  grep and are correct documentation.
- **mypy** still not wired (per the M.0.5 gate agreement — ruff + pytest is the chimera-lite
  gate). Adapting `check_taste.ps1` + adding a ruff/mypy config remains an open tooling
  task (candidate for a future small sprint); flagged at M.0.5.

## Phase M status after M.4
All wiring + cleanup complete and independent of oligo/astrocyte. Only **M.5 (live E2E
smoke)** remains — user-run. See `docs/audits/M.5-e2e-smoke.md`.
