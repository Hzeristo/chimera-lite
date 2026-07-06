---
name: chimera-lens-agentic-illusion
description: Strip the illusion from "agentic" papers — audit the real plumbing behind agent / autonomous-loop / tool-use claims. Activate when deep-reading a paper that claims agents, autonomous loops, tool use, or agentic memory. Exposes whether the "agent" is a real programmatic loop with true mutable state or a single-pass API call dressed up with an orchestration framework. Distinct from chimera-lens-forensic-leakage (empirical leakage in evaluation) — this lens targets ARCHITECTURAL illusion (is the agent real?).
---

# chimera-lens-agentic-illusion

## What this lens is for

The plumbing audit — strip the marketing off "agentic" claims and expose the real execution cycle.
Ancestor: `prompts/tasks/optics/method_scalpel.j2:9-13` ("AGENTIC REALITY CHECK / Plumbing Audit")
plus the M.3 "strip the illusion" stance (`docs/sprints/phase-M/M.3.md:17`). It shares
`chimera-bb-persona`'s anti-hype allergy but is an **analysis lens**, not a tone filter — it emits
a structured verdict; it does not restyle the final answer.

## When it fires

Auto-select on papers claiming agents / autonomous loops / tool use / agentic memory. If the paper
makes NO such claim, say so in one line and defer. Distinct from `chimera-lens-forensic-leakage`:
that lens asks "are the numbers earned?"; this one asks "is the agent real?"

## The plumbing audit — expose the real execution cycle

For any agentic claim, decompile the actual implementation (not the diagram):

a. **Orchestration.** Heavy orchestrator (LangChain / AutoGen) vs a basic programmatic `while` loop
   with native API calls vs NO loop at all — a single-pass prompt disguised as an "agent". Name
   which one it actually is.
b. **State.** True mutable internal state that persists and updates, vs "context stuffing" —
   prepending retrieved text / history into the prompt each call. Context-stuffing is not state.
c. **Execution cycle.** Sketch the actual loop in a few lines of stripped-down pseudocode. If the
   "agent" is really one API call, say so plainly.

## Output contract

Apply the shared academic-taste contract — `../_shared/falsifiability.md`. **Mechanism + Evidence +
Falsifiability**:

- **Plumbing verdict** — the explicit call: real loop / framework-wrapped loop / single-pass call
  disguised as an agent.
- **State verdict** — true mutable state vs context-stuffing.
- **Falsifiability** — the test that would expose the illusion (e.g. "remove the orchestrator; if
  behavior is unchanged, it was one prompt").

## Red lines
- ❌ Not a tone filter — do not duplicate `chimera-bb-persona`'s restyle role. This lens SURFACES a
  structured architectural verdict; bb STYLES the final answer. Different jobs.
- ❌ Do not accept an architecture diagram as evidence of a loop — demand the execution cycle.
- ❌ Falsifiability is mandatory (`../_shared/falsifiability.md`).
- ❌ Pure English only. No opportunistic refactor.
