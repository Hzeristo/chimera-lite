# Requirements, Failure Modes, and Evaluation Limits for an L2 Auto-Research Harness

**Document type:** Normative requirements specification (system-agnostic).
**Status:** Living document. Revision 2 (2026-08-03).
**Scope:** Computer-science literature research; single-researcher instantiation. No multi-user,
deployment, or service concerns.
**Coverage:** 0th-order requirements complete; 1st/2nd-order and path-dependent layers are stated as
open problems (§7), not as satisfied requirements.

**Changelog**
- **r2 (2026-08-03)** — Separated *enforcement mode* (design property) from *compliance* (dated
  property of an instantiation); moved all per-system verdicts to Appendix B and made anchors
  mandatory there. Redefined the autonomy ladder by its belief-advance predicate alone. Introduced
  agnostic role vocabulary (§2) and a definition of the novelty function (§4). Weakened P2 to a
  claim about correlated error, supplied a falsification condition for P5, moved P4's independence
  assumption into the subjunctive. Added the traceability matrix (§6), an explicit perturbation
  variable for the order-of-effects scaffold (§7), and the evaluation-limits section (§9). Retired
  T6 to Appendix A. Fixed the dangling "T6–T9" reference (the sub-traps are T5a–T5d).
- **r1** — Initial 0th-order coverage.

---

## How to read this document

This document states **what an L2 auto-research harness must guarantee, what it must never claim,
and how it characteristically fails.** It is written to be readable by anyone building such a
harness; it names no implementation and asserts no compliance.

**Position in the authority hierarchy.** This is an ARCHITECTURE-level document, subordinate to the
invariant rule set of the instantiating system and to its formal framework. Where this document and
an enforcing authority disagree on a detail, the enforcing authority wins and this document defers.
It supplies requirements and their rationale; it is never a second source of truth for a tag, an
edge, a gate, or a compliance state.

**The self-suspicion clause.** The governing standard is that *advisory rigor is negative value*: a
flag, criterion, or verifier that only **performs** diligence launders opinion into the appearance
of knowledge, and is worse than its own absence. This document is subject to that standard. Its
first revision failed it — recording requirement RE-1 as *satisfied* by a mechanism that the same
tables recorded as *unbuilt*, and issuing verdicts (`PASS`, `Verified`, `Implemented`) with no
source anchor or date. §1 exists so that failure is structurally unavailable.

---

## 0. Foundational Claims

The ten claims this document's requirements rest on. Architect-authored, stated verbatim. They are
the middle layer of a three-layer disclosure: **operational rules (§5 P, §6 RE/RO, §8 T) →
foundational claims (this section) → formal definitions (`FORMAL_MODEL.md`)**. A P, T, or RE entry
that cannot be traced to a claim here is unmotivated; a claim that no entry invokes is inert.

**Claim 1 — Computable change ≠ epistemic truth.**
Persistent representation changes (d(K_t, K_{t+1})) are computable but do not confer external truth.
External truth requires p(e|θ), which L2 systems lack. L2 has provenance (anchors to sources), not
posteriors.

**Claim 2 — No universal verifier.**
No single verifier simultaneously assesses truth, novelty, and importance. Each requires a different
independence grade: factual truth (verbatim grounding, medium independence), novelty (bounded witness
search, low independence), significance (human judgment, no independent verifier exists).

**Claim 3 — Novelty is ontology-relative.**
N(c; timeborder, Doc, ontology, claim-equiv, budget) is well-defined only given fixed parameters.
Research changes the ontology while measuring novelty against it. Any system claiming NOVEL=true
conflates measurement with theory revision. The correct output is witness-bounded: {prior_found,
no_prior_in_budget, inconclusive}.

**Claim 4 — No p(e|θ) = no Bayesian gain.**
A distance d(K_t, Update(K_t,c)) in representation space is change. Bayesian information gain
KL(p(θ|e) ∥ p(θ)) requires an external likelihood p(e|θ). L2 systems lack this; they have provenance,
not posterior updates.

**Claim 5 — Fixed-ontology search = recombination, not invention.**
Search over a fixed {node types, edge types, representation language} produces internal
recombinations. It cannot discover concepts outside the type system. The ontology's expansion is
human-driven (Phase-driven in chimera-lite).

**Claim 6 — Generator self-verify = permission boundary.**
A generator verifying its own output is endogenous closure: the same optimization pressure shaping
the claim shapes the verdict. The prohibition is on permission (whose verdict counts), not
capability.

**Claim 7 — Compaction defines operational ontology.**
What survives session-boundary compression defines what the system can reason about. Fields absent
from the compacted context are outside the operational ontology, regardless of their presence in the
full artifact.

