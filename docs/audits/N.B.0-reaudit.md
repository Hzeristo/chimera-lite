# Phase Re-Audit: Phase N.B — JIT Deep Recall (re-run after Phase O seal)

**Scope:** Re-run of the state-dependent questions from `docs/audits/N.B.0.md` (2026-07-07), now that
Phase O sealed and grew the vault typed-edge graph. Read-only; the one write is this report.
**Output location:** `docs/audits/N.B.0-reaudit.md`
**Date:** 2026-07-08
**Q-list:** approved by user (2026-07-08). Re-run **RE-Q4** (the gate), **RE-Q8** (deep_recall vs
`obsidian_graph_query` on the live graph), **RE-Q3** (schema authority, now that `NODE_ONTOLOGY.md`
exists), **RE-Q7** (realistic depth). **Carried unchanged** from N.B.0 (code-facts, not re-run): Q1
(BFS core reusable, type-blind), Q2 (ripgrep seed partial fit), Q5 (adapter-method home), Q6 (string-only
MCP return).
**Method:** live-graph probe over the MCP-sanctioned vault root (excluding `.migration_backup/` +
`templates/`) + `VaultReadAdapter.query_graph` run on real seeds; traversal code read in full at N.B.0.

---

## Probes run

| Probe | What |
|---|---|
| graph-shape probe (scratchpad) | adjacency, shared-target count, BFS max depth (directed / +body / undirected) from every typed source; edge-key histogram |
| `query_graph(node_type='thought', depth=2)` | 24 rows |
| `query_graph(link_pattern='MemOS', depth=2)` | 10 rows |
| `query_graph(link_pattern='trajectory', depth=2)` | 67 rows |
| `docs/ARCHITECTURE/NODE_ONTOLOGY.md` exists | True (O.1a, `dac1629`) |

---

## Findings

