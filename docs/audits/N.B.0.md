# Phase Audit: Phase N.B — JIT Deep Recall

**Scope:** Read-only audit prerequisite for `batch_planning` of Phase N.B (add
`deep_recall(query, depth=2, max_nodes=20)` to `chimera-vault`: a BFS over the K/T/I/D
typed-edge graph from ripgrep-matched seeds, returning a bounded structured subgraph).
**Output location:** `docs/audits/N.B.0.md` (named for the N.B.0 sprint that authors it).
**Date:** 2026-07-07
**Mode:** Read-only w.r.t. source — no fix proposals, no code changes. The one write is this report.
**Q-list:** approved by user (2026-07-07). Q4 upgraded by user to a **hard empirical gate**:
count live nodes with non-empty typed edges; if < 20, document that `deep_recall` over typed
edges is PREMATURE. Vault probed directly via ripgrep over the MCP-sanctioned vault root
(`D:\MAS\project_chimera_vault`); no code-scan scouts fanned out — the in-scope code surface
(5 files) was small enough to read in full, and the decisive question (Q4) is a live-data probe,
not a repo pattern scan.

---

## Files read

| Path | Lines | Notes |
|---|---|---|
| `docs/phases/phase-N.B.md` | 1–48 | full — mission, 3 sprints, 3 sealing conditions, design decisions, out-of-scope |
| `mcp-servers/chimera-vault/server.py` | 1–126 | full — thin adapter (126 lines ✅), 5 `@mcp.tool`, `obsidian_graph_query` + `vault_query` contracts |
| `mcp-servers/chimera-vault/vault_tools.py` | 1–114 | full — tool bodies, **string-only return contract**, `_format_graph_rows` |
| `mcp-servers/chimera-vault/vault_query.py` | 1–83 | full — ripgrep seed, `graph_edges` `linked_to` substring match |
| `mcp-servers/chimera-papers/ports/vault/vault_read_adapter.py` | 1–570 | full — the real BFS: `_query_graph_sync`, `_collect_graph_links`, `_graph_edge_targets_from_frontmatter` |
| `mcp-servers/chimera-papers/ports/vault/vault_note_writer.py` | 1–75 | full — `write_knowledge_node` / `write_deep_read_node` → `*.j2` templates (the write path) |
| `docs/FINAL_CONTRACT/V.A-final-contract.md` | 1–85 | full — K/T/I/D schema authority, `NODE_ONTOLOGY.md` reference, no-embeddings out-of-scope |
| `<vault>/templates/Tpl_knowledge.md` | 1–46 | full — `graph_edges: {derives_from, supersedes, contradicts}` (all empty) |
| `<vault>/templates/Tpl_{thought,insight,decision}.md` | grep | edge vocabulary (scattered per node type) |
| `<vault>/inbox/Must_Read/2602.02474v1-MemSkill.md` | 1–78 | full — a live pipeline-written knowledge node: **no `graph_edges` block** |
| `<vault>/Insight/Dynamic empirical study on agent memory.md` | grep | live insight node — all edge lists empty |
| `<vault>/Thoughts/Thought-memory bench-*.md` (×3) | grep | body-prose "Triggered By" cross-links (only real edges found) |
| live vault probe | — | type distribution (~250+ knowledge, 3 thought, 1–3 insight, 0 decision); edge-population count |

---

## Findings

