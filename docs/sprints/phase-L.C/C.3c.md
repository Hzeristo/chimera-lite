# Sprint C.3c — Route 3 collapse: the batch review surface

**Phase:** L.C (Colligo) · **Risk:** 🟡 MED · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Baseline:** `docs/audits/L.C.1-friction-baseline.md`
**Executed by:** Opus main session (skill authoring is reasoning-shaped — L.1b precedent, not
delegated).
**Outcome:** ⚠️ **Built and mechanically verified; live acceptance blocked on an MCP restart.**

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

## Live acceptance — blocked, not skipped

The running MCP server still holds the pre-fix `vault_query` (**DEBT-023**: server-side changes
are invisible to a running server). So the live run cannot yet enumerate correctly, and driving
the workflow off my own direct file reads would verify nothing about the skill — that is the
in-process-import shortcut that produced L.B's false seal.

**Owed at restart:** run `chimera-w1-review`, confirm 4 verdicts render (not 2), each with its
grounding quote; select a subset; confirm promotion and `[V]`-only edge staging.

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
- [ ] **Live end-to-end run** — blocked on MCP restart (DEBT-023)
- [ ] Route-3 friction re-measured against the C.1 baseline — follows the live run

## Red lines

All held. Nothing auto-promotes, nothing auto-applies, no picker built by hand (the harness's
`AskUserQuestion` multi-select is the surface), no new MCP tool, no re-judging of verdicts.

Full suite 236 passed, exit 0; `ruff` clean on new files.
