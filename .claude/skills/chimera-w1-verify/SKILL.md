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
   - `identity` = `<arxiv_id>__<claim_slug>` — the paper's arXiv id, `__`, and a short deterministic
     kebab-case slug of `claim_text` (4-6 words). No arXiv id → the slug alone.
     **The claim slug is not optional.** `identity` is the artifact's filename
     (`result_service.py:173`) and `write_result` defaults to `supersede`, so a bare arXiv id makes
     every claim about one paper overwrite the previous one — a re-run and a *different* claim are
     indistinguishable to the tool. The slug is what makes supersede mean "this same claim again."
     Keep it short for a second reason: `_slug` truncates at 80 characters, so two long slugs sharing
     a prefix still collide.

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

## Queue mode — a claim spotted mid-read

**Trigger:** the Architect queues a claim rather than asking for it now — "queue this", "check this
in the background", "verify this while I keep reading", or any claim raised while they are plainly
mid-read and did not ask to stop. When in doubt, run foreground; queueing a claim they wanted
answered now is the worse error.

Queue mode runs **the same loop**, moved off the Architect's session:

1. Do step 1 above yourself — normalize the claim and compute `identity`. **Only this step.** The
   identity must be computed here, in the session that knows what else is queued, not by the runner.
2. Spawn `chimera-w1-runner` with `{claim_text, cited_ref, identity}`. It runs detached; you get
   control back immediately.
3. **Report the handle in one line and stop:** the `identity` you queued and the claim, so the
   Architect knows what is in flight. Do not narrate the loop, do not poll, do not wait.
4. **On the completion notification,** report the runner's `queued-claim`, verdict, grounding quote,
   and Harness path — leading with `queued-claim`, because by then several may be outstanding and a
   verdict the Architect cannot attribute is worse than no verdict.

Queueing does not weaken anything: the judgment still happens in `chimera-verbatim-verifier` under
isolation, one layer further out. Both modes coexist — queue mode never replaces the foreground path.

## Red lines

- ❌ The verbatim judgment happens in the `chimera-verbatim-verifier` subagent — NEVER in the main
  context (isolation), and NEVER via deepseek.
- ❌ **Queue mode spawns `chimera-w1-runner` and nothing else** — never an unpinned or
  general-purpose agent. The runner's tool list is deliberately narrow: no `Write`, no `Edit`, no
  shell. A detached agent runs unwatched, so its authority is bounded by construction.
- ❌ **Never queue and foreground the same claim.** They share an `identity` and the second write
  supersedes the first.
- ❌ Queue mode does not promote and does not link. The artifact lands `PENDING_REVIEW`;
  `chimera-w1-review` is where the Architect promotes it (I0.1).
- ❌ No `[V]/[P]/[U]` tag without a verbatim quote + location. A claim you cannot ground is `[U]`.
- ❌ W1 stops at verification — it does NOT interpret what a verified fact "means" (that is Phase K's
  framing gate). The verdict answers "is the claim supported?", nothing more (C2).
- ❌ Criteria are loaded via `load_criteria` (vault-dynamic), disposition after capability — never inline
  criteria in this skill or the subagent prompt.
- ❌ Record `depends_on` — the dependency structure, not the bare verdict (C1).
