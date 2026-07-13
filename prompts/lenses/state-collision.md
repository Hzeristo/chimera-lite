# Lens: State Collision Stress Test

## Trigger (function-based)
Apply when the paper FUNCTIONS as a claim about resolving conflicting information — it
describes memory update, belief revision, knowledge editing, reconciling contradictory
context, or multi-turn state that must handle new facts contradicting old ones — and asks the
reader to trust that the architecture arbitrates the conflict correctly. Do not apply merely
because the paper says "updates memory" as a keyword; apply because the paper's argument
depends on conflict resolution actually working. Distinct from thermodynamic-decay (temporal
degradation over a horizon, no contradiction involved) and forensic-leakage (empirical
measurement audit, not architecture).

## Method
Do not accept "the model updates its memory" at face value. Collide two facts and ask (at
minimum these three tests):

1. **Superposition check.** When new information contradicts stored state, does the
   architecture actually *resolve* the conflict (pick a winner, merge with an explicit rule,
   discard the loser), or does it just append both versions and let the prompt hold the
   contradiction unresolved? Naive superposition — stuffing both facts into context and hoping
   the model sorts it out at inference time — is not resolution. Name it when found.
2. **Arbitration mechanism.** What actually decides the winner when two facts conflict —
   recency (last-write-wins), source weight/trust, an explicit reconciliation or verification
   step, a learned gate? Name the mechanism concretely, or report explicitly that none exists
   and the paper leaves arbitration undefined.
3. **Inertia threshold.** Is the belief-revision threshold *measured* — e.g. how many
   contradicting turns, or how much counter-evidence, is required to flip an embedded belief —
   or is it merely asserted ("the model adapts to new information")? A measured threshold is
   falsifiable; a bare adaptation claim is not.

## Discipline
Every finding must satisfy the mandatory triple:
1. **Mechanism** — how contradictions are actually arbitrated (name the rule), or the explicit
   finding that they are only superimposed with no arbitration at all.
2. **Evidence** — the measured evidence-to-revision threshold if reported, and the gap where it
   is left undefined. An undefined threshold is itself a finding.
3. **Falsifiability** — state the contradiction-injection test that would settle the claim
   (e.g. "feed fact A, then k turns of ¬A; measure the k at which the embedded belief flips").
   If the paper provides no way to run such a test, the claim is unfalsifiable — report it as
   such rather than as a validated capability.
