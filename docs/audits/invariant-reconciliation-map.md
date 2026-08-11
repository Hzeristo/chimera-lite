# Invariant Reconciliation Map — repository vs. the Architect-authored canonical

**Status:** PASS 1 OUTPUT (rebuild r2) — READ-ONLY. Nothing in this map has been applied. No file
other than this one was modified while producing it.
**Produced:** 2026-08-11 · **Supersedes:** the r1 map of the same name, stale in nine rows after the
Architect's canonical revision.
**Gate 0:** PASSED — `INVARIANTS.md` and `FORMAL_MODEL.md` both tracked, 2 commits each, zero
uncommitted changes (`60cc4b2`). All documents the canonical references are committed:
`ENFORCEMENT_DEBT.md` (`1bc761d`), `NODE_ONTOLOGY.md`.

**Canonical (FROZEN, never edited by this pass):** `docs/ARCHITECTURE/INVARIANTS.md`,
`docs/ARCHITECTURE/FORMAL_MODEL.md`.

**Naming note.** `FORMAL_MODEL.md` uses `R1–R4` for *reduction operations*; `ARCHITECTURE_RULES.md`
uses `R1–R6` for *invariant rules*; `ENFORCEMENT_DEBT.md` uses `R2/R3/R5a/R5b/R6` as *debt ids*
inherited from the latter. Below, `R1..R6` means the ARCHITECTURE_RULES register.

---

## Progressive-disclosure check — PASSED

Canonical references resolve to three committed documents: `ENFORCEMENT_DEBT.md`, `INVARIANTS.md`,
`NODE_ONTOLOGY.md`. No unlanded document is referenced. Reconciliation is not blocked.

---

## Closed since r1 — by the Architect's own revision

Recorded so the work is not re-litigated in Pass 2. Nine rows, no action needed.

| r1 id | was | closed by |
|---|---|---|
| C-1 | canonical asserted monotonicity "is pipeline-enforced" while the verifier reported VIOLATED | **RULED as a normative target.** `INVARIANTS.md:22-23` — "MUST BE pipeline-enforced. This is a structural target, not a descriptive claim of current state"; compliance exiled to `ENFORCEMENT_DEBT.md` R5b |
| C-2 | canonical λ carried retired `depends_on`, omitted 4 ratified edges | `FORMAL_MODEL.md:19` — `depends_on` dropped, ratified vocabulary carried, `collides_with` added |
| C-3 | I2.1 omitted the live `synthesis` tier | `INVARIANTS.md:125` — four tier values restored |
| C-5 | two disjoint status vocabularies, no crosswalk | `INVARIANTS.md:151-155` — abstract↔concrete crosswalk added |
| C-6 | canonical made W1/W2 committed-node types | `FORMAL_MODEL.md:14-16` / `INVARIANTS.md:131-132` — `S_c` / `S_h` sort split |
| C-7 | three divergent Tier definitions | `FORMAL_MODEL.md:32-37` — aligned with `TAG_SYSTEM.md §4`, incl. external primary artifacts |
| C-8 | `U(c)` omitted the out-of-scope branch | `FORMAL_MODEL.md:66-67` |
| C-10 | R6's "I nodes only from verified T-groups" had no canonical home | `INVARIANTS.md:96-99` (I1.3) |
| G-1 | I0.5 mandated `informed_by`, defined nowhere | `INVARIANTS.md:136,142-143` — added to I2.2, explicitly non-support-bearing |
| G-5 | canonical had no enforcement-status axis | `ENFORCEMENT_DEBT.md` now owns mode-vs-compliance |

---

## CONFLICTS — existing text contradicting the canonical

Default is "canonical wins." **⚑** marks rows where the existing text carries information the
canonical omits, or where the canonical contradicts itself.