**Claim 8 — Capability = foundation ∘ policy.**
Auto-research effective capability is the composition of the foundation model and the epistemic
state-transition policy (when to verify, when to stop, when to call external verifiers). Neither
alone defines the capability.

**Claim 9 — Compaction inherits four failure modes.**
Session-boundary compression inherits: premature closure (summary says "done"), salience decoupling
(HIGH-salience flags compressed away), ontology lock-in (new concepts lost), verifier contamination
(framing leaks into the next verifier).

**Claim 10 — Verifier independence = raw-material construction.**
A verifier constructs its judgment from raw evidence (source markdown, original logs, Tier-1 data),
not from generator narrative (K-node synthesis, abstract). Evidence independence is the load-bearing
boundary.

---

## 1. Status vocabulary (normative)

Two axes are orthogonal and must never share a cell.

**Axis 1 — Enforcement mode.** A property of the *design*. Declared in this document.

| Mode | Meaning |
|---|---|
| **STRUCTURAL** | A schema, gate, or code path refuses the violation. Honoring the requirement is not at any agent's discretion. |
| **ADVISORY** | The requirement is committed, but the enforcing mechanism does not exist yet. A promise with no teeth. |
| **CONVENTION** | No mechanism is attempted; the requirement rests on human practice. Distinct from ADVISORY: no mechanism is *planned*, and the reason must be stated. |

**Axis 2 — Compliance.** A property of a *specific instantiation at a specific date*. Never
declared in this document; recorded only in an instantiation record (Appendix B).

| Value | Admissibility condition |
|---|---|
| **PASS** | Requires an anchor: artifact path or identifier, verification method, date, and verifier. |
| **FAIL** | Same anchor requirement. Asserts an observed occurrence. |
| **UNASSESSED** | The default. Correct whenever no anchored check has been run. |

**Three rules that follow, and that r1 broke:**

- **1a.** A requirement whose enforcing mechanism is unbuilt is **ADVISORY**. It may not be recorded
  as satisfied by that mechanism, in any table, under any status word.
- **1b.** "Unenforced" and "violated" are different predicates with different evidentiary burdens.
  Absence of enforcement is a design fact; a violation is an observed event requiring a witness.
  Record the former as **ADVISORY**, never as **FAIL**.
- **1c.** A compliance value without an anchor is, by this document's own tier taxonomy, a Tier-3
  self-report. It is inadmissible. Omit it and write **UNASSESSED**.

---

## 2. Role vocabulary (agnostic)

The requirements below refer to functional roles, not to any system's component names. An
instantiation maps its components onto these roles in its Appendix B record.

| Role | Function |
|---|---|
| **VERBATIM-VERIFIER** | Given a claim and a primary source, decides whether a verbatim span of the source entails the claim. Reads the source, never the generator's synthesis. |
| **BREADTH-MAPPER** | Given a claim and a corpus, searches for prior art and emits a witness state (§4). Never emits a novelty boolean. |
| **INDEPENDENT-AUDITOR** | A verifier constructed outside the generator's model family or prompt lineage, used to probe for correlated error. |
| **CRITERIA SET** | Externally editable statements of the researcher's standards, loaded at run time, versioned on human-time. |
| **LENS** | A named analytical pattern selected by artifact type, specifying what evidence would falsify the artifact's central claim. |
| **SALIENCE LEDGER** | An append-only record of events marked HIGH-salience, required to survive session-boundary compression (P6, RO-4). |
| **ARCHITECT** | The single human researcher; terminal epistemic authority. |

**A verifier is defined by its function and its evidence independence, never by its substrate.**
Nothing in this document requires a verifier to be a language model. What makes anything a verifier
is Claim 10: judgment constructed from raw material rather than from the generator's narrative. The
substrate only sets the *independence grade* the role can reach.

*Illustrations from outside this instantiation, to fix the point that the role is substrate-free:* a
proof kernel (a Lean 4 checker deciding whether a proof term inhabits the stated type) in formal
mathematics; a physical apparatus (a wet-lab protocol executed by embodied agents) in the empirical
sciences. Both are verifiers, neither emits a token, and both reach an independence grade no model
can — they share **no optimization pressure** with the generator. **Neither is available here, and
neither is a chimera-lite mechanism**; they are named only to show that "verifier" does not mean
"language model."

**The ARCHITECT is not a verifier.** The role table lists the human separately, and Claim 2's third
clause is explicit that significance has *no independent verifier*. A human assessing all three
properties is an agent exercising terminal authority, not a verifier role being filled — this is the
distinction P2 previously blurred.

### The verifier substrate HERE

In chimera-lite every verifier role is filled by **an agent** — there is no kernel, no apparatus, no
deterministic checker. Two substrates, chosen for different independence grades:

| Substrate | Fills | Built? | Independence grade | Why |
|---|---|---|---|---|
| **Isolated Claude subagent** — a forked Task worker that reads the source itself and returns only its verdict | VERBATIM-VERIFIER, BREADTH-MAPPER | **live** | **Context-independent, same-family** | Isolation removes *conversational* contamination: the worker never sees the generator's synthesis (Claim 10, T4). It does not remove *model-family* correlation. |
| **Zero-shot Codex agent** — a new session, no prior context, different model family | INDEPENDENT-AUDITOR | **NOT BUILT** — designed in `phase-I.md`, Architect-invoked today | **Cross-family** *(by design; unmeasured)* | Deliberately chosen to escape model bias and echo. A same-family auditor agreeing with the generator is weak evidence; a different family agreeing is stronger. Zero-shot is load-bearing: a fresh session inherits no framing (T5d). |

The cross-family auditor is the *intended* answer to P4's endogenous-closure problem — same-family
isolation alone leaves the shared optimization pressure intact. Two limits, both live:

1. **It is not built.** Until Phase I lands, the only verifier substrate actually running is the
   same-family Claude subagent, so the endogenous-closure gap P4 names is **currently open** in this
   instantiation, not closed by a mechanism that exists.
2. **Even once built, independence stays unmeasured.** P4's caveat is unchanged: cross-model error
   correlation here is *unmeasured* and filed at §10 Q4. "Different family" is a design argument for
   decorrelation, never evidence of it. An instantiation stating "independent auditor" in the
   indicative, absent a correlation measurement, asserts what it has not shown — P4's own words.

> **Enforcement status.** The mandatory zero-shot Codex audit is specified in `phase-I.md`
> (I.6, `:47`, `:79` — once per dialectic session, new session, no contamination). **Phase I —
> Isostheneia is Queued, not built** (`THEORETICAL_FRAMEWORK.md:328`). Today the cross-family audit
> is Architect-invoked, not harness-enforced. Per rule 1a, that is ADVISORY, and this note is the
> whole of its compliance claim; the instantiation record (Appendix B) carries the rest.

---

## 3. The autonomy ladder, defined by one predicate

Levels are defined **solely by who advances belief.** Feature inventories (staging, provenance,
tiering) are consequences, not definitions; defining by feature checklist is what made r1's ladder
unable to classify intermittent gating.

Let `advance(n)` be the event that moves node `n` into the set of the system's committed beliefs.

- **L1 — Tool.** `advance` is not a system event at all; there is no committed-belief set inside the
  system. The machine retrieves; belief lives entirely in the researcher's head or prose.
- **L2 — Gated accumulator.** For every `n`, `advance(n)` requires a human action in its provenance
  chain, and the system is *architecturally incapable* of firing `advance` otherwise. Machine-time
  accumulates candidates without bound; belief moves only on human-time.
- **L3 — Autonomous.** Some `advance(n)` fires without a human action. The presence of internal
  verifiers does not change the level; a verifier is not a human action.

**The boundary case r1 could not express.** A system where human gating is *typical but skippable*
is **L3**, not "L2 with exceptions." The predicate is universally quantified: one unattended
`advance` path collapses the level. This matters because external taxonomies place a distinct level
here (§8).

**L2 is not a way-station.** It is the correct terminal architecture where the researcher's own
judgment is the terminal epistemic authority — the person who must publish, defend, and live with
the claims. This is a normative commitment, not an estimate of current capability.

---

## 4. The novelty function (definition)

Novelty is a **parameterized measurement**, and the parameters are load-bearing:

> `N(c; τ, D, Ω, ≈, B)`

| Parameter | Meaning |
|---|---|
| `c` | The candidate claim, expressed in `Ω`. |
| `τ` | Evidence cutoff date. Prior art after `τ` is out of scope by construction. |
| `D` | The finite corpus actually searched. Not "the literature." |
| `Ω` | The ontology: the vocabulary and the **resolution** at which claims are individuated. |
| `≈` | The claim-equivalence relation over `Ω`-expressed claims. |
| `B` | Search budget: queries, documents read, wall-clock. |

**Output — a witness state, never a boolean:**

- **`prior_found(w)`** — exhibits a witness `w ∈ D` with `w ≈ c`. This is the only positive result
  the function can return, and it must carry `w`.
- **`no_prior_in_budget`** — `B` was exhausted without a witness. This is **not** `¬∃ prior`; it is a
  statement about `B`.
- **`inconclusive`** — `≈` is undecidable at `Ω`'s resolution, or candidate witnesses remain
  unresolved at exhaustion.

