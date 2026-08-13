# Sprint C.3b — `evidence_base` extended to K

**Phase:** L.C (Colligo) · **Risk:** 🟡 MED · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Ratification:** Architect, 2026-08-12 (phase-doc D4)
**Executed by:** `chimera-sprint-executor` (pinned Sonnet). Scope repair + verification by the
Opus main session; commit owned by main.
**Outcome:** ✅ Pass — **after a main-session scope repair (see below).**

## Why

W1 verifies a claim that usually lives in a **Knowledge** node, and its verdict artifact is that
claim's supporting evidence. No legal K edge expressed "supported by this verdict" —
`evidence_base` is the semantically correct edge and was scoped I-node-only in both the canonical
doc and the code. Without it the phase Mission (every committed node's support chain is
traceable) is unreachable, and C.3c has nothing to stage.

I2.2 (Tier 2) states the edge vocabulary is mutable — "edges may be added or merged" — with
changes documented in `NODE_ONTOLOGY.md`. A documented evolution, not a canonical breach.
`INVARIANTS.md` untouched.

## Changes

- `docs/ARCHITECTURE/NODE_ONTOLOGY.md` §2 — `evidence_base` row's *Applies to* becomes `K I`; the
  K canonical set gains it; a ratification note records the justification against **I0.2**
  (support-bearing edges stay structural and traversable) and **I1.3** (support chains traceable
  to Tier-1 evidence), and flags that Phase K's monotonicity gate will read this edge on K nodes.
- `mcp-servers/chimera-papers/staging_service.py:14` — `_TYPE_EDGES["knowledge"]` gains
  `"evidence_base": []`. One change unlocks both `stage_link_patch` (`:227-231`) and
  `apply_link_patch` (`:281-285`), which validate against the same dict.
- `tests/test_link_tools.py` — `evidence_base` accepted for a knowledge node; still refused for a
  type that does not carry it.
- **Scope repair (main session):** `tests/test_staging_tools.py:24` — the `CANONICAL` mirror dict
  gains `evidence_base`.

## The scope error was the plan's, not the executor's

The batch plan named three files. The change legitimately required a fourth: `test_staging_tools.py`
carries its own hardcoded `CANONICAL` dict mirroring NODE_ONTOLOGY §2, and
`test_ontology_mirrors_node_ontology_doc` asserts `_TYPE_EDGES` equals it. That test **failed
correctly** — it is the code-mirrors-canonical guard and it fired exactly when the canonical moved.

The executor declined to touch a file outside its named scope and reported it instead. That was
the right call under a red line that forbids opportunistic edits; the planning miss was mine, and
the repair was made in-session rather than by widening a sprint mid-flight.

(`test_architecture_dataflow.py::test_committed_artifact_matches_current_source` also failed in
the same window. It belongs to **C.3a**, not here — the regenerated delta is a line-number shift
from C.3a's docstring edit.)

## Verification

| Command | Result | Exit |
|---|---|---|
| `pytest tests/test_link_tools.py -q` | `11 passed` | **0** |
| negative control — `_TYPE_EDGES` line reverted | `FAILED ...::test_stage_link_patch_accepts_evidence_base_for_knowledge` · `ValueError: Invalid edge 'evidence_base' for node type 'knowledge'` | **1** |
| negative control — restored | `11 passed` | **0** |
| full suite (post-repair) | `233 passed in 6.98s` | **0** |

## Red lines

All held. Only `evidence_base`, only for `knowledge`. `collides_with` / `informed_by`
(`ENFORCEMENT_DEBT` D-3) untouched and still not emittable — out of scope by design.
`INVARIANTS.md` untouched. No direction or support-bearing semantics changed. Pre-existing
`DTZ005` ruff findings on `staging_service.py` left alone (confirmed pre-existing).

## Notes

`ENFORCEMENT_DEBT` D-3's "code sync owed" note in NODE_ONTOLOGY §2 remains accurate for
`collides_with` / `informed_by`; this sprint closed neither, deliberately.
