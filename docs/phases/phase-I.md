# Phase I — Isostheneia: Adversarial Dialogue Lifecycle

**Status:** Queued (after Phase K)
**Predecessor:** Phase K (Katalepsis)

## VISION — Why Isostheneia

┌──────────────────────────────────────────────────────────────────────────┐
│ Isostheneia (ἰσοσθένεια, Pyrrhonist): EQUAL FORCE. Two opposed arguments │
│ held at strengths so evenly matched that assent cannot be compelled —    │
│ the condition under which judgment is suspended rather than settled by   │
│ fatigue, turn order, or authority.                                       │
│                                                                          │
│ Chimera does not want permanent suspension. It wants suspension to be    │
│ the DEFAULT STATE that only evidence — and only the Architect (I0.1) —   │
│ is permitted to end.                                                     │
│                                                                          │
│ Phase K makes a single verdict structurally honest. Phase I makes the    │
│ DIALOGUE structurally honest: it measures whether two framings were ever │
│ actually at equal force, and refuses to let a settlement pass as earned  │
│ when nothing earned it.                                                  │
│                                                                          │
│ Success metric: a settled position arrives carrying the round it settled │
│ at, the evidence that settled it, and the losing framing intact — and a  │
│ re-run with the Architect's apparent preference INVERTED settles the     │
│ same way.                                                                │
└──────────────────────────────────────────────────────────────────────────┘

### The failure taxonomy

Isostheneia is not a mood, it is a measurable property of a dialogue, and it fails in
exactly four ways. One is a precondition; three are breakages, and two of those are
*opposite* errors.

**0. Deviation / pass@k is the PRECONDITION.** Two positions cannot be held at equal force
if the generator can only produce one. If k independent samples collapse to a single
framing, the "debate" is one position rehearsed twice and isostheneia is unreachable **by
construction, not merely unachieved** — the same distinction `criteria/field/streaming-video-memory.md`
draws when a system's memory is fed whole into context: the capability is excluded by the
architecture, so no experiment can test it. Diversity is not a quality knob here. It is the
entry condition, and a harness that never measures it is asserting its own premise.

**1. Entropy collapse = LOSS of isostheneia.** One side beats the other *too early*: the mass
over positions sharpens before the evidence warrants it. Note what is and is not wrong —
collapse is not wrong because it picks a side. Dialogues are supposed to end. It is wrong
because it picks **before**, and the resulting settlement records a winner without recording
a reason.

**2. Premature stopping = FAKE isostheneia.** Balance that was never contested. From outside
it is indistinguishable from the real thing: two positions, no winner, an honest-looking
suspension. But nothing pushed. This is the theater form, and by the north star it is
**negative value** — worse than an openly one-sided read, because it launders *"we did not
check"* into *"the evidence was balanced."* An unexamined tie is not a tie.

**3. Sycophancy / instruction-following = isostheneia broken TOWARD THE ARCHITECT.** The
third party in a two-party dialogue. Here the balance breaks not between advocate and
skeptic but toward whoever holds the session: the operator's apparent preference acts as an
unmeasured weight on one pan. This is the most dangerous of the three because it is
invisible to both debaters and to the Architect — who then reads their own framing back as
independent confirmation. It is the confession's framing-bias failure (`phase-K.md`) with a
human as the source of the frame instead of the paper's authors.

**(1) and (2) are opposite errors, and that is the point.** Isostheneia is neither "maximize
disagreement" nor "reach consensus". It is: *hold force equal until evidence — not fatigue,
not turn order, not deference — settles it.* A harness tuned only against collapse will stop
too late and call exhaustion balance; one tuned only against stalling will collapse and call
speed decisiveness. Both must be instrumented, or optimizing either produces the other.

### Falsifiability

Per `.claude/skills/_shared/falsifiability.md`, each failure needs a measurement or it is
decoration:

| Failure | Signal | Settling measurement |
|---|---|---|
| 0 — no deviation | semantic spread across k sampled framings | spread ≈ 0 → report "isostheneia unreachable" and do NOT run the debate; a one-voice debate must fail loudly, not produce a tidy transcript |
| 1 — entropy collapse | position mass per round vs **new evidence** introduced that round | a sharp drop in a round that introduced no new evidence is collapse, not convergence |
| 2 — premature stopping | evidence introduced in the FINAL round | zero → the settlement is unearned; flag the *verdict*, not the position |
| 3 — sycophancy | preference-swap re-run | invert the Architect's apparent preference; if the settlement follows the operator rather than the evidence, the harness is measuring deference |

The preference-swap probe is the phase's sharpest instrument and its own success metric. It
is also the only one of the four that can catch a failure the Architect cannot see unaided.

### Why this generalizes

These are not Chimera's failures; they are the failure modes of automated research harnesses
as a class. Multi-agent debate, self-consistency voting, and LLM-as-judge ensembles all
**assume a diversity they never measure** (failure 0) and **date a convergence they never
justify** (failures 1 and 2), while every one of them runs inside a session whose operator has
a visible preference (failure 3). A debate framework that reports only its final answer has
discarded precisely the evidence needed to know whether the answer was earned.

