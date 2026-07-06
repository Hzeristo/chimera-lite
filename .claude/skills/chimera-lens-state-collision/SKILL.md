---
name: chimera-lens-state-collision
description: Stress-test how a paper's architecture arbitrates CONFLICTING information — state overwrite and cognitive inertia. Activate when deep-reading a paper about memory update, belief revision, knowledge editing, conflicting-context resolution, multi-turn state, or agent memory that must reconcile contradictions. Asks how conflicting state is resolved (naive superposition vs true arbitration) and at what evidence threshold an embedded belief flips. Distinct from chimera-lens-thermodynamic-decay, which is temporal degradation; this lens is conflict arbitration.
---

# chimera-lens-state-collision

## What this lens is for

The State-Collision stress test — the Architect's second and third Big Three targets
(`prompts/chimera_sys/user_profile.j2:12-13`):
- **State Overwrite** — how does the architecture resolve conflicting information WITHOUT naive
  superposition (just adding more text)?
- **Cognitive Inertia** — what threshold of new evidence forces the model to revise a deeply
  embedded belief?

This lens is **net-new** — no wired registry ancestor. It is authored from the stance vocabulary
and the `memory_physics` notion of "overwrites" (`core/schemas.py:192`). Its job is not to describe
memory; it is to collide two facts and watch what the architecture does.

## When it fires

Auto-select on memory-update / belief-revision / knowledge-editing / conflicting-context /
multi-turn-state papers. Not `chimera-lens-thermodynamic-decay` (temporal degradation over horizon)
and not `chimera-lens-forensic-leakage` (empirical audit).

## The collision stress test

Do not accept "the model updates its memory." Collide two facts and ask (≥2 falsifiable tests;
these three by default):

a. **Superposition check.** When new information contradicts stored state, does the architecture
   *resolve* the conflict, or does it just append both versions and let the prompt hold the
   contradiction? Naive superposition (stuff both into context) is not resolution — expose it.
b. **Arbitration mechanism.** What actually decides the winner — recency, source weight, an explicit
   reconciliation step, a learned gate? Name the mechanism, or report that none exists.
c. **Inertia threshold.** Is the belief-revision threshold *measured* — how many contradicting turns
   / how much counter-evidence to flip an embedded belief — or merely asserted? A measured threshold
   is falsifiable; "the model adapts" is not.

## Output contract

Apply the shared academic-taste contract — `../_shared/falsifiability.md`. **Mechanism + Evidence +
Falsifiability**:

- **Conflict-resolution mechanism** — how contradictions are arbitrated, or the finding that they
  are only superimposed.
- **Inertia threshold** — the measured evidence-to-revision threshold, or the gap where it is
  undefined.
- **Falsifiability** — the contradiction-injection test that would settle it (e.g. "feed fact A,
  then k turns of ¬A; measure the k at which the belief flips").

## Red lines
- ❌ State collision ≠ temporal decay — do not duplicate `chimera-lens-thermodynamic-decay`. This
  lens is about *conflict arbitration*, not degradation over time.
- ❌ Do not accept naive superposition (context-stuffing both versions) as conflict resolution.
- ❌ Falsifiability is mandatory (`../_shared/falsifiability.md`).
- ❌ Pure English only. No opportunistic refactor.
