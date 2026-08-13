# Modification Summary: L.B.1

**Phase:** L.B — Consolidation: Tier Integrity + Model Migration + Unified Ascension
**Sprint:** L.B.1 — `chimera_tier` field + status vocabulary 🔴 (LOAD-BEARING)
**Batch position:** 1 of 7 (must seal before L.B.2/L.B.3)
**Date:** 2026-07-21
**Executed by:** Sonnet subagent (`chimera-sprint-executor`, batch delegation); design authored + reviewed + committed by main session (Opus). Forked per user directive.

---

## Objective

Add the orthogonal `chimera_tier` frontmatter field so a scout-tier triage card and a
deep-read node are machine-distinguishable (fixes audit C-1), and codify the tier + status
lifecycle axes in the schema authority. Extend the existing `PENDING_REVIEW → active`
machinery; do not rebuild it. Do not overload `status`.

---

## Files touched

| Path | Change |
|---|---|
| `prompts/obsidian_tpl/knowledge_node.j2` | `+ chimera_tier: scout` (active writer: `write_knowledge_node` — daily/ingest scout card) |
| `prompts/obsidian_tpl/deep_read_node.j2` | `+ chimera_tier: deep_read` (active writer: `write_deep_read_node`) |
| `prompts/obsidian_tpl/deep_read_survey_node.j2` | `+ chimera_tier: deep_read` (`chimera_status` anomaly left untouched) |
| `prompts/obsidian_tpl/thought_node.j2` | `+ chimera_tier: synthesis` |
| `prompts/obsidian_tpl/insight_node.j2` | `+ chimera_tier: synthesis` |
| `prompts/obsidian_tpl/decision_node.j2` | `+ chimera_tier: synthesis` |
| `mcp-servers/chimera-papers/staging_service.py` | `create_staging_node` gains `chimera_tier` param; T/I/D default to `synthesis`; K never defaulted; written authoritatively over `metadata` |
| `mcp-servers/chimera-papers/single_paper_extract.py` | `extract_paper` passes `chimera_tier="deep_read"` |
| `mcp-servers/chimera-vault/server.py` | docstrings only: `search_vault_attribute` + `vault_query` advertise the tier axis + the four `type` values (thin adapter — no logic) |
| `docs/ARCHITECTURE/NODE_ONTOLOGY.md` | new §7: `chimera_tier` axis + `status` lifecycle tables (orthogonal axes) |
| `tests/test_chimera_tier.py` | new — 6 tests (tier resolution + template render + C-1 distinctness) |

Note 1 (user gate) satisfied: `chimera_tier` added to **all six** node templates, not just the enumerated inbox one.

---

## In-sprint decisions (cited)

1. **`synthesis` as a fourth tier value + a type-based default for T/I/D.** The locked D1
   vocabulary was `{scout, deep_read, harness_candidate}` — all ingestion/harness origins.
   T/I/D are user-authored reasoning nodes, not ingestion; leaving the template field
   unemitted by the active writer (`create_staging_node`, not the `.j2`) would be exactly
   the "advisory rigor is negative value" theater the core philosophy forbids. Resolution:
   add `synthesis` as the origin value for T/I/D and default it in `create_staging_node`
   (definitionally correct, needs no `create_node` change), making note-1's "all nodes carry
   a tier" real end-to-end. Cited in `NODE_ONTOLOGY.md` §7.1. Licensed by the plan's "decide
   in-sprint, cite it" clause for tier assignment.
2. **`knowledge` is never defaulted.** A K node with no tier stays untiered so its writer is
   forced to declare `scout` vs `deep_read` — a silent K default would re-open C-1. Enforced
   by `test_knowledge_is_never_defaulted`.
3. **`harness_candidate` is a documented mapping, not a template edit.** Harness artifacts are
   written by `ResultService.write_result` (already `kind`-keyed with a review status); they
   are not K/T/I/D nodes. The tier mapping is documented in §7.1; no code change (out of the
   six-template + staging scope).
4. **Deferred, not fixed (no opportunistic refactoring):** `deep_read_survey_node.j2` uses
   `chimera_status: survey_deep_read` instead of `status:`. Flagged in §7.2; carries
   `chimera_tier: deep_read` like its sibling; the status-key reconciliation is deferred.

---

## Verification

| Check | Status | Output |
|---|---|---|
| ruff | clean | exit 0 — "All checks passed!" (`uvx ruff check .`; ruff is not a project dep, run ephemerally) |
| pytest (full) | 116 passed / 1 env-artifact | exit 1 solely from `test_core_imports.py::test_project_root_is_chimera_lite` |
| pytest (env-artifact deselected) | 116 passed | exit 0 — independently re-run in main session via `chimera-verify-runner` |
| check_taste.ps1 | N/A | stale template targeting `crucible_core/` (per Q.1b evidence) — gate = ruff + pytest |

**The one failure is not a defect.** `test_project_root_is_chimera_lite` asserts the checkout
directory is named `chimera-lite`; this session runs inside a git worktree named `phase-L.B`,
so it fails on the unmodified tree too. The test file is not in this sprint's diff. It is a
brittle, pre-existing environment assumption (out of L.B.1 scope to fix).

---

## Red Line Status

| Red Line | Status | Verification |
|---|---|---|
| `chimera_tier` in frontmatter only, never in body | ✓ | grep: appears only in `---` frontmatter blocks + the service `fm` dict |
| Extend `PENDING_REVIEW → active`, do not rebuild | ✓ | `promote_node`/staging transition untouched; only additive `chimera_tier` writes |
| `status` not overloaded to carry tier | ✓ | two separate keys; §7 documents them as orthogonal axes |
| Thin adapter — no query/tier logic in `server.py` | ✓ | server.py diff is docstrings only |
| No opportunistic refactoring | ✓ | survey `chimera_status` anomaly left as-is; only scope files changed |

---

## Acceptance

- ✅ A scout K node and a deep_read K node differ by `chimera_tier` — `test_scout_and_deep_read_tiers_are_distinct` + template-render tests.
- ✅ HSC #1 documentation side: `vault_query` docstring advertises `type ∈ {knowledge, thought, insight, decision}` (already did) — live "returns T nodes" verification deferred to L.B.6 (requires a T node in the live vault; holds via fact F6, `vault_query` has no type allowlist).
- ✅ `NODE_ONTOLOGY.md` §7 documents the tier axis + status lifecycle; the inert-inbox-status gap is resolved-by-design (scout `unverified` is human-gated via `ascend_node`, L.B.3), stated explicitly.

**Seal:** L.B.1 complete — unblocks L.B.2a / L.B.3 (parallel-eligible).
