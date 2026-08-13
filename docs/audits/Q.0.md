# Phase Audit: Phase Q — Deterministic ARA Workflow

**Scope:** Read-only audit prerequisite for batch_planning of Phase Q (the Q.0 sprint).
**Output location:** `docs/audits/Q.0.md`
**Date:** 2026-07-09
**Mode:** Read-only w.r.t. source — no fix proposals, no code modifications. The one write is this report.
**Q-list source:** derived from the phase doc's sprint goals (Q.0–Q.4); Phase Q re-grounded on
`docs/audits/ara-2604.24658-structure.md` (correct ARA = Agent-Native Research Artifact).
**Evidence base:** three read-only scouts over `mcp-servers/chimera-papers`, `mcp-servers/chimera-vault`,
`docs/ARCHITECTURE`.

---

## Files read

| Path | Notes |
|---|---|
| `mcp-servers/chimera-papers/server.py` | `ingest_paper` tool + `_start_lock` |
| `mcp-servers/chimera-papers/miner_tools.py` | ingest delegate, task launch, `check_task_status` |
| `mcp-servers/chimera-papers/single_paper_ingest.py` | ingest orchestration (the substrate to extend) |
| `mcp-servers/chimera-papers/ports/ingest/mineru_pipeline.py`, `ports/ingest/paper2md.py` | MinerU PDF→md |
| `mcp-servers/chimera-papers/filter_service.py`, `ports/llm/openai_compatible_client.py`, `bootstrap.py` | the structured-LLM path |
| `mcp-servers/chimera-papers/ports/vault/vault_note_writer.py`, `prompts/obsidian_tpl/knowledge_node.j2` | K-node write + edge scaffold |
| `mcp-servers/chimera-papers/task_service.py` | poll model + `has_active_long_task` |
| `mcp-servers/chimera-papers/staging_service.py` | `create_staging_node` / `stage_link_patch` / `_TYPE_EDGES` |
| `mcp-servers/chimera-vault/server.py`, `vault_tools.py`, `vault_query.py`, `vault_read_adapter.py` | write tools + query/grounding tools |
| `docs/ARCHITECTURE/NODE_ONTOLOGY.md` | K/T/I/D edge vocabulary |
| `.claude/commands/`, `.claude/workflows/` | absent (net-new for Path B) |

---

## Findings

