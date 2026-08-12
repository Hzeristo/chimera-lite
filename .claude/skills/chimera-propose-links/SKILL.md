---
name: chimera-propose-links
description: Propose `informed_by` provenance edges for a hand-authored Thought/Insight/Decision node (Phase L.C route 2, the Obsidian boundary bridge). Activate when the Architect has just written a judgment node in Obsidian and wants its provenance recorded — "propose links for my new thought", "what informed this note", "record what I was reading", "link this thought to the map I was using", or after a deep-extract / W2 run when the Architect says they have written something from it. Proposes only artifacts this session actually consulted, stages each via link_nodes, and stops — applying is the Architect's explicit order. Never writes a node's body, never creates a node, never applies a patch. Explicitly invoked (not ambient).
---

# Propose Links — `informed_by` for a hand-authored judgment node

<expected_model>
**Run this at Sonnet.** The loop is resolution and staging glue; the only judgment in it —
*did this artifact actually inform that note?* — is the Architect's, and it is answered by them,
not by you. If the session model is Opus, follow the recommendation procedure (detect → inform →
wait, never auto-switch): see `../_shared/expected_model.md`.
</expected_model>

## Why this exists

`informed_by` is **mandated by I0.5** as the provenance record for a judgment node authored while
consulting AI output. It was measured as **never used** — the Architect writes a T-node via
keyboard shortcut, fills the contents, and adds **no links**
(`docs/audits/L.C.1-friction-baseline.md` §5). That is not negligence: filling a structured edge
means knowing the exact key, the exact wikilink stem, and the exact list syntax. It is machine
work, and it is not the work being done at the moment a thought is written.

So the machine does the format work and the Architect keeps the judgment. **I0.5 reserves the
body, not the frontmatter** — an edge is metadata, not content (`ENFORCEMENT_DEBT` D-7), so
proposing and staging one authors nothing.

## The loop

1. **Get the judgment node.** The Architect names it, or a `Monitor` event surfaced it. Resolve
   with `vault_query(type="thought"|"insight"|"decision")` or `read_vault_file`.
   - Its frontmatter `type` **must** be `thought`, `insight`, or `decision`. `informed_by` is
     T/I/D-only (I0.5 scopes it to judgment nodes); refuse a `knowledge` node and say why.
   - Read its existing `graph_edges.informed_by`. Already-present targets are **not** re-proposed;
     `apply_link_patch` is idempotent, but a duplicate proposal wastes the Architect's attention,
     which is the scarce thing here.

2. **Assemble candidates from THIS session only.** An artifact is a candidate when this
   conversation actually produced or read it — a W2 breadth map, a W1 verdict, a K node you
   opened. **Do not search the vault for plausible matches.** A provenance edge asserting a
   connection nobody made is a fabricated record, and worse than an absent one.
   - If the session consulted nothing, say so and stop. Proposing nothing is a valid outcome.

3. **Check each candidate resolves.** `link_nodes` resolves both endpoints against the **vault
   root only** (`vault_read_adapter.py:417`). Consequences worth stating to the Architect rather
   than discovering at stage time:
   - `Harness/` artifacts (W2 maps, W1 verdicts) and `Knowledge/` nodes resolve.
   - A **staged** `deep_read` node in `docs/staging/` does **not** — it is not in the vault yet.
     It becomes linkable only after `ascend_node`. Report that; do not substitute the paper.

4. **Propose, with the reason.** One row per candidate:

   ```
   <artifact stem>
       consulted: <what happened in this session — "W2 map you ran on <topic>", "verdict you
                   promoted for <id>">
       edge:      [[<judgment node>]] --informed_by--> [[<artifact stem>]]
   ```

   The `consulted` line is mandatory. It is what lets the Architect refuse a wrong proposal, and a
   proposal they cannot check is one they can only rubber-stamp.

5. **Require an explicit order.** Present the rows as a single `AskUserQuestion` with
   `multiSelect: true`. No default selection, no "all of them" option. Silence is not consent and
   neither is plausibility — an edge is staged only for a candidate the Architect names.

6. **Stage only what was ordered.** Per ordered candidate:
   `link_nodes(from_node=<judgment node>, to_node=<artifact stem>, edge_type="informed_by")`.
   This writes a patch to `docs/staging/`. **Stop there.**

7. **Report** each staged patch path, and state plainly that the patches are staged and that
   applying them is the Architect's call via `apply_link_patch`. Do not offer to apply them.

## Red lines

- ❌ **Never write, create, scaffold, or edit a judgment node's BODY.** No tool authors T/I/D
  content (I0.5). This skill touches `graph_edges` through a staged patch and nothing else.
- ❌ **Never call `apply_link_patch`.** Proposing is machine-time; applying is human-time (I0.1).
  Not as a convenience, not for a single pending patch, not when told to "finish up" — that
  instruction means apply it yourself.
- ❌ **Never propose an artifact this session did not consult.** No vault-wide similarity search,
  no "this looks related". A fabricated provenance edge is worse than a missing one.
- ❌ **`informed_by`, never `derives_from`.** A judgment node informed by a tool is not derived
  from it; `derives_from` would assert machine parentage over an Architect-authored claim (I0.5).
  If a genuine derivation exists, that is the Architect's call to make by hand.
- ❌ **`informed_by` is not support-bearing.** It records a tool consulted, not a dependency, and
  must never enter a monotonicity or support-chain computation (I2.2).
- ❌ **T/I/D only.** Refuse a `knowledge` node — `_TYPE_EDGES` will reject it anyway, but say why
  rather than letting the error surface raw.
- ❌ No default selection and no bulk approve. Per-candidate or not at all.

## Notes

**Ambient detection (optional).** A persistent `Monitor` over the vault's `Thoughts/`, `Insight/`
and `Decision/` folders emits one event per new file, which is enough to offer this workflow the
moment a node is written. It is **session-scoped** — it cannot see authoring that happens while no
session is open, which is a real limitation and not a bug. The Architect-initiated path is the
one that always works; treat the monitor as a convenience over it, never as the mechanism.

**Why the edge and not the whole node.** The temptation is to notice that the Architect writes
nodes without links and to start filling more of the node for them. That is the line: format is
the machine's, judgment is the Architect's, and the body is judgment all the way down.
