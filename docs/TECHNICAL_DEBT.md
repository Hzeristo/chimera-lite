# Technical Debt

Items found during review or use that are NOT accepted partials. These are deficiencies with eventual resolution intent.

**Distinction:** Accepted Partials are trade-off decisions. Technical Debt are unresolved problems.

---

## Open

| ID | Source | Description | Priority | Resolution Plan |
|---|---|---|---|---|
| DEBT-002 | Vibe coding residue | Long-name single-call-site functions across `agent.py` and earlier prompt code (e.g., `_build_router_system_prompt_with_skill_override_and_allowed_tools_filtered_by_whitelist` style) | Low | Touch-and-repair: rename when modifying surrounding code, no dedicated sprint |
| DEBT-003 | Phase II.E friction E2 | `search_vault` keyword-only matching produces low-precision results on conceptual queries | Low | Defer to Phase IV (Exocortex retrieval). Marked OPEN to remind that friction is real but not currently scheduled |
| DEBT-004 | III.B.2 audit | `_execute_tool` no longer needs to re-parse `raw_args` after `PlannedToolCall.args` carries the dict, but legacy parse path remains | Low | Touch-and-repair when next modifying tool dispatch |
| DEBT-005 | III.B.3 audit | Router prompt's args description rendering occasionally falls back to compact mode under non-extreme tool counts; threshold tuning needed | Low | Observe across Phase III.C usage; tune if frictions arise |
| DEBT-006 | UI residue | Stage cards persist across sessions until manually cleared; no automatic cleanup older than N days | Very Low | Backlog |
| DEBT-007 | III.B.3 review (IR.3.1 boundary case) | Tool telemetry doesn't cover *parsing-stage* failures (malformed XML before any plan is built); only execution-stage covered | Low | Next debt week if frictions arise |
| DEBT-009 | FC.2a smoke work (May 2026) | FC.2a smoke test stalled: mock never transitions to PASS, exhausting `max_turns`. Roots: (a) `conftest.MockLLMClient` lacks PASS-switch logic (b) workaround only exists in `agent.py` `__main__`; testing via `__main__` is an antipattern (c) `test_run_theater_with_tool_calls_executes_and_streams` may hide the mock gap | Medium | Unify mock harness; add PASS-switch (or equivalent) on `MockLLMClient`; debt week remove `__main__`-oriented test code from agent |
| DEBT-011 | skill-memory alignment audit (2026-05-24) | Pre-existing friction entries (friction-260426, friction-260506) use legacy field labels (`想做的事`/`我想做的事情`, `实际怎么做的`/`我实际怎么做的`, `摩擦成本`) instead of canonical (`想做`/`实际`/`成本`); tolerated under D9 documented variance, not retroactively rewritten | Very Low | Touch-and-repair: when a future session edits a legacy entry, opportunistically migrate field labels |
| DEBT-013 | V.A.2b audit (`V.A.2b-toolout-fix.md`) open question | `_collect_pipeline_artifacts` (`daily_chimera_service.py`) hardcodes vault subfolder literals (`"Must_Read"`, `"Skim"`) when building chip paths, duplicating `VaultNoteWriter`'s source of truth `verdict.value.replace(" ", "_")` (`vault_note_writer.py:40`). Verified they agree today (not a live bug), but a future `VerdictDecision` label or subfolder-convention change would silently desync chips from the on-disk notes | Low | Touch-and-repair: derive the subfolder from `VerdictDecision.value.replace(" ", "_")` (or a shared helper) when next editing artifact emission |
| DEBT-014 | debt-test-triage audit #7 (2026-06-20) | `conftest.MockLLMClient` distinguishes Router vs Final calls by the literal `"Chimera OS local router"` in the system prompt; the turn-2 `router_continuation.md.j2` lacks that marker, so a continuation probe is miscounted as a Final call (`final_call_count==2`). Confirmed root cause of `test_run_theater_with_tool_calls_executes_and_streams`, left intentionally failing (orthogonal to the `_step_execute` regression fixed in `bedf323`). Refines DEBT-009(c) | Low | Give `MockLLMClient` a reliable router signal (a stable marker present in both router prompts, or a turn counter), then re-enable the assertion |
| DEBT-015 | post-migration incidents audit (2026-06-30, I-2 perf note) | MinerU is invoked as a fresh subprocess **per PDF** (`ports/ingest/paper2md.py`), reloading its models each time — the dominant per-PDF cost (~68-105 s/PDF, mostly cold model load, not the ~30-40% GPU convert). MinerU ships a persistent service (`mineru-api` / `mineru-vllm-server`, both in `.venv\Scripts`) that would keep models warm. | Medium (perf) | Future perf sprint: run a persistent MinerU worker/service and route converts to it instead of per-PDF CLI. NOT an incident fix — deliberate design change. |
| DEBT-016 | Phase Q Q.4 seal (2026-07-10) | 5 Schema-C papers (`2606.19319`, `2606.30639`, `2607.01224`, `2607.02509`, `2607.02514`) were NOT backfilled by `extract_paper` — their K-node `source_md` frontmatter points at a `papers/md_papers/<id>.md` file that is gone, and `_resolve_markdown` hardcodes that path rather than reading the node's own `source_md`. | Low | Either re-ingest the 5 (regenerate markdown), or teach `_resolve_markdown` to read each existing K node's `source_md` frontmatter (authoritative path) before the standard-location fallback; then run `extract_paper` on the 5. |
| DEBT-017 | Phase Q re-seal (2026-07-13) | A rebuilt node is staged with `title=<paper name>`, so on promotion its vault stem is the title slug, not the arXiv id. `_find_superseded_stem(paper_id, …)` matches the OLD node by paper_id in its stem (works for the first rebuild — triage/Schema-C nodes are id-stemmed), but a SECOND extraction of an already-promoted rebuilt node would not self-supersede (its stem lacks the id) → a duplicate rather than a supersede. `arxiv_id` is preserved in frontmatter. | Low | Teach `_find_superseded_stem` to also match on each K node's `arxiv_id` frontmatter (authoritative) before the stem-substring fallback. |
| DEBT-018 | Phase Q live use (AgingBench, 2026-07-13) | **Grounding-by-quote is UNVERIFIED.** The extraction LLM produces both a value and its `"quote" ← location`, and nothing checks that the quote actually appears in the paper's `source_md` — so it can fabricate a number *and* a plausible-looking citation for it. Live extraction of AgingBench surfaced made-up numbers with unverifiable quotes; the human staging-review gate is the ONLY check (nothing false was promoted, but "grounded = trustworthy" is weaker than it appears). Realizes the risk of Accepted Partial Q.reseal.2. | Medium | Substring-verify each `ClaimSource.quote` (and the motivation/results inline quotes) against the converted markdown before staging; drop or visibly flag any quote that does not appear verbatim in the source. |
| DEBT-019 | Phase R spec — R.5 design (2026-07-14); Phase R retired into Phase L 2026-07-16, debt inherited (impl → Phase S) | **`semantic_vault_search` is a forward-declared mock interface, not a real tool.** R.5's dual retrieval path names it as the embedding-search leg, but Phase R does NOT build it — R.5's academic-observe skill calls the real registered tool `vault_query` (keyword) directly. `semantic_vault_search` is not a registered MCP tool; naming it as callable in any skill/code before Phase S would make the agent invoke a tool that does not exist. The interface is pre-defined only so the calling contract stays stable when Phase S swaps in embedding search. | Low | Phase S: implement `semantic_vault_search` as embedding-based retrieval behind the stable interface, replacing the `vault_query` keyword leg. Until then, no skill/code names `semantic_vault_search` as a callable — use `vault_query`. |
| DEBT-020 | Phase L.3 build (2026-07-18) | **W2 reference parser deferred (D5 cheap-first).** The bounded BFS engine `mcp-servers/chimera-papers/w2_breadth.py::plan_expansion` is built + tested, but its `get_refs` leg (the citation/reference parser) is NOT — so W2 expands only over cheaply-available references (bare arXiv ids already in the vault or supplied by the Architect), never a parsed reference crawl. Deep breadth mapping beyond depth-1 supplied ids cannot run until the parser exists; the `chimera-w2-map` skill is scoped to the shallow frontier meanwhile. | Medium | Implement a reference parser behind `plan_expansion`'s `get_refs` contract (arXiv / OpenReview reference extraction), then W2 crawls to the caps. Record a friction if seed+supplied-ref coverage proves insufficient (the L.0 D3 risk). |
| DEBT-021 | Phase L.3 build (2026-07-18) | **W2 BFS bounds are code-spec'd but orchestration-enforced.** `plan_expansion` fixes and TESTS the cap semantics (hard `max_depth` / `max_papers`, cycle & diamond dedup), but at RUNTIME the `chimera-w2-map` SKILL applies the caps in prose — the main agent enforces them, not the tested function. Prose can drift from the tested spec (mis-tracked depth, an over-cap paper count) and nothing structurally prevents it; the "bounded BFS, no unbounded crawl" red line is only as strong as the orchestration's fidelity. | Low | Expose `plan_expansion` as an MCP primitive (or a thin harness step) the W2 skill CALLS, so the runtime bound-enforcement is the tested code, not orchestration prose. The engine already exists (`w2_breadth.py`) — only the wiring is owed. |


