---
name: chimera-lens-forensic-leakage
description: Forensic audit of a paper's EMPIRICAL claims — datasets, baselines, metrics, ablations — hunting for evaluation leakage and contamination. Activate when deep-reading or evaluating a paper that reports experiments, benchmarks, LLM-as-Judge scores, or ablation studies (empirical / eval-heavy work). Not for pure surveys (use chimera-lens-ontological-map) or pure theory with no experiments. Exposes self-enhancement bias, mock-vs-streaming evaluation, and asymmetric prompting advantages; prices every reported gain against its baseline.
---

# chimera-lens-forensic-leakage

The canonical methodology for this lens lives in `prompts/lenses/forensic-leakage.md` — the
SINGLE source of truth, read by both this interactive skill and the server-side `extract_paper`
extraction. Apply the trigger, method, and discipline defined there.

(Do not duplicate the method here. Edit the canonical file to change the lens.)

The discipline contract this lens enforces (mechanism + evidence + falsifiability) is folded
into the canonical file directly, sourced from `../_shared/falsifiability.md`.
