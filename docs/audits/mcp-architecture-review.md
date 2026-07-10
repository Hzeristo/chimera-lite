# MCP Architecture Review — SWE Briefing

**Type:** Technical briefing (no code changes). SWE-perspective review of the two MCP servers.
**Date:** 2026-07-09
**Files reviewed (full):** `mcp-servers/chimera-papers/server.py`, `mcp-servers/chimera-vault/server.py`,
`mcp-servers/chimera-papers/staging_service.py`, `mcp-servers/chimera-papers/ports/vault/vault_read_adapter.py`
(the vault server imports the last two from the sibling papers domain package via `sys.path`).
**Lens:** general SWE (SRP/ISP/contract/idempotency) + `chimera-mcp-taste` for the transport layer.

---

## Q1 — Single Responsibility

**Server-level responsibilities:**

| Server | Actual responsibilities | Verdict |
|---|---|---|
| **chimera-papers** (`server.py`) | Paper *acquisition + ingest*: `arxiv_miner` (mine), `daily_paper_pipeline` (batch), `ingest_paper` (single), `check_task_status` (poll). Plus the concurrency guard. | **Cohesive.** One domain (papers in). |
| **chimera-vault** (`server.py`) | *Two* jobs in one module: **(a) read/query** (`search_vault`, `search_vault_attribute`, `read_vault_file`, `obsidian_graph_query`, `vault_query` — 5 tools) and **(b) write/stage + one live mutation** (`create_node`, `link_nodes`, `apply_link_patch` — 3 tools). | **Mild SRP strain.** |

**Findings:**

