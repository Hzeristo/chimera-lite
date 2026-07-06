---
name: chimera-lens-forensic-leakage
description: Forensic audit of a paper's EMPIRICAL claims — datasets, baselines, metrics, ablations — hunting for evaluation leakage and contamination. Activate when deep-reading or evaluating a paper that reports experiments, benchmarks, LLM-as-Judge scores, or ablation studies (empirical / eval-heavy work). Not for pure surveys (use chimera-lens-ontological-map) or pure theory with no experiments. Exposes self-enhancement bias, mock-vs-streaming evaluation, and asymmetric prompting advantages; prices every reported gain against its baseline.
---

# chimera-lens-forensic-leakage

## What this lens is for

The empirical-integrity scalpel. When a paper reports numbers, this lens does not summarize the
gains — it audits how the gains were manufactured. Ancestor: the "ruthless Forensic Auditor"
(`prompts/tasks/optics/eval_scalpel.j2`), sharpened onto the wired `eval_rigor` schema
(baselines / datasets / metrics / ablation target).

## When it fires

Auto-select on empirical / evaluation-heavy papers: reported benchmarks, LLM-as-Judge protocols,
ablation tables, SOTA claims. Do NOT fire on pure surveys (→ `chimera-lens-ontological-map`) or
pure theory with no experiments. Distinct from `chimera-lens-agentic-illusion`: this lens targets
**empirical** leakage (are the numbers earned?), not **architectural** illusion (is the agent real?).

## The forensic procedure — expose the hacks

Extract the empirical skeleton first — **datasets**, **baselines**, **primary metrics**, **core
ablation finding** — then hunt for the leakage patterns (at minimum these three):

a. **LLM-as-Judge self-enhancement bias.** Does model X judge model X's own outputs? If GPT-4o
   scores GPT-4o, the win-rate is a mirror, not a measurement. Name the judge and the judged.
b. **Mock interaction vs turn-by-turn streaming.** Is the "memory"/"agent" evaluated by
   batch-feeding static chat logs (the answers sit in context the whole time), or by true
   turn-by-turn streaming where history must actually be recalled? Mock evaluation inflates
   recall claims — expose it.
c. **Asymmetric prompting advantages.** Did their method get CoT / few-shot / tool access while
   the baselines got 0-shot? An unequal prompt budget is a rigged comparison.

Also price: data contamination (test set seen in pretraining), cherry-picked seeds, and
endpoint-only metrics that hide per-turn failure.

## Output contract

Apply the shared academic-taste contract — `../_shared/falsifiability.md`. Every verdict carries
**Mechanism + Evidence + Falsifiability**. Concretely:

- **Empirical skeleton** — datasets, baselines, metrics, ablation target (the `eval_rigor` fields).
- **Leakage findings** — each exposed hack named with the specific offending detail; use lettered
  subpoints (a. b. c.), not numbered.
- **Falsifiability** — the one measurement, run tomorrow, that would confirm or break the headline
  claim (e.g. "re-run under streaming evaluation with a held-out, third-party judge").

## Red lines
- ❌ Do not summarize gains without pricing them against a baseline.
- ❌ Do not accept a win-rate at face value — name the judge, name the protocol.
- ❌ Falsifiability is mandatory — every output carries the check (`../_shared/falsifiability.md`).
- ❌ Pure English only. This is a structured analysis lens, not the bb-persona tone filter.
- ❌ No opportunistic refactor — analysis only; do not edit the wired pipeline.
