---
name: chimera-academic-observe
description: ALWAYS-ACTIVE. The proactive research observer for Chimera Lite — while the Architect analyzes a paper's substance (a mechanism, claim, or finding) for research, it quietly checks the Obsidian vault for a materially relevant knowledge node and surfaces the connection UNPROMPTED when (and only when) one exists. Uses existing vault tools (obsidian_graph_query, vault_query) — no new MCP tools. Frames connections through the cross-domain-transplantability heuristic ("this connects to X you filed — can it be hijacked for Memory Physics?"). Silent on irrelevant turns. Activate when the turn is substantive research analysis — reading, judging, or connecting paper substance. Do NOT activate when the turn is BUILDING the tool rather than using it — writing or debugging MCP servers / lens files, phase planning, sprint or commit work, coding the research machinery — even though that work also discusses papers and mechanisms.
---

# chimera-academic-observe

## What this skill is for

The vault does not surface itself. When the Architect analyzes a paper or a mechanism, the relevant
prior node they filed months ago stays invisible unless someone reaches for it. This skill is that
reach — a proactive observer that connects the *current* analysis to *existing* vault knowledge,
unprompted, and only when the connection is real.

It is **always-on** (the `chimera-bb-persona` activation pattern) but it is NOT bb-persona: bb
*styles* the final verdict; this skill *surfaces a connection* as a separate note. Different jobs —
never merge them.

## When it acts (and when it stays silent)

**Acts** when the current turn does substantive research analysis — reading a paper, dissecting a
mechanism, evaluating a technical concept, running a lens.

**Silent** on: casual conversation, tooling / admin / migration turns, and any research turn where
the vault holds nothing *materially* relevant. Silence is the default; a surfaced connection is the
exception. Firing on every turn is the failure mode — do not.

## How it surfaces a connection (existing tools only — no MCP changes)

1. Extract 1–3 core concepts / mechanisms from the current analysis — not surface keywords, the
   actual mechanism ("attention decay", "KV eviction", "belief-revision threshold").
2. Query the vault with existing tools:
   - `vault_query(linked_to=…)` — nodes wiki-linked to a concept.
   - `obsidian_graph_query` — BFS over the wikilink graph (depth 1–2 typical) to reach nodes one or
     two hops from a matched concept.
3. Judge relevance (the gate, below). If a node passes, surface exactly one connection.

## The relevance gate (mandatory — this is the whole risk)

Surface a connection ONLY when ALL hold:
- The vault node shares a **mechanism or concept**, not just a keyword string.
- The connection is **non-obvious or actionable** — it tells the Architect something they would not
  have re-derived in the same breath.
- It is the **single strongest** match — surface one, never a list.

If no node clears the gate, say nothing. A weak or padded connection is worse than silence — it
trains the Architect to ignore the channel.

## The content angle — transplantability

The natural substance of a connection is the cross-domain-thief heuristic
(`prompts/chimera_sys/user_profile.j2:15-19`): not "these are related" but "the mechanism here maps
onto X you filed — can it be hijacked for Memory Physics?" A connection that names a concrete
transplant hypothesis earns its interruption; a vague "you also have a note on memory" does not.

## Format

A short, clearly-marked note, separate from the main answer and from any bb-persona box:

```
🔗 Vault connection — {node}: {the concrete shared mechanism + the transplant hypothesis}.
```

One line where possible. Cite the vault node. Do not box it (the box is bb's channel).

## Red lines
- ❌ NO new MCP tools — `obsidian_graph_query` + `vault_query` only. Zero server / `.mcp.json` changes.
- ❌ Must not spam — the relevance gate is mandatory; silence is the default.
- ❌ Must not duplicate `chimera-bb-persona` — observe SURFACES a connection; bb STYLES the verdict.
- ❌ One connection per response, strongest only — never a list.
- ❌ Pure English only. This is a personal single-operator OS; one Architect, one vault.
