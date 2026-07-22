# Modification Summary: L.B.6

**Phase:** L.B — Consolidation
**Sprint:** L.B.6 — Verify + Rebuild (five-path e2e; fix failing paths in-sprint) 🔴
**Batch position:** last (gate) — runs after L.B.1–L.B.5 sealed; regenerates the L.B.5 diagram at close
**Date:** 2026-07-21
**Executed by:** main session (Opus) — live e2e + in-sprint defect fix + regression tests.

---

## Objective

Exercise all four ingestion/write paths + the ascension guard end-to-end against the real vault,
confirm each produces the correct on-disk state, and **fix any failing path in-sprint before seal**
(the sprint does not seal if any path fails silently). This is the "rebuild" half: the e2e is a
forcing function that surfaces defects the unit tests didn't.

---

## The five paths — run + verdict

| Path | What ran | Result |
|---|---|---|
| 1 — scout (`ingest_paper`) | live MCP `ingest_paper` `2605.06527` → `inbox/Must_Read/2605.06527-STALE.md` | ✅ scout card written (`type: knowledge`, score 8 "Must Read"). ⚠️ **no `chimera_tier` field** — see Finding 1. |
| 2 — deep_read stage (`stage_deep_read_node`) | worktree service, `KNodeExtraction` from `chimera-deep-extractor` (Sonnet) → `docs/staging/…-STALE….md` | ✅ `chimera_tier: deep_read`, `status: PENDING_REVIEW`, `grounded: no_prior_match`, `supersedes: []` **after** the Finding 2 fix. |
| 3 — W1 verbatim verify | `chimera-verbatim-verifier` (Sonnet) on the "best model 55.2%" claim → `Harness/w1_verdict__2605.06527-best-model-55.2.md` | ✅ verdict **[P]** (partial) with `depends_on`. |
| 4 — W2 breadth map | `chimera-breadth-reducer` (Sonnet), 3 on-disk seeds → `Harness/w2_breadth_map__agentic-memory-reliability-over-time.md` | ✅ per-paper gap + headline number, promote flags. |
| 5 — ascend + guard | worktree `StagingService`: `promote_node(deep_read)` then `ascend_node(deep_read)` | ✅ guard **refused** deep_read (`ValueError` naming `ascend_node`, staging file untouched); `ascend_node` wrote `Knowledge/…` (`status: active`, `chimera_tier: deep_read`); W1 verdict **survived**. |

Seeds for Paths 2–5 were already-converted on-disk papers (no fresh GPU cost), per the operator's
"use papers already on disk, pick reasonable seeds."

---

## Finding 1 — registry staleness (deployment gap, not a code defect)

