# Phase L.C — Colligo: Seal Review (Functional)

**Date:** 2026-08-12 · **Branch:** `phase-L.C` (19 commits) · **Suite:** 241 passed, exit 0
**Spec:** `docs/phases/phase-L.C.md` · **Plan:** `docs/plans/Phase-L.C-batch.md`
**Verdict:** ⚠️ **Functionally sealed** — 8 of 8 sprints executed; 4 of 7 hard sealing conditions
met, 1 partial, 2 **open and Architect-owed**. The two open conditions are longitudinal by
construction and cannot be closed from a build session; sealing on the mechanical six is the
Architect's explicit call (2026-08-12).

## Sprints

| Sprint | Goal | Commit | Status |
|---|---|---|---|
| C.0 | Audit — 9 questions, 61 file:line refs | `73a3059` | ✅ |
| C.1 | Friction instrument: metric + baseline, 3 routes × 3 registers | `dc7375d` | ✅ (§5 corrected in C.4b) |
| C.2 | Registration reachability across both surfaces | `4f980a9` | ✅ + negative control |
| C.3a | The `promote` transition route 3 never had | `40508af` | ✅ |
| C.3b | `evidence_base` extended to K | `eb0f1d2` | ✅ |
| C.3c | Route-3 collapse: `chimera-w1-review` | `aeaa860`, live `45d9d4a` | ✅ live |
| C.4a | Close D-3; `informed_by` emittable | `14aa957` | ✅ |
| C.4b | `chimera-propose-links` | `3d550a7` | ✅ mechanism; semantics owed |
| C.5 | Mid-read verification (queue mode) | `4b60e98` | ✅ probe 3/3 + live |
| C.6 | W2 handoff | `ca535e9` | ✅ end-to-end, map withheld |

## Hard sealing conditions

| # | Condition | Verdict |
|---|---|---|
| 1 | (C.1) Metric defined; 3 routes baselined; composition drift with explicit window | ✅ **Met** — `docs/audits/L.C.1-friction-baseline.md`. §5 carried a false claim ("all six T-nodes carry empty edge lists"); corrected to 5 of 6 populated, 15 links. The corrected reading is the stronger one. |
| 2 | (C.2) One assertion over `@mcp.tool` + `.claude/agents/*.md`; every skill covered; **negative control** | ✅ **Met** — `tests/test_registration.py`, 25 assertions; negative control run twice (byte-prepend, agent-file hide). **Caveat (D-8):** the assertion covers files, not the live registry; a component is unreachable for the turn that authors it. |
| 3 | (C.3a+b+c) Pending `[V]` reviewed and promoted in one decision; `evidence_base` staged with correct type and direction | ⚠️ **Partial** — the promote half is verified live (the vault's first `PROMOTED` artifact, `45d9d4a`). The **staging half was never exercised end-to-end**: the only `[V]` (`2606.16353`) has no committed K node, so no edge was possible. The mechanism is unit-tested (C.3b); the route-3 integration of it is not. Closes the first time a `[V]` lands on a paper that has a K node. |
| 4 | (C.4) A hand-authored T/I/D node receives a **proposed** `informed_by`, Architect **orders** the apply, edge lands via the staged-patch path | ❌ **Open — Architect-owed.** Mechanism verified live and the probe patch deleted rather than kept, because this session authored no node while consulting anything; keeping it would have fabricated the provenance the skill exists to protect. Deferred by the Architect 2026-08-12. Needs one real authoring session. |
| 5 | (C.5) A queued claim returns without blocking; both modes coexist — or the probe's failure is the finding | ✅ **Met** — probe passed 3/3; two claims queued against one paper returned `[V]` and `[P]`, attributable, in 113 s and 154 s while this session stayed working. `chimera-w1-runner` binding verified: 9 tools, no `Write`/`Edit`/shell. |
| 6 | (C.6) A W2 promote-candidate triggers extract with gap context, no map dependency | ✅ **Met** — executor given an id and a gap sentence only, instructed to report failure rather than seek a map; reached a staged `deep_read` node. Verified by reading the file. |
| 7 | (VISION gate) Three sessions with seal-time friction numbers beside the baseline; no route against the grain | ❌ **Open — Architect-assessed, longitudinal.** Cannot be produced by a build session: it requires three *real research* sessions. Composition drift is explicitly longitudinal — L.C delivers the baseline; a widening trend later is a re-opening trigger, not a seal blocker. |

## Red lines

All phase-wide red lines **Held**. No tool authored a T/I/D body; no skill calls `apply_link_patch`;
nothing auto-promoted or auto-applied; no `Literal` relaxed to `str`; `write_result`'s `depends_on`
untouched (D-4); `INVARIANTS.md` untouched; `.mcp.json` still two servers; no new MCP tool shipped
in the phase.

One process red line was **violated and logged**: two `chimera-sprint-executor` spawns ran
concurrently in one worktree on the grounds that their file scopes were disjoint — wrong invariant;
they share the index, the stash, and `HEAD`, and C.3a's `git stash` reverted C.3b's work
(`docs/incidents/2026-08-12-parallel-executors-shared-worktree.md`). Orchestration error, not a
sprint failure; the rule is now written into the plan.

## What this phase actually bought

- **I1.4 has an observable at all** — it was one of eight canonical invariants with no verifier
  (D-5), so the phase named for it could have sealed on an impression.
- **Route 3 has a terminal operation.** `phase-L.md:139-142` declared `PENDING_REVIEW → PROMOTED`
  and no code implemented it; all six harness artifacts had sat at `PENDING_REVIEW` since written.
- **I0.5's provenance mandate has a mechanism** (D-3 discharged). `informed_by` was canonical and
  unemittable.
- **A measurement that inverted its own diagnosis.** "The Architect does not fill edges" was false:
  5 of 6 T-nodes carry 15 `derives_from` links. What is never filled is the one key absent from the
  template. **Template presence predicts edge population** — which makes the one-line template
  change, not the skill, the intervention most likely to move the number.

## Debt carried out

| id | what |
|---|---|
| **D-8** (new) | A newly authored agent/skill is unreachable for the turn that authors it; no in-process test can assert the live registry. `friction-260811-01` instance 4. |
| **D-5** | Unchanged — I1.4 now has a *measurement*, not a verifier. |
| **D-4, D-1, D-2, R5b, R6, R2, R3** | Unchanged; none touched by this phase. |
| **D-3, D-7** | Discharged / resolved during this phase. |

## Open items handed to the Architect

1. **Condition 4** — one real authoring session: write a T/I/D node while consulting an artifact,
   let `chimera-propose-links` propose, order the apply.
2. **Condition 7** — three research sessions with friction re-measured against
   `docs/audits/L.C.1-friction-baseline.md`.
3. **`criteria/disposition/_general.md` does not exist**, yet `chimera-w1-verify` documents it as
   the disposition layer countering early-stopping, and `load_criteria` degrades to a silent
   marker. Every W1 verdict ever produced ran without it. Writing criteria is Architect judgment.
4. **`docs/staging/` holds an unreviewed MemDreamer `deep_read` node** from C.6's acceptance run —
   `ascend_node` or discard.
5. **`CLAUDE.md` is stale** (lists 5 `chimera-vault` tools; 11 exist). Outside this batch's write
   authority.
6. **Phase L's own seal** — L has six sprint records and no review; its VISION gate has never been
   assessed. Recorded so the parent is not forgotten under its children.

---

*A functional seal is not a green seal. Conditions 4 and 7 are the two that test whether the phase
did what it was named for, and both are open. What is sealed is that the machinery exists, is
reachable, and was exercised on real fixtures — not that the Architect's routes came out equal.*