| Q# | Driving sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| Q1 | N.B.1 | Does `obsidian_graph_query` traverse **typed** edges or only wikilinks? Is the BFS core reusable? | It ALREADY does BFS over **both** body wikilinks **and** `graph_edges` frontmatter — but **type-blind**: `_graph_edge_targets_from_frontmatter` flattens *all* `graph_edges` sub-keys regardless of edge type. The frontier BFS, stem resolution, and result cap are directly reusable; `deep_recall`'s delta is type-filtering + query-seed + structured output. | `vault_read_adapter.py:39-55, 430-440, 442-544` (frontier `:502-526`); `server.py:87-103` | Low |
| Q2 | N.B.1 | Is `vault_query`'s ripgrep seed reusable as `deep_recall`'s seed step? | Partially. `vault_query`'s `rg` patterns are **frontmatter-line-anchored** (`^type:`, `^status:`, or raw `linked_to`) — not the fuzzy keyword/body seed the friction names ("那篇 memory 的"). The adapter seeds instead by Python substring (`link_pattern in norm`) or token scoring (`_ripper_sync`), not ripgrep. A keyword-seed primitive exists (`_ripper_sync`) but is not wired to graph traversal. | `vault_query.py:42-55`; `vault_read_adapter.py:219-259, 484-496` | Med |
| Q3 | N.B.0/N.B.1 | Exact K/T/I/D typed-edge schema + parse path? | Canonical `docs/ARCHITECTURE/NODE_ONTOLOGY.md` (V.A's authoritative edge table) is **referenced but ABSENT from this repo** — never carried into the migration. De-facto schema = user-synced `Tpl_*.md`, and it **drifts**: `contradicts` only in `Tpl_knowledge`; `dead_ends` only in `Tpl_decision`; the live insight node uses `supported_by`/`supersedes` not in its own template. `graph_edges` is a dict-of-lists parsed via `yaml.safe_load` + flatten. The spec's 4 edges all exist in vocabulary but are split across node types. | `V.A-final-contract.md:14`; Glob `NODE_ONTOLOGY*` → none; `Tpl_knowledge.md:15-18`; `vault_read_adapter.py:39-55` | Med |
| **Q4** | N.B.0/N.B.2 | **⚠️ GATE: do typed inter-node edges actually exist in the live vault?** | **NO. Zero live nodes have populated typed `graph_edges`.** Every `graph_edges` block in a live (non-backup, non-template) node is `[]` or an unfilled `{{PLACEHOLDER}}`. The ~250+ pipeline-written knowledge nodes carry **no `graph_edges` block at all** — only a `[[…pdf]]` self-link + an unfilled `[[Thought/ ...]]` body placeholder. Real cross-node links exist ONLY as **body prose in ~5 nodes** (3 Thought "Triggered By: [[…Deep_Read]]" + 2 Meta-theory "Related Notes:"). **Nodes with non-empty typed edges: 0. Nodes with any cross-node link: ~5. Both < 20.** Per the user's honest gate → `deep_recall` over typed edges is **PREMATURE; the vault must grow its graph first.** | `graph_edges` grep (63 occ/32 files, all `[]`/`{{…}}`); `2602.02474v1-MemSkill.md:16,75`; `Tpl_knowledge.md:15-18`; `Insight/Dynamic…:15-19`; `Thought-memory bench-mix arch.md:89`, `…implementation pitfalls.md:34` | **High** |
| Q5 | N.B.1 | Where should `deep_recall` live for thin-adapter compliance? | Clear precedent: BFS domain logic → new `VaultReadAdapter` method (beside `query_graph`); formatting → new `vault_tools` body (beside `obsidian_graph_query`); thin `@mcp.tool` in `server.py` delegating after `_ensure_adapter()`. No agentic loop in the server — honored by keeping BFS in the adapter. `server.py` is 126 lines (thin ✅). | `server.py:38-48, 87-103`; `vault_tools.py:104-113`; `vault_read_adapter.py:546-569` | Low |
| Q6 | N.B.1 | Return schema — structured `list[dict]` or string only? | MCP boundary for vault tools is **string-only** (docstring: "the MCP layer has no structured ToolOutput/artifact channel, so the adapter's formatted text is the contract"). `query_graph` returns `list[dict]` internally; `obsidian_graph_query` renders it to a string via `_format_graph_rows`. So the spec'd `{node_id, type, title, excerpt, edge_from, hops}` list is the **adapter's** internal return, formatted to a string at the tool body. (The papers server *does* have a `ToolOutput`/`Artifact` channel — V.A.2b — but that is the long-task path, not the vault tools.) | `vault_tools.py:1-8, 75-101`; `vault_read_adapter.py:528-544`; `V.A-final-contract.md:23-28` | Low |
| Q7 | N.B.0 | Is `depth=2` + `max_nodes=20` realistic on the current vault? | Vault ≈ **250+ typed knowledge** nodes, **3 thought**, **1–3 insight**, **0 decision**. Existing BFS caps `max_results=200`, `max_depth` clamp 1–8. But because edges are empty (Q4), depth-2 from any seed expands to ~nothing beyond the seeds — the 20-node cap **never binds**; result size ≈ number of ripgrep seeds. Params are safe but **moot until the graph is populated**. Branching factor today ≈ 0 (typed) / near-0 (body-prose). | type-distribution grep (~250 knowledge); `vault_read_adapter.py:453, 456, 502-526`; Q4 | Med |
| Q8 | all | Is `deep_recall` genuinely distinct from `obsidian_graph_query` + `vault_query` (CLAUDE.md tool-invention rule)? | `deep_recall` appears only in phase docs (no pre-existing code) → net-new. Genuine deltas over `query_graph`: (a) fuzzy **query-keyword** seed vs `node_type`/`link_pattern`; (b) **typed** edge filter vs flatten-all; (c) structured records with **`edge_from` provenance + hop depth** (current BFS drops both). Real but **incremental** — overlap with `obsidian_graph_query` is high. The 3 frictions justify graph-aware recall, but the honest reading is this may be better shaped as an **enhancement to `obsidian_graph_query`** (add typed-filter + query-seed + `edge_from`/`hops`) than a near-duplicate parallel tool. | Grep `deep_recall` → `ROADMAP.md` + `phase-N.B.md` only; `vault_read_adapter.py:442-544`; `CLAUDE.md` hard rules; `phase-N.B.md:6-8` | Med |

---

## Cross-references discovered

- **The BFS `deep_recall` needs is ~80% already built** inside `VaultReadAdapter._query_graph_sync`
  (`vault_read_adapter.py:442-544`): frontier expansion, stem→path resolution, `graph_edges` +
  wikilink harvesting, `max_results` cap. It is type-blind and string-returning; that is the gap.
- **`graph_edges` is consumed in two places** — read: `_graph_edge_targets_from_frontmatter`
  (`vault_read_adapter.py:39-55`); query-filter: `vault_query` `linked_to` substring
  (`vault_query.py:74`). Neither distinguishes edge *type*.
- **V.A already fenced the out-of-scope** `deep_recall` inherits: no embeddings / vector / PPR /
  random-walk (`V.A-final-contract.md:79`), which `phase-N.B.md:44-47` re-affirms. No conflict.

---

## Notable cross-findings (no fix proposals — flagging for planning)

1. **⚠️ THE PHASE PREMISE FAILS THE Q4 GATE.** `deep_recall` is specified to traverse typed
   K/T/I/D edges (`derives_from` / `synthesizes` / `contradicts` / `dead_ends`) that **do not exist
   in the live vault**: 0 populated `graph_edges`, ~5 body-prose cross-links, all < 20. Per the
   user's explicit honest gate, **`deep_recall` over typed edges is PREMATURE.** Two evidence-based
   paths for the user to choose between: **(A) defer N.B.1** until a graph-population effort backfills
   typed edges; **(B) rescope N.B.1** to traverse the only real edges that exist today — **body
   wikilinks** ("Triggered By" / "Related Notes" prose + `[[…Deep_Read]]` links), which
   `_collect_graph_links` already harvests — treating typed-edge filtering as a forward-compatible
   enhancement. Evidence: `phase-N.B.md:12-17,39`; Q4 evidence rows; `vault_read_adapter.py:430-440`.

2. **Root cause is the WRITE path, not the read path.** The graph is empty because pipeline node
   templates (`knowledge_node.j2` / `deep_read_node.j2`, rendered by `vault_note_writer.py:34,59`)
   emit no typed `graph_edges` and leave `[[Thought/ ...]]` unfilled. Only hand-authoring via
   `Tpl_*.md` or `StagingService.create_staging_node(..., edges?)` can populate edges — neither is
   routine. Any "grow the graph" effort is a **papers-pipeline + vault-template** concern, outside
   `chimera-vault`'s read surface. Evidence: `vault_note_writer.py:31-74`; `2602.02474v1-MemSkill.md:75`.

3. **Schema-authority doc missing + vocabulary drift.** `NODE_ONTOLOGY.md` (V.A's authoritative
   edge-name table) never made the migration into this repo, and the de-facto schema (`Tpl_*.md`)
   drifts — edges split across node types, live insight node diverges from its template, and the
   spec's `contradicts`/`dead_ends` are rare-to-absent. A canonical edge set must be fixed before
   N.B.1 hardcodes traversal keys. Evidence: `V.A-final-contract.md:14`; Glob `NODE_ONTOLOGY*` → none;
   `Tpl_knowledge.md:15-18` vs `Insight/Dynamic…:15-19`.

4. **High overlap argues enhancement over new tool.** With the BFS core already in `query_graph`
   and CLAUDE.md forbidding tool invention without a clear friction delta, batch planning should
   explicitly decide *enhance `obsidian_graph_query`* vs *new `deep_recall`* (ties Q8 → cross-finding 1).
   Evidence: `vault_read_adapter.py:442-544`; `CLAUDE.md` hard rules; `server.py:87-103`.

5. **The `.migration_backup/` tree pollutes naive edge greps** — it contains template copies with
   `{{REFERENCE_PAPER_OR_KNOWLEDGE}}` placeholders. The Q4 count excludes it and `templates/`.
   Evidence: `graph_edges` grep hits under `.migration_backup/20260615_173311/`.

---

## Audit complete

- 8 questions answered (Q4 = user's hard empirical gate)
- ~35 `file:line` references
- 3 cross-references
- 5 notable cross-findings

**Suggested next — NOT an automatic go to `batch_planning`.** The Q4 gate is a **stop-and-decide**:
the typed-edge premise as written cannot be satisfied by the current vault. Recommend the user choose
between **(A)** defer N.B.1 behind a graph-population effort (write-path work, cross-finding 2), or
**(B)** rescope N.B.1 to body-wikilink recall now + typed filtering as forward-compat (cross-finding 1),
and resolve the enhance-vs-new-tool question (cross-finding 4) and canonical edge set (cross-finding 3)
before any sprint is planned.

---

*Generated by chimera-sprint-discipline phase_audit mode.*
