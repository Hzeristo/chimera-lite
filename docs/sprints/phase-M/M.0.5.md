# Sprint M.0.5 — Domain foundation port (core modules + flat imports)

**Status:** ✅ Complete
**Commit:** {filled at commit}
**Risk:** 🔴 HIGH (multi-file foundation) — executed under batch approval "execute … starting M.0.5".
**Plan ref:** `docs/plans/Phase-M-batch.md` → Sprint M.0.5
**Audit ref:** `docs/audits/M.0.md` Q2/Q3/Q4/Q6/Q7 + cross-findings #1/#2

## Objective
Port `config` / `schemas` / `naming` / `platform` into a flat domain package so the
copied domain layer is importable, with the dead oligo surface pruned.

## What was done
- Created `mcp-servers/chimera-papers/core/` package (`__init__.py` + 4 modules), copied
  from `project_chimera/crucible_core/src/crucible/core/`.
- **Settled the M.0.5 design decision (plan flagged):** shared core lives at
  `chimera-papers/core/` (a proper subpackage — avoids stdlib `platform` shadowing; sits
  where most consumers run). `chimera-vault`'s access to it is deferred to M.1.
- Internal imports fixed to flat/relative:
  - `config.py`: `from src.crucible.core.platform …` → `from .platform …`
  - `naming.py`: `from src.crucible.core.schemas …` → `from .schemas …` (TYPE_CHECKING)
- `platform.py`: `get_project_root()` depth fixed `parents[4]` → `parents[3]` (file moved
  shallower; now returns `chimera-lite`, verified).
- **Prune (per user decision "Prune-on-port"):**
  - `schemas.py`: removed the `from src.oligo.core.schemas import (11 types)` re-export;
    inlined local `Artifact` + `ToolOutput` (the only 2 used by surviving domain). Dropped
    unused `model_validator` import (ruff F401).
  - `config.py`: removed `OligoConfig`, the `oligo` field, `oligo_host`/`oligo_port`/
    `oligo_agent` properties, the `OligoAgentConfig` import, and the legacy-YAML `oligo`
    block. `WashConfig` kept (not oligo-specific; out of decision scope).

## Verification (real exit codes)
- ruff (`uvx ruff check core/*.py`): **0** — All checks passed.
- pytest (`tests/test_core_imports.py`): **0** — 4 passed.
- import smoke: `import core.{config,schemas,naming,platform}` OK; `get_project_root()` →
  `D:\MAS\chimera-lite`.
- independence: `grep src.oligo core/` → **0**.

## Accepted deviations (declared at execution)
1. **M.0.5 reclassified "pure port" → "port + prune".** The source `config.py`/`schemas.py`
   import `src.oligo.core.schemas`; a literal pure port would violate the independence red
   line. User chose prune-on-port (2026-06-28). Audit gap: M.0 missed this coupling
   (only flagged `daily_chimera_service.py:15`).
2. **+3 dependencies** (`pydantic-settings`, `tomlkit`, `python-dotenv`) added to
   `pyproject.toml`. These are `config.py`'s own existing footprint, not new capability —
   small pure-Python config libs; pass `chimera-dependency-veto`. Relaxes the M.0.5 "no new
   deps beyond pydantic/pyyaml" red line, which was based on a wrong assumption.

## Known gaps (surfaced to user, not silently bypassed)
- **`check_taste.ps1` not chimera-lite-ready:** ported script `Push-Location`s into
  `crucible_core/` and calls `python -m ruff`/`mypy` (absent in this venv). The M.0.5 gate
  was satisfied via `uvx ruff` + venv `pytest` (both exit 0) + import smoke. Adapting
  `check_taste.ps1` ( + porting ruff/mypy config) is a chimera-lite tooling task — propose
  folding into M.4 or a small M.0.6.
- **mypy not run** for the same reason (no mypy config/stubs wired). Risk low: changes were
  deletions + import-path fixes; ruff + import + pytest are green.
- Comment-level oligo references remain in `schemas.py` (docstring + a few stale
  "migrated to oligo" comments) — left for M.4's dead-ref sweep.

## Predecessor handoff to M.1 / M.2
- `core.config.ChimeraConfig` / `get_config`, `core.naming`, `core.schemas.{Artifact,ToolOutput}`,
  `core.platform.get_chimera_root` are importable from the `chimera-papers` package root.
- Consumer files still import `src.crucible.*` / `src.oligo.*` — M.1 (vault) and M.2 (papers)
  rewrite those as part of wiring, per the distributed-rewrite reconciliation.
