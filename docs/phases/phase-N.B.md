# Phase N.B — JIT Deep Recall

**Status:** Active (after N.A sealed)
**Sealed predecessor:** Phase N.A
**Driving frictions:**
- vault_query 是关键词匹配:模糊 query("那篇 memory 的")找不到
- 复杂多跳 query 需要 5+ 工具调用:慢 + context膨胀
- K/T/I/D 图结构没被利用:derives_from / synthesizes 边没有被遍历

## Mission

Add deep_recall(query, depth=2) to chimera-vault MCP server:
a BFS traversal of the K/T/I/D graph, starting from ripgrep-matched seed nodes,
returning a structured subgraph that Claude synthesizes natively.

NOT: a JIT agentic loop inside the MCP server.
YES: a pre-fetch tool that respects the thin-adapter principle.

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| N.B.0 | Audit: existing vault graph traversal (obsidian_graph_query BFS), ripgrep seed-finding, K/T/I/D typed-edge schema, what BFS depth is realistic on current vault size |
| N.B.1 | deep_recall(query, depth=2, max_nodes=20) → structured subgraph; BFS over derives_from/synthesizes/contradicts edges |
| N.B.2 | Verify: complex3-hop query returns relevant nodes + Claude synthesizes from subgraph (not from raw vault_query keyword match) |

## Hard Sealing Conditions

1. deep_recall on "memory decay graph-based deletion" returns K/T/I nodesspanning at least 2 hop depths (not just direct keyword matches)
2. Result subgraph ≤ 20 nodes (bounded; not unbounded BFS)
3. Claude synthesizes a coherent multi-hop answer from the subgraph
   without additional vault calls

## Design Decisions

- Option B: thin adapter (BFS + return subgraph), NOT mini agentic loop
- No vector store / No embeddings — pure graph + ripgrep
- max_depth=2 default, max_nodes=20 cap (prevents graph explosion)
- Edge types to traverse: derives_from, synthesizes, contradicts, dead_ends(typed edges from Phase V.A K/T/I/D schema — already in frontmatter)
- Seed selection: ripgrep frontmatter + body match (same as vault_query)
- Return format: list of {node_id, type, title, excerpt, edge_from, hops}

## Out of Scope

- Ranking/scoring (return all, let Claude rank)
- Semantic similarity (no embeddings)
- Graph random walk / PPR (Phase O+ if ever)
