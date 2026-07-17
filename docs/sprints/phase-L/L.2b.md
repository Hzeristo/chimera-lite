# Sprint L.2b — `write_result` (write + identity-supersede + `depends_on`)

**Phase:** L (Locus) · **Risk:** 🔴 HIGH (gated, approved) · **Date:** 2026-07-16
**Plan:** `docs/plans/Phase-L-batch.md` · **Audit:** `docs/audits/L.0.md` (F2) · **Constraint:** C1 (Phase K Gate 1)
**Executed by:** Opus main session (🔴 kept in-session per skill; human gate passed). **Open decision #9 resolved:** target = `<vault>/Harness/`.

## What was built
- `mcp-servers/chimera-papers/result_service.py` — `ResultService.write_result(kind, identity, title,
  body, metadata=None)`. Writes a review-gated artifact into `<vault>/Harness/` with
  `status: PENDING_REVIEW`. Filename is identity-keyed (`{kind}__{identity}.md`) → a re-run with the
  same identity OVERWRITES (supersede, never duplicate); `superseded_prior` records whether it replaced
  one. `metadata` (e.g. `verdict`, `depends_on`) lands in frontmatter.
- Thin `@mcp.tool write_result(kind, identity, title, body, verdict=None, depends_on=None)` in
  `chimera-vault/server.py` — dispatcher; builds metadata from verdict/depends_on, constructs
  `ResultService` at `<vault>/Harness/`. Full WHEN/WHAT docstring.
- `tests/test_write_result.py` — 4 tests: PENDING artifact with `depends_on` in frontmatter (C1);
  same-identity re-run supersedes (1 file, verdict replaced, `superseded_prior=True`); distinct
  identities → distinct files; empty identity rejected.

## Decisions
- **Open decision #9 → vault subfolder** (`<vault>/Harness/`), Architect-approved. EXPANDS
  chimera-vault's write scope beyond `docs/staging/` (intentional per CHANGE 5 — the two curation
  paths: harness `write_result` + Obsidian edit). These are the harness's OWN output surface, not
  K/T/I/D nodes, so the "never auto-promote staging candidates" rule is untouched.
- **C1 (Phase K Gate 1):** the W1 verdict artifact records `depends_on` in frontmatter — the dependency
  structure Phase K's monotonicity gate reads. The verdict is never stored bare.
- **Identity-supersede** is a deterministic identity-keyed overwrite (simpler + more robust than the
  Phase Q supersedes-edge scan; same "replace, never duplicate" contract).

## Verification
- pytest `tests/test_write_result.py`: **4 passed**, exit **0**. Full suite: **96 passed** (no regressions).
- `uvx ruff check`: clean, exit **0**.
- **Decision: PASS** (0/0).

## Red-line check
- ✅ Records `depends_on` dependency structure, not verdict-only (C1).
- ✅ Identity-supersede — never duplicates on re-run.
- ✅ Writes only the harness surface (`<vault>/Harness/`); no K/T/I/D mutation, no auto-promote.
- ✅ Thin adapter — lifecycle in `result_service.py`; server body is a dispatcher.
- ✅ No new dependency; `.mcp.json` unchanged.

## Notes
- L.3a (W2) will extend `write_result` with MERGE mode (preserve annotations) + `mark_stale`.
- `chimera-vault/server.py` now ~300 lines (O.seal.1 overage watch, reconciliation #8) — the
  `write_tools.py` extraction is a deferred cleanup, NOT done here (no opportunistic refactoring).

**Delivers:** the W1 result sink with dependency structure (C1). **Next:** L.2c (🔴 W1 orchestration) — the ROI core + prove-value gate.
