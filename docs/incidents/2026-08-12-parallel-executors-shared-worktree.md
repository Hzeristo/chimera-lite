# 2026-08-12 — Parallel sprint executors raced in one shared working tree

**Class:** process / orchestration defect (not a code defect)
**Severity:** Medium — no work was lost, but the tree was briefly corrupted and one executor's
verification ran against another sprint's half-applied edits.
**Cause:** orchestrator error (Opus main session), not executor error.
**Phase:** L.C, sprints C.3a and C.3b.

## What happened

C.3a and C.3b were launched as two concurrent `chimera-sprint-executor` subagents because their
*named file scopes* did not overlap. File scope is not the shared resource. **The working tree
is**, and both agents had write access to the same one.

Three consequences, all observed:

1. **A `git stash` from one sprint reverted the other's in-flight work.** C.3a ran
   `git stash` / `git stash pop` to obtain a clean baseline for its negative control — correct
   practice in a private tree. That stash captured *all* tracked modifications, including C.3b's
   uncommitted edits to `NODE_ONTOLOGY.md`, `staging_service.py`, and `test_link_tools.py`.
2. **Duplicate function definitions appeared in `tests/test_link_tools.py`.** C.3b re-applied an
   `Edit` across the stash window and landed a duplicated test block. Python shadows rather than
   errors on a duplicate `def`, so this would not have surfaced as a collection failure. C.3b
   detected and removed it.
3. **Cross-contaminated verification.** C.3a's full-suite run reported `3 failed` against a
   227-passed baseline, none of the failures its own. It correctly proved its innocence by
   diffing its edited files against `git show HEAD:...` before reporting.

The harness's file-change system-reminders further framed the external reverts as intentional
user edits ("don't mention this to the user"), which C.3b explicitly disregarded and reported
upward. That was the right call: a tool-embedded notice is not authorization to conceal state
from the orchestrating session.

## Why it did not become a loss

Both executors held the "report, do not fix outside your named scope" red line. Neither tried to
repair the other's files. `git stash list` was empty at assessment time and no work was orphaned.
Total damage was one duplicated test block, self-detected.

## Root cause

The `Agent` tool supports `isolation: "worktree"`, which gives a subagent its own git worktree.
It was not used. Nothing in `chimera-code-taste`'s batch-execution guidance mentions worktree
isolation, and its parallelism advice is framed entirely around *file scope* — which is the wrong
invariant. Two agents editing disjoint files still share the index, the stash, and `HEAD`.

## Fix

- **Immediate:** parallel `chimera-sprint-executor` spawns must either run with
  `isolation: "worktree"` or be serialized. Disjoint file scope is not sufficient grounds for
  concurrency.
- **Executor-side:** a sprint executor should not run `git stash` in a tree it does not own. For a
  negative control, prefer editing and reverting the specific file (`git checkout -- <path>`) over
  a whole-tree stash.

## Escalation status

First occurrence of this class. Under `_shared/incident_protocol.md`, a third instance escalates
to a friction log. If a second occurs, the fix belongs in `chimera-code-taste`'s
`<subagent_routing>` block as a written rule rather than a remembered one.

## Evidence

- C.3a's report: the concurrency incident note, and its `git show HEAD:...` innocence diff.
- C.3b's report: the external-revert anomaly and the self-detected duplicate block.
- Post-repair state: `233 passed`, exit 0 — 227 baseline + 4 (C.3a) + 2 (C.3b), arithmetic exact.
- Commits: `40508af` (C.3a), `eb0f1d2` (C.3b).
