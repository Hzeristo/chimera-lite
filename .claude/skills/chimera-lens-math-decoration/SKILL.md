---
name: chimera-lens-math-decoration
description: Judge whether a paper's mathematics is load-bearing or decorative — does the notation do work, or dress up a simple operation to look rigorous? Activate when deep-reading any modeling / algorithm / architecture paper with equations, formal notation, or theoretical framing. Extracts the core equations and architecture, then delivers an explicit load-bearing-vs-decorative verdict per equation. Not for pure empirical audits (use chimera-lens-forensic-leakage) or surveys (use chimera-lens-ontological-map).
---

# chimera-lens-math-decoration

The canonical methodology for this lens lives in `prompts/lenses/math-decoration.md` — the
SINGLE source of truth, read by both this interactive skill and the server-side `extract_paper`
extraction. Apply the trigger, method, and discipline defined there.

(Do not duplicate the method here. Edit the canonical file to change the lens.)

The discipline contract this lens enforces (mechanism + evidence + falsifiability) is folded
into the canonical file directly, sourced from `../_shared/falsifiability.md`.
