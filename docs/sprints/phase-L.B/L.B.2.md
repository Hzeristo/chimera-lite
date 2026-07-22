# Modification Summary: L.B.2

**Phase:** L.B — Consolidation
**Sprint:** L.B.2 — Externalize judgment: MCP primitives + judgment skills 🔴
**Batch position:** 3 of 7 (parallel-eligible with L.B.3 after L.B.1; the phase-wide red line applies to both)
**Date:** 2026-07-21
**Executed by:** Sonnet subagent (`chimera-sprint-executor`); design authored + reviewed + committed in two halves by main session (Opus). Verification re-run by main session.

---

## Objective

Remove every LLM call of any kind from the MCP server (`chimera-papers`). The former
`FilterService.evaluate_paper` (structured-output deepseek call) is retired entirely; judgment now
lives in Claude Code skills / pinned subagents. The MCP layer is reduced to deterministic
primitives only. Two complementary judgment skills land alongside: `chimera-deep-extract`
(Sonnet subagent for deep-read extraction — extract half) and `chimera-triage-paper` (Haiku subagent
for cheap scout-tier screening — triage half).

Committed in two halves:
- `608c1a7` — extract half (1/2): `stage_deep_read_node`, `get_paper_markdown`, retired `_extract_node`
- `37619ca` — triage half (2/2): `write_scout_card`, `analyze_paper_data`, retired `FilterService`, `batch_filter_workflow`

---

## Files touched

| Path | Change |
|---|---|
| `mcp-servers/chimera-papers/filter_service.py` | Retired `FilterService` class + `evaluate_paper` (structured-output LLM call). New `analyze_paper_data`: deterministic data primitive — resolves markdown path + metadata dict, NO LLM call. |
| `mcp-servers/chimera-papers/batch_filter_workflow.py` | **Deleted** — both LLM-triage loops (`run_batch_filter`, `filter_queue_worker`) have no role under Option B (externalized). |
| `mcp-servers/chimera-papers/daily_chimera_service.py` | Three-stage pipeline (download → convert → **filter**) collapsed to two (download → convert → notify). Filter stage and its LLM judgment removed. `_drain_md_queue` added as the sole `md_queue` consumer (prevents deadlock on batches > maxsize=5). `PipelineCounts` drops verdict tallies; Telegram digest drops verdict links, points at `chimera-triage-paper` skill. |
| `mcp-servers/chimera-papers/single_paper_ingest.py` | **New module** (domain layer for the triage half). `ingest_single_paper`: fetch+convert ONLY — returns `Path`, no LLM call, no vault write. `write_scout_card`: deterministic write half — validates `PaperAnalysisResult | dict` at the boundary, writes to `inbox/<verdict>/` at `chimera_tier="scout"`. |
| `mcp-servers/chimera-papers/single_paper_extract.py` | (Extract half.) Retired `_extract_node`, `_load_lens_catalog`, `json` import, `PromptManager` import. `extract_single_paper` → `stage_deep_read_node` (deterministic back-half: grounding + supersede + render + write at `deep_read`; accepts `KNodeExtraction | dict`, validates at boundary) + `get_paper_markdown` (bare path primitive). |
| `mcp-servers/chimera-papers/single_paper_pipeline_service.py` | `SinglePaperPipelineService.run_single` stubbed as `NotImplementedError` — module is retired (L.B.2 removed its `FilterService` dep); fails loudly at instantiation. DEBT: delete this module. |
| `mcp-servers/chimera-papers/miner_tools.py` | (Extract half) `extract_paper` → `get_paper_markdown` + `stage_deep_read_node` lazy-import dispatchers. (Triage half) `ingest_paper` docstring rewritten (fetch+convert only, no K node); `daily_paper_pipeline` docstring updated; new `write_scout_card` async dispatcher. |
| `mcp-servers/chimera-papers/server.py` | (Extract half) `extract_paper @mcp.tool` → `get_paper_markdown @mcp.tool` + `stage_deep_read_node @mcp.tool`. (Triage half) `ingest_paper` docstring rewritten; `daily_paper_pipeline` docstring updated; new `write_scout_card @mcp.tool`. Fixed stale "writes a Knowledge node" language on `fetch_paper` + `convert_pdf_to_md` docstrings. |
| `.claude/agents/chimera-paper-triager.md` | **New** — pinned Haiku; returns one `PaperAnalysisResult` JSON, no prose. The judgment worker that replaces `FilterService.evaluate_paper`. |
| `.claude/skills/chimera-triage-paper/SKILL.md` | **New** — orchestrates `analyze_paper_data` → `chimera-paper-classifier` → `load_criteria` → `chimera-paper-triager` subagent → `write_scout_card`. Judgment in subagent; loop is pure glue. |
| `tests/test_filter_service.py` | **New** — `FilterService` class + `generate_structured_data` gone; `analyze_paper_data` returns markdown path + metadata dict; settings injectable. |
| `tests/test_daily_chimera_service.py` | **New** — pipeline queues + anti-hollow-success guard preserved; verdict digest absent; `chimera-triage-paper` pointer in summary + Telegram; fake fetcher / convert worker / Telegram notifier stubs. |
| `tests/test_single_paper_ingest.py` | **New** — `ingest_single_paper` never calls `write_knowledge_node`; `write_scout_card` validates dict payload; writes `chimera_tier: scout` inbox card. |
| `tests/test_miner_tools.py` | Extended with `write_scout_card` tool contract tests (delegates + error path). |

---

## Key design facts / decisions