The live MCP servers are registered in `.mcp.json` by **absolute path into the main checkout**
(`D:\MAS\chimera-lite\mcp-servers\…`), so a live Claude Code session calls the **main** code, which
predates L.B. Proof: the Path-1 scout card carries **no `chimera_tier`** (L.B.1's field), because
`ingest_paper` ran from main. Consequence: the L.B.2/L.B.3 tools + the pinned L.B agent types are
**not reachable through the live client** while phase-L.B is unmerged — Paths 2 and 5 had to be
driven by importing the **worktree** service in-process (`.claude/jobs/…/tmp/drive_path{2,5}_*.py`)
against the worktree venv.

This is expected for an unmerged worktree and is **not a blocker**: it resolves the moment
phase-L.B merges to phase-L and the session re-reads `.mcp.json`. Recorded so the seal is honest
about what was verified *live* (Paths 1, 3, 4 — vault reads/writes through primitives already on
main or through subagents) vs *via worktree code* (Paths 2, 5 — the new L.B write path).

## Finding 2 — mis-supersede defect (found + fixed in-sprint)

`_find_superseded_stem` (`single_paper_extract.py`) matched **any** vault `*.md` whose *filename
stem contained the arxiv id* (`if self_id in path.stem`), excluding only `.obsidian` /
`.migration_backup` / `templates`. On the real vault this matched
`Harness/w1_verdict__2605.06527-best-model-55.2.md` (its stem contains `2605.06527`), so the staged
deep_read node acquired `supersedes: [[w1_verdict__2605.06527-best-model-55.2]]` — and on `ascend`,
`_unlink_superseded` would have **deleted the W1 verdict from the vault**. A destructive misfire:
exactly the "advisory theater is negative value" the north star forbids.

The match was also *doubly* wrong: committed Knowledge nodes are named by **title slug**
(`_promote_write`), so the arxiv id is not in their stem at all — the old match would have **missed
every real prior committed node** (theater) while hitting Harness/inbox artifacts that happen to
embed the id.

**Fix (thin, one helper):** scope the scan to the committed `Knowledge/` tier only and match on
frontmatter `arxiv_id` + `type: knowledge`, never a filename substring. This is how prior committed
nodes are actually identified regardless of naming convention (title-slug *or* the older
id-suffixed `…-MemoryOS_Deep_Read.md` form both match by `arxiv_id`); scout cards in `inbox/`
(ascend_node contract: "scout cards stay in inbox/") and Harness results are excluded by
construction. Dropped the now-unused `_NONVAULT_DIRS` constant; added `import yaml`.

---

## Files touched

| Path | Change |
|---|---|
| `mcp-servers/chimera-papers/single_paper_extract.py` | Rewrote `_find_superseded_stem` to scan `Knowledge/` and match frontmatter `arxiv_id` + `type: knowledge` (was: any-vault-`*.md` stem-substring). Added `import yaml`; removed the now-dead `_NONVAULT_DIRS`. |
| `tests/test_extract_paper.py` | `_k_node` gains an optional `arxiv_id`. `test_supersede_edge_when_existing_node` rewritten to place the prior node in `Knowledge/` matched by frontmatter `arxiv_id` (filename deliberately ≠ the id). **New** `test_supersede_ignores_non_knowledge_artifacts` — the regression: a `Harness/` verdict + an `inbox/` scout card sharing the id must **not** be superseded. |

---

## Verification

| Check | Status | Output |
|---|---|---|
| Path 2 re-run (post-fix) | PASS | staged node `supersedes: []`; `chimera_tier: deep_read`; `status: PENDING_REVIEW` |
| Path 5 driver | PASS | guard refused deep_read; `ascend_node` wrote `Knowledge/`; **W1 verdict survived** (`ALL PATH-5 ASSERTIONS PASSED`) |
| pytest `test_extract_paper.py` + `test_extract_schemas.py` | 18 passed | exit 0 |
| pytest full `tests/` | 150 passed, 1 failed | the 1 failure is `test_core_imports.py::test_project_root_is_chimera_lite` — asserts the checkout dir is named `chimera-lite`; fails in **any** worktree (`phase-L.B`). Pre-existing, env-coupled, not touched by this sprint. |
| ruff (`single_paper_extract.py`, `test_extract_paper.py`) | clean | "All checks passed!" (via `uvx ruff`; `.venv` lacks a ruff module — pre-existing env gap) |
| Architecture diagram regen (L.B.6 task 3) | PASS | re-ran `gen_architecture_diagram.py` → **no git diff** (deterministic; supersede fix doesn't change the tool/agent inventory it introspects) |

---

## Vault state left clean (never-auto-promote)

Path 5's `ascend_node` wrote a real `Knowledge/` node; since that ascension was a **test action, not
an operator review**, the committed node was removed (hard rule: never auto-promote staging
candidates) and the STALE deep_read node was **re-staged as `PENDING_REVIEW`** in `docs/staging/`
for the operator to review + ascend themselves once L.B is live. Left in the vault: the Path-1
scout card (a normal `ingest_paper` result) and the Harness W1/W2 review artifacts (Harness/ is the
harness review area by design, not the committed tier).

---

## Red Line Status

| Red Line | Status |
|---|---|
| No LLM judgment inside the MCP server | ✓ — all judgment via subagents (deep-extractor, verbatim-verifier, breadth-reducer); the fix is pure deterministic frontmatter matching |
| Does not seal if any path fails silently | ✓ — Path 2's misfire was caught, root-caused, fixed, and regression-tested before seal |
| Nothing enters `Knowledge/` without `chimera_tier: deep_read` + `ascend_node` | ✓ — guard test confirms `promote_node` refuses deep_read; ascend requires it |
| Thin, non-refactoring change | ✓ — one helper rewritten + its test; no opportunistic refactor |
| Never auto-promote `docs/staging/` to the vault | ✓ — test-ascended node removed, re-staged PENDING_REVIEW for operator |

---

## Acceptance

- ✅ All four paths + the ascension guard exercised end-to-end against the real vault; each produces
  the correct on-disk state.
- ✅ The one failing path (Path 2 mis-supersede) was fixed in-sprint with a regression test, not
  deferred.
- ✅ Registry-staleness deployment gap recorded (Finding 1) — a merge-time resolution, not a code
  defect.
- ✅ Architecture diagram regenerated at seal; reproduces byte-identically.

**Seal:** L.B.6 complete. Phase L.B ready for phase_review/seal (chimera-sprint-discipline); merge
phase-L.B → phase-L is a post-seal, operator-gated step.