| Q# | Question | Answer (2026-07-08) | Evidence | Risk |
|---|---|---|---|---|
| **RE-Q4** | **GATE re-measured: does the graph now support HSC 1 (≥ 2 hop depths)?** | **Count gate MET, structural gate NOT.** Participation is 20 (5 typed **sources**, all thoughts; 15 **targets**, all papers). But the typed graph is **5 disjoint 1-hop stars**: every thought `derives_from` its own papers, the papers are empty-edge **leaves**, and **0 papers are shared between thoughts**. Directional BFS depth from every thought = **1**; adding body wikilinks does not deepen it (`+body-dir` also = 1). So HSC 1's "≥ 2 hop depths" is **unreachable directionally**. The only path to depth 2 is **undirected, from a *paper* seed** (paper → its thought → the thought's *other* papers), which needs bidirectional BFS (the current traversal is outgoing-only) and paper-seeding. The graph grew **wide, not deep**. | shape probe: 5 sources / 15 targets / 20 participation / **0 shared** / max dir depth **1**, max undirected **2**; `phase-N.B.md:29` (HSC 1) | **High** |
| **RE-Q7** | Realistic depth / subgraph size on the populated graph? | Typed-directed reach from any seed = **hop 1 only** (a thought's 2–7 papers; papers reach nothing). The `max_nodes=20` cap never binds — the largest typed neighborhood is DR6's 6. `depth=2` over typed edges returns **nothing beyond depth 1**. Params remain safe but the *depth* they guard is not exercised by the current graph. | shape probe (per-seed n=2..7, DR6 largest); `vault_read_adapter.py:453,456` | Med |
| **RE-Q3** | Schema authority — resolved now that O.1a authored `NODE_ONTOLOGY.md`? | **Authority gap CLOSED** — `docs/ARCHITECTURE/NODE_ONTOLOGY.md` is the ratified K/T/I/D edge vocabulary (O.1a). But the live graph populates **only `derives_from`** (5 edges); `synthesizes` / `contradicts` / `dead_ends` / `drives_decision` are unused. So N.B.0's "absent authority + Tpl drift" is fixed, yet **typed-edge *filtering* has effectively one type to filter** today. | `NODE_ONTOLOGY.md` exists; edge-key histogram = `{derives_from: 5}` | Low |
| **RE-Q8** | Does `deep_recall` add anything over `obsidian_graph_query` on the LIVE graph? | **Overlap is even higher than N.B.0 estimated; the honest shape is an *enhancement*, not a new tool.** `query_graph` already does keyword-seeded (`link_pattern`) BFS over `graph_edges` **and** body wikilinks — it returned 24 / 10 / 67 rows on live seeds. `deep_recall`'s three claimed deltas shrink on this graph: (a) **typed filter** — marginal, one type is populated (mostly it would *de-noise* body-wikilink junk like `[[Pasted image…]]`); (b) **query-keyword seed** — already exists (`link_pattern` is a substring seed); (c) **`edge_from` / hop provenance** — genuine (the rows carry `{title, path, type, links}`, no hops/edge). And `deep_recall`'s reason for being — deep *typed* multi-hop — has **nothing to traverse** (RE-Q4). Its incremental value = typed-filter + provenance + optional bidirectional, all cleanly addable to `obsidian_graph_query`. | `query_graph` rows (keys `{links,path,title,type}`, no hops); N.B.0 Q8; `vault_read_adapter.py:458-461, 502-544` | Med |

**Carried from N.B.0 (code unchanged):** Q1 — the frontier BFS in `_query_graph_sync` is directly reusable, type-blind (`vault_read_adapter.py:442-544`). Q5 — thin-adapter home is a `VaultReadAdapter` method + `vault_tools` body + thin `@mcp.tool`. Q6 — vault-tool MCP return is string-only.

---

## Cross-findings (flagging for the user's disposition; no fix proposals)

1. **The Q4 count-gate was necessary but NOT sufficient.** "≥ 20 nodes with typed edges" (the gate that
   deferred N.B) is now met, but it measured *width* (participation), while HSC 1 requires *depth*
   (≥ 2 hops). The live graph is 5 disjoint 1-hop stars with 0 shared papers, so a typed multi-hop
   traversal still reaches nothing at depth 2. Unblocking-by-count did not deliver a deep graph.

2. **The only 2-hop structure that exists is "papers co-cited by one thought"** (paper → thought →
   sibling papers), reachable only with *bidirectional* BFS from a *paper* seed. Whether that shallow
   co-citation relation is the "multi-hop recall" the phase wanted is a judgment call — it is not the
   `derives_from → derives_from` chain the spec implies.

3. **`deep_recall` reads honestly as an enhancement to `obsidian_graph_query`, not a new tool** — its
   real deltas (typed-filter, `edge_from`/hops provenance, optional bidirectional) are additive params
   on the existing keyword-seeded BFS. This confirms N.B.0's Q8 lean on a now-populated graph, and
   engages the CLAUDE.md tool-invention rule.

4. **Only `derives_from` is exercised.** The typed graph is single-relation today; `synthesizes` /
   `contradicts` etc. are defined (NODE_ONTOLOGY.md) but unused. Multi-*type* recall has no data yet.

---

## Re-audit complete — stop-and-decide (the disposition is the Architect's)

The gate that deferred N.B is cleared **on count**, but the re-measure shows the typed graph is
**wide-and-shallow** (depth 1), so N.B.1's typed multi-hop `deep_recall` still lacks a deep graph to
traverse, and its value collapses toward an enhancement of `obsidian_graph_query`. Evidence-based
options for you to choose between (I am not deciding this):

- **(A) Rescope N.B.1 as an enhancement** — add typed-filter + `edge_from`/hops provenance (+ optional
  bidirectional, which is what unlocks the co-citation 2-hop) to `obsidian_graph_query`, rather than a
  near-duplicate `deep_recall` tool. Ships value on today's graph; honors the tool-invention rule.
- **(B) Deepen the graph first** — HSC 1's ≥ 2 typed hops need interconnection (shared references,
  cross-thought / paper→paper edges, or dense edge-filling). That is write-path work, not a read tool;
  it is also where friction-260708-01 (prose-grounded edge filling) would help.
- **(C) Keep N.B as specified and accept it seals only when the graph deepens** — leave N.B.1/N.B.2 ready
  but gated on a real 2-hop typed neighborhood existing, re-measured before batch-planning.

Recommendation weighting is yours. My read of the evidence: the count-unblock was real but oversold the
graph's readiness; (A) is the honest near-term shape and (B) is the actual prerequisite for the phase's
multi-hop ambition.

---

*Generated by chimera-sprint-discipline phase_audit mode (re-run).*

---

## Disposition (Architect, 2026-07-09): **Option A — rescope N.B as an enhancement**