1. **Option B daily pipeline — fetch → convert → notify only.** The former three-stage pipeline
   (download → convert → filter) is now two stages. The filter stage is gone and will not return.
   The converted papers sit in `md_papers/` awaiting the explicitly invoked `chimera-triage-paper`
   skill — there is no ambient triage. This matches the "explicit invocation, not ambient judgment"
   principle from the plan redesign (Reconciliation #2).

2. **`_drain_md_queue` is not optional.** `convert_queue_worker` uses a bounded queue
   (`maxsize=5`). Removing `filter_queue_worker` (the former consumer) without adding a drain would
   deadlock any batch of more than 5 PDFs at `queue.put()`. The drain runs as a task alongside the
   convert worker and does nothing besides advancing the queue to its sentinel.

3. **`analyze_paper_data` reuses `get_paper_markdown` (one resolution scheme, not two).** Rather
   than duplicating md-dir resolution logic, `filter_service.analyze_paper_data` delegates to
   `single_paper_extract.get_paper_markdown` for path resolution — the same scheme the deep-read
   path uses. This keeps the two paths consistent and avoids a future drift point.

4. **`write_scout_card` validates at the tool boundary.** The MCP tool receives a plain dict (JSON
   crossing the tool boundary). `single_paper_ingest.write_scout_card` calls
   `PaperAnalysisResult.model_validate(analysis)` at the entry point so downstream code always sees
   a validated object. The model is `extra="forbid"` — an extra key from the subagent would raise
   here, not silently downstream.

5. **`SinglePaperPipelineService` retired as `NotImplementedError`, not deleted yet.** The module
   imports `FilterService` which is now gone; removing it outright would turn any stale external
   import into an `ImportError` at module load (silently missed by the test suite because nothing
   under test imports it). Stubbing `__init__` as `NotImplementedError` makes the failure loud and
   attribution-preserving. DEBT logged — the module should be deleted once confirmed unused by any
   CLI entry point.

6. **`chimera-paper-triager` pinned Haiku — never upgraded.** Triage is deliberately cheap bulk
   judgment. An ambiguous verdict is a signal to escalate to `chimera-deep-extract`, not a reason
   to spend a bigger model on the screen itself. The pin lives in the agent def
   (`.claude/agents/chimera-paper-triager.md`), not at the call site, per the model-routing audit
   (no call-site `model:` param fragility).

7. **The `chimera-triage-paper` skill uses `chimera-paper-classifier` for type/field first.**
   The criteria block (`load_criteria`) requires `type` + `field` labels; the classifier subagent
   (already existing at `.claude/agents/chimera-paper-classifier.md`) reads the paper and returns
   only those two labels in isolation. The triage skill orchestrates: resolve → classify → load
   criteria → triage subagent → write. Each step is isolated from the ones it doesn't need to see.

---

## Verification

| Check | Status | Output |
|---|---|---|
| ruff (full) | clean | exit 0 — "All checks passed!" |
| pytest (L.B.2 triage-half scope) | 27 passed | exit 0 — `27 passed in 0.57s` |
| pytest (env-artifact deselected, full suite) | verified at L.B.3 seal | 124 passed — unchanged by triage half |
| `grep -r "generate_structured_data" mcp-servers/` | 0 hits | LLM call removed |
| `grep -r "FilterService" mcp-servers/` | 0 hits in live code | Only in retired stub's docstring |
| `grep -r "build_openai_client" mcp-servers/` | 0 hits | openai client import gone |

---

## Red Line Status

| Red Line | Status |
|---|---|
| No LLM judgment call of any kind inside the MCP server | ✓ — verified by grep + test |
| deepseek retired; no Anthropic API call from within MCP | ✓ — `generate_structured_data` + `build_openai_client` gone |
| `chimera-paper-triager` is Claude judgment, never MCP-internal | ✓ — agent def + skill wiring |
| Scout cards always land in `inbox/<verdict>/` at `chimera_tier="scout"` | ✓ — `write_scout_card` + `test_write_scout_card_writes_inbox_scout_card` |
| `write_scout_card` never writes to `Harness/` | ✓ — routed via `VaultNoteWriter.write_knowledge_node` → `inbox/` |
| `ingest_paper` makes NO LLM call and writes NO Knowledge node | ✓ — `test_ingest_single_paper_arxiv_id_returns_markdown_no_vault_write` |
| `daily_paper_pipeline` makes NO LLM call and writes NO Knowledge node | ✓ — `test_pipeline_fetch_convert_notify_no_filter_stage` |
| Anti-hollow-success guard preserved across rewrite | ✓ — `test_anti_hollow_success_guard_raises` |
| No opportunistic refactoring beyond the sprint scope | ✓ — `single_paper_pipeline_service` stubbed, not rewritten |

---

## Acceptance

- ✅ HSC #2 (extract half): `get_paper_markdown` returns the markdown path; `stage_deep_read_node` accepts a `KNodeExtraction | dict`, writes to `docs/staging/` at `chimera_tier="deep_read"`, makes no LLM call.
- ✅ HSC #2 (triage half): `analyze_paper_data` returns `{markdown_path, metadata}` with no LLM call; `write_scout_card` validates + writes `chimera_tier="scout"` inbox card from a dict verdict.
- ✅ Phase-wide red line: `grep -r "generate_structured_data" mcp-servers/` → 0 hits; `grep -r "build_openai_client" mcp-servers/` → 0 hits. The MCP server is a zero-LLM-call layer across all paths.
- ✅ `chimera-triage-paper` skill + `chimera-paper-triager` agent land: the skill orchestrates the judgment loop; the agent carries the judgment itself.
- ✅ Anti-hollow-success guard preserved verbatim across the daily pipeline rewrite.

**Seal:** L.B.2 complete.
