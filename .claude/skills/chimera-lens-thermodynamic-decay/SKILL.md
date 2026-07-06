---
name: chimera-lens-thermodynamic-decay
description: Probe a paper's handling of memory decay over long interaction horizons — does memory degrade, and is the degradation measured or merely asserted? Activate when deep-reading a paper about LLM memory, long-context, agentic memory, KV-cache, retention, forgetting, or state over long / multi-turn horizons. Reframes context-bound and state-management claims as falsifiable decay probes (measured over horizon length vs asserted). Not for pure evaluation audits (use chimera-lens-forensic-leakage) or surveys (use chimera-lens-ontological-map).
---

# chimera-lens-thermodynamic-decay

## What this lens is for

The Temporal-Decay probe — the first of the Architect's Big Three diagnostic targets
(`prompts/chimera_sys/user_profile.j2:11`): *how does memory degrade across long, high-entropy
interaction horizons?* Ancestor: the `memory_physics` lens (`optics_lens_registry.py:111`),
reframed from DESCRIPTION into PROBE. It is not enough to narrate the mechanism — the lens demands
the falsifiable decay test.

## When it fires

Auto-select on memory / long-context / retention / forgetting / KV-cache / multi-turn-state papers.
Not for pure evaluation audits (→ `chimera-lens-forensic-leakage`) or surveys
(→ `chimera-lens-ontological-map`).

## The decay probe — measure, don't narrate

For every memory/state claim, run the probe (≥2 falsifiable tests; these three by default):

a. **Horizon test.** Does the paper measure performance AS A FUNCTION of horizon length /
   interaction count / entropy — a decay curve — or does it report one aggregate number at one
   length? A single number cannot show decay. Demand the curve; if it is absent, the retention
   claim is untested.
b. **Attribution test.** Is forgetting *attributed* to a named mechanism (eviction policy,
   summarization loss, attention dilution) with evidence, or merely *asserted* ("the model
   remembers")? Attributed forgetting is falsifiable; asserted retention is not.
c. **Buffer-vs-dynamics test.** Does the method introduce true memory-state dynamics, or does it
   just enlarge the context buffer? If longer context is the only lever, there is no decay physics
   here — expose it (`../_shared/falsifiability.md`: buffer-scaling ≠ memory dynamics).

## Output contract

Apply the shared academic-taste contract — `../_shared/falsifiability.md`. **Mechanism + Evidence +
Falsifiability** on every verdict:

- **Mechanics** — memory states, context bounds, overwrites (the `memory_physics` deep-dive), named
  concretely, not as sparse labels.
- **Forgetting mechanism** — the specific decay/eviction rule, or the finding that none is given.
- **Decay probe verdict** — the ≥2 falsifiable tests above, each answered *measured / asserted /
  absent*, with the one horizon-length measurement that would settle it.

## Red lines
- ❌ Do not accept a narrated mechanism as evidence of decay — demand the curve over horizon length.
- ❌ Decay ≠ state collision — temporal degradation is this lens; conflicting-state arbitration is
  `chimera-lens-state-collision`. Stay on decay.
- ❌ Falsifiability is mandatory (`../_shared/falsifiability.md`).
- ❌ Pure English only. Structured analysis lens, not a tone filter.
- ❌ 不进行机会主义重构 — analysis only; do not edit the wired pipeline.
