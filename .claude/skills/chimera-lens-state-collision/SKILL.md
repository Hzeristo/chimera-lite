---
name: chimera-lens-state-collision
description: Stress-test how a paper's architecture arbitrates CONFLICTING information — state overwrite and cognitive inertia. Activate when deep-reading a paper about memory update, belief revision, knowledge editing, conflicting-context resolution, multi-turn state, or agent memory that must reconcile contradictions. Asks how conflicting state is resolved (naive superposition vs true arbitration) and at what evidence threshold an embedded belief flips. Distinct from chimera-lens-thermodynamic-decay, which is temporal degradation; this lens is conflict arbitration.
---

# chimera-lens-state-collision

The canonical methodology for this lens lives in `prompts/lenses/state-collision.md` — the
SINGLE source of truth, read by both this interactive skill and the server-side `extract_paper`
extraction. Apply the trigger, method, and discipline defined there.

(Do not duplicate the method here. Edit the canonical file to change the lens.)

The discipline contract this lens enforces (mechanism + evidence + falsifiability) is folded
into the canonical file directly, sourced from `../_shared/falsifiability.md`.