**Why no boolean is available.** Research revises `Ω` while measuring against it. `N` is well-defined
only relative to a fixed parameter tuple, so two `N` values computed under different `Ω` are
incomparable unless `Ω` is versioned. A system emitting `NOVEL = true` has conflated measurement
with theory revision, and has silently universally quantified over a corpus it did not search.

---

## 5. Scientific problems addressed

**P1 — Provenance opacity.** Machine-generated claims present the surface features of knowledge
while carrying no verifiable grounding. The characteristic failure is not absent rigor but
*cosmetic* rigor: a provenance flag that is emitted and then ignored downstream, which is worse than
no flag because it certifies. **Anchor:** dated incident record, 2026-07-12 — an agent flagged claims
as unverified and then reasoned with them as verified, described in the record as *"worse than not
flagging, because it performs rigor."* **Requirement:** provenance must be load-bearing (RE-1). *(← Claim 1, Claim 4)*

**P2 — Verification conflation.** Truth, novelty, significance, and ontology adequacy are distinct
properties with distinct evidence bases. The claim here is **not** that no single *agent* can assess
them — a competent human reviewer does exactly that. The claim is narrower and defensible, and is
scoped to **verifiers as defined in §2**: no constructed verifier role covers all three, because each
demands a different independence grade. When one property is used as a *proxy* for another, the
errors become **correlated and unattributable** — a wrong verdict cannot be localized to the property
that failed, so it cannot be corrected. A verified-true claim silently reads as important; an
unfound prior silently reads as significant.
**Requirement:** tier-separated verification with separately recorded verdicts (RE-2, RE-3).
*(← Claim 2)*

**P3 — Novelty underdetermination.** Per §4, `N` is defined only given fixed parameters, and research
mutates one of them. **Requirement:** witness-only novelty output with all parameters externalized
and recorded (RE-2). *(← Claim 3)*

**P4 — Generator self-verification.** A generator assessing its own output is endogenous closure: the
optimization pressure that shaped the claim also shapes the verdict, so agreement carries little
information. **Requirement:** the verifier is constructed from raw material, not generator narrative
(RE-5); an independent auditor is *intended* to decorrelate errors. **Status of that intent:**
independence is a design goal, **not a measured property**. Cross-model error correlation is
unmeasured and is filed as an open question (§10 Q4). Any instantiation stating "independent
auditor" in the indicative, absent a correlation measurement, is asserting what it has not shown.
*(← Claim 6)*

**P5 — Attractor dynamics (hypothesis, not finding).** *Hypothesis:* a harness that accumulates
material against a slowly-changing criteria set will tend toward a self-confirming region, and the
artifact will stop surprising the researcher. This is stated as a hypothesis because T1 requires any
saturation-type conclusion to carry a falsification condition, and P5 is a saturation-type
conclusion; r1 asserted it and failed its own test. **Falsification condition:** over a fixed window
of committed nodes, measure the fraction that require *extending* the ontology (a new concept,
category, or edge target absent from `Ω` at window start) versus the fraction that fill existing
slots. If the extension fraction does not decline monotonically as the corpus grows, P5 is not
occurring in this instantiation. **Requirement:** the extension fraction is instrumented and
periodic heterogeneous external input (advisor discussion, cross-field reading) is scheduled
(RO-5). Both the metric and its threshold are unvalidated; the requirement is to *measure*, not to
assume the effect. *(← Claim 5, Claim 7)*

**P6 — Compaction inheritance.** Session-boundary compression silently resets four distinct
safeguards: premature closure, salience decoupling, ontology lock-in, and verifier contamination
(T5a–T5d). Each failure is silent — no error is raised, behavior merely degrades. **Requirement:**
the salience ledger survives compaction; handoff carries ontological *vocabulary*, not conclusions
(RO-3, RO-4). *(← Claim 9)*

---

## 6. Requirements

Each requirement declares the enforcement mode it **demands of a conforming design**, and an
acceptance criterion — the observation that would license a `PASS` in an instantiation record. No
compliance value appears here (rule 1c).

### 6.1 R-Epistemic — fundamental; not tradeable against operational convenience

> **Instantiation crosswalk.** This document is system-agnostic: it states what a *conforming* L2
> harness must require. In this repository those requirements are instantiated by the canonical
> invariants, and the mapping is recorded here so the two registers cannot drift into a second
> source of truth (the `RA-1..6` failure of r1, §6.2):
>
> | requirement | instantiated by |
> |---|---|
> | RE-1 | `INVARIANTS.md` **I0.2** (provenance load-bearing) |
> | RE-2 | `INVARIANTS.md` **I0.3** (novelty via bounded witness search) |
> | RE-3 | `INVARIANTS.md` **I0.3** + **I0.5** (significance is human-only; judgment authorship) |
> | RE-4 | `INVARIANTS.md` **I0.1** (human-time supremacy) |
> | RE-5 | `INVARIANTS.md` **I0.3** (verification tier-separation) |
> | RO-1 | `INVARIANTS.md` **I2.4** (criteria externalization) |
>
> Compliance for this instantiation is **not** recorded here — see `ENFORCEMENT_DEBT.md`, and
> Appendix B below for the record template.

