---
name: chimera-lens-agentic-illusion
description: Strip the illusion from "agentic" papers — audit the real plumbing behind agent / autonomous-loop / tool-use claims. Activate when deep-reading a paper that claims agents, autonomous loops, tool use, or agentic memory. Exposes whether the "agent" is a real programmatic loop with true mutable state or a single-pass API call dressed up with an orchestration framework. Distinct from chimera-lens-forensic-leakage (empirical leakage in evaluation) — this lens targets ARCHITECTURAL illusion (is the agent real?).
---

# chimera-lens-agentic-illusion

The canonical methodology for this lens lives in `prompts/lenses/agentic-illusion.md` — the
SINGLE source of truth, read by both this interactive skill and the server-side `extract_paper`
extraction. Apply the trigger, method, and discipline defined there.

(Do not duplicate the method here. Edit the canonical file to change the lens.)

The discipline contract this lens enforces (mechanism + evidence + falsifiability) is folded
into the canonical file directly, sourced from `../_shared/falsifiability.md`.

Note: this lens is an analysis lens, not a tone filter — it emits a structured architectural
verdict and is distinct from `chimera-bb-persona`, which restyles the final answer.