---

## Resolved

| ID | Resolved in | Commit | Original Description |
|---|---|---|---|
| DEBT-pre-001 | Phase I M1 | `{commit}` | LLM main path had no outer timeout, allowing indefinite hangs |
| DEBT-pre-002 | Phase I M1 | `{commit}` | `_run_one` used `except BaseException` swallowing `KeyboardInterrupt` |
| DEBT-pre-003 | Phase I M1 | `{commit}` | `web_search` invoked `ddgs.text()` synchronously, blocking event loop |
| DEBT-pre-004 | Phase I M2 | `{commit}` | Hardcoded `127.0.0.1:33333` in Rust + Python |
| DEBT-pre-005 | Phase I M2 | `{commit}` | `_TOOL_TIMEOUT_MESSAGE` hardcoded "45 seconds" decoupled from configurable deadline |
| DEBT-pre-006 | Phase III.A Step 0 | `{commit}` | `<CMD:...>` literal mentions in natural-language explanations triggered actual execution |
| DEBT-pre-007 | Phase III.A Step 0 | `{commit}` | LLM hallucinated tool names not in `TOOL_REGISTRY` |
| DEBT-pre-008 | Phase III.B.1 | `{commit}` | Persona / skill_override / system_core hand-concatenated across 5+ sites |
| DEBT-pre-009 | Phase III.B.2 | `{commit}` | Argument JSON parsing failed on smart quotes, code fences, trailing commas |
| DEBT-012 | `6974cd8` | Append-only contract for ACCEPTED_PARTIALS.md and TECHNICAL_DEBT.md was undocumented in skill process docs. Resolved opposite-direction: phase_review mode now has explicit auto-apply authority for both files via `<state_write_authority>` block in `chimera-sprint-discipline/SKILL.md` and `references/phase-review-process.md` step 8; no separate prohibition needed because the granted scope itself is the contract |
| DEBT-001 | uv env establishment | `db6bc54` | 6 async tests in `tests/oligo/test_tool_execution.py` lacked `@pytest.mark.asyncio` and were silently skipped; `asyncio_mode = "auto"` in `pyproject.toml` now collects and runs them (verified: PASSED/FAILED, never SKIPPED) |
| DEBT-008 | uv env establishment | `db6bc54` | Replace inherited PaperMiner conda environment with a clean `uv`-managed `.venv` pinned to `pyproject.toml` only (env now uv-managed per CLAUDE.md; conda-archival housekeeping not separately verified) |
| DEBT-010 | uv env establishment | `db6bc54` | Python deps unmanaged; conda paper env polluted; no lockfile — now `pyproject.toml` + `requirements.txt`/`requirements-dev.txt` lockfiles + `docs/audits/python-deps.md` audit + CLAUDE.md env block |

---

## Triage Rules

- **Critical:** Block next sprint. Fix immediately.
- **High:** Fix within current phase before seal.
- **Medium:** Fix in next dedicated debt week.
- **Low:** Fix opportunistically when modifying nearby code.
- **Very Low:** Backlog. Re-evaluate annually.

---

## Debt Week Process

When backlog accumulates:
1. Schedule a Use Week (no new code) followed by a Debt Week (only this list).
2. Pick highest-priority Open items.
3. For each: read, scope, sprint, fix, verify.
4. Move to Resolved with commit hash.
5. New friction in Use Week may surface DEBT-NEW items; append, don't preempt the queue.

---

*Update protocol: New entries appended by `chimera-sprint-discipline` phase_review mode under `<state_write_authority>` (auto-apply, no diff). Resolved entries moved by author at fix-commit time.*