| ID | Requirement | Mode demanded | Acceptance criterion |
|---|---|---|---|
| **RE-1** | Every committed claim carries a verbatim span from a primary or structural source that entails it. | STRUCTURAL | A synthesis whose recorded dependencies include an unverified claim is **rejected by schema**, not by prompt compliance. Demonstrated by a rejected fixture. *(← Claim 1, Claim 4)* |
| **RE-2** | Novelty output is witness-bounded (§4), never boolean, with `τ, D, Ω, ≈, B` recorded alongside. | STRUCTURAL | The output type admits only the three witness states; the parameter tuple is present in every emitted record. *(← Claim 3)* |
| **RE-3** | Significance is assessed by the Architect alone; no code path authors a significance judgment. | CONVENTION *(acknowledged debt)* | A gate that refuses machine-authored judgment bodies. **No such gate is specified by this document.** See the note below. |
| **RE-4** | Belief advances only on human-time (§3, L2 predicate). | STRUCTURAL | Exactly one write path into the committed tier; it requires a human invocation; no other path can reach that tier. *(← Claim 6 — permission boundary)* |
| **RE-5** | The verifier is constructed from raw source material, not from generator narrative. | STRUCTURAL | The verifier's input contract admits the source artifact and excludes the generator's synthesis. Demonstrated by the input schema, not by prompt text. *(← Claim 10)* |

> **Note on RE-3 — do not upgrade debt into a law.** r1 recorded RE-3 as satisfied because structural
> enforcement is *"impossible by design."* That is a category error twice over. First, a CONVENTION
> is never "satisfied" by a mechanism; it is held by practice, and its correct compliance value is
> UNASSESSED absent a review anchor. Second, nothing about the requirement is impossible: a gate
> refusing machine-written judgment bodies is straightforwardly implementable. What is impossible is
> *verifying that a human-written body reflects genuine judgment* — a much narrower impossibility.
> Restating unlanded debt as metaphysical necessity removes the pressure to land it, which is the
> P1 failure applied to the specification itself.

### 6.2 R-Architectural

Architectural invariants are **owned by the instantiating system's rule set, not by this document.**
r1 restated them here as a parallel `RA-1…RA-6` register with its own verdict column; that
duplication is drift — it created a second source of truth that immediately contradicted the first
(RE-1 satisfied by a mechanism `RA-5` reported as violated).

A conforming instantiation therefore:

- **RA-a.** Maintains its invariant rules in exactly one authority, and **references** them here.
- **RA-b.** Declares each invariant's enforcement mode per §1, Axis 1.
- **RA-c.** Records compliance only in an instantiation record with anchors (Appendix B).
- **RA-d.** Declares an explicit precedence rule for conflicts between invariant, sprint, and style
  level rules. **Anchor:** dated incident record, 2026-07 (referred to elsewhere as the L.B.2 class)
  — a locally reasonable, minimal-diff edit violated an architectural invariant that had never been
  stated at the executor's altitude, because no precedence rule existed to adjudicate.

### 6.3 R-Operational — usability, subordinate to R-Epistemic

The precedence rule: where an operational requirement conflicts with an epistemic one, the epistemic
requirement wins. r1 implied this ordering without stating it.

| ID | Requirement | Mode demanded | Acceptance criterion |
|---|---|---|---|
| **RO-1** | Criteria are editable in the researcher's own environment with no code or version-control action, and are re-read on every run. | STRUCTURAL | An edit with no commit changes the next run's behavior. |
| **RO-2** | Field ontology distinguishes claims, not topics — `Ω`'s resolution is claim-level. | ADVISORY | Criteria files state at least one claim-level distinction per field that a topic-level match would collapse (T2). |
| **RO-3** | Session handoff injects ontological vocabulary, not conclusions. | ADVISORY | Handoff artifacts contain the run's new vocabulary and open items; a handoff asserting closure on an open item is a defect (T5a). |
| **RO-4** | HIGH-salience events persist across compaction and interrupt execution before further work proceeds. | ADVISORY | A HIGH mark written before a compaction boundary is present and actionable after it. |
| **RO-5** | Ontology-extension fraction is instrumented; heterogeneous external input is scheduled. | ADVISORY | The metric of P5's falsification condition is computable from stored records. |

