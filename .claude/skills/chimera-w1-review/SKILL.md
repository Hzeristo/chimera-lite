---
name: chimera-w1-review
description: Review pending W1 verdicts and promote the ones the Architect selects (Phase L.C route 3). Activate when the Architect wants to curate the harness backlog — "review pending verdicts", "promote my verdicts", "what's waiting in Harness", "batch-promote the verified claims", or after a run of W1 has left several verdicts unreviewed. Presents every PENDING_REVIEW w1_verdict as one row carrying its tag, its grounding quote, and the exact support edge proposed, in a single structured decision; promotes only what the Architect selects and stages the evidence_base patch for [V] rows. Never promotes, never applies a patch, and never approves in bulk. Explicitly invoked (not ambient).
---

# W1 Review — Route 3: review, promote, stage the support edge

<expected_model>
**Run this at Sonnet.** This loop is curation glue — enumerate, render, ask, dispatch. It carries
no judgment: the verdicts were judged when W1 produced them, and the only decision in this
workflow belongs to the Architect. Running it at Opus is dev-time overspend with no fidelity gain
(`docs/audits/model-routing-gaps.md`). If the session model is Opus, follow the recommendation
procedure (detect → inform → wait, never auto-switch): see `../_shared/expected_model.md`.
</expected_model>

You present; the Architect decides. This skill re-judges nothing — a `[P]` stays `[P]`, and no
row is filtered out because it looks weak. Hiding a verdict is a judgment, and judgments here are
not yours.

## The loop

1. **Enumerate.** `vault_query(status="PENDING_REVIEW")`. Keep only rows whose `type` is
   `w1_verdict`; W2 breadth maps live at the same status and are **not** in this workflow.
   If none are pending, say so and stop — do not offer to run W1.

2. **Read each verdict in full.** `read_vault_file` per artifact. You need four things from each:
   - `identity` (frontmatter) — the paper's arXiv id, and the artifact's key for `write_result`.
   - `verdict` (frontmatter) — `V` / `P` / `U`.
   - the **first grounding quote** with its location, from the body.
   - the claim line (the body's `**Claim verified:**`).

3. **Resolve the support-edge target — never invent one.** For a `[V]`, the edge is
   `<K node> --evidence_base--> [[<verdict stem>]]`, so the K node whose claim was verified must be
   found. W1 does not record it, so resolve by paper:
   `search_vault_attribute(key="arxiv_id", value=<identity>)`, and keep only hits under
   `Knowledge/` (a committed node — inbox scout cards and staging are not edge targets).
   - Exactly one hit → that is the target.
   - Zero hits → **no edge is possible.** The paper has no committed K node. Say so in the row.
   - More than one hit → do not choose. Show the candidates and let the Architect name one, or
     decline the edge.

4. **Render one row per verdict.** Every row shows, without exception:

   ```
   [<V|P|U>]  <identity> — <claim, one line>
       quote: "<first verbatim quote>" ← <location>
       edge:  <K node stem> --evidence_base--> [[<verdict stem>]]
              (or: none — no committed K node carries arxiv_id <identity>)
   ```

   The quote is **mandatory on every row**. A verdict whose grounding you cannot show is a verdict
   the Architect cannot review, and it is rendered as `quote: MISSING — inspect <path> directly`,
   never omitted and never summarised in your own words.

5. **Ask once.** Present the rows as a single `AskUserQuestion` with `multiSelect: true`, one
   option per verdict. Do not add an "all of them" option; there is no bulk approve. If there are
   more rows than the question tool accepts, ask in batches — never silently truncate the list, and
   say how many remain.

6. **Promote only what was selected.** For each selected verdict:
   `write_result(kind="w1_verdict", identity=<its identity>, title=<its title>, body="",
   mode="promote")`. On a transition mode the title and body are ignored; `identity` is what
   locates the artifact. Unselected verdicts are left at `PENDING_REVIEW` — untouched, not
   rejected.

7. **Stage the support edge — `[V]` only.** For each selected verdict whose tag is `V` **and**
   whose target resolved in step 3:
   `link_nodes(from_node=<K node>, to_node=<verdict stem>, edge_type="evidence_base")`.
   This writes a patch to `docs/staging/` and stops there.

8. **Report.** Per promoted verdict: its new status, and either the staged patch path or the reason
   no edge was staged. Close by stating plainly that the patches are **staged, not applied**, and
   that applying them is the Architect's call via `apply_link_patch`. Do not offer to apply them
   yourself.

## Red lines

- ❌ **Nothing is promoted that was not selected**, and **nothing is applied at all**. Promotion
  and application are Architect actions (I0.1). Never call `apply_link_patch` from this skill —
  not as a convenience, not when a single patch is pending, not when asked to "finish up".
- ❌ **No bulk approve.** No "select all" option, no "promote the rest", no default selection. The
  review is per-row or it is not a review. This is the entire protection: an edge is metadata and
  cheap to mint (`ENFORCEMENT_DEBT` D-7), so the Architect reading each row IS the gate.
- ❌ **Every row carries its grounding quote, verbatim.** Never paraphrase a quote, never drop it
  to fit the display, never summarise a verdict in place of showing its evidence.
- ❌ **`[P]` and `[U]` stage no support edge, ever** — even when selected for promotion. A weak tag
  annotates a weak support chain; it does not participate in support (I1.3).
- ❌ **Never invent an edge target.** If no committed K node carries the paper's `arxiv_id`, the
  edge does not exist. Do not point it at an inbox card, a staged node, or a deep-read file.
- ❌ **Do not re-judge.** No filtering of "obviously bad" verdicts, no re-reading the paper, no
  changing a tag. W1 judged; you enumerate.
- ❌ **`kind` is `w1_verdict`.** W2 breadth maps share the `PENDING_REVIEW` status and are out of
  scope for this workflow.

## Notes

**Why the edge often cannot be staged.** `Knowledge/` is small and W1 is routinely run on
conversation claims about papers that were never deep-read into a committed node. A `[V]` with no
resolvable target is the normal case today, not an error — promote it and report the absence. The
support chain becomes traceable when the paper earns a K node, not before.

**W1 does not record its claim's origin node.** Step 3 re-derives the target from `arxiv_id`
because the verdict carries only the paper identity. This is a real gap in the W1 artifact and it
will bite Phase K, which reads these same artifacts to compute support — recorded in
`docs/sprints/phase-L.C/C.3c.md`.