| # | file:line | existing statement | canonical | conflict nature |
|---|---|---|---|---|
| **N-1 ⚑⚑** | `FORMAL_MODEL.md:19` — λ has **8** edges, no `informed_by` | — | `INVARIANTS.md:136` (I2.2) — **9** edges, including `informed_by` | **Canonical contradicts itself.** I0.5 (`:58`) *mandates* provenance record `informed_by`; I2.2 lists it; but λ, the edge-label function of the graph those edges live in, omits it. Either λ gains it, or I2.2 must say why an edge exists outside λ. **Frozen doc — Architect ruling required.** |
| **N-2 ⚑** | `NODE_ONTOLOGY.md:54-57` — ratified 7-edge set, no `collides_with`, no `informed_by` | `INVARIANTS.md:136` (I2.2) — 9 edges | I2.2 states "**Changes documented in NODE_ONTOLOGY.md**", so the ontology is now two edges behind its own canonical. Needs per-type assignment for both new edges (which node types may carry `collides_with`? `informed_by` presumably T/I/D only, per I0.5). Also `staging_service.py:14-17` implements the 7-edge set. |
| **N-3 ⚑** | `NODE_ONTOLOGY.md:161` — live status `cross_verified` (set by `insight_node.j2`) | `INVARIANTS.md:151-155` (I2.3) — crosswalk has 4 rows | `cross_verified` has **no abstract counterpart** in the crosswalk. Is it a sub-state of `committed`, or a fifth status the canonical omits? |
| **C-4** | `ARCHITECTURE_RULES.md:124-139` (R4) | "`chimera_tier` is the vault's type system… `scout`/`deep_read`/… are **not metadata**" — stated as invariant over the *values* | `INVARIANTS.md:111-117` (I1.5) + `:123-129` (I2.1) | Canonical splits: stratification is Tier-1 architectural, the **values are Tier-2 mutable**. R4 over-protects. Note this is the one row where "canonical wins" *removes* protection by design. |
| **C-9** | `ARCHITECTURE_RULES.md:47-48` (R1) | "No MCP server process may **call any LLM**" — call/client framing | `INVARIANTS.md:66-71` (I1.1) | Canonical bans judgment **by any route** incl. host sampling; prohibition is on judgment **location**, not client construction. R1's framing does not catch `ctx.session.create_message`. *(`chimera-mcp-taste/SKILL.md:40-46` already matches I1.1 — STYLE is ahead of the SOT.)* |
| **C-11** | `CLAUDE.md:31`, `:101` | "`ARCHITECTURE_RULES.md` is the **single source of truth for invariant rules**"; "Invariants **R1–R6**… are binding" | `INVARIANTS.md` is canonical | Two documents each claim to be the invariant SOT. |
| **C-12** | `CLAUDE.md:40-43` | restates all six R-rules inline | I0.x / I1.x / I2.x | Restatement of a superseded register in the always-loaded file. |
| **C-13** | `ARCHITECTURE_RULES.md:5`; `CLAUDE.md:49` | "**Source:** `INVARIANT_RULES_AUDIT.md` §4, §5" | — | Cites a file deleted in `2d8f595`. Dangling. *(Architect has assigned to Pass 2.)* |
| **C-14 ⚑** | `ARCHITECTURE.md:104-115` (generated); `scripts/gen_architecture_diagram.py` | verifier table keyed to `R1..R6`, re-parsed from `ARCHITECTURE_RULES.md` | canonical I-ids | If the canonical becomes SOT, the verifier verifies a superseded register. **Compounded by `ENFORCEMENT_DEBT.md` R5b-v:** `_verify_r5b` greps comparisons over `depends_on`, retired by canonical r2; `FORMAL_MODEL.md:107` now defines `support(v)` over `{evidence_base, synthesizes, derives_from}`. The VIOLATED verdict is correct **by accident** and would persist after monotonicity is correctly implemented. Code change, not a doc edit. |
| **C-15** | `THEORETICAL_FRAMEWORK.md:107-108`, Def 4 | T/I nodes rest on "cross-person verification (I-nodes: advisor discussion)" | `INVARIANTS.md:172-173` | Canonical lists the "independent observer" framing of T-nodes as an explicit **non-invariant**. |
| **C-16** | `chimera-w2-map/SKILL.md:3`, `:49-50` | "30-60 papers"; "Breadth target: ≥3 subfields" | `INVARIANTS.md:174` | Canonical: any specific number as an HSC gate is a **non-invariant**. *(Mitigated — the skill already calls it "a warning, not a failure.")* |
| **C-17** | `TAG_SYSTEM.md:141`, `:144-145`; `THEORETICAL_FRAMEWORK.md:124,126` | monotonicity quantified over "dependency set `D`" / "recorded `depends_on`" | `FORMAL_MODEL.md:104,107` | Canonical r2 quantifies over `support(v)` — support-bearing edges, **explicitly "not a specific edge name"** (`:109`). Both docs still describe the retired single-edge formulation. |
| **C-18** | `TAG_SYSTEM.md:148-150`; `ARCHITECTURE_RULES.md:149` | "Gate 1 **reads the recorded `depends_on`** (Phase L's `write_result` writes it)" | `FORMAL_MODEL.md:107,186` | The written edge is now `evidence_base` (R3 reduction, `:186`). `write_result`'s `depends_on` parameter (`chimera-vault/server.py:295`) is now named for a retired concept. Naming collision to resolve in Pass 2 — a rename touches a live tool signature. |