---

## 7. Traceability

Every problem reaches a requirement; every requirement has a failure mode that detects its absence.
The r1 registers overlapped without a crosswalk, so the same concern was counted three times and
coverage looked broader than it was. This table is also the mechanical check that would have caught
the RE-1 contradiction.

| Problem | Requirement(s) | Detecting trap | Mode demanded |
|---|---|---|---|
| P1 Provenance opacity | RE-1 | T3 Cosmetic rigor | STRUCTURAL |
| P2 Verification conflation | RE-2, RE-3 | T2 Topic-level collapse | STRUCTURAL / CONVENTION |
| P3 Novelty underdetermination | RE-2 | T1 Safe-closure bias, T2 | STRUCTURAL |
| P4 Generator self-verification | RE-5 | T4 Evaluator contamination | STRUCTURAL |
| P5 Attractor dynamics *(hypothesis)* | RO-5 | T1 | ADVISORY |
| P6 Compaction inheritance | RO-3, RO-4 | T5a–T5d | ADVISORY |
| *(cross-cutting)* L2 predicate, §3 | RE-4 | — | STRUCTURAL |
| *(cross-cutting)* rule precedence | RA-d | — | STRUCTURAL |

---

## 8. Failure modes

Each entry states a mechanism, a detection condition, and where it surfaces. All five are **live**;
retired items move to Appendix A rather than remaining in the register with a status marker.

### T1 — Safe-closure bias
**Mechanism.** "This direction is saturated" is nearly unfalsifiable and carries low reputational
risk. "There is a gap at Y" is falsifiable and carries high risk. Any feedback signal that penalizes
being wrong more than being uninformative biases toward the former.
**Detection.** Every saturation-type conclusion must supply a falsification condition; falsifiability
is required symmetrically of positive and negative conclusions. A saturation claim without one is
the defect. *(This document applies the rule to itself at P5.)*
**Surfaces at.** Breadth mapping; any audit run with an under-specified ontology.
*(← Claim 3 — novelty output is witness-bounded, so a saturation claim is a novelty claim in disguise)*

### T2 — Topic-level collapse
**Mechanism.** "A document exists that touches this topic" is substituted for "this specific claim is
covered." `N` requires equivalence at `Ω`'s resolution (§4); a coarse `Ω` cannot represent the
distinction, so the substitution is invisible rather than wrong.
**Detection.** Criteria must state claim-level distinctions that a topic match would collapse — e.g.
distinguishing *a mechanism that updates stored state* from *a mechanism that revises its own update
rule*, where a topic-level index files both under "memory update."
**Surfaces at.** Breadth classification; gap assessment. *(← Claim 3, Claim 7)*

### T3 — Cosmetic rigor
**Mechanism.** Provenance tags are advisory (an agent may honor them) rather than structural (the
pipeline refuses to propagate an inadequately grounded claim). The flag is emitted correctly and
then ignored, so the record shows diligence that did not occur.
**Detection.** A synthesis appearing at a stronger provenance status than the minimum of its
recorded dependencies. Equivalently: an unconstrained verdict type that permits silent upgrade.
**Surfaces at.** Any system whose provenance field is a free-form string rather than a closed
enumeration checked at write time. *(← Claim 2 — tier-separation; Claim 10 — evidence independence)*

### T4 — Evaluator contamination
**Mechanism.** The verifier reads the generator's framing before the raw evidence. Shared framing
produces correlated errors, so agreement between generator and verifier stops being evidence.
**Detection.** Inspect the verifier's *input contract*, not its instructions: it must receive the
source artifact and the field vocabulary, and must not receive the generator's synthesis or
conclusions. A broken source path that silently falls back to the synthesis is the same defect.
**Surfaces at.** Auditor invocation without vocabulary injection; verifier input resolution failures.
*(← Claim 10)*

### T5 — Compaction cascade
**Mechanism.** Session-boundary compression resets four safeguards at once, silently.
- **T5a Premature closure** — the compacted summary reports open items as done.
- **T5b Salience decoupling** — HIGH-salience marks are compressed away.
- **T5c Ontology lock-in** — concepts discovered during the session are lost, so `Ω` reverts.
- **T5d Verifier contamination** — the auditor inherits the generator's framing instead of the
  vocabulary (T4 by way of handoff).

**Detection.** Compare the post-boundary open-item set and salience ledger against the pre-boundary
state; any silent contraction is a defect.
**Surfaces at.** Every session boundary, unconditionally. This is the only failure mode with a
guaranteed trigger. *(← Claim 9)*

---

## 9. What an L2 harness cannot claim