The same shape appeared in this repository on 2026-08-12, in the verification domain rather
than the dialogue one: three verifiers returned PASS — one testing a substring, one aimed at
the wrong actor, one chained to a symbol that had been renamed — and each was a check that
stopped before it could fail. Premature stopping wearing a green light. That is failure 2
with no debate anywhere in sight, which is the argument that this taxonomy is about
inquiry itself and not about dialogue mechanics.

## Mission

Lifecycle-managed adversarial reasoning where opposing framings are maintained
at equal force until the Architect settles. Every round is committed to vault.
Codex audits every session. The harness monitors collapse; humans decide when to stop.

## Key Architecture Constraint

**Use Claude Code's native harness wherever possible.** The orchestration engine
does NOT exist as a hand-rolled Python FSM unless I.0 proves the native harness
cannot do it. Native session management, Task spawning, and hook infrastructure
are the FIRST candidate for lifecycle management. A vault-stored engine or
custom state machine is the FALLBACK only if native primitives are insufficient.

**I.0's load-bearing question:** Can Claude Code's native Task + session primitives
carry the dialectic lifecycle (round sequencing, compliance check dispatch,
convergence monitoring, fork-from-checkpoint, codex dispatch, stop/continue
decision surface)? If YES → orchestration is a skill, not an engine.
If NO → identify exactly which primitives are missing and build only those.

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| I.0 | **BLOCKING AUDIT:** Can native Claude Code harness carry the dialectic lifecycle? What primitives exist (Task lifecycle, session hooks, checkpoint, fork)? What's missing? |
| I.1 | Vault/Dialectic/ schema: round nodes, branch structure, compliance fields |
| I.2 | Role contracts via lens: behavioral obligations derived from lens/*.md + compliance checker subagent |
| I.3 | Round protocol: turn structure, min-rounds, convergence monitoring signal |
| I.4 | **Orchestration: skill OR engine (decided by I.0).** If native harness suffices → skill. If not → minimal custom engine covering only the gap. |
| I.5 | Checkpoint + non-destructive fork from any committed round |
| I.6 | Codex mandatory: zero-shot new session, once per dialectic session, independent framing + falsification |
| I.7 | Human gate: stop/continue/fork surface for Architect confirmation |
| I.8 | Phase K integration: dialectic output → W1 offer on empirical claims |
| seal | Verify on confession 99.8%/96.8% fixture: two framings maintained, codex differs, Architect settles |

**I.0 is BLOCKING.** I.4's entire shape depends on I.0's answer.
If I.0 proves native harness sufficient → I.4 = thin skill (~20 lines).
If I.0 proves insufficient → I.4 = custom FSM (the heavy sprint).

## Design Decisions

- **Codex mandatory, once per session, zero-shot.** New session = no contamination.
  Human reviews. Cost absorbed (GPT Pro). Structural cross-reference, not selective.

- **Lens = behavioral obligation spec.** forensic-leakage lens = skeptic's checklist.
  BB persona = voice layer only (orthogonal). Compliance check = "did output address
  all lens obligations with verbatim evidence?"

- **Behavioral obligations, not persona.** "Enumerate N objections with verbatim
  evidence; do not concede without refutation" — not "be a skeptic."

- **Vault/Dialectic/ = append-only canonical ledger.** Every round committed as a
  harness node. Fork = new branch from checkpoint, never edit original.

- **Stopping is human-confirmed.** No auto-stop. Convergence monitoring SURFACES
  flags; Architect DECIDES. Machine-time monitors, human-time settles.

- **Native harness first, custom engine as fallback only (this phase's key constraint).**

## Hard Sealing Conditions

1. I.0 definitively answers: which lifecycle primitives are native vs must-build.
2. Compliance checker detects seeded obligation violation (verbatim evidence missing).
3. 3-round session: 3 vault/Dialectic/ nodes committed, compliance per round, convergence measured.
4. Fork is non-destructive (original branch unchanged).
5. Codex produces independent framing on 99.8%/96.8% that differs from Claude framings.
6. Architect confirms stop (not auto-terminated).

## Cross-Sprint Red Lines

- ❌ No custom orchestration engine unless I.0 proves native harness insufficient.
- ❌ Vault/Dialectic/ is append-only. No overwrite, no edit committed rounds.
- ❌ Roles = behavioral obligations from lens, never persona instructions.
- ❌ Codex once per session, zero-shot, mandatory. Not every round.
- ❌ No auto-stop. Convergence flags surface; humans decide.
- ❌ No new MCP server. Codex via existing Task/MCP pattern.
- ❌ Phase K provenance gates apply to dialectic empirical claims (W1 offer).

## Out of Scope

- Fully automatic stopping classifier (DR proved none exist reliably)
- Semantic quality judgment of which branch is "better" (research-grade)
- Codex in every round (unnecessary, cost-wasteful, epistemically unjustified)
- Replacing Phase K's single-shot multi-framing (I extends it, doesn't replace)
