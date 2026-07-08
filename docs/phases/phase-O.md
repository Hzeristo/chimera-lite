# Phase O — Exocortex Write Surface

**Status:** ✅ Sealed 2026-07-08 (`docs/sprints/phase-O/phase-review.md`) — HSC 1/2/3 all pass; unblocks Phase N.B
**Sealed predecessor:** Phase N.A
**Driving frictions:**
- N.B.0 audit revealed vault typed-edge graph is empty
- No tools to create T/I/D nodes or fill derives_from/synthesizes edges
- PaperMiner only writes K Nodes; T/I/D are manual → no workflow support

## Mission

Complete the exocortex write surface: tools for creating T/I/D nodes,
filling typed edges, and integrating with Obsidian for vault maintenance.
Unblocks Phase N.B (deep_recall over typed-edge graph).

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| O.0 | Audit: what write operations exist (PaperMiner K Node creation), what's missing (T/I/D + typed-edge填充), Obsidian MCP capabilities |
| O.1 | create_node(type, title, body, edges) → writes K/T/I/D with frontmatter + typed edges |
| O.2 | link_nodes(from, to, edge_type) → adds derives_from/synthesizes/contradicts to existing nodes |
| O.3 | Obsidian MCP integration: if market MCP exists, adapt; else minimal file-write tool |

## Hard Sealing Conditions

1. create_node can write all 4 types (K/T/I/D) with typed edges in frontmatter
2. link_nodes can add derives_from/synthesizes edges to existing nodes
3. After O.3, manually create 5 T Nodes + 10 typed edges → vault probe
   confirms ≥ 20 nodes with typed edges (N.B unblock threshold)

## Design Decisions

- Thin adapter: tools write markdown files, don't embed Obsidian
- Use Obsidian MCP if available(market); else plain file-write
- Frontmatter format = Phase V.A K/T/I/D schema(already defined)
- create_node returns staging path (user reviews before moving to vault)

## O.3 Resolution (2026-07-07)

Obsidian-MCP integration → **Option C (self-build)**, per the market survey
`docs/audits/obsidian-mcp-necessity.md` (12 candidates, 0 pass; all app-dependent or thick
foreign runtimes, none K/T/I/D-aware). No market MCP adopted, no new dependency — the write
surface IS the O.1b/O.2 tools over `StagingService`. `chimera-dependency-veto` recorded.
Remaining O.3 work: the HSC-3 seal seed (`scripts/seed_hsc3.py`).

## Out of Scope

- Auto-linking (AI infers edges): the AUTONOMOUS BULK version (scan ~250 papers, invent a graph)
  stays deferred. But `friction-260708-01` carved out the user-triggered / single-node / review-gated /
  prose-grounded version, now scoped as **Phase P — Prose-Grounded Edge Inference** (`docs/phases/phase-P.md`).
- Graph visualization — Obsidian plugin territory
- Bulk backfill (filling edges for 250 existing K Nodes) — user work after O.3