These are boundary statements, not deficiencies. A system claiming any of them is either mistaken or
relying on a human whose role it is not acknowledging.

- **Cannot claim Bayesian information gain.** Not because no likelihood is written down — a Bayesian
  reading can be imposed on almost anything — but because there is **no held-out outcome data and no
  scoring rule.** The artifact records provenance, which is a claim about grounding, not a posterior
  update. The honest version is a **calibration** claim, and it requires resolved predictions.
- **Cannot claim novelty.** Only witness-bounded results (§4). `no_prior_in_budget` is a statement
  about the budget.
- **Cannot claim verified significance.** No independent verifier for significance exists; the
  Architect's judgment is terminal by construction, not by convenience.
- **Cannot certify conceptual novelty.** A fixed node-and-edge schema generates recombinations within
  its expressive range. Note the weaker form is the defensible one: a fixed schema does not preclude
  expressing new concepts — natural language has fixed syntax — but the system cannot *certify* that
  a given recombination is a new concept, and it cannot introduce a new **node kind** without a human
  schema change. Distinguish schema-ontology from domain-ontology; r1 equivocated between them
  (denying ontology expansion in one sense while measuring it in the other).

---

## 10. Evaluation, and the limits of an n=1 setting

**The two criteria.** An L2 harness is evaluated on (i) the **quality of candidate material** reaching
the Architect, and (ii) the **reduction in Architect time-cost per settled belief.** Not on
autonomous task completion — task completion is not the goal, and measuring it rewards the L3
behavior the architecture exists to refuse.

**The constraint r1 never acknowledged.** The stated scope is one researcher with no control
condition, no randomization, and no possibility of blinding. Learning effects (the researcher
improves independently), expectancy effects (the researcher built the instrument), and outcome
latency (research quality resolves over years) are unavoidable and mutually confounded. Most
questions of the form "does the harness improve outcomes" are therefore **not answerable as posed**
in this setting, and stating them as an empirical programme overstates what the setting can deliver.

**What remains feasible at n=1.** Not experiments about the researcher; measurements about the
instrument:

- **Fixture-set comparisons.** Fixed claim sets with independently established ground truth, re-run
  under varied control parameters. Within-instrument, no human outcome measure required.
- **Inter-verifier agreement.** Two verifiers of different construction on identical inputs; report
  agreement rate and disagreement structure. This is the measurement P4's independence claim needs.
- **Retrospective calibration.** For verdicts whose ground truth later resolves, plot claimed
  confidence against observed correctness.
- **Preregistration in the ledger.** Record the expected result *before* a run. Cheap, and it is the
  only available defense against T1 in one's own analysis.

**Report format.** Any evaluation result carries its parameter tuple and its date, or it is a Tier-3
self-report (rule 1c).

---

## 11. Open questions

Distinguished from implementation tasks: none of these has a known answer, and the first three may be
unanswerable in this setting (§10).

1. Does human gating improve research outcomes relative to careful unaided use of the same tools?
   *(Confounded at n=1; approachable only through fixture-level proxies.)*
2. What is the minimum criteria specificity at which `Ω` stops collapsing to topic level (T2)?
3. Under what conditions do accumulated-artifact dynamics begin to dominate independent judgment
   (P5)? *(Requires the extension-fraction metric to be instrumented and validated first.)*
