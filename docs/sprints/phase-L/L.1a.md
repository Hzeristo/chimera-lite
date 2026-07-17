# Sprint L.1a — Criteria matrix scaffold + `load_criteria`

**Phase:** L (Locus) · **Risk:** 🟡 MED · **Date:** 2026-07-16
**Plan:** `docs/plans/Phase-L-batch.md` · **Audit:** `docs/audits/L.0.md` (B1/B2)
**Executed by:** Sonnet subagent (edits) + Opus main session (review + commit).

## What was built
- `compose_criteria(read_file, *, type, role, field=None)` — pure function in
  `mcp-servers/chimera-vault/vault_tools.py`. Composes, in the mandatory capability→disposition
  order: `criteria/type/{type}.md` → `criteria/field/{field}.md` (optional) →
  `criteria/disposition/{role}.md` → `criteria/disposition/_general.md`. Missing files degrade
  to `[no criteria file: …]` markers — never fabricated, never crashes. Pure over an injected
  `read_file` callable → unit-testable without a live vault.
- `load_criteria(type, role, field=None)` thin body binding compose to the module adapter.
- Thin `@mcp.tool load_criteria` in `chimera-vault/server.py` (dispatcher + WHEN/WHAT docstring).
- Seeded 8 vault criteria stubs under `<vault>/criteria/` (type×4, `field/_example`, disposition×3)
  — placeholders; the Architect authors real content in Obsidian.
- `tests/test_load_criteria.py` — 8 tests (compose order, missing-field marker, verbatim content,
  `field=None` omission, all-missing degradation, headers) over a `tmp_path` fake reader.

## Verification
- pytest `tests/test_load_criteria.py`: **8 passed**, exit **0**.
- `uvx ruff check`: all checks passed, exit **0**.
- **Decision: PASS** (exit codes 0/0, authoritative per batch_execution).

## Red-line check
- ✅ No criteria content in repo (only loader + markers); real criteria live in the vault.
- ✅ Thin adapter — compose in `vault_tools.py`; `server.py` body is a dispatcher.
- ✅ Capability composes before disposition.
- ✅ No new dependency; `.mcp.json` unchanged (2 servers).
- ✅ No opportunistic refactoring.

## Notes / deviations
- Implemented signature `load_criteria(type, role, field=None)` (field optional, last) vs. the
  doc's nominal `(type, field, role)` — MCP args are keyword-based, so order is cosmetic; field
  is the open, frequently-absent axis, so optional-last is the better shape. Docs left unchanged.
- `chimera-vault/server.py` grows ~30 lines (~255 total) — the O.seal.1 overage watch (batch-plan
  reconciliation #8) applies; revisit the `write_tools.py` extraction when `write_result` lands (L.2b).
- HSC #1 (vault-dynamic criteria) is delivered structurally; the live edit-in-Obsidian confirmation
  is a seal-time check.

**Delivers:** HSC #1 (criteria are vault-dynamic). **Next:** L.1b (classifier subagent).