The stop-and-decide above is answered. The Architect selects **Option A**: N.B ships as an
enhancement to the existing `obsidian_graph_query` — **no new `deep_recall` tool**. The re-audit's
evidence (RE-Q4/RE-Q8) is accepted: the count-unblock was real but the typed graph is wide-and-shallow
(5 disjoint 1-hop stars, 0 shared papers, directional BFS depth 1), so a typed multi-hop `deep_recall`
has nothing to traverse and its honest shape is additive params on the keyword-seeded BFS that already
exists. This also honors the CLAUDE.md tool-invention rule and keeps `.mcp.json` at 2 servers.

### What Option A rescopes N.B to (supersedes `docs/phases/phase-N.B.md` Mission / Sprint / HSC)

**Rescoped mission.** Extend `obsidian_graph_query` (adapter method `VaultReadAdapter.query_graph`)
with three additive, opt-in parameters — no new MCP tool, thin adapter preserved:
- `edge_types` — restrict BFS to named typed edges (e.g. `['derives_from']`); de-noises body-wikilink
  junk like `[[Pasted image…]]`.
- provenance — each returned row carries `edge_from` (reached-through node/edge) and `hops` (depth);
  today `query_graph` returns `{title, path, type, links}` with no hop/edge (RE-Q8's genuine delta).
- `bidirectional` — undirected BFS, which unlocks the **only real depth-2 structure on the live graph**:
  the co-citation 2-hop `paper seed → its thought → the thought's sibling papers` (RE-Q4 cross-finding 2).

**Rescoped sprint sequence:**

| Sprint | Rescoped goal |
|---|---|
| N.B.0 | ✅ Complete (audit) + re-audit (this doc) |
| N.B.1 | Add `edge_types` / provenance (`edge_from`+`hops`) / `bidirectional` params to `obsidian_graph_query` — `VaultReadAdapter.query_graph` + `vault_tools` body + thin `@mcp.tool`. **No new tool; `.mcp.json` stays 2.** |
| N.B.2 | Verify: a paper-seeded, typed-filtered, `bidirectional` query returns the co-citation subgraph with per-row provenance, bounded ≤ `max_nodes`, and Claude synthesizes a multi-hop answer from the single call — no extra `vault_query` round-trips. |

**Rescoped Hard Sealing Conditions** (the original HSC 1 "≥ 2 typed hop depths from a keyword seed"
is **withdrawn** — RE-Q4 proved it structurally unreachable on today's directional graph; replaced by
the achievable co-citation 2-hop):
1. **Typed-filter + provenance** — `obsidian_graph_query` accepts `edge_types` and returns per-row
   `edge_from` + `hops`; verified live (typed filter yields a `derives_from`-only subgraph; rows carry hops).
2. **Bidirectional co-citation 2-hop** — opt-in `bidirectional` surfaces `paper → thought → sibling papers`
   from a paper seed (≥ 1 sibling at hop 2), result bounded ≤ `max_nodes`.
3. **Synthesis** — Claude answers a multi-hop recall query from the single enhanced call, no additional
   vault/keyword round-trips.

### What Option A explicitly does NOT do (kept honest)

- It does **not deepen the graph**. The `derives_from → derives_from` typed chain the original spec
  implied still has no data (RE-Q4). Real typed multi-hop remains gated on interconnection — that is
  **write-path work (Option B)**, not this read enhancement.
- Therefore `friction-260708-01` (prose-grounded typed-edge filling) stays **OPEN** and is the separate
  prerequisite for a genuinely deep graph. Its phasing (queued as Phase P) is the **Architect's** to
  author — not authored here (cf. `f6561e8`).
- Only `derives_from` is populated today; multi-*type* recall (`synthesizes`/`contradicts`) has no data
  yet, so `edge_types` filtering has effectively one type to filter until the graph gains more edge types.

**Next step:** batch-planning of the rescoped N.B.1/N.B.2 (`chimera-sprint-discipline` batch_planning →
`docs/plans/Phase-N.B-batch.md`) is now unblocked whenever the Architect calls it.

> ⚠️ **SUPERSEDED 2026-07-09 — N.B CANCELLED (Phase N truncation seal).** Disposition A (the enhancement
> rescope) never batch-planned. Later the same day, `friction-260709-01` established that the vault is
> **absent from the agentic loop** — even the enhancement has no consumer. The Architect retired N.B
> entirely: advanced retrieval is premature until the agentic defect is sealed and the vault is filled
> with ARA-styled structured nodes. See `docs/sprints/phase-N/phase-review.md`.
