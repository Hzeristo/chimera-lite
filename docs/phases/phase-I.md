# Phase I — Isostheneia: Adversarial Dialogue Lifecycle

**Status:** Queued (after Phase K)
**Predecessor:** Phase K (Katalepsis)

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
