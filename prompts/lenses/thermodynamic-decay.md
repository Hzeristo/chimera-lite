# Lens: Thermodynamic Decay Probe

## Trigger (function-based)
Apply when the paper FUNCTIONS as a claim about memory, retention, or state persisting over an
interaction horizon — it claims something is "remembered," "retained," or "kept in context"
across turns, time, or growing history, and asks the reader to trust that persistence holds up
at scale. Do not apply merely because the paper mentions memory or long-context as a keyword;
apply because the paper's argument depends on state surviving a horizon. Do not apply to pure
evaluation audits with no temporal dimension (use forensic-leakage) or to surveys
(use ontological-map).

## Method
Measure decay, don't accept a narrated mechanism. For every memory/state claim in the paper,
run the decay probe (at minimum these three tests):

1. **Horizon test.** Does the paper measure performance AS A FUNCTION of horizon length,
   interaction count, or accumulated entropy — i.e. an actual decay curve — or does it report
   one aggregate number at one fixed length? A single number cannot demonstrate decay or its
   absence. If no curve is given, mark the retention claim as untested and say so.
2. **Attribution test.** Is forgetting (or retention) *attributed* to a named mechanism —
   an eviction policy, a summarization step that lossily replaces raw history, attention
   dilution over a growing window — with supporting evidence? Or is it merely *asserted*
   ("the model remembers X")? Attributed forgetting is falsifiable; asserted retention is not.
3. **Buffer-vs-dynamics test.** Does the method introduce genuine memory-state dynamics (an
   update rule, an eviction rule, a compression step that changes what is retrievable), or does
   it simply enlarge the context/prompt buffer and call that "memory"? If longer context is the
   only lever, there is no decay physics in the paper — state this plainly. Buffer-scaling is
   not memory dynamics.

Report, for each claim, the mechanics (memory states, context bounds, overwrite behavior) named
concretely — not as sparse labels like "uses memory module" — and the specific
forgetting/retention mechanism, or the explicit finding that none is given.

## Discipline
Every finding must satisfy the mandatory triple:
1. **Mechanism** — the specific rule that governs decay or retention (an equation, an eviction
   policy, a summarization trigger). "The model learns to remember" is not a mechanism.
2. **Evidence** — the measurement that supports the claim (ideally a curve over horizon
   length), and the measurement that is missing. State the gap; do not paper over it.
3. **Falsifiability** — for each of the three probes above, answer *measured / asserted /
   absent*, and state the one horizon-length measurement that would settle the claim if it is
   false. If the paper offers no such test, report the claim as unfalsifiable decoration.
