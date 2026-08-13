---
name: chimera-lens-thermodynamic-decay
description: Probe a paper's handling of memory decay over long interaction horizons — does memory degrade, and is the degradation measured or merely asserted? Activate when deep-reading a paper about LLM memory, long-context, agentic memory, KV-cache, retention, forgetting, or state over long / multi-turn horizons. Reframes context-bound and state-management claims as falsifiable decay probes (measured over horizon length vs asserted). Not for pure evaluation audits (use chimera-lens-forensic-leakage) or surveys (use chimera-lens-ontological-map).
---

# chimera-lens-thermodynamic-decay

The canonical methodology for this lens lives in `prompts/lenses/thermodynamic-decay.md` — the
SINGLE source of truth, read by both this interactive skill and the server-side `extract_paper`
extraction. Apply the trigger, method, and discipline defined there.

(Do not duplicate the method here. Edit the canonical file to change the lens.)

The discipline contract this lens enforces (mechanism + evidence + falsifiability) is folded
into the canonical file directly, sourced from `../_shared/falsifiability.md`.