4. Is cross-model verifier error correlation measurable with realistic fixture-set sizes? *(This
   gates whether P4's mitigation may be stated in the indicative.)*
5. Does a two-phase criteria shape — classify the artifact type, then judge against
   type-specific criteria — reduce type-attribution errors relative to single-phase judgment?
6. **First-order response curves.** How does verdict quality vary with evidence budget `B`? What is
   the marginal return on criteria specificity? Does repeated intervention of the same type show
   diminishing response?
7. **Second-order interactions.** Does tightening field criteria change which lens fires? Do verifier
   and generator err in the same domains?
8. **Path dependence.** Does corpus ingestion order shape the developing `Ω` (non-commutativity)? Do
   criteria exhibit hysteresis — resisting revision after contrary evidence, at a threshold higher
   than the one that established them?

> **The perturbation variable.** Questions 6–8 use a borrowed order-of-effects vocabulary, which is
> empty unless the perturbed quantity is named. Let `θ` be the harness's **control-parameter vector**
> — evidence budget, criteria specificity, verifier sample count, ingestion order, lens selection.
> Then: **0th order** = behavior at fixed `θ`; **1st order** = the response of an outcome to a single
> `∂θᵢ`; **2nd order** = cross-parameter interaction `∂θᵢ∂θⱼ`. **Path dependence** (Q8) is a distinct
> category, not a higher order: outcomes depend on the *history* of `θ` rather than its current
> value. r1 listed these as a separate "dynamic layers" bucket without noticing it was not orthogonal
> to the order scaffold.

---

## Appendix A — Retired failure modes

Kept for the lesson, removed from the live register so that register length reflects live risk.

### A1 — Asserted-not-derived architecture description *(retired)*
**Mechanism.** A generated architecture description built from hardcoded literals reproduces
perfectly across runs while being wrong. Determinism was read as accuracy.
**Resolution.** The generator was changed to introspect the actual write surfaces.
**Lesson.** **Reproducibility is not accuracy.** A stable wrong answer is harder to detect than an
unstable one, because stability is a common proxy for correctness.

---

## Appendix B — Instantiation record (template)

All system-specific compliance belongs here, and nowhere else in this document. An entry without a
complete anchor is inadmissible; write **UNASSESSED**.

**Role mapping.** Map each §2 role onto the instantiation's component names, so the body's agnostic
vocabulary resolves. **Substrate is recorded** because it bounds the independence grade a verifier
role can reach (§2): a proof kernel or physical apparatus shares no optimization pressure with the
generator; a sibling model instance shares a family and cannot be assumed decorrelated (P4, §10 Q4).

| §2 Role | Component in this instantiation | Substrate | Independence grade |
|---|---|---|---|
| VERBATIM-VERIFIER | | | |
| BREADTH-MAPPER | | | |
| INDEPENDENT-AUDITOR | | | |
| CRITERIA SET | | — | — |
| LENS | | — | — |
| SALIENCE LEDGER | | — | — |

**Compliance register.** One row per requirement. `Mode as built` may be weaker than the mode
demanded in §6 — that gap *is* the enforcement debt, and naming it is the point of the column.

| Req | Mode demanded (§6) | Mode as built | Compliance | Anchor (artifact + method + date + verifier) |
|---|---|---|---|---|
| RE-1 | STRUCTURAL | | UNASSESSED | |
| RE-2 | STRUCTURAL | | UNASSESSED | |
| RE-3 | CONVENTION | | UNASSESSED | |
| RE-4 | STRUCTURAL | | UNASSESSED | |
| RE-5 | STRUCTURAL | | UNASSESSED | |
| RO-1 | STRUCTURAL | | UNASSESSED | |
| RO-2 | ADVISORY | | UNASSESSED | |
| RO-3 | ADVISORY | | UNASSESSED | |
| RO-4 | ADVISORY | | UNASSESSED | |
| RO-5 | ADVISORY | | UNASSESSED | |

**Enforcement-debt list.** Every row where `mode as built` is weaker than the mode demanded, with the
work item that would close it and its owner. A debt with no owner is a debt that will not close.

---

## Appendix C — Relation to external autonomy taxonomies

The ladder of §3 is **internal** and its numbering does not align with published autonomy spectra.
The following mapping is inherited from a companion framework document's reconciliation section
(verified 2026-07-18; **not re-verified in this revision** — treat the mapping as anchored to that
dated check, not to this document).

Against the L0–L4 spectrum of arXiv 2605.23204, which grades *workflow coverage* (how much of the
research pipeline the machine executes):

- That survey's **L2** — "human-verified, AI-executed," subdivided into single-step, interactive, and
  pipeline variants — is the classification a conforming system of this document falls under, in its
  pipeline variant.
- This document's **L3** ("some `advance` fires without a human action") corresponds to that survey's
  **L4** (AI-autonomous). The survey's **L3** (AI-led, human-assisted) has **no counterpart** here:
  §3's predicate is universally quantified, so it collapses the survey's L3 and L4 into one pole.
  When citing a level number across the two documents, use this mapping, not the bare number.

**The difference that matters is not the number.** The survey grades *how much the machine does* and
treats human verification as the **current practical ceiling** that higher levels are expected to
lift. This document grades *whether the machine may author a belief* and treats human settlement as a
**permanent architectural invariant**. Same classification; incompatible semantics. A conforming
system does not escape the survey's L2 box — it reinterprets what occupying that box commits it to.

**References**
- arXiv 2605.23204 — *AutoResearch AI: Towards AI-Powered Research Automation for Scientific
  Discovery.* Source of the L0–L4 coverage spectrum.
- arXiv 2506.12469 — *Levels of Autonomy for AI Agents.* Corroborating L1–L5 register.
- arXiv 2505.13259 — *From Automation to Autonomy: A Survey on LLMs in Scientific Discovery.*
  Tool / Analyst / Scientist taxonomy.

---

*A requirements document is subject to the standard it imposes. Every status word above is either a
declared design mode or an anchored, dated observation; where neither is available, the entry reads
UNASSESSED.*
