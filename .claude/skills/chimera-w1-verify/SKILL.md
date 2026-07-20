---
name: chimera-w1-verify
description: Run W1 — Claim Verbatim Verification (Phase L research harness). Activate when the Architect wants a SPECIFIC claim checked against its cited paper — "verify this claim", "run W1 on <claim>", "is <claim> actually supported by <paper>?", or when a claim raised in conversation needs grounding before it feeds a proposal. Orchestrates fetch → classify → load criteria+disposition → an isolated verbatim subagent → a [V]/[P]/[U] verdict with grounding quotes, written to the vault Harness folder. Judgment is Claude-in-subagent, never deepseek. Explicitly invoked (not ambient).
---

# W1 — Claim Verbatim Verification

<expected_model>
**Run this orchestration loop at Sonnet.** W1's loop is glue — normalize the claim, resolve the
paper, sequence the MCP primitives (`fetch_paper` / `convert_pdf_to_md` / `load_criteria` /
`write_result`), assemble the verdict, report. Every unit of *judgment* is delegated to a
**pinned-Sonnet** worker (`chimera-paper-classifier`, `chimera-verbatim-verifier`), so the loop
itself carries no reasoning that needs Opus. Running it at Opus is dev-time overspend with zero
fidelity gain (`docs/audits/model-routing-gaps.md`, gap #2).

If the session model is Opus, follow the recommendation procedure (detect → inform → wait, never
auto-switch): see ../_shared/expected_model.md. The pinned workers stay Sonnet regardless of the
session model — do NOT downgrade `chimera-verbatim-verifier`; it is the fidelity-critical judgment,
so if anything spend UP there, never down.
</expected_model>

You (the main agent) **orchestrate**; the judgment happens in an **isolated subagent**. Never perform
the verbatim check yourself in the main context — the paper's full text must stay in the worker
(isolation by construction).

## The loop

1. **Normalize the claim** into `{claim_text, cited_ref}`, and compute a stable `identity` for supersede.
   - **Conversation claim (first-class — D3):** the Architect states a claim mid-conversation — take it
     verbatim as `claim_text`; `cited_ref` is the paper they attribute it to (arXiv id, title, or vault
     K-node).
   - **K-node claim:** `read_vault_file` the node; the claim is a mechanism claim inside it; `cited_ref`
     is its paper.
   - **Raw-text claim:** use the pasted text as `claim_text`; `cited_ref` is whatever it cites.
   - `identity` = the paper's arXiv id when the claim is about one paper; else a short deterministic slug
     of `claim_text` (so re-running the same claim supersedes, never duplicates).

2. **Resolve the cited paper (cheap-first — D5).**
   - `cited_ref` is an arXiv id already in the vault → read its converted markdown.
   - Otherwise → `fetch_paper(arxiv_id)` then `convert_pdf_to_md(...)` for a markdown path.
   - Paper cannot be resolved → go to step 5 with no paper; the verdict will be **[U]** (never a
     fabricated [V]).

3. **Classify.** Spawn the `chimera-paper-classifier` subagent on the paper → `{type, field}`.

4. **Load criteria.** Call `load_criteria(type, field, role="paper-critic")` → the composed criteria
   block (capability: `type` + `field`, THEN disposition: `paper-critic` + `_general`). Do NOT reorder it.

5. **Verify (in a subagent).** Spawn the `chimera-verbatim-verifier` subagent with: the `claim_text`, the
   paper's markdown **path** (it reads the paper itself — isolation), and the composed criteria block. It
   returns `{verdict: V/P/U, quotes:[{quote, location}], depends_on:[...]}`.

6. **Write the result.** Call `write_result(kind="w1_verdict", identity=<identity>, title=<one-line claim
   summary>, body=<the verdict + verbatim quotes, formatted>, verdict=<V/P/U>, depends_on=<the
   subagent's depends_on>)`. It lands in `<vault>/Harness/` at `status: PENDING_REVIEW` for the Architect
   to curate.

7. **Report** to the Architect: the `[V]/[P]/[U]` tag, its grounding quote(s) + location, and the Harness path.

## Red lines

- ❌ The verbatim judgment happens in the `chimera-verbatim-verifier` subagent — NEVER in the main
  context (isolation), and NEVER via deepseek.
- ❌ No `[V]/[P]/[U]` tag without a verbatim quote + location. A claim you cannot ground is `[U]`.
- ❌ W1 stops at verification — it does NOT interpret what a verified fact "means" (that is Phase K's
  framing gate). The verdict answers "is the claim supported?", nothing more (C2).
- ❌ Criteria are loaded via `load_criteria` (vault-dynamic), disposition after capability — never inline
  criteria in this skill or the subagent prompt.
- ❌ Record `depends_on` — the dependency structure, not the bare verdict (C1).