---

## REDUNDANCY — existing text duplicating the canonical

Disposition is "demote to cross-reference" throughout; none proposed for deletion.

| # | file:line | duplicated rule | canonical source | proposed |
|---|---|---|---|---|
| D-1 | `ARCHITECTURE_RULES.md:72-99` (R2) | human-time supremacy | I0.1 | demote; **retain** the elicit clarification (`:91-99`) — G-6 |
| D-2 | `ARCHITECTURE_RULES.md:143-166` (R5) | provenance load-bearing + monotonicity | I0.2 | demote; the R5a/R5b split now lives in `ENFORCEMENT_DEBT.md` |
| D-3 | `ARCHITECTURE_RULES.md:45-68` (R1) | MCP judgment prohibition | I1.1 | demote; canonical is strictly stronger (C-9) |
| D-4 | `ARCHITECTURE_RULES.md:103-120` (R3) | staging gate universality | I1.2 | demote; the `inbox/` caveat now lives in `ENFORCEMENT_DEBT.md` R3 |
| D-5 | `ARCHITECTURE_RULES.md:124-139` (R4) | tier integrity | I1.5 + I2.1 | demote **and re-scope** per C-4 |
| D-6 | `ARCHITECTURE_RULES.md:170-185` (R6) | human authorship of judgment | I0.5 | demote; T-group clause re-homed at I1.3 |
| D-7 | `AUTO_RESEARCH_REQ_REFS.md:215` (RE-4) | belief advances only on human-time | I0.1 | cross-ref |
| D-8 | `AUTO_RESEARCH_REQ_REFS.md:212` (RE-1) | committed claim carries an entailing verbatim span | I0.2 | cross-ref |
| D-9 | `AUTO_RESEARCH_REQ_REFS.md:214` (RE-3) | significance by Architect alone | I0.3 + I0.5 | cross-ref; **retain** the "do not upgrade debt into a law" note (`:218-225`) |
| D-10 | `AUTO_RESEARCH_REQ_REFS.md:216` (RE-5) | verifier built from raw source | I0.3 | cross-ref |
| D-11 | `AUTO_RESEARCH_REQ_REFS.md:213` (RE-2) | novelty witness-bounded | I0.3 | partial; canonical states the principle, not the `τ,D,Ω,≈,B` tuple (G-4) |
| D-12 | `AUTO_RESEARCH_REQ_REFS.md:251` (RO-1) | criteria editable, no VCS action | I2.4 | cross-ref |
| D-13 | `THEORETICAL_FRAMEWORK.md:46-53` (Def 1) | manifold triple **M = (N,E,T)** | `FORMAL_MODEL.md` 𝒢 | demote; self-flags its edge list as illustrative (`:55-57`) |
| D-14 | `THEORETICAL_FRAMEWORK.md:59-64` (Def 2) | dual clock | `FORMAL_MODEL.md` State Transitions | cross-ref |
| D-15 | `THEORETICAL_FRAMEWORK.md:66-71` (Thm 1) | truth advances on human-time | I0.1 + FM I1 | cross-ref |
| D-16 | `THEORETICAL_FRAMEWORK.md:84-89` (Def 3) | source verification / `[V]` | `FORMAL_MODEL.md` Tag semantics | cross-ref |
| D-17 | `THEORETICAL_FRAMEWORK.md:119-130` (Def 5 + Gate 1) | `U<P<V`, monotonicity | FM Verification Tags + monotonicity | demote; `:129` still asserts "structural (pipeline-enforced)" as fact — now contradicted by `INVARIANTS.md:22-23` + `ENFORCEMENT_DEBT.md` R5b |
| D-18 | `THEORETICAL_FRAMEWORK.md:146-155` (§4) | provenance decay | I0.4 + FM decay | cross-ref; note D-1 debt |
| D-19 | `THEORETICAL_FRAMEWORK.md:104-113` (Def 4) | taste verification cannot be automated | I0.5 + I0.3 | cross-ref; re-scope per C-15 |
| D-20 | `TAG_SYSTEM.md:33-40` (§2) | partial order + numeric encoding | FM Verification Tags | cross-ref |
| D-21 | `TAG_SYSTEM.md:136-150` (§6) | monotonicity | FM monotonicity + I0.2 | demote **and correct** per C-17 |
| D-22 | `TAG_SYSTEM.md:44-91` (§3) | `[V]/[P]/[U]` formal definitions | FM Tag semantics | demote the **formal lines** only; worked cases are G-2 |
| D-23 | `CLAUDE.md:40-43` | six-invariant summary | I0.x/I1.x/I2.x | replace with a pointer |

