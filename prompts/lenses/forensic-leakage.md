# Lens: Forensic Leakage Audit

## Trigger (function-based)
Apply when the paper FUNCTIONS as an empirical/eval claim — it reports benchmark gains,
LLM-as-judge scores, ablation tables, or SOTA numbers, and asks the reader to accept that a
measured improvement is real and earned. Do not apply based on surface type (e.g. "has a
results section") — apply because the paper's argument rests on numbers being trustworthy.
Do not apply to pure surveys with no experiments (that is the ontological-map lens) or to
pure theory papers with no empirical section.

## Method
This is a forensic audit, not a summary of gains. Extract the empirical skeleton first, then
hunt for leakage.

1. **Extract the skeleton**: datasets used, baselines compared against, primary metrics
   reported, and the core ablation finding.
2. **Hunt for leakage patterns** (at minimum, run these three probes on every paper):
   a. **LLM-as-Judge self-enhancement bias.** Does model X judge model X's own outputs? If
      GPT-4o scores GPT-4o's responses, the win-rate is a mirror, not a measurement. Name the
      judge model and the judged model explicitly and check whether they are the same family.
   b. **Mock interaction vs turn-by-turn streaming.** Is the "memory"/"agent" evaluated by
      batch-feeding a static chat log (so the answer sits in context the whole time), or by
      true turn-by-turn streaming where history must actually be recalled from a prior state?
      Mock evaluation inflates recall claims — call this out explicitly when found.
   c. **Asymmetric prompting advantages.** Did the paper's own method get CoT, few-shot
      examples, or tool access while the baselines were run 0-shot or under a smaller prompt
      budget? An unequal prompt budget makes the comparison rigged regardless of the reported
      delta.
3. **Price additional leakage vectors**: data contamination (was the test set plausibly seen
   during pretraining?), cherry-picked seeds/runs, and endpoint-only metrics (final accuracy /
   win-rate) that hide per-turn or per-step failure — demand process-level evidence instead.
4. **Price every gain against its baseline** — a delta without a named, fairly-matched
   baseline is unpriced and should be reported as such, not passed through as a finding.

## Discipline
Every finding must satisfy the mandatory triple:
1. **Mechanism** — name the concrete thing that produced the number (which judge, which
   protocol, which prompt configuration) — not a vague description.
2. **Evidence** — what was actually measured, under what protocol, against what baseline; and
   what measurement is conspicuously absent. An absent measurement is itself a finding.
3. **Falsifiability** — state the one measurement, run tomorrow, that would confirm or break
   the headline claim (e.g. "re-run under streaming evaluation with a held-out, third-party
   judge"). If no such test is stated or implied by the paper, the claim is unfalsifiable —
   report it as decoration, not as a validated result, and price it accordingly.

## W1 epistemic translation

When this lens runs inside W1/W2 verification, its analytical signals become `[V]/[P]/[U]` tags. The
mapping is CANONICAL in `docs/ARCHITECTURE/TAG_SYSTEM.md` §8 (Doubt-signal → tag) — reference it; the
two below are the load-bearing cases, not a private redefinition:

- signal `experiment-design-leak` (asymmetric prompting / contamination / cherry-picked seeds)
  → in W1 context, a **[P]** signal (partial, caveats required — the number stands, the "gain is
  earned" inference is confounded).
- signal `self-evaluation-only` (the judge model is the same family as the judged model)
  → in W1 context, a **[U]** signal (unverifiable with available evidence — a self-graded score is a
  mirror, not a measurement).

A lens signal never sets a tag directly: it names the doubt; W1 assigns the tag via TAG_SYSTEM §8 +
the §3–5 definitions.
