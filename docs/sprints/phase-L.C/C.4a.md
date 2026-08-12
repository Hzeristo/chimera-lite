# Sprint C.4a — Close D-3: `_TYPE_EDGES` mirrors the canonical

**Phase:** L.C (Colligo) · **Risk:** 🟡 MED · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` (C.4 split per its own guidance: C.4a closes D-3, C.4b
builds the proposal path)
**Executed by:** `chimera-sprint-executor` (pinned Sonnet), **serialized** — no parallel spawn,
per `docs/incidents/2026-08-12-parallel-executors-shared-worktree.md`. Reviewed, independently
negative-controlled, and committed by the Opus main session.
**Outcome:** ✅ Pass

## Why

`ENFORCEMENT_DEBT` D-3: `collides_with` and `informed_by` were ratified into the canonical by r2
and never added to `_TYPE_EDGES`, so no node could carry either. For `informed_by` this meant
**I0.5's provenance mandate had no mechanism at all**.

The correction that made this sprint possible: `_TYPE_EDGES` is not only the staging creator's
dict. It has three consumers — `staging_service.py:104` (`create_staging_node`, which rejects
T/I/D) and `:225-230` / `:279-284` (`stage_link_patch` / `apply_link_patch`), which validate edges
on **existing** vault nodes of any type, routinely hand-written Thoughts. So one dict entry is
load-bearing on every caller at once, and adding `informed_by` is what makes it writable onto a
hand-authored judgment node. This does not touch I0.5: that invariant reserves the **body**, and
an edge is metadata, not content (D-7).

## Changes

- `staging_service.py:13-18` — `_TYPE_EDGES` now mirrors `NODE_ONTOLOGY.md` §2 exactly:
  `collides_with` on all four types, `informed_by` on **thought / insight / decision only**.
  `knowledge` deliberately excluded — I0.5 scopes `informed_by` to judgment nodes.
- `tests/test_staging_tools.py` — the `CANONICAL` mirror updated to the true §2 sets. It had been
  mirroring the *code*, which is why it never failed while the doc and code disagreed.
- `prompts/obsidian_tpl/Tpl_{thought,insight,decision}.md` — `informed_by: []` added.
  `Tpl_knowledge.md` untouched.
- `tests/test_link_tools.py` — `informed_by` accepted for `thought`, refused for `knowledge`.
- `docs/ARCHITECTURE/ENFORCEMENT_DEBT.md` — **D-3 moved to Discharged.**

**Main-session follow-up (outside the executor's named scope, hence mine):** two claims in
`NODE_ONTOLOGY.md` went stale the moment the code changed and were corrected —
the §2 "Code sync owed" note asserting the code "still implements the pre-r2 seven-edge set", and
§4's snapshot claiming to be "exactly the §2 canonical set" while showing the pre-r2 set. §4 is
now annotated as a superseded O.1b-era record rather than rewritten. §5 gained the `informed_by`
vault-template sync as user work.

## Verification

| Command | Result | Exit |
|---|---|---|
| `pytest tests/test_staging_tools.py tests/test_link_tools.py -q` | `20 passed` | **0** |
| full suite | `238 passed` (236 baseline + the 2 new regressions) | **0** |
| `pytest tests/test_architecture_dataflow.py -q` | `27 passed` — no regen needed | **0** |
| `ruff check staging_service.py` | 4 `DTZ005`, all outside the diff, confirmed pre-existing against `git stash` | 1 |

**Negative control — run twice.** The executor reported one; the main session re-ran it
independently after a first attempt of its own failed silently (a PowerShell parse error meant the
file was never modified and the "pass" proved nothing — caught, redone). Removing `informed_by`
from `thought` fails **two** guards:

```
FAILED tests/test_link_tools.py::test_stage_link_patch_accepts_informed_by_for_thought
FAILED tests/test_staging_tools.py::test_ontology_mirrors_node_ontology_doc
2 failed, 18 passed — exit 1
```

Restored: `238 passed`, exit 0.

## Red lines

All held. `informed_by` never added to `knowledge`; `INVARIANTS.md` untouched (FROZEN); no
direction or support-bearing semantics changed (`informed_by` remains **not** support-bearing, so
this discharge does not touch monotonicity); the Obsidian vault's own `templates/` untouched —
repo sources only, the sync is the Architect's.

## Note carried

The executor ran `git stash` to confirm pre-existing ruff findings. Harmless here because the
batch was serialized, but it is the same manoeuvre that caused this morning's incident. The
incident's rule — *do not stash a tree you do not own; revert the specific file instead* — lives
in a doc the executor never reads. It belongs in the agent definition or in
`chimera-code-taste`'s routing block, not in my memory of it.
