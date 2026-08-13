# Sprint C.3c — Route 3 collapse: the batch review surface

**Phase:** L.C (Colligo) · **Risk:** 🟡 MED · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Baseline:** `docs/audits/L.C.1-friction-baseline.md`
**Executed by:** Opus main session (skill authoring is reasoning-shaped — L.1b precedent, not
delegated).
**Outcome:** ✅ **Pass — verified live through the MCP client after a server restart.**

## What was built

`.claude/skills/chimera-w1-review/SKILL.md` — a sibling skill rather than a mode on
`chimera-w1-verify`. The two have different jobs and different triggers: W1 *verifies a claim*,
this *curates a backlog*. Folding curation into the verifier would have muddied a description
that the skill registry uses to decide activation.

The loop: `vault_query(status="PENDING_REVIEW")` → keep `type: w1_verdict` → read each in full →
resolve the support-edge target by `arxiv_id` → render one row per verdict → **one**
`AskUserQuestion` multi-select → `write_result(mode="promote")` on the selected → `link_nodes(...,
edge_type="evidence_base")` for `[V]` rows only → report, and stop.

## Two guards fired on this sprint's own work

Both unprompted, on real changes, one sprint after they shipped:

1. **C.2 caught the unregistered skill.** Adding the skill directory made
   `test_every_skill_is_covered_by_the_map` fail by name:
   `AssertionError: skill(s) missing from _SKILL_REQUIRED_TOOLS: ['chimera-w1-review']`.
   This is `friction-260811-01`'s class caught at the moment of creation rather than three weeks
   later, which is exactly what C.2 was homed here to do.
2. **The generated architecture map went stale**, failing
   `test_skill_layer_declared_out_of_scope_with_real_counts` and
   `test_committed_artifact_matches_current_source` — the map counts skills. Regenerated.

## The defect this sprint found

**On the first live call, `vault_query(status="PENDING_REVIEW")` returned 2 of 6 pending
artifacts.** Root cause: anchored ripgrep patterns without `--crlf`, so every CRLF note in the
vault was silently absent. Handled as an incident, not folded into this sprint:
`docs/incidents/2026-08-12-vault-query-crlf-silent-truncation.md`, fixed in `f8c2e52` with a
negative-controlled regression.

The irony is load-bearing: this workflow's central red line is *never silently truncate the list*,
and its data source was doing precisely that. Built on the unfixed tool, the review surface would
have hidden four verdicts from a review whose entire purpose is that nothing is hidden — and it
would have looked correct while doing it.

## Live acceptance — run through the MCP client, 2026-08-12

The first attempt was correctly **deferred**, not faked: the running server still held the pre-fix
`vault_query` (**DEBT-023**), and driving the workflow off direct file reads would have verified
nothing about the skill — the in-process-import shortcut behind L.B's false seal. The Architect
restarted both servers; the run then proceeded end to end.

| Step | Observed |
|---|---|
| Enumerate | `vault_query(status="PENDING_REVIEW")` → **6** matches (**2** before the fix); filtered to **4** `w1_verdict`, both W2 maps correctly excluded |
| Read | all 4 read via `read_vault_file` |
| Resolve target | `search_vault_attribute(arxiv_id=2606.16353)` → **0 hits**; no edge possible, reported rather than invented |
| Render | 4 rows, each with its verbatim grounding quote and location |
| Ask | one `AskUserQuestion` multi-select, no default, no bulk option |
| Promote | Architect selected the `[V]` only → `PENDING_REVIEW → PROMOTED` |
| Untouched | the 3 unselected verdicts and both W2 maps unchanged |
| Body integrity | promoted artifact keeps its quotes and `depends_on`; 27 lines |
| Staging | empty — no patch written, correct with no K node |

**This was the first promotion in the vault's history.** All six harness artifacts had sat at
`PENDING_REVIEW` since they were written, because the transition did not exist until C.3a.

**Architect ruling during the run:** a missing K node is acceptable in L.C — "R&D nodes are cheap,
K node missing is allowed. dev, not prod." So the unresolvable edge is not a blocker; the support
chain becomes traceable when papers earn committed nodes.

## Refinement surfaced by the live run

The skill required a grounding quote per row and rendered `MISSING` when none existed. But `[U]`
verdicts legitimately have no *supporting* quote — W1's red line forbids fabricating one — while
they do record what **refutes** the claim. `2501.05510` proved it: the paper states the opposite of
the claim (human 92.81 vs best model 63.00). Rendering that as `MISSING` would understate a
*refuted* claim as merely unproven. The skill now requires the refuting evidence to be shown and
labelled, reserving `MISSING` for a `[U]` that records nothing at all.

## Findings carried out

1. **W1 verdicts do not record their claim's origin node.** A verdict carries `identity` (the
   paper's arXiv id) and `depends_on` (quote slugs) — not the K node whose claim was verified. The
   support-edge target must therefore be re-derived from `arxiv_id`. **Phase K reads these same
   artifacts to compute support and will hit this.** Recorded, not fixed (out of scope).
2. **The support edge usually cannot be staged, and that is not an error.** `Knowledge/` holds 2
   committed nodes; the only `[V]` verdict (`2606.16353`) has no K node for its paper. W1 is
   routinely run on conversation claims about papers never deep-read into a committed node. The
   skill promotes and reports the absence rather than inventing a target.
3. **A thin vault masked the CRLF defect's blast radius.** Four hidden verdicts, not four hundred.
   The same bug on a populated vault would have been far more expensive, and it had been shipped
   since the tool was written.

## Acceptance

- [x] One invocation enumerates pending `w1_verdict` artifacts and promotes only the selection
- [x] Every rendered row carries its grounding quote verbatim (mandatory; `MISSING` is rendered
      explicitly, never omitted or paraphrased)
- [x] `[P]`/`[U]` promote if selected but stage no support edge (I1.3)
- [x] No bulk-approve affordance; no default selection
- [x] The skill never calls `apply_link_patch`
- [x] **Live end-to-end run** through the MCP client, post-restart
- [x] Route-3 friction re-measured: N invocations + a dead end → **1 invocation, 0 context
      switches, 0 manual transcription, and the route completes.** Recorded in
      `docs/audits/L.C.1-friction-baseline.md` §4

## Red lines

All held. Nothing auto-promotes, nothing auto-applies, no picker built by hand (the harness's
`AskUserQuestion` multi-select is the surface), no new MCP tool, no re-judging of verdicts.

Full suite 236 passed, exit 0; `ruff` clean on new files.
