# Phase Audit: Phase M — Chimera Lite Migration

**Scope:** Read-only audit prerequisite for batch_planning of Phase M.
**Output location:** `docs/audits/M.0.md` (M.0 is the phase's first read-only sprint).
**Date:** 2026-06-28
**Mode:** Read-only w.r.t. source — no fix proposals, no code modifications. The one
write is this report.
**Method:** 5 parallel Haiku scouts, one group per audit question (deduped by file
scope). Evidence sources: live `D:\MAS\chimera-lite\` filesystem + the
`archive/chimera-oligo` branch of `project_chimera` (oligo originals).

---

## Files read

| Path | Notes |
|---|---|
| `mcp-servers/chimera-vault/server.py` | full — 128 lines |
| `mcp-servers/chimera-papers/server.py` | full — 102 lines |
| `mcp-servers/chimera-papers/**/*.py` (24 files) | import-surface + red-line scan |
| `mcp-servers/chimera-papers/task_service.py` | task_id + lock + coupling |
| `mcp-servers/chimera-papers/daily_chimera_service.py` | oligo coupling + locks |
| `mcp-servers/chimera-papers/ports/vault/vault_read_adapter.py` | full — adapter surface |
| `pyproject.toml`, `.mcp.json` | declared deps + env wiring |
| `archive:…/oligo/tools/{vault_tools,vault_query,miner_tools,web_search}.py` | original tool wrappers |
| `archive:…/oligo/prompts/final_*.md`, `router_skill_directive.md` | persona templates |
| `archive:…/docs/prompt_archive/review_zero_v3.md` | "Reviewer Zero" persona precedent |
| `docs/phases/phase-M.md` | intent + red lines + BB trait spec |

---

## Findings

| Q# | Sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| Q1 | M.1 | What does `VaultReadAdapter` need, and does its surface cover the 5 vault tools? | Constructs from a `ChimeraConfig`; exposes all needed methods. Tool→method map complete (vault_query is separate, ripgrep-based, not adapter-backed). | `vault_read_adapter.py:137` (`__init__(self, settings: ChimeraConfig)`); `read_file@203`, `search_notes@397`, `search_by_attribute@404`, `query_graph@546` | Low |
| Q2 | M.1 | Broken import/dep closure for vault tools + which modules are absent? | Tool wrappers `vault_tools.py`/`vault_query.py` were **never copied** (only the adapter). `ToolOutput`/`Artifact` come from `src.oligo.core.schemas`; `vault_query` needs `get_config()` + `settings.require_path("vault_root")` + ripgrep. Missing local modules: `config`, `naming`. | `vault_tools.py:5` (oligo schemas); archived `vault_query.py` (`get_config`, `rg`); `vault_read_adapter.py:15-16` | High |
| Q3 | M.2 | Was `miner_tools.py` copied? Its closure? | **ABSENT** — must be authored fresh. Archived original defines `arxiv_miner`, `daily_paper_pipeline`, `check_task_status` (+ `_run_daily_with_progress`). | Glob `**/miner_tools.py` → none; archived imports: `fetch_and_process_arxiv`, `task_service`, `daily_chimera_service.run_daily_pipeline_with_stage_events`, `src.oligo.core.schemas.ToolOutput` | High |
| Q4 | M.2 | Is the 8-hex `task_id` contract preserved, is `TaskService` oligo-free, and where is the concurrency lock? | `task_id = uuid4()[:8]` → **8 hex, contract holds** (poll model valid). `TaskService` is oligo-free. **No concurrent-pipeline lock exists** — only internal `stats_lock` + download `Semaphore(3)`. Red-line server lock is net-new. | `task_service.py:265`; `daily_chimera_service.py:232` (Semaphore), `:234` (stats_lock) | Med |
| Q5 | M.3 | Is a portable BB persona source recoverable? | **Actual BB voice text NOT in repo or archive** — `final_*.md` are templates with `{persona}`/`{authors_note}` placeholders. Only the 4-trait spec (`toxicity+warmth+anti-hype+forensic`) and the "Reviewer Zero" precedent exist. "warmth" is undefined (Reviewer Zero is pure cynicism). | `phase-M.md:57-58` (trait spec); `archive:…/prompt_archive/review_zero_v3.md` (precedent); `final_persona_override.md` (placeholder only) | Med |
| Q6 | M.4 | Full `src.*` import-rewrite surface? | **74 `src.*` import lines across 24 files**: 1 `src.oligo.*`, 73 `src.crucible.*`. Plus a **package-layout mismatch** — code imports `src.crucible.services.*` / `src.crucible.core.*` but files are flattened at the package root. | Scout A enumeration (74 lines / 24 files); `task_service.py` at root vs `src.crucible.services.task_service` import | High |
| Q7 | M.4 | Any oligo/astrocyte independence violations vs legit crucible reuse? | **One real code violation**: `from src.oligo.core.schemas import Artifact, ToolOutput`. All other `oligo` hits are docstrings in my `server.py` stubs. No `astrocyte` / `oligo.core` / `oligo.api` code refs. | `daily_chimera_service.py:15` (used at `:189`); `server.py` hits are comments only | Med |
| Q8 | M.5 | External/config prerequisites for a live E2E run? | Needs: ripgrep on PATH, MinerU + paper2md ingest, Telegram bot token, OpenAI-compatible LLM `api_key`. Env vars (`CHIMERA_VAULT_ROOT`/`CHIMERA_PAPERS_ROOT`) wired in `.mcp.json`. **`pyproject.toml` deps are insufficient for the domain** (missing jinja2, arxiv client, mineru, etc.). | `.mcp.json` env; `ports/ingest/mineru_pipeline.py`; `ports/notify/telegram_notifier.py`; `ports/llm/openai_compatible_client.py`; `pyproject.toml` deps list | Med |
| Q9 | red lines | Are the MCP adapters thin and free of agent-loop/SSE/DSL code? | **PASS.** vault server 128 lines, papers server 102 lines (both <200). **Zero** forbidden tokens (`bb-stream`, `sse_event`, `ChimeraAgent`, `parse_args_with_repair`, `_run_theater`, `<CMD`, `<tool_call`, `prompt_composer`) anywhere under `mcp-servers/`. | server line counts; red-line grep → all none | Low |

---

## Cross-references discovered

Structural facts spanning multiple sprints — these change batch_planning's file scope:

- **`ChimeraConfig` is the lynchpin.** The vault adapter, `vault_query`, and nearly all
  papers domain code construct from / call it. Porting `config.py` gates **both** M.1
  and M.2. Evidence: `vault_read_adapter.py:137,15`, `daily_chimera_service.py:12`,
  `fetch_arxiv_workflow.py:9`, `arxiv_fetch.py:15`.
- **The schema pair (`ToolOutput`/`Artifact`) is the only oligo coupling, but it's
  shared.** Used by both the archived vault wrappers and live `daily_chimera_service`.
  Resolving it is joint M.1/M.2/M.4 work, not a single-sprint fix. Evidence:
  `vault_tools.py:5`, `daily_chimera_service.py:15,189`.
- **Package-layout decision precedes the import rewrite.** Imports assume a
  `src/crucible/{core,ports,services}/` tree; the files are flattened. M.4's "import
  path fixes" implicitly require choosing: re-vendor the `src/crucible` package tree
  (keeps 73 imports working, honors "minimal changes") **or** rewrite all 74 lines to a
  flat layout. Evidence: `task_service.py` at root vs `src.crucible.services.task_service`.
- **`platform.py` is also missing** (`get_chimera_root`), used by `TaskService`'s default
  tasks dir. Evidence: `task_service.py:57`.

---

## Notable cross-findings (no fix proposals — flagging for planning)

1. **The "minimal changes" red line favors vendoring the package tree over flat rewrites.**
   `phase-M.md:41-42` says domain code should need "primarily import path fixes, not logic
   rewrites." Recreating `src/crucible/...` (so the 73 `src.crucible.*` imports resolve
   unchanged) changes *zero* domain lines; rewriting 74 import statements touches every
   file. Planning should make this an explicit M.4 (or pre-M.1) decision, because M.1 and
   M.2 both depend on it. Evidence: `phase-M.md:41-42`; 74 imports / 24 files.

2. **A "port config/schemas/naming/platform" step is an unlisted prerequisite to M.1 *and*
   M.2.** `phase-M.md` lists M.1 (vault) and M.2 (papers) as independent/parallelizable
   (`phase-M.md:29-30`), but both are blocked on the same four missing core modules. This
   shared foundation is not its own sprint. Planning should either prepend it to M.1 or
   split it out, or the "parallel" assumption breaks. Evidence: `config`/`naming`/`schemas`/
   `platform` all MISSING; consumed by `vault_read_adapter.py:15-16`, `task_service.py:21,57`.

3. **The actual BB persona text is not recoverable from the repo or archive branch.** The
   `final_*.md` files are runtime-injection templates (placeholders only); the real voice
   was supplied at request time — most plausibly from `~/.chimera/skills/*.json` (Phase II.A:
   "Six skill JSONs in `~/.chimera/skills/`"), which is outside the repo and was not audited.
   M.3 should first attempt to locate that source; absent it, BB must be authored fresh from
   the 4-trait spec, and the **undefined "warmth" vector needs a design decision** (the only
   precedent, Reviewer Zero, has none). Evidence: `final_persona_override.md` (placeholder);
   `phase-M.md:57-58`; `review_zero_v3.md`.

4. **The server-enforced concurrency lock is net-new code, not a port.** `phase-M.md:92-96`
   mandates the "no concurrent `daily_paper_pipeline`" guard move *into* the MCP server. No
   such guard exists anywhere today (oligo enforced it in the now-deleted agent loop's
   `concurrency_safe` partition). M.2 must write it; it is the one place the "thin adapter,
   minimal logic" rule is intentionally exceeded. Evidence: only internal locks at
   `daily_chimera_service.py:232,234`; red line `phase-M.md:92-96`.

5. **`pyproject.toml` declares only the scaffold deps; the domain runtime will not import.**
   The manifest lists `mcp/pydantic/pyyaml/httpx/ddgs` but the domain needs (at least) a
   Jinja2 prompt manager, an arXiv client, MinerU, and the OpenAI-compatible client's deps.
   M.1/M.2 must extend dependencies, and `chimera-dependency-veto` applies to each addition.
   Evidence: `pyproject.toml` deps vs `jinja_prompt_manager.py`, `arxiv_fetch.py`,
   `mineru_pipeline.py`, `openai_compatible_client.py`.

6. **Cleanliness of the new surface is already a PASS — the risk is entirely in the copied
   domain layer.** Both adapters are thin and DSL/SSE/loop-free (Q9). Every High-risk finding
   lives in the verbatim-copied `mcp-servers/chimera-papers/` tree, not in anything written
   for chimera-lite. This validates the "thin adapter" architecture and localizes the work.

---

## Audit complete

- 9 questions answered (all with file:line evidence)
- ~40 file:line references
- 4 cross-references
- 6 notable cross-findings
- Risk profile: 3 High (Q2, Q3, Q6), 4 Med (Q4, Q5, Q7, Q8), 2 Low (Q1, Q9)

**Headline:** The migration's hard part is not the MCP layer (already clean and thin) — it
is rehydrating the copied domain code's missing foundation (`config`/`schemas`/`naming`/
`platform`), deciding package-layout-vs-import-rewrite, and authoring two net-new pieces
(the BB persona text and the server concurrency lock). One real oligo coupling remains
(`daily_chimera_service.py:15`).

**Suggested next:** `batch_planning` for Phase M — and resolve cross-finding #1 (vendor
tree vs flat rewrite) and #2 (shared core-port prerequisite) before sequencing M.1/M.2.

---

*Generated by chimera-sprint-discipline phase_audit mode.*
