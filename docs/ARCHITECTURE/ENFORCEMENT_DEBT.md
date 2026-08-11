# ENFORCEMENT_DEBT — what the code actually holds

**Status:** ✅ COMPLIANCE RECORD. Extracted from `ARCHITECTURE_RULES.md` Appendix B (2026-08-11).
**Role:** `INVARIANTS.md` and `FORMAL_MODEL.md` state what **MUST BE**. This file states what
**currently IS**, and names the gap between them. It is the only place a gap is allowed to be
recorded, so that an unenforced invariant can never be mistaken for a shipped guarantee.

**This file is NOT canonical.** It never states, reinterprets, or weakens an invariant — it only
reports compliance against one. Where this file and the canonical disagree about what the rule *is*,
the canonical wins and this file is wrong. Where they disagree about what the code *does*, this file
is the record and must be re-verified, never edited to agree.

**Cited by the canonical at:** `INVARIANTS.md:28` (I0.2 → R5b), `INVARIANTS.md:47` (I0.4 → D-1),
`INVARIANTS.md:155` (I2.3 → D-2), `FORMAL_MODEL.md:99` (monotonicity → R5b).

---

## Vocabulary — mode and compliance are orthogonal

Following `AUTO_RESEARCH_REQ_REFS.md §1`. Conflating these is how r1 recorded a requirement as
satisfied by a mechanism it simultaneously reported as unbuilt.

**Enforcement mode** — what the invariant *demands of a conforming design*:

- **STRUCTURAL** — a schema, gate, or code path makes it load-bearing. Violating it is impossible or
  is caught by an automated check.
- **CONVENTION** — held by practice. No mechanism refuses a violation.

**Compliance** — what the code *currently does*, against that demand:

- **HELD** — the demanded mechanism exists and is verified by a named check.
- **OPEN** — the mechanism does not exist. The invariant is a target, not a guarantee.
- **PARTIAL** — some halves hold; the row states which.
- **UNASSESSED** — no anchor. The default. Never assume HELD from silence.

**Every row carries an anchor** (artifact + method). A row without one is UNASSESSED by definition,
regardless of how confident the prose sounds.

---

## Open debt

