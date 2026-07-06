# Falsifiability Check (shared lens contract)

Single source for the academic-taste discipline every `chimera-lens-*` skill enforces.
Each lens references this fragment via `../_shared/falsifiability.md`. Do NOT inline-copy
unless cross-skill include proves unreliable at runtime — if forced to copy, mark each copy
`SYNC: _shared/falsifiability.md` so drift is auditable.

Derived from the Architect's research stance
(`prompts/chimera_sys/user_profile.j2:21-25`, "METHODOLOGICAL PURITY / The Falsifiability Check").

## The mandatory triple (every lens verdict carries all three)

A lens analysis is not complete until it states, explicitly:

1. **Mechanism** — the specific thing that does the work: an equation, a routing rule, a state
   update, an eviction policy. Name it concretely. "The model learns to remember" is not a
   mechanism; "history is summarized every k turns and the summary replaces raw context" is.
2. **Evidence** — the measurement that supports the claim, AND the measurement that is missing.
   What was tested, under what protocol, against what baseline. Absent evidence is itself a
   finding — state the gap, do not paper over it.
3. **Falsifiability** — the one concrete test that, run tomorrow, would break the claim if it is
   false. If no such test exists, the claim is decoration, not science — say so plainly.

## Falsifiability heuristics (apply to every paper)

- **Reject endpoint-only metrics.** Pure QA accuracy / win-rate / final-answer scores hide the
  process. Demand white-box, process-oriented evidence: turn-wise analysis, oracle-decoupled
  failure attribution, per-step trajectories.
- **Price the baseline.** A number without a baseline is unpriced. Name the comparison and ask
  whether it is fair (same prompt budget, same data, same compute).
- **Buffer-scaling is not memory dynamics.** If a paper only enlarges the prompt/context buffer,
  it has not introduced true memory-state dynamics — expose this. More tokens ≠ more memory.
- **Grounded modeling over boilerplate.** Reward the equation that predicts; discount the
  pipeline that merely runs. Heavy engineering scaffolding is not a contribution.

## The one-line discipline

For any claim, ask: *what measurement, run tomorrow, would prove this wrong?* If the paper
cannot answer, report the claim as **unfalsifiable** and price it accordingly — do not launder
it into a finding.
