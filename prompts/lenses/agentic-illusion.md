# Lens: Agentic Illusion Plumbing Audit

## Trigger (function-based)
Apply when the paper FUNCTIONS as a claim of agency — it claims an "agent," an autonomous
loop, tool use, or agentic memory, and asks the reader to trust that the system acts
independently over multiple steps rather than answering once. Do not apply merely because the
word "agent" appears; apply because the paper's argument depends on real autonomous execution
existing. If the paper makes no such claim, say so in one line and defer — do not force the
lens onto a paper that isn't making an agentic claim. Distinct from forensic-leakage (asks "are
the numbers earned?") — this lens asks "is the agent real?"

## Method
Decompile the actual implementation described in the paper — not the architecture diagram, not
the marketing language. For any agentic claim, determine:

1. **Orchestration.** Is the "agent" run by a heavy orchestration framework (LangChain,
   AutoGen, or similar), by a basic programmatic loop (e.g. a `while` condition with native API
   calls and real branching), or is there NO loop at all — a single-pass prompt dressed up with
   agent terminology? Name explicitly which one it actually is, based on what the paper
   describes as the execution mechanism, not the framing language it uses.
2. **State.** Does the system carry true mutable internal state that persists and is updated
   across steps (a data structure that changes and that later steps read and write), or is
   "memory" really context-stuffing — re-prepending retrieved text or prior history into the
   prompt on every call, with no persistent structure behind it? Context-stuffing is not state;
   name it when found.
3. **Execution cycle.** Sketch the actual loop in a few lines of stripped-down pseudocode based
   on what the paper describes. If, once stripped of framework scaffolding and diagram
   language, the "agent" reduces to one API call, say so plainly and without hedging.

## Discipline
Every finding must satisfy the mandatory triple:
1. **Mechanism** — the explicit plumbing verdict: real loop / framework-wrapped loop /
   single-pass call disguised as an agent. Name which one, concretely.
2. **Evidence** — the state verdict (true mutable state vs. context-stuffing) and the paper
   text or described implementation that supports it; note where the paper is silent on
   implementation detail and the verdict is therefore inferred rather than confirmed.
3. **Falsifiability** — the test that would expose the illusion if it exists (e.g. "remove the
   orchestrator scaffolding; if the observed behavior is unchanged, the system was one prompt
   the whole time"). If no such test can be stated, say the architectural claim cannot be
   checked from the paper as written.
