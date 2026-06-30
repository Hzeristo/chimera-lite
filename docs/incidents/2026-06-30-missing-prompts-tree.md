# Incident — daily_paper_pipeline crash: missing `prompts/` template tree

**Date:** 2026-06-30
**Surfaced by:** M.5 E2E smoke, Test 2 (`docs/audits/M.5-e2e-smoke.md`).
**Severity:** Critical (pipeline unrunnable) / Fix difficulty: minor (resource port).

## Symptom
`daily_paper_pipeline` started (task_id returned), got past arXiv fetch and all imports,
then the background task died at `PromptManager.__init__`.

## Root cause
The Jinja prompt template tree was **never ported** in Phase M. `PromptManager()` resolves
its dir to `<repo-root>/prompts/` (`jinja_prompt_manager.py:26`, `parents[4]` →
`D:\MAS\chimera-lite\prompts`), which did not exist → `FileNotFoundError`. The migration
ported domain *code* and the missing core *modules* (config/schemas/naming/platform,
bootstrap) but not this domain *resource*. The audit's import-surface scan only tracked
`from src.*` imports, so a filesystem resource dependency was invisible to it.

## Fix
Ported the full template tree `project_chimera/crucible_core/prompts/` →
`chimera-lite/prompts/` (18 files: `chimera_sys/`, `obsidian_tpl/`, `tasks/` incl.
`optics/`). No code change — `PromptManager`'s `parents[4]` already resolves to the
chimera-lite repo root.

## Verification
- `PromptManager()` initializes → `D:\MAS\chimera-lite\prompts`.
- All pipeline `.j2` templates parse (filter / reviewer_zero / user_profile / daily_summary
  / node templates).
- Downstream construction probed clean: `inbox_folder` resolves
  (`…\project_chimera_vault\inbox`, absolute), OpenAI client constructs, `VaultNoteWriter`
  constructs.
- Regression guard added: `tests/test_prompts.py` (fails if the tree goes missing).
- ruff + pytest green.

## Notes / non-issues
- `obsidian_tpl/Tpl_*.md` (4 files) fail Jinja parse — **expected**: they are Obsidian
  Templater files (synced to the vault per CLAUDE.md's hard rule), **never** Jinja-rendered
  by the pipeline (`grep Tpl_ *.py` → 0). Harmless.
- The next failure point is now genuine **runtime** (live LLM calls, MinerU model load,
  real arXiv fetch) — exercised by the M.5 live re-run, not a construction gap.

## Open governance question (for the user — NOT fixed here)
`obsidian_tpl/Tpl_*.md` + the node `.j2` now exist in **both** repos. CLAUDE.md's hard rule
says the vault `templates/` sync from `crucible_core/prompts/obsidian_tpl/`. Decide which
repo is canonical for `obsidian_tpl/` going forward (project_chimera vs chimera-lite) so
the vault-sync source-of-truth stays single. Flagged, deferred — like `status=?`.