| Q# | Sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| Q0.1 | Q.0 | Do Path-B primitives (Workflow `pipeline()`/schema/model/isolation, MCP access) exist here, and is there a `/read` entry point? | Harness primitives exist, but **no `.claude/commands/` or `.claude/workflows/` exists** — the `/read` command and the Workflow script are **net-new** infrastructure, not an extension of anything present. | glob: `.claude/{commands,workflows}` → none | Med |
| Q0.2 | Q.0 | What is the `ingest_paper` substrate Q must extend? | `ingest_paper` → `ingest_single_paper`: fetch arXiv PDF → **MinerU** → `PaperLoader` → **one structured-LLM triage call** → `VaultNoteWriter.write_knowledge_node`. Synchronous; gated by `_start_lock`+`has_active_long_task`. | `server.py:85-108`, `single_paper_ingest.py:60-94` | Low |
| Q1.1 | Q.1 | What vault query tools exist for Grounding, and what do they return? | 6 tools (`obsidian_graph_query`, `vault_query`, `search_vault`, `search_vault_attribute`, `read_vault_file`) — **all return plain strings, no structured artifact channel.** Structured `list[dict]{title,path,type,links}` exists only *inside* `query_graph`, flattened to text before crossing MCP. | `vault_tools.py:3-7,75-113`, `vault_read_adapter.py:564-571` | Med |
| Q1.2 | Q.1 | How are seeds found, and what dirs are excluded? | `query_graph` seeds via **pure-Python `rglob`** (not rg), excluding **only `.obsidian`**; `vault_query` shells to `rg` with **no exclusions**. `_NONVAULT_DIRS` (`.obsidian`,`.migration_backup`,`templates`) is applied only in `resolve_note_path`, **not** in graph/seed scans. | `vault_read_adapter.py:25,420,491-524`, `vault_query.py:49-54` | **High** |
| Q2.1 | Q.2 | Is there a schema-constrained LLM path to reuse for ARA extraction? | **Yes — already built.** `FilterService.evaluate_paper` calls `llm_client.generate_structured_data(..., response_model=<Pydantic>)` (`response_format=json_object`, temp 0.01, 3-retry). An `ARA` response_model drops straight into this path. | `filter_service.py:26-49`, `openai_compatible_client.py:124-161` | Low |
| Q2.2 | Q.2 | Does the paper markdown already exist on disk (extraction reads a file, not re-converts)? | Yes. MinerU writes `output_root/<stem>/<stem>.md`; cleaned md lands in `pm.md_papers_dir`. Extraction reads the existing clean `.md`. | `paper2md.py:64-66`, `mineru_pipeline.py:120,128` | Low |
| Q3.1 | Q.3 | What is the orchestration substrate + entry point? | **Two candidates, and they conflict** — a Claude Code Workflow (B1, net-new) vs. extending the Python `ingest_single_paper` at `:90-92` (R1). See cross-finding #1. | `single_paper_ingest.py:90-92`; `.claude/` absent | **High** |
| Q3.2 | Q.3 | How does structured data pass between stages? | In a **Python** pipeline: in-process objects (trivial). In a **Workflow**: vault tools return strings, so a Grounding agent must digest text→schema itself; `agent(schema=…)` then yields validated JSON. | `vault_tools.py:3-7`; harness | Med |
| Q4.1 | Q.4 | What does `create_staging_node` accept, how are edges encoded, and where do files land? | `create_staging_node(type,title,body,edges)` → `docs/staging/{stamp}-{slug}.md`, `status: PENDING_REVIEW`; `edges` validated against `_TYPE_EDGES` and normalized to `[[stem]]` wikilinks in a `graph_edges` block. Never touches the live vault. | `staging_service.py:61-93,13-18`, `core/config.py:138` | Low |
| Q4.2 | Q.4 | Can it stage B3's `grounded: no_prior_match` + edgeless nodes? | **Edgeless: yes** (`edges` optional). **Custom frontmatter field: no** — `create_staging_node` emits a *fixed* frontmatter (`type,status,title,created_at,tags,graph_edges`); a `grounded:` field would need the body or a signature change. | `staging_service.py:80-92` | Med |
| Q4.3 | Q.4 | Does the substrate already write K-nodes, and via which path? | Yes — `ingest_paper` writes via **`VaultNoteWriter`** to the live **inbox** (`<Verdict>/…`, e.g. `Must_Read`), rendering `knowledge_node.j2` whose `graph_edges` scaffold is **hard-coded empty** and populated by no writer. This is a *different* write path than Phase-O's `StagingService` (staging→review). See cross-finding #4. | `vault_note_writer.py:31-45`, `knowledge_node.j2:14-17` | Med |

---

## Cross-references discovered

- **`StagingService` is owned by `chimera-papers`**, not `chimera-vault`; `chimera-vault` reaches it by putting the papers dir on `sys.path` (`chimera-vault/server.py:15-19`). So a Python ARA step *inside* `ingest_paper` can call `create_staging_node` **in-process** with no cross-server MCP hop. Precedent: `scripts/seed_hsc3.py:84`.
- **`_TYPE_EDGES` mirrors `NODE_ONTOLOGY.md`** (ratified 2026-07-07): K=`derives_from/supersedes/contradicts`; T=+`dead_ends/drives_decision`; I=`synthesizes/evidence_base/derives_from/drives_decision/…`; D=`derives_from/drives_decision/dead_ends/…`. Edge targets are `[[stem]]` wikilinks. Evidence: `staging_service.py:13-18`, `NODE_ONTOLOGY.md:42-57`.
- **Only one LLM role exists today** (triage), via a config-driven `OpenAICompatibleClient` with a `generate_structured_data(response_model=…)` method — the exact primitive ARA extraction needs. Evidence: `filter_service.py:26-49`, `openai_compatible_client.py:113-161`.

---

## Notable cross-findings (no fix proposals — flagging for batch_planning)

