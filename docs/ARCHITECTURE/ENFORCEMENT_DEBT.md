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
| **D-3** | I2.2 | STRUCTURAL | **OPEN** | The two edges canonical r2 added — `collides_with`, `informed_by` — are **defined but not emittable**. `StagingService._TYPE_EDGES` implements the pre-r2 seven-edge set, so no node can carry either edge. This matters most for `informed_by`: I0.5 *mandates* it as the provenance record for AI-informed T/I/D nodes, so the invariant currently has no mechanism at all. | `mcp-servers/chimera-papers/staging_service.py:14-17` — the four per-type dicts, compared against `NODE_ONTOLOGY.md §2` canonical sets and `INVARIANTS.md:136`. Verified by read, 2026-08-11. | **Unhomed** — next ontology/code-sync sprint |
| **D-4** | I0.2 | — *(naming, not enforcement)* | **OPEN** | `write_result`'s parameter is still named `depends_on`, a concept canonical r2 retired. The value it records now feeds `support(v)`, and R3's reduction auto-writes `evidence_base` (`FORMAL_MODEL.md:186`). The name now misdescribes what the field is for, and Phase K reads this field. **Deliberately not renamed:** it is a live MCP tool signature reached by `chimera-w1-verify` and the Phase-K design; a rename is a coordinated change, not a doc edit. | `mcp-servers/chimera-vault/server.py:295` (parameter) and `:327` (docstring); `result_service.py` writes it to frontmatter. | With K.1 — rename and call-site update together |
| **D-5** | I0.3, I0.4, I1.3, I1.4, I2.1–I2.4 | — *(verification coverage, not enforcement)* | **OPEN** | **Eight of fourteen canonical invariants have no mechanical verifier.** They render UNCHECKABLE in the generated map — honestly, but that is coverage, not conformance: nothing checks them, so nothing would notice a violation. I0.3 (verification tier-separation) and I0.4 (append-only) are **Tier 0**, where a silent violation means the system is no longer L2. Newly visible only because Pass 2 re-keyed the map to the canonical; under the old R1–R6 keying these invariants were not listed at all. | `ARCHITECTURE.md` Layer 2 — the verdict table renders `UNCHECKABLE` for each, with the reason. Re-run: `python scripts/gen_architecture_diagram.py`. | **Unhomed** — verifier coverage sprint |
| **D-1** | I0.4 | STRUCTURAL | **OPEN** | Provenance decay is not implemented. No code path propagates STALE from a superseded node to its dependents. `STALE` exists only as a **manual, operator-invoked** status transition on a Harness artifact via `write_result(mode="mark_stale")` — a single-artifact edit, not propagation, and it does not touch K/T/I/D nodes at all. | `mcp-servers/chimera-papers/result_service.py:175` (`_transition` → `"STALE"`), reachable only from `_VALID_MODES` (`:56`); no caller computes dependents. Verified by read, 2026-08-11. | Phase H — **unhomed** (`THEORETICAL_FRAMEWORK.md:302-304`) |
| **D-2** | I2.3 | STRUCTURAL | **OPEN** | The abstract status `stale` has no concrete counterpart in the live node vocabulary. `INVARIANTS.md:155` records the crosswalk row as unimplemented; the other three (`candidate↔unverified`, `staged↔PENDING_REVIEW`, `committed↔active`) are live. | `NODE_ONTOLOGY.md:155-161` §7.2 lists four live statuses — `unverified`, `PENDING_REVIEW`, `active`, `cross_verified` — none of which is `stale`. | With D-1 (same phase) |
| **R6** | I0.5 | STRUCTURAL | **PARTIAL** | **Threat model corrected 2026-08-11.** This row previously reasoned: "`body` is a caller-supplied parameter, and no LLM call is tool-reachable (I1.1) — so no *present* server path can synthesise one." That defends against the SERVER authoring a body; the threat is the CALLER, and the caller of the MCP surface is Claude. "Caller-supplied" was the vulnerability, not the mitigation — the same mis-pointed-check shape as the old R3 verifier. The affordance is now removed: `create_staging_node` and the `create_node` tool are knowledge-only, and `promote_node` (which moved staged T/I/D into the vault) is retired, so **no code path authors or writes a T/I/D node**. Residual gap unchanged and narrow: nothing verifies that a hand-written body reflects genuine judgment, which is not mechanisable (`AUTO_RESEARCH_REQ_REFS.md:218-225`). | `staging_service.py` — `create_staging_node` refuses `node_type != "knowledge"`; no `def promote_node` remains; `_ascend_write` refuses any destination but `Knowledge/`. Regressions: `tests/test_ascend_node.py::test_staging_refuses_to_author_judgment_nodes`, `::test_no_code_path_writes_a_judgment_node`, `::test_promote_node_is_retired`. Empirical: every T/I/D node in the vault has spaces in its filename, so none came through the (whitespace-slugging) retired writer. | **Unhomed** — next authorship sprint |
| **R2** | I0.1 | STRUCTURAL | **PARTIAL** | The gate exists and is reachable only from a human invocation. The stronger **seal** claim — "a direct write to the committed tier without `ascend_node` is impossible by code constraint" — now holds for `Knowledge/` and was verified by execution (2026-08-11), where it previously **failed**: a `type: knowledge` node with an absent or `scout` tier reached `Knowledge/` via `promote_node`. Residual: the claim is enforced for the K destination, not asserted for T/I/D destinations (see the I1.2 scope question below). | `ARCHITECTURE.md` Layer 2 — verifier returns **PASS**. **Correction:** this row previously read "`_promote_write` reached only by `ascend_node`, no background path", which was false at the function level — `_promote_write` has two callers (`staging_service.py:145` `promote_node`, `:162` `ascend_node`). The verifier only ever computed tool-reachability (`find_chain` over `@mcp.tool` names); the prose over-claimed what it established. `promote_node` is not an MCP tool, which bounded the exposure to in-process callers. | L.B.3 seal / L.B.6 end-to-end |
| **R3** | I1.2 | STRUCTURAL | **PARTIAL** | The `Knowledge/` write path is now structural **on the destination**: `_promote_write` refuses any write routed to `Knowledge/` unless the caller passes `allow_knowledge=True`, which only `ascend_node` does. Residual gap unchanged: the **non-advancement of a scout card** in `inbox/` rests on convention plus the tier axis, not a dedicated refusal. | `ARCHITECTURE.md` Layer 2 — verifier returns **PASS**, and is negative-controlled: run against the pre-fix source (`git show 67cba2c:…/staging_service.py`) the same verifier returns **VIOLATED**. Regression: `tests/test_ascend_node.py::test_promote_node_refuses_any_knowledge_node_whatever_its_tier`. | L.B.6 verification |
| **D-6** | I1.2 | — *(canonical scope question)* | **RESOLVED 2026-08-11 — settled in the canonical, and moot in code** | The question was whether I1.2's "committed tier" means `Knowledge/` alone or all of {K,T,I,D}, since `promote_node` wrote T/I/D at `status: active`. **The Architect settled it from the canonical side** (commit `40b94c4`): I1.2 now scopes the staging gate to "AI-authored Knowledge node", so the gate — and `ascend_node`'s sole-writership — govern the K tier. T/I/D were never in scope, consistent with I0.5 reserving their bodies for the Architect. Independently moot in code: `promote_node` is retired and no path writes T/I/D, so `ascend_node` is the sole writer of every committed destination under either reading. Note for the record: `FORMAL_MODEL.md:91-97`'s human-commit transition is generic — `Architect(v) = promote ⟹ σ' = committed` — and names no gate, so it never settled this either way. | `INVARIANTS.md` I1.2 (as amended by `40b94c4`), I2.1, I0.5; `FORMAL_MODEL.md:91-97`; code at `staging_service.py` (`_ascend_write`, single caller). Verified by read + execution, 2026-08-11. | Closed |

---

## Discharged

| id | owed to | discharged how | verified by |
|---|---|---|---|
| ~~**R5a**~~ | I0.2 | `write_result.verdict` is `Literal["V","P","U"]` and `mode` a closed `Literal` set, so a malformed tag is rejected by pydantic at the JSON-RPC boundary **before the handler body runs**. Same treatment for `create_node.type`, `mineru_sidecar.action`. | `ARCHITECTURE.md` Layer 2 — verifier flipped **VIOLATED → PASS** on `3f8d107`. Boundary rejection probed directly (`literal_error` raised pre-handler). **Widening any of these back to `str` silently re-opens the gap.** |
| ~~**R5b-v**~~ | I0.2 | The R5b verifier was re-targeted from the retired `depends_on` to the canonical support-bearing set `{evidence_base, synthesizes, derives_from}` (`SUPPORT_BEARING_EDGES`), so its VIOLATED verdict is now *earned* rather than an artifact of checking a dead vocabulary. It will flip to PASS when — and only when — a real comparison over a support edge appears. | Pass 2, 2026-08-11. `scripts/gen_architecture_diagram.py` `_verify_r5b`; the constant carries an inline note that re-adding `depends_on` re-opens this. **This discharge does not touch R5b itself, which remains OPEN** — the checker is now correct; the gate it checks for still does not exist. |

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