**On the predicted `RA-1..6` duplication:** already gone. `d019c5e` removed that register and
replaced it with the reference-pattern `RA-a..d` (`AUTO_RESEARCH_REQ_REFS.md:227-242`), naming the
old one as drift. The live duplication in that file is the `RE-*` / `RO-1` set above.

---

## COVERAGE-GAPS — existing content the canonical does not address

| # | file:line | content | question |
|---|---|---|---|
| **G-2** | `TAG_SYSTEM.md:95-132` (§4, §5) | Tier taxonomy **admits** column, split-scoring rule, `[P]`-vs-`[U]` "robust" resolution | Canonical now matches §4's tier *contents* (C-7 closed) but not the split-scoring rule. Retain §5 as operational elaboration? |
| **G-3** | `TAG_SYSTEM.md:177-204` (§8) | 10-row doubt-signal → tag bridge; the single source lenses and `criteria/**` both reference | Canonical is silent on lenses. Retain as-is? |
| **G-4** | `TAG_SYSTEM.md:154-173` (§7) | crosswalk `[V]/[P]/[U]` ↔ `hypothesis/supported/refuted`; Gate 1 operates **only** on V/P/U | Canonical knows one tag vocabulary; `ExtractedClaim.status` exists in code. Operational only, or does the canonical need it? |
| **G-6** | `ARCHITECTURE_RULES.md:91-99` | R2 elicit clarification — a mid-tool confirm is not human-time invocation | I0.1 says "Architect-initiated action" without addressing confirm-click laundering. Retain under I0.1? |
| **G-7** | `ARCHITECTURE_RULES.md:20-41`, `189-206` | **level hierarchy** (ARCHITECTURE > SPRINT > STYLE) and the mandatory **Violation Detector** | Canonical has per-invariant "Violation:" lines but no precedence rule and no pre-change checklist. `AUTO_RESEARCH_REQ_REFS.md:239-242` (RA-d) *requires* an explicit precedence rule. Where does it live now? |
| **G-8** | `NODE_ONTOLOGY.md:37-60` (§2) | per-type edge sets, direction convention, universal-backbone rationale | I2.2 lists a flat vocabulary with no per-type assignment. Retain §2 as elaboration — and extend it per N-2. |
| **G-9** | `THEORETICAL_FRAMEWORK.md:228-281` (§8) | reconciliation with arXiv 2605.23204's L0–L4 taxonomy | Canonical never uses the external ladder. Context-only? |
| **G-10** | `THEORETICAL_FRAMEWORK.md:165-179` (§5) | futures/settlement model | Canonical silent; doc self-flags as descriptive (`:308-310`). Retain, or non-invariant? |
| **G-11** | `AUTO_RESEARCH_REQ_REFS.md:279-333` (§8) | five live failure modes T1–T5 | Canonical has no failure-mode taxonomy. Independent layer? |
| **G-12** | `AUTO_RESEARCH_REQ_REFS.md:356-386` (§10) | evaluation limits at n=1 | Canonical silent on evaluation. Out of scope? |
| **G-13** | `NODE_ONTOLOGY.md:168-170` | `deep_read_survey_node.j2` uses `chimera_status:` instead of `status:` | Does I2.3's crosswalk absorb this, or stay deferred? |

