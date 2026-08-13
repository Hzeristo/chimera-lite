# Sprint C.5 — Mid-read verification (queue mode)

**Phase:** L.C (Colligo) · **Risk:** 🔴 HIGH · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Approval:** Architect, per-sprint, 2026-08-12
**Executed by:** Opus main session (probe + skill/agent authoring is reasoning-shaped).
**Outcome:** ✅ Probe passed on all three gates; queue mode built. One gate deferred to a session
restart, for a reason that is itself the sprint's most important finding.

## Task 1 — the probe (the gate that could have ended the sprint)

Run as a detached `general-purpose` agent at Sonnet, instructed to report failures verbatim and
never work around them.

| Gate | Question | Result |
|---|---|---|
| (a) | Can a background subagent call `chimera-vault` MCP tools? | **PASS** — `load_criteria` returned the composed criteria block |
| (b) | Can it spawn its own judgment sub-subagent? | **PASS** — spawned `chimera-verbatim-verifier`, which returned in 4.7 s |
| (c) | Does completion identify which queued claim finished? | **PASS** — see below |

Gate (a) was confirmed twice: the probe also called `write_result` and the artifact
(`Harness/w1_verdict__PROBE-C5-DELETE-ME.md`) was observed on disk independently of the agent's own
report, then deleted. It asserted nothing; it was a reachability probe, not a verdict.

**Gate (b) is the one D6 was worried about,** and it passed: a detached subagent can spawn its own
detached subagent. So the full W1 chain — main session → runner → isolated verifier — survives
backgrounding with isolation intact. The paper's text never enters the Architect's context, which
was the constraint that made `TaskService` structurally unusable in the first place.

**Gate (c) resolved better than specified.** The Architect's session gets control back the moment
the spawn returns, and completion arrives as a task notification. Attribution is not automatic
though — it is *designed*: the runner's report leads with a `queued-claim: <identity>` line, because
with several claims outstanding a verdict that cannot be attributed is worse than no verdict.

## What was built

- **`.claude/agents/chimera-w1-runner.md`** — pinned Sonnet. Runs the W1 loop detached and returns
  the attributable report block. Orchestration only: it is forbidden from judging, and returns `[U]`
  if the verifier fails to spawn rather than deciding alone.
- **`.claude/skills/chimera-w1-verify/SKILL.md`** — a queue-mode section and its red lines. The
  foreground path is untouched; both modes coexist.

**Why a pinned agent and not the `general-purpose` spawn the probe used.** Not taste —
`check_model_routing.ps1` check 4 fails any skill containing `subagent_type: "general-purpose"`.
The probe's construction is already illegal in a skill by an enforced rule. The pin also bounds a
detached agent's authority by construction: the runner has no `Write`, no `Edit`, no shell, and
reaches the vault only through MCP. An unwatched background process should not hold write authority
it never needs.

## Task 3 — identity discipline

`identity` IS the artifact filename (`result_service.py:173`) and `write_result` defaults to
`supersede`, so under the old rule ("`identity` = the paper's arXiv id") two *different* claims about
one paper silently overwrite each other. Now `<arxiv_id>__<claim_slug>`.

Measured rather than assumed: all four existing verdicts carry `superseded_prior: false`, so the
collision has **not** yet destroyed anything — N=4, zero losses. It was, however, already worked
around by hand once: `w1_verdict__2605.06527-best-model-55.2.md` carries a hand-appended claim slug
that no rule asked for. The fix promotes an existing manual workaround into the skill.

**Bounded, not eliminated:** `_slug` truncates at 80 characters, so two long slugs sharing a prefix
still collide. The skill asks for 4-6 words for that reason.

**Enforcement, stated honestly:** `tests/test_write_result.py` pins the *mechanism* (bare id
overwrites; `<id>__<slug>` does not; `__` survives `_slug`). The rule that callers append a slug
lives in prose and is enforced by nothing — a caller passing a bare id still overwrites silently.
Recorded as debt rather than dressed up as a guarantee.

## The finding: a green suite and an unreachable component

`chimera-w1-runner.md` was written, parsed, passed `check_model_routing.ps1`, and passed all 25
`test_registration.py` assertions. Spawning it failed:

```
Agent type 'chimera-w1-runner' not found. Available agents: chimera-breadth-reducer, ...
```

**The agent registry is a session-start snapshot.** A newly authored agent is unreachable for the
remainder of the session that authored it. This is `friction-260811-01` instance 4, arriving through
the exact door C.2 was built to close — and C.2 is not at fault: no in-process test can assert the
live registry, because the gap is a session boundary, not a missing assertion.

This is why the batch's red line says the seal exercises new components **through the live client**.
That rule just caught something.

**Consequence for C.5:** the loop was verified live by running the runner's contract inline in a
detached agent (below). What is *not* verified in this session is the agent-type binding — one
restart away, and owed before this sprint's acceptance is complete.

## Live acceptance run

Two claims about the same paper (arXiv 2606.16353, SelectStream), queued together, deliberately
chosen to test the identity fix and attribution in one run:

| identity | verdict | duration | outcome |
|---|---|---|---|
| `2606.16353__bounded-evidence-budget-frozen-vlm` | **[V]** | 113 s | own artifact |
| `2606.16353__outperforms-prior-streaming-baselines` | **[P]** | 154 s | own artifact |

Both returned leading with their `queued-claim` line, so each was attributable on arrival. During
the ~2.5 minutes they ran, this session executed the full test suite, edited two skills,
regenerated the architecture map, and wrote this document — the session was never blocked, which is
the whole claim of the sprint.

**Three artifacts now coexist for one paper**, all at `superseded_prior: false`:
the pre-existing `2606.16353` (PROMOTED) plus the two new ones. **Under the old rule claim A would
have overwritten the PROMOTED verdict** — the identity fix prevented the destruction of committed
work on its first live run, which is a better argument for it than the N=4 measurement was.

The `[P]` is worth noting as evidence the chain is not rubber-stamping: the verifier declined `[V]`
because the quote it found covers *streaming* benchmarks (StreamingBench, OVO-Bench) while the claim
said *long-video QA*. A scope mismatch caught by an isolated worker two layers out from this
session.

**Caveat on what this run proves.** The loop ran under the runner's contract read from
`chimera-w1-runner.md`, executed by a detached generic agent, because of the registry finding above.
It proves the loop, the isolation, the attribution, and the identity discipline. It does **not**
prove the agent-type binding or the tool-list narrowing — those are what the restart is owed for.

## A regression C.5 caused in C.3c, found by the skill review

Changing `identity` broke a consumer. `chimera-w1-review` declared `identity` to *be* the paper's
arXiv id and resolved the support-edge target with
`search_vault_attribute(key="arxiv_id", value=<identity>)`. With `<arxiv_id>__<claim_slug>` that
lookup matches nothing — and the failure mode is the worst kind: it renders as
`edge: none — no committed K node carries arxiv_id ...`, **identical to the legitimate no-K-node
case**, which the skill's own Notes section says is the normal outcome today. A silent wrong answer
wearing the costume of an expected one.

Fixed in `chimera-w1-review/SKILL.md`: derive the paper id by taking the part before the first
`__`, spelled out rather than left to inference, with the reason stated so a later editor does not
"simplify" it back.

**On the skill-creator pass more broadly.** Its guidance to make descriptions deliberately "pushy"
to combat under-triggering was **not** applied, and should not be. Both skills mutate the vault —
one promotes committed artifacts, the other stages provenance edges — so over-triggering is
strictly worse than under-triggering, and both correctly end their descriptions with "Explicitly
invoked (not ambient)" under I0.1. This is the CLAUDE.md precedence rule doing real work: generic
skill-writing best practice is subordinate to the repo's invariants, and here it points the wrong
way.

## A finding outside the task scope

The probe's `load_criteria` call returned `[no criteria file: criteria/disposition/_general.md]`.
**That file does not exist in the vault.** Yet `chimera-w1-verify/SKILL.md:46-48` documents
`_general` as the disposition layer that "counters early-stopping and binary snap-verdicts", and the
composition order treats it as load-bearing. Every W1 verdict ever produced ran with half its
disposition layer absent, and `load_criteria` degraded silently to a marker rather than saying so.

Not fixed here: writing criteria content is Architect judgment, and C.5's scope is the queue.
Recorded because a criteria file that does not exist cannot shape a judgment, and a skill that
documents it as though it does is exactly the advisory rigor this repo refuses.

## Verification

- Full suite **241 passed**, exit 0 (`ARCHITECTURE.md` regenerated — the agent-count guard fired on
  the new pin, as it did for the last two skills).
- `check_model_routing.ps1` — all passed, including the new pin.
- **Negative control, run and recorded:** hiding `.claude/agents/chimera-w1-runner.md` makes
  `test_agents_named_by_skills_exist` fail with
  ``chimera-w1-verify/SKILL.md references `chimera-w1-runner` ``; restoring it returns 25 passed.
  The skill→agent reference is genuinely enforced, not merely asserted.

## Acceptance

- [x] Probe gates (a), (b), (c) recorded — all pass
- [x] A queued claim leaves the session responsive
- [x] Two claims against one paper produce two artifacts, neither overwriting the other
- [x] Both W1 modes coexist; the foreground path is unchanged
- [x] **`chimera-w1-runner` spawns by agent type** — closed 2026-08-12, one turn later. Returned
      `BINDING-OK` and a tool list matching its frontmatter **exactly**: 9 tools, no `Write`, no
      `Edit`, no shell. The authority narrowing is real, not just declared.

**Correction to the finding above.** No restart was needed. The registry refreshed on a subsequent
turn of the same session and announced the new type. "Unreachable for the remainder of the session"
was over-generalized from a single failed spawn; the true gap is **one turn wide** — the turn that
authors an agent cannot verify it. Narrower than first stated, and still real: D-8 is corrected
rather than deleted, because the too-strong claim was already committed.

## Red lines

Held. Judgment stayed in `chimera-verbatim-verifier` under isolation; nothing routed through
`TaskService`; no queue added to an MCP server; no verdict rendered inline into a reading context
(that is L.D); the foreground mode is unchanged; nothing auto-promoted and nothing auto-applied.
