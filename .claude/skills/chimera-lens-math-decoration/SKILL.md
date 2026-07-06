---
name: chimera-lens-math-decoration
description: Judge whether a paper's mathematics is load-bearing or decorative — does the notation do work, or dress up a simple operation to look rigorous? Activate when deep-reading any modeling / algorithm / architecture paper with equations, formal notation, or theoretical framing. Extracts the core equations and architecture, then delivers an explicit load-bearing-vs-decorative verdict per equation. Not for pure empirical audits (use chimera-lens-forensic-leakage) or surveys (use chimera-lens-ontological-map).
---

# chimera-lens-math-decoration

## What this lens is for

The math validator — extract the formal content, then judge whether it earns its place. Extraction
ancestor: the `math_arch` lens (`optics_lens_registry.py:87`; `core/schemas.py:156-167` —
`core_equations`, `pseudo_code`, `architecture_narrative`) + `method_scalpel.j2` Objective 1. The
**delta** is the validation judgment, fused from the Architect's stance
(`prompts/chimera_sys/user_profile.j2:24-25`): value grounded modeling over engineering boilerplate;
expose math that only scales context without introducing true dynamics.

## When it fires

Auto-select on modeling / algorithm / architecture papers carrying equations or formal notation.
Not `chimera-lens-forensic-leakage` (pure empirical audit) or `chimera-lens-ontological-map` (surveys).

## The validation — extract, then judge

Step 1 — **extract** (the `math_arch` skeleton): core equations (LaTeX), the essential forward-pass
pseudocode, the architecture narrative (design philosophy + data flow).

Step 2 — **judge each equation** (this is the delta; do not stop at extraction):

a. **Load-bearing vs decorative.** Does the equation *do work* — predict, constrain, or define the
   mechanism — or does it restate a simple operation (a mean, a concat, a softmax) in heavy notation
   to look rigorous? Decorative math dresses up plumbing.
b. **Deletion test.** If you replaced the equation with its plain-language operation, would any
   result change? Decorative math survives deletion untouched; load-bearing math does not.
c. **Dynamics vs scaling.** Does the formalism introduce genuine dynamics, or does it merely
   parameterize "use a bigger buffer / more context"? Scaling wearing a Greek letter is still
   scaling (`../_shared/falsifiability.md`).

## Output contract

Apply the shared academic-taste contract — `../_shared/falsifiability.md`. **Mechanism + Evidence +
Falsifiability**:

- **Extraction** — core equations, forward-pass pseudocode, architecture narrative.
- **Decoration verdict** — per key equation: load-bearing or decorative, with the reason.
- **Falsifiability** — the deletion / ablation test that would prove the math is (or is not) doing
  work.

## Red lines
- ❌ Do NOT merely re-extract what `math_arch` already extracts — the judgment (load-bearing vs
  decorative) is mandatory and is the reason this lens exists.
- ❌ Do not be impressed by notation density — price the math against what it does.
- ❌ Falsifiability is mandatory (`../_shared/falsifiability.md`).
- ❌ Pure English only. 不进行机会主义重构。