| id | owed to | mode demanded | compliance | gap | anchor (artifact + method) | lands at |
|---|---|---|---|---|---|---|
| **R5b** | I0.2 | STRUCTURAL | **OPEN** | Monotonicity is not enforced. A well-formed `[V]` resting on a `[U]` dependency is accepted. `support(v)` is never computed; support edges are written and never read back for a comparison. | `ARCHITECTURE.md` Layer 2 — AST verifier `_verify_r5b` returns **VIOLATED**; positive-controlled (a planted comparison flips it to PASS). Re-run: `python scripts/gen_architecture_diagram.py`. | Phase K — K.1 (Queued) |
| **R5b-v** | I0.2 | — *(defect in the checker, not the rule)* | **OPEN** | The R5b verifier greps for comparisons over `depends_on`, an edge the canonical **retired**. `FORMAL_MODEL.md:107` now defines `support(v)` over `{evidence_base, synthesizes, derives_from}`. The verifier's VIOLATED verdict is currently correct **by accident** — it is checking a vocabulary the canonical no longer uses, and would keep returning VIOLATED even if monotonicity were implemented over the correct edges. | `scripts/gen_architecture_diagram.py` `_verify_r5b`; compare against `FORMAL_MODEL.md:107` and `INVARIANTS.md:137-138`. | Before K.1 — the checker must be re-targeted first, or K.1 cannot be verified |
| **D-1** | I0.4 | STRUCTURAL | **OPEN** | Provenance decay is not implemented. No code path propagates STALE from a superseded node to its dependents. `STALE` exists only as a **manual, operator-invoked** status transition on a Harness artifact via `write_result(mode="mark_stale")` — a single-artifact edit, not propagation, and it does not touch K/T/I/D nodes at all. | `mcp-servers/chimera-papers/result_service.py:175` (`_transition` → `"STALE"`), reachable only from `_VALID_MODES` (`:56`); no caller computes dependents. Verified by read, 2026-08-11. | Phase H — **unhomed** (`THEORETICAL_FRAMEWORK.md:302-304`) |
| **D-2** | I2.3 | STRUCTURAL | **OPEN** | The abstract status `stale` has no concrete counterpart in the live node vocabulary. `INVARIANTS.md:155` records the crosswalk row as unimplemented; the other three (`candidate↔unverified`, `staged↔PENDING_REVIEW`, `committed↔active`) are live. | `NODE_ONTOLOGY.md:155-161` §7.2 lists four live statuses — `unverified`, `PENDING_REVIEW`, `active`, `cross_verified` — none of which is `stale`. | With D-1 (same phase) |
| **R6** | I0.5 | STRUCTURAL | **PARTIAL** | No structural gate prevents a future code path from populating a T/I/D **body**. Both mechanisable halves currently hold — `body` is a caller-supplied parameter, and no LLM call is tool-reachable (I1.1) — so no *present* server path can synthesise one. Nothing refuses a future one. | `ARCHITECTURE.md` Layer 2 — verifier returns **PARTIAL** with both sub-checks stated. Note the narrow impossibility per `AUTO_RESEARCH_REQ_REFS.md:218-225`: a gate refusing machine-written bodies is implementable; only *verifying that a human-written body reflects genuine judgment* is not. | **Unhomed** — next authorship sprint |
| **R2** | I0.1 | STRUCTURAL | **PARTIAL** | The gate exists and is verified reachable only from a human invocation. The stronger **seal** claim — "a direct write to the committed tier without `ascend_node` is impossible by code constraint" — has not been verified end-to-end in-context. | `ARCHITECTURE.md` Layer 2 — verifier returns **PASS** for reachability (`_promote_write` reached only by `ascend_node`, no background path). The seal claim is a separate, unrun check. | L.B.3 seal / L.B.6 end-to-end |
| **R3** | I1.2 | STRUCTURAL | **PARTIAL** | The `Knowledge/` write path is structural. The **non-advancement of a scout card** in `inbox/` rests on convention plus the tier axis, not a dedicated refusal. | `ARCHITECTURE.md` Layer 2 — verifier returns **PASS** for the sole-writer property (`promote_node` refuses `deep_read`, `ascend_node` requires it). No check exists for scout non-advancement. | L.B.6 verification |

---

## Discharged

| id | owed to | discharged how | verified by |
|---|---|---|---|
| ~~**R5a**~~ | I0.2 | `write_result.verdict` is `Literal["V","P","U"]` and `mode` a closed `Literal` set, so a malformed tag is rejected by pydantic at the JSON-RPC boundary **before the handler body runs**. Same treatment for `create_node.type`, `mineru_sidecar.action`. | `ARCHITECTURE.md` Layer 2 — verifier flipped **VIOLATED → PASS** on `3f8d107`. Boundary rejection probed directly (`literal_error` raised pre-handler). **Widening any of these back to `str` silently re-opens the gap.** |

---

## The clause this file exists for

> An invariant with no enforcement machinery is a **promise with no teeth yet**. It is listed here so
> it cannot be mistaken for a shipped guarantee, and so the debt is discharged deliberately — not
> quietly dropped when its phase is built.

Two corollaries, both learned the hard way in this repo:

1. **Absence is reported as a failure, not as a blank.** A debt whose machinery was never built is
   OPEN, not "missing" or "n/a". A status that reads as an empty slot gets skipped by a reader, and
   that is how an aspirational rule comes to be read as a shipped one.
2. **A passing half never speaks for its rule.** R5a HELD says nothing about R5b OPEN. Where an
   invariant splits, each half is adjudicated and reported on its own — a merged verdict lets the
   enforced half carry the unenforced one to a clean bill of health.
