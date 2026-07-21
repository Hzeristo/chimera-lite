# Lens: Math Decoration Verdict

## Trigger (function-based)
Apply when the paper FUNCTIONS as a modeling/algorithmic claim — it presents equations, formal
notation, or a theoretical framework and asks the reader to accept that the formalism explains
or drives the method's behavior. Do not apply merely because equations are present on the page;
apply because the paper's argument leans on the reader being impressed by rigor. Do not apply
to pure empirical audits with no formal content (use forensic-leakage) or to surveys (use
ontological-map).

## Method
Two steps: extract, then judge. Do not stop at extraction — the judgment is the point of this
lens.

1. **Extract** the formal skeleton: the core equations (reproduce them, e.g. in LaTeX or plain
   notation), the essential forward-pass pseudocode, and the architecture narrative (the design
   philosophy and data flow the equations are supposed to formalize).
2. **Judge each key equation** against three tests:
   a. **Load-bearing vs decorative.** Does the equation actually *do work* — predict an
      outcome, constrain a search space, define a mechanism that changes behavior — or does it
      restate a simple operation (a mean, a concatenation, a softmax, a weighted sum) in heavy
      notation purely to look rigorous? Name each equation's verdict explicitly.
   b. **Deletion test.** If the equation were replaced with its plain-language description of
      the operation, would any downstream result or claim change? Decorative math survives
      deletion untouched. Load-bearing math does not — removing it breaks something concrete.
      State what, if anything, breaks.
   c. **Dynamics vs scaling.** Does the formalism introduce genuine dynamics (a state update, a
      constraint, a learned interaction), or does it merely parameterize "use a bigger buffer /
      more context / more parameters" in symbolic clothing? Scaling wearing a Greek letter is
      still scaling — call it out.

## Discipline
Every finding must satisfy the mandatory triple:
1. **Mechanism** — for each key equation, the concrete operation it performs and whether that
   operation is load-bearing or decorative, stated plainly with the reason.
2. **Evidence** — what in the paper (an ablation, a results table, a stated dependency) shows
   the equation matters to the outcome, or the absence of any such evidence.
3. **Falsifiability** — the deletion/ablation test that would prove, if run, whether the math is
   doing real work (e.g. "swap the equation for its plain-language equivalent and check whether
   reported results change"). If the paper gives no way to test this and no ablation exists,
   treat the load-bearing claim as unverified and price it accordingly.

## W1 epistemic translation

When this lens runs inside W1/W2 verification, its signals become `[V]/[P]/[U]` tags per the canonical
table in `docs/ARCHITECTURE/TAG_SYSTEM.md` §8 (Doubt-signal → tag) — reference it, do not restate a
mapping:

- signal `decorative-math` (the equation survives the deletion test; no ablation shows it matters)
  → in W1 context, a **[U]** signal (the "formalism drives behavior" claim is unverified).
- signal `mechanism-from-name` (a mechanism's function asserted from its name, the equation unread)
  → in W1 context, a **[U]** signal (Tier-1/2 unread → direction unverifiable).

A lens signal never sets a tag directly: it names the doubt; W1 assigns the tag via TAG_SYSTEM §8 +
the §3–5 definitions.
