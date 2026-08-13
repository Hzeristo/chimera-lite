# Sprint C.1 — The friction instrument

**Phase:** L.C (Colligo) · **Risk:** 🟢 LOW · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Audit:** `docs/audits/L.C.0.md` · **Spec:** `phase-L.C.md` D1/D2
**Executed by:** Opus main session (measurement + judgment-shaped; not delegated).
**Outcome:** ⚠️ **PARTIAL — closes on repo/vault evidence; two registers await the Architect.**

## What was done

Authored `docs/audits/L.C.1-friction-baseline.md`: the metric definition (three registers per
D1), the reproduction commands, the composition-drift baseline (D2), and per-route counts.

Measured against the live vault (`D:\MAS\project_chimera_vault`), 2026-08-12.

## Deviation declared

The batch plan names the output `docs/audits/L.C.1-friction-baseline.md`, and that path was used.
`chimera-code-taste`'s folder rule says the skill does not write `audits/`. The approved plan's
explicit output location was followed over the general guard, because the artifact is measurement
evidence (audit-shaped), not an execution record. This file is the execution record.

## Results

**Composition baseline:** 378 inbox scout cards · 18 deep-reads · **2** committed K nodes ·
6 Harness artifacts — against **7** hand-authored judgment nodes (6 T, 1 I, **0 D**).

**Route 3 — measured, and it does not complete.** All 6 Harness artifacts are `PENDING_REVIEW`.
`_VALID_MODES` has no `promote` (`result_service.py:56`) while `phase-L.md:139-142` declares the
state. Not one artifact has ever been promoted, rejected, or marked stale. The route has never
been walked to its end, which is why the missing terminal operation survived two phase specs.

**Route 2 — partial.** Skill-side invocations and the `informed_by` transcription cost are
measured; the authoring session's own action count is not observable from here.

**Route 1 — Architect-blocked by construction.** No repo surface at all; friction lives entirely
in Obsidian. Recorded as the finding it is, not as a gap.

## Acceptance

- [x] Metric defined with counting rules — the transcription register explicitly excludes the
      Architect's own prose, without which route 1 would score as maximally high-friction
- [x] Reproduction commands recorded, re-runnable at seal
- [x] Composition-drift baseline with an explicit window start (2026-08-12)
- [x] Route 3 baselined
- [~] Routes 1 and 2 — §5 of the baseline lists the two data owed from the Architect
- [x] No route tuned while measuring (phase red line held)
- [x] No code touched

## Findings carried out

1. Route 3 has never been completed — owned by C.3a.
2. Zero D nodes, one schema-conformant I node: K/T/I/D is in practice a K/T ontology, so D2's
   drift measure is near-degenerate on two axes.
3. `Insight/` holds 6 legacy free-form notes outside the schema, invisible to `vault_query`.
4. A stray `....md` exists in `Insight/`, `Decision/`, `Knowledge/` — excluded from counts, not
   investigated (out of scope).
5. `chimera_tier` is absent from every hand-authored judgment node, consistent with
   `NODE_ONTOLOGY.md §7.1`. Count the judgment side by `type` + folder, never by tier.

## Red lines

All held. No code touched; no route tuned during measurement; no estimated counts recorded
(unmeasurable registers are marked blocked, not guessed).