1. **chimera-vault bundles read + staging-write + a live mutation.** `apply_link_patch` (`vault/server.py:203-221`) is the *only* tool that writes into the live vault; it sits beside five read tools and two staging-only writers. The read surface and the write surface are different responsibilities sharing a module. **Low severity** — they are cohesive as "vault access" and the module is a thin face — but a future split (`vault_read` vs `vault_write`) is defensible if the write surface grows (e.g. Phase Q).
2. **The two servers share ONE domain package, owned by chimera-papers.** `vault/server.py:15-19` injects `../chimera-papers` onto `sys.path` and imports `StagingService`, `VaultReadAdapter`, `core.config` from it. So the "vault" server cannot stand alone — its domain lives under "papers." SRP *of the domain code* is fine (single ownership), but the **coupling is structural and path-fragile** (import order, relative-path assumption). **Med severity** as a boundary smell; benign today.
3. **Thin-adapter (mcp-taste #9) — one real violation.** `link_nodes` (`vault/server.py:171-200`) is NOT pure delegation: it resolves both endpoints, **parses the FROM node's frontmatter YAML inline to derive `from_type`** (`:187`), then constructs the service. That endpoint-resolution + frontmatter-parse is domain logic living in the tool body. Contrast `create_node`/`apply_link_patch`, which are ~3-line dispatchers. The O.seal follow-up (move write bodies to `write_tools.py`) would fix this. `papers/server.py` is a clean thin adapter (123 lines); `vault/server.py` is 226 lines — the documented Accepted Partial `O.seal.1` (>200), driven by the 3 write-tool docstrings + the `link_nodes` inline logic. **Med.**
4. **The concurrency lock in `papers/server.py:30-55` is logic-in-adapter — but it's the sanctioned exception** (mcp-taste #9, documented at `server.py:5`). Not a violation.

---

## Q2 — Interface Segregation (>4 params / non-orthogonal inputs)

**No tool exceeds 4 parameters.** `create_node(type, title, body, edges)` sits exactly at 4 (`vault/server.py:126-132`). Parameter *count* is healthy across both servers.

**Non-orthogonal inputs — three flags:**

1. **`ingest_paper(arxiv_id=None, pdf_path=None)`** (`papers/server.py:85-86) — an implicit **XOR**: exactly one must be supplied, both default to `None`, and the "provide one" rule lives only in the docstring, not the type system. A caller can pass neither (→ runtime error) or both (ambiguous). **Med** — and Phase Q's proposed `mode='ara'` adds a third axis to this already-implicit contract; worth a typed discriminator if it grows.
2. **`vault_query(type=None, status=None, linked_to=None)`** (`vault/server.py:108-113`) — all optional, but **≥1 is required**, enforced at runtime (`vault_query.py:33-34` per the tool body), not in the signature. The signature says "all optional"; the real contract says "at least one." **Low.**
3. **`obsidian_graph_query(node_type=None, link_pattern=None, max_depth=2)`** (`vault/server.py:89-93`) — fully callable with *zero* filters, in which case every note becomes a seed (up to the internal `max_results=200`, `vault_read_adapter.py:484`). No required narrowing arg. **Low** — a large unfiltered dump is possible by design.

Otherwise inputs are orthogonal (`search_vault_attribute(key,value,top_k)` — key+value are inherently paired; fine).

---

## Q3 — Schema as an API contract (defined-but-not-enforced?)

**Headline: Pydantic is a real contract in exactly ONE place, and it is NOT the MCP boundary.**

- **The only enforced Pydantic contract is the LLM output path:** `FilterService.evaluate_paper` calls `generate_structured_data(..., response_model=PaperAnalysisResult)` (`filter_service.py:26-49`) — the model output is *validated* against a Pydantic schema. This is the correct pattern, and it is exactly what Phase Q's ARA extraction should reuse.
- **The MCP tool I/O uses plain type hints, not Pydantic**, so FastMCP derives a weak JSON schema and the *real* contract is enforced at runtime by hand:
  - **`create_node(type: str, ...)`** — `type` is typed `str`, but only `knowledge/thought/insight/decision` are legal; the check is a runtime `ValueError` inside `create_staging_node` (`staging_service.py:69`). A `Literal[...]` would make it boundary-checkable. **Contract defined in prose + runtime, not in schema.**
  - **`create_node(edges: dict | None)`** — `dict` is *untyped*. The real contract (keys must be valid edges for the node type; values are lists of stems) is enforced only at runtime (`staging_service.py:72-79`, raises on unknown key). A caller/LLM sees `dict` and learns the constraints by failing. **The schema is strictly weaker than the contract.** **Med.**
  - Same shape for `obsidian_graph_query(node_type: str)` and `vault_query(type/status)` — valid values are docstring + runtime, not schema.
- **Return contract: there is none.** All ten tools return `str` (`vault/server.py` and `papers/server.py` throughout; `vault_read_adapter.query_graph` produces `list[dict]` internally but it is flattened to text before crossing the boundary). Outputs are unschematized free text. For an LLM consumer this is acceptable; from an API-contract view it means **no machine-checkable output schema and no versioning** — a real constraint for Phase Q, which wants structured ARA output (it will need either a genuine return schema or an explicit "summary-string" convention).

**Bottom line:** the servers lean on *docstrings + runtime validation* as the contract, not the schema. This is a deliberate thin-adapter trade-off, but it means several tools have contracts that are **documented and runtime-enforced but not schema-enforced** — errors surface late (at call time) rather than at the boundary.

---

## Q4 — Transport correctness (stdio blocking) — the mcp-taste heartland

**Overall: correct, and notably disciplined.** The classic stdio failure modes are handled:

1. **Long-running work uses the poll model, not a blocking call.** `arxiv_miner` / `daily_paper_pipeline` return a `task_id` immediately (fire-and-forget `asyncio.create_task` in `miner_tools`), so the tool call does not block. ✓ (`papers/server.py:42-82`).
2. **Blocking CPU/IO is offloaded off the event loop.** `ingest_paper`'s heavy work runs via `asyncio.to_thread` (`miner_tools.py:89-116`); the vault scans run via `asyncio.to_thread(_ripper_sync / _attribute_search_sync / _query_graph_sync)` (`vault_read_adapter.py:430,441,595`); `vault_query` uses async `create_subprocess_exec("rg", …)` with a 10s timeout. So full-vault `rglob` scans and MinerU do **not** freeze stdio. ✓
3. **Logging goes to stderr, never stdout.** Both servers set `logging.basicConfig(stream=sys.stderr, …)` with explicit "stdout is the JSON-RPC channel" comments (`papers/server.py:19-26`, `vault/server.py:28-33`). mcp-taste #4 satisfied. ✓
4. **The MinerU console child is spawned headless with its output sunk.** `paper2md.py:106-114` — `subprocess.run(..., stdin=DEVNULL, stdout=<temp logfile>, stderr=STDOUT, creationflags=CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP)`. This is mcp-taste #4 (child output sink — NOT `capture_output`, NOT the server's stdout) and #5 (headless spawn) done correctly. ✓

**The one flag (Med):** **`ingest_paper` is a *synchronous, long* tool with no progress and no `task_id`** (`papers/server.py:85-108`). It does not corrupt stdio (the work is on a worker thread), but the client holds one open tool call for up to the MinerU `timeout=600` plus the LLM call, with zero progress. Phase Q's `mode='ara'` **extends** that synchronous window (an extra structured-LLM extraction call). Against the VISION's "I can trust it to work," a multi-minute silent call is adoption-hostile — Q should decide whether ARA-mode ingest moves to the `task_id` poll model (like the batch tools) or stays synchronous with a tighter budget. *(Note: verifying the loop truly stays free during a live ingest is a one-command check — poll `check_task_status`/another tool mid-convert — per mcp-taste's verification-first rule; the code path says it should.)*

---

## Q5 — Idempotency (duplicate side effects on retry)

**The exemplar first:** **`apply_link_patch` is idempotent by design** (`staging_service.py:166-210`). If the edge is already present it is a no-op and the node stays byte-identical (`:202-205`); it consumes the patch on apply, so re-applying the same patch path fails cleanly (`FileNotFoundError`) rather than duplicating. This is the model the other writers do not follow.

**Non-idempotent tools (flags):**

1. **`create_node` — NOT idempotent.** The staging filename is timestamped `{YYYYMMDD_HHMMSS}-{slug}.md` (`staging_service.py:88-90`). Two identical calls → **two staging files.** **Med** — mitigated by the staging→review gate (the user sees and rejects the dup), but at the tool level a retry duplicates.
2. **`link_nodes` — NOT idempotent at creation.** Timestamped patch filename (`staging_service.py:151-153`) → retry makes a **second patch**. The downstream `apply_link_patch` *is* idempotent, so the end state converges, but the staging area accumulates duplicate patches. **Low.**
3. **`ingest_paper` — NOT idempotent, with an orphaning hazard.** The K-node is written by `VaultNoteWriter` into a **verdict-subfoldered** path `<inbox>/<Verdict>/<basename>.md` (`vault_note_writer.py:31-45`). The verdict comes from a non-deterministic LLM triage (`FilterService`, temp 0.01). A retry that yields a *different* verdict (e.g. `Must_Read` → `Skim`) writes a **new node in the new subfolder and leaves the old node orphaned in the old one** — a genuine duplicate side effect, not just an overwrite. **Med** — relevant to Phase Q, which routes ARA output through staging (review-gated), partially side-stepping this.
4. **`arxiv_miner` / `daily_paper_pipeline` — partially idempotent.** Re-running re-fetches/re-ingests; the arXiv fetch skips if the PDF is already present and the batch path has a seen-filter, but single ingest bypasses the seen-filter. The concurrency lock (`has_active_long_task`) prevents *concurrent* duplicates, not *sequential* re-runs. **Low.**
5. **`check_task_status` — idempotent** (read-only). ✓

---

## Summary

| # | Finding | Location | Severity |
|---|---|---|---|
| Q1 | `link_nodes` carries domain logic inline (frontmatter parse, type resolution) — thin-adapter violation | `vault/server.py:171-200` | Med |
| Q1 | vault server bundles read + staging-write + live mutation; depends on papers' domain via `sys.path` | `vault/server.py:15-19,203-221` | Med/Low |
| Q2 | `ingest_paper` arxiv_id⊕pdf_path is an untyped XOR; `mode='ara'` will widen it | `papers/server.py:85-86` | Med |
| Q3 | MCP I/O contracts are type-hint + runtime, not schema-enforced (`type: str`, `edges: dict`, `str` returns) | `vault/server.py:126-132`; `staging_service.py:69-79` | Med |
| Q3 | Pydantic-as-contract exists only on the LLM output path (the model Phase Q should reuse) | `filter_service.py:26-49` | (good) |
| Q4 | `ingest_paper` is a long synchronous tool (no task_id/progress); `mode='ara'` extends it | `papers/server.py:85-108` | Med |
| Q4 | poll model, `to_thread`, stderr logging, headless MinerU spawn + output sink all correct | multiple | (good) |
| Q5 | `create_node` / `link_nodes` duplicate staged files on retry (timestamped names) | `staging_service.py:88-90,151-153` | Med/Low |
| Q5 | `ingest_paper` retry can orphan a node in a stale verdict subfolder (non-deterministic verdict) | `vault_note_writer.py:31-45` | Med |
| Q5 | `apply_link_patch` is the idempotency exemplar | `staging_service.py:202-205` | (good) |

**Coaching takeaway:** the *transport seam* is handled with real discipline (poll model, `to_thread`, stderr, headless spawn) — the hard mcp-taste bugs are absent. The softer weaknesses are **contract strength** (schema weaker than the real runtime rules; string-only returns) and **idempotency of the write path** (timestamped filenames duplicate on retry; `ingest_paper`'s verdict-routing can orphan). Both are directly relevant to Phase Q: it should reuse the enforced-Pydantic LLM path (Q3-good) and route through the idempotent, review-gated staging surface rather than the verdict-subfoldered inbox writer.

---

*Technical briefing — no code modified.*