---

## Is the R-family inside the I-family's closure?

**Almost — proper, one-directional, failing in two places.** Unchanged by the r2 revision except
that R6's residue is now re-homed.

| R | I counterpart | contained? | residue |
|---|---|---|---|
| R1 | I1.1 | **YES**, strictly — I1.1 is broader | none; R1 is a weaker special case (C-9) |
| R2 | I0.1 | **YES** for the rule statement | elicit clarification is a derived corollary (G-6) |
| R3 | I1.2 | **YES** | none; the `inbox/` caveat is compliance, now in `ENFORCEMENT_DEBT.md` |
| R4 | I1.5 + I2.1 | **NO — contradicted** | R4 asserts tier values are invariant; I2.1 makes them mutable (C-4) |
| R5 | I0.2 | **YES** | the a/b split is compliance, now in `ENFORCEMENT_DEBT.md` |
| R6 | I0.5 | **YES** now | the T-group clause was residue in r1; **re-homed at I1.3 (`:96-99`)** |

The reverse fails: I0.3, I0.4, I1.3, I1.4, I2.2, I2.3, I2.4 have no R counterpart. `I ⊄ closure(R)`.

**Conclusion.** Rule-wise `ARCHITECTURE_RULES.md` is now dissolvable — five of six rules become
cross-references, R4 must be **dropped rather than migrated** (C-4). What cannot dissolve is the
non-rule scaffolding, and one leg of it has already moved out:

- ~~enforcement-status axis + debt register~~ → **now `ENFORCEMENT_DEBT.md`** (G-5 closed)
- the **level hierarchy** ARCHITECTURE > SPRINT > STYLE (`:20-41`) — G-7, required by RA-d
- the **Violation Detector** pre-change checklist (`:189-206`) — G-7

So the shape after Pass 2: **`INVARIANTS.md` states what must be true · `ENFORCEMENT_DEBT.md`
records how well the code holds it · `ARCHITECTURE_RULES.md` survives (if at all) as precedence +
pre-change checklist.**

---

## Files measured and found clean

- `.claude/skills/chimera-mcp-taste/**` — **ahead of the SOT.** `SKILL.md:40-46` already carries the
  judgment-location framing and sampling ban I1.1 requires (C-9); `mcp_rules.md:71-72` carries the
  elicit ruling. References by pointer, never restates.
- `chimera-w1-verify`, `chimera-triage-paper`, `chimera-deep-extract` — "never auto-promoted /
  staging-only / Architect promotes" lines describe **tool behaviour**, consistent with I1.2. Not
  invariant restatements. No demotion proposed.
- `chimera-sprint-discipline`, `chimera-code-taste`, `chimera-commit-style`,
  `chimera-dependency-veto`, the six lens skills, `_shared/**` — no invariant statements.

---

## Recommended ruling order for Pass 2

1. **N-1** — `informed_by` is in I2.2 but not in λ. The canonical contradicts itself; only you can
   resolve it, and N-2 depends on the answer.
2. **N-2 / N-3** — propagate the r2 vocabulary into `NODE_ONTOLOGY.md`: per-type assignment for
   `collides_with` and `informed_by`, and an abstract counterpart for `cross_verified`.
3. **C-17 / C-18** — the `depends_on` → `support(v)` migration across `TAG_SYSTEM.md`,
   `THEORETICAL_FRAMEWORK.md`, and the `write_result` parameter name. Touches a live tool signature.
4. **C-14 + `ENFORCEMENT_DEBT.md` R5b-v** — re-target the verifier to the support-edge set and
   re-key it to I-ids. Until done, R5b cannot be verified even once implemented.
5. **C-4** and **G-7** — whether `ARCHITECTURE_RULES.md` survives as precedence + checklist, and R4
   is dropped. Determines the shape of every D-row demotion.
6. Everything else is mechanical once 1–5 are settled.

**Nothing in this map has been applied.** Pass 2 begins on your approval, and will show diffs before
writing.