1. **B1 (Path B Workflow) and R1 (extend `ingest_paper`) name two different machines, and they are in tension.** This is the headline finding. B1 says orchestration is a Claude Code **Workflow** (`/read` → main agent → `pipeline(Grounding→Extraction)` → `create_node`). R1/C2 say **extend the existing `ingest_paper` Python pipeline**. But `ingest_paper` is a *server-side Python pipeline* (`single_paper_ingest.py:60-94`) that already owns MinerU, a **structured-output LLM path** (`generate_structured_data(response_model=…)`), an in-process `StagingService`, the TaskService poll model, and — because it is an MCP tool that returns a summary string — **total context isolation for free** (the main agent never sees the markdown; V1/HSC-2 satisfied trivially, arguably more cleanly than a fork). A Claude Code Workflow would **not** reuse that pipeline; it would re-orchestrate at the harness layer and would need an MCP surface for MinerU-only conversion that does not exist (the only MinerU entry today is `ingest_paper`, which also writes a node). **The evidence surfaces the conflict; the disposition is batch_planning's.** What each path reuses vs. adds: *Python-extension* reuses ~all of the above, zero new deps, no new command/ritual — but the "subagents" become Python functions, not Claude Code agents (contradicting B1's letter). *Workflow* honors B1's subagent-isolation model but contradicts R1 and duplicates MinerU orchestration. Evidence: `single_paper_ingest.py:60-94,90-92`, `filter_service.py:26-49`, `staging_service.py:61-93`, `.claude/{commands,workflows}` absent.

2. **The graph-seed exclusion gap directly threatens B3/HSC-1 edge integrity.** `query_graph` (the likely Grounding call) excludes only `.obsidian` from its seed scan — **not** `.migration_backup/` or `templates/` (`vault_read_adapter.py:496` vs the unused `_NONVAULT_DIRS` at `:25,420`). A Grounding step could therefore match a **backup or template node** and emit a `derives_from` edge to it — a fabricated-looking prior link, the exact failure mode B3 and `[[vault-graph-edges-empty]]` warn against. Any grounding built on these tools must add its own exclusion, or the "no fabrication" seal is porous. Evidence: `vault_read_adapter.py:25,420,491-524`, `vault_query.py:49-54`.

3. **`create_staging_node` cannot carry B3's `grounded: no_prior_match` field as written.** Its frontmatter is fixed (`staging_service.py:80-92`); there is no arbitrary-field passthrough. B3's explicit-no-match marker would have to live in the node body, or `create_staging_node` gains a param. A planning decision, flagged not fixed. Evidence: `staging_service.py:80-92`.

4. **Two K-node write paths coexist, and Q.4 must pick one.** `ingest_paper` writes via `VaultNoteWriter` **directly into the live inbox** (`<Verdict>/…`) with an *empty* `graph_edges` scaffold (`knowledge_node.j2:14-17`); Phase-O's `StagingService.create_staging_node` writes to **`docs/staging/` for review** (never auto-promote). B2/Q.4 assume the staging path, but the substrate ARA extends uses the inbox path. Whether ARA (a) redirects the K-node into staging, (b) adds staged T/I/D nodes alongside the inbox K-node, or (c) populates the inbox node's empty `graph_edges` in place — is unresolved and interacts with the "never auto-promote" red line. Evidence: `vault_note_writer.py:31-45`, `knowledge_node.j2:14-17`, `staging_service.py:61-93`.

5. **Q.2 (Extraction) is ~80% pre-built.** The schema-constrained extraction Q.2 calls for already exists as `generate_structured_data(response_model=…)` (temp 0.01, 3-retry). Q.2 largely reduces to authoring the ARA Pydantic schema (the four layers + the G1 functional flag vocabulary) and the extraction prompt — not building an LLM harness. Evidence: `filter_service.py:26-49`, `openai_compatible_client.py:124-161`.

6. **VISION-lens check (the spec's own governing test).** Cross-finding #1 has a simplicity/adoption dimension the VISION makes load-bearing: the Python-extension path adds ARA to an **existing single-call tool** (`ingest_paper`) with no new command to remember; the Workflow path adds a `/read` ritual + net-new orchestration infra. Against the VISION's "cut rituals / 80-20 / adoption > purity" tests, the two paths are not equal, and #1's resolution should be weighed on that axis, not only on architectural elegance. Evidence: VISION section (`phase-Q.md`), `.claude/` absent.

---

## Audit complete

- **11 questions answered**, all file:line-anchored.
- **3 cross-references**, **6 notable cross-findings** (2 High-risk: the B1↔R1 substrate tension and the seed-exclusion gap).
- No fixes proposed. The central decision — **Path B Workflow vs. Python-extension of `ingest_paper`** (cross-finding #1) — is the Architect's / batch_planning's to make, and it reshapes Q.1–Q.4.

**Suggested next:** resolve cross-finding #1 (substrate), then `batch_planning` for Phase Q.

---

*Generated by chimera-sprint-discipline phase_audit mode.*
