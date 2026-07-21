# THEORETICAL FRAMEWORK — The L2 Research Artifact Manifold

**Status:** 🟢 Conceptual authority for the backward-of-M refactor arc (Phases **L — Locus**,
**K — Katalepsis**, and the not-yet-opened **H** / **I — Isostheneia**). Formalizes *why* those
phases exist; it does **not** redefine the operational objects they enforce.
**Authored:** 2026-07-18 (ported from the Architect's formal contribution statements).
**Register:** epistemology (backward of M — see [`docs/phases/CODENAMES.md`](../phases/CODENAMES.md)).

**Relation to the operational authorities — this doc is the *why*, they are the enforced *how*:**

| Formal object here | Operational authority (the teeth) |
|---|---|
| Tags `[V]/[P]/[U]`, tier taxonomy, monotonicity arithmetic (§2, §3) | [`docs/ARCHITECTURE/TAG_SYSTEM.md`](TAG_SYSTEM.md) |
| Typed edges `derives_from / synthesizes / contradicts / dead_ends / …` (§1) | [`docs/ARCHITECTURE/NODE_ONTOLOGY.md`](NODE_ONTOLOGY.md) |
| Gate 1 (monotonicity) + Gate 2 (multi-framing) as *structural* refusals (§3) | [`docs/phases/phase-K.md`](../phases/phase-K.md) |
| Candidate lifecycle `PENDING → PROMOTED → SUPERSEDED/MERGED/STALE` (§4, §5) | [`docs/phases/phase-L.md`](../phases/phase-L.md) (`write_result`) |
| The `criteria(field, t)` mechanism (§7) | `vault/criteria/{type,field,disposition}/*.md` + TAG_SYSTEM §8 |

> **Drift rule (this document's own Gate 1).** Where a statement here and an operational authority
> disagree on a *detail*, the operational authority wins and this doc defers — exactly as
> `TAG_SYSTEM.md §9` binds its own consumers ("reference this file, do not restate it"). This doc
> supplies the model and the motivation; it is never a second source of truth for a tag, an edge, or
> a gate. A theory doc that quietly re-defines the objects it explains would *perform* the very
> rigor-theater the project exists to delete (`CLAUDE.md` product philosophy; the confession, §3).

---

## 0. What this document is — and the self-suspicion clause

This is the formal architecture of Chimera Lite as a **Level-2 (L2) research artifact management
system**. It is authoritative context for all Phase L / K / H / I work: it names the objects
(manifold, dual clock, two verification categories, the gates) and states the theorems that make the
backward-of-M refactor phases *necessary* rather than decorative.

**The clause that keeps this honest.** The project's north star is self-suspicious: *advisory rigor
is negative value*. A formalism that only **performs** rigor — Greek letters and "Theorem 1" wrapped
around an operation no gate enforces — is worse than no formalism, because it launders opinion into
the appearance of knowledge. Every definition below earns its place only insofar as an *operational
authority* (the table above) makes it load-bearing. Read this file as the map; read `TAG_SYSTEM.md`,
`NODE_ONTOLOGY.md`, and `phase-K.md` as the ground the map is accountable to.

---

## 1. The Research Artifact Manifold

**Definition 1 (Research Artifact Manifold).** A research artifact manifold **M** is a triple
**M = (N, E, T)** where:

- **N** is a set of typed nodes. A node is `n = (type, body, status, provenance, t_commit)` with
  `type ∈ {K, T, I, D}` (Knowledge, Thought, Insight, Decision).
- **E ⊆ N × N** is a set of typed, directed edges with
  `edge_type ∈ {derives_from, synthesizes, contradicts, dead_ends}`.
- **T = (T_m, T_h)** is a dual-clock structure (Definition 2).

> The edge set above is an *illustrative subset*. The canonical, ratified edge vocabulary — seven
> edges with the per-type sets and the direction convention — is [`NODE_ONTOLOGY.md`](NODE_ONTOLOGY.md);
> this document defers to it.

**Definition 2 (Dual Clock).** The manifold operates on two time axes:

- **Machine-time `T_m`** — continuous; governs *candidate material accumulation*. All harness outputs
  (W1 verdicts, W2 breadth maps, K-node candidates) advance on `T_m`.
- **Human-time `T_h`** — discrete, event-driven; governs *truth-state transitions*. Only the
  Architect's commit actions advance `T_h`.

**Theorem 1 (The L2 Signature).** In an L2 system, truth advances *exclusively* on human-time: for
any node `n`,

> `belief(n, t) = true` only if `n` was committed by a human-time event.

Machine-time transitions never change belief state.

**Corollary.** `T_h` defines the **position** of the manifold; `T_m` defines the **candidate pool**.
L2 is not a compromise on the road to full automation — it is a formal architectural commitment that
*preserves human authorship of belief*.

---

## 2. Two-Category Epistemic Verification

Verification decomposes into two structurally separate categories: one the harness can perform, one
only the Architect can.

**Definition 3 (Source Verification).** A claim `c` is **source-verified** iff

> `∃ source s ∈ Tier1 ∪ Tier2`, `∃ verbatim quote q` extracted from `s`, such that `q ⊢ c`
> (`q` entails `c`) and `q` is cited in `c`'s provenance record.

Source-verified claims earn the tag **`[V]`**. This is W1's domain.

*Tier taxonomy* (the source hierarchy `[V]` is built on):

- **Tier 1 — Primary evidence.** Table entries, equation variable definitions, arXiv metadata,
  citation counts, ablation rows. Highest epistemic warrant.
- **Tier 2 — Structural / verbatim self-report.** Non-interpretive, checkable statements of method,
  architecture, or setup; result numbers with their stated context. Verifiable, with caveats.
- **Tier 3 — Authorial framing.** Introduction rhetoric, conclusion implications, superlatives.
  **Cannot ground `[V]`; at most `[P]`.** This tier is the adversary.

> The tier definitions and the exact `[V]/[P]/[U]` algebra are ratified in
> [`TAG_SYSTEM.md §3–§4`](TAG_SYSTEM.md). The confession (§3) is the worked case: a Tier-1 *number*
> is `[V]`; the Tier-3 *inference* drawn from it is not.

**Definition 4 (Taste Verification).** A judgment `j` is **taste-verified** iff the Architect has
hand-authored `j` in a **T** or **I** node on human-time `T_h`, on the basis of (i) accumulated
source-verified evidence, (ii) cross-person verification (I-nodes: advisor discussion), and
(iii) domain expertise that exceeds W1's scope. Taste verification **cannot be automated**; T and I
nodes are hand-written.

**Separation Principle.** Source-verification (the W1/W2 domain) and taste-verification (the
Architect's domain) are *structurally* separate. The harness produces source-verified candidate
material; the Architect settles taste judgments. This separation is not a limitation — it is the
mechanism by which the system refuses to inherit *authorial framing as knowledge*.

---

## 3. Provenance Monotonicity (Gate 1)

**Definition 5 (Status Ordering).** The tags form a total order:

> `U < P < V` — numeric encoding `U = 0, P = 1, V = 2` (used *only* for the Gate-1 arithmetic).

**Gate 1 (Provenance Monotonicity).** For any synthesis node `n` with dependency set
`D = {d₁, …, dₖ}`:

> `status(n) ≤ min_{dᵢ ∈ D} status(dᵢ)`

A node dependent on a `[U]` claim cannot be `[V]`; a synthesis dependent on a `[P]` claim is at most
`[P]`. This rule is **structural** (pipeline-enforced), not **advisory** (prompt-suggested). A
`[U]`-dependent conclusion is rejected by the pipeline schema, not by the agent's discretion.

**Motivation — the confession.** The confession
([`GPT-confession.txt`](../../GPT-confession.txt), 2026-07-12) recorded an agent that flagged claims
`[U]` and then reasoned with them as if `[V]` — *"worse than not flagging, because it performs
rigor."* Advisory provenance is cosmetic. Gate 1 makes it load-bearing.

> Gate 1's implementation as a *structural refusal* — schema-reject, not prompt-honor — and its
> arithmetic are specified in [`TAG_SYSTEM.md §6`](TAG_SYSTEM.md) and
> [`phase-K.md` (K.1)](../phases/phase-K.md). Gate 1 reads the recorded `depends_on` that
> `write_result` writes; it never re-infers dependencies with an LLM.

---

## 4. Provenance Decay (temporal extension)

**Definition 6 (Belief).** `belief(n, t) = (status(n) = PROMOTED) ∧ ¬SUPERSEDED(n, t)`.

**Provenance Decay.** If node `n` has status `PROMOTED` with a source dependency `d`, and `d`
transitions to `SUPERSEDED` at time `t' > t_commit(n)`, then `n` transitions to `STALE` at `t'`.
`STALE` nodes require Architect re-evaluation before belief is restored.

This is the *temporal analog* of Gate 1. Not only does a synthesis inherit its weakest source's
status at commit time (§3) — if a source is later invalidated, downstream syntheses decay. The
manifold is **not a monotone-growing knowledge base**; beliefs can and should retract when evidence
is superseded.

> The lifecycle states (`PENDING_REVIEW → PROMOTED → SUPERSEDED | MERGED | STALE`) and the
> supersede/mark-stale operations are `write_result`'s ([`phase-L.md` — Artifact Lifecycle](../phases/phase-L.md)).
> **Open debt:** §4 is theory with no phase yet. The temporal-belief-revision phase is the natural
> **Phase H** (backward of M → epistemology register, per `CODENAMES.md`); until it is opened, decay
> lives here as specification, not as an enforced gate.

---

## 5. The Futures Model (L2 operational semantics)

The L2 system is best understood as an **asymmetric market** in two coupled books:

**Machine-side — candidate positions (high volatility, `T_m`).** W1/W2 candidate material, suggested
criteria, breadth maps. All positions are `PENDING`. *Hallucination is permitted here* — un-settled
positions carry no epistemic cost.

**Human-side — settled positions (low volatility, `T_h`).** T/I/D nodes authored by the Architect.
**Settlement** = converting a candidate into a belief. Once settled, only the Architect can reverse.

This captures the actual value proposition: the harness provides **alpha** — candidate insights the
Architect would not have surfaced manually in 20–30-minute cycles — while the Architect provides
**settlement** — the taste judgment that decides which candidates become beliefs. *The harness never
settles; the Architect never generates raw candidates solo.*

---

## 6. L2 vs Full Automation (the formal distinction)

L2 is **not** "automation with a human in the loop as a safety check." It is:

- **Full automation (L3, in this document's internal numbering):** `T_h` is either absent or
  simulated by `T_m`. Machine-time transitions advance belief. The manifold is autonomous.
- **L2:** `T_h` is *structurally required*. No belief transition without a human commit. The system
  is architecturally *incapable* of promoting its own candidates.

This distinction governs **evaluation**. An L2 system should be judged on

1. the **quality of candidate material** reaching the Architect, and
2. the **reduction in Architect time-cost per settled belief**,

**not** on autonomous task completion — because task completion is not its goal. Its goal is
*augmenting* human research judgment, not replacing it.

> This internal L2/L3 vocabulary differs from the autonomy taxonomy of the survey **arXiv 2605.23204**.
> That difference is verified and reconciled in **§8** — read it before citing "L2" across the two
> vocabularies; the numbers do not line up (this document's "L3 = full automation" is the survey's
> **L4**).

---

## 7. Manifold Consistency (the criteria connection)

The Architect's taste, formalized in `vault/criteria/`, is the bridge between source-verification
(W1: facts) and taste-verification (T/I nodes: judgment).

> `criteria(field, t)` — the set of standards the Architect uses at human-time `t` to translate
> source-verified evidence into settled beliefs.

Criteria evolve on **human-time**: the Architect edits them in Obsidian, with zero git. W1 loads the
latest criteria on each run — the harness adapts to evolving taste *without code changes*. This is
the mechanism by which the manifold stays **brain–machine consistent**: the machine's verification
standards track the Architect's *current* epistemic commitments, not a frozen snapshot.

**Consistency failure mode.** If criteria drift from the lens analytical patterns (Option A of the
reconciliation, [`docs/audits/lens-criteria-reconciliation.md`](../audits/lens-criteria-reconciliation.md)),
the manifold **bifurcates** — W1 applies one standard, `extract_paper` applies another. The **Option C**
reconciliation (bidirectional slug links; `TAG_SYSTEM.md` as the shared doubt-signal → tag vocabulary,
[§8](TAG_SYSTEM.md)) prevents this by making the two vocabularies reference a common authority.

---

## 8. Reconciliation with the external autonomy taxonomy (arXiv 2605.23204)

*(This section discharges the "WebSearch and verify" instruction embedded in the source statement of
§6. Verified 2026-07-18.)*

**The survey exists.** arXiv **2605.23204**, *"AutoResearch AI: Towards AI-Powered Research Automation
for Scientific Discovery,"* defines an **L0–L4** autonomy spectrum measured along *workflow control,
task execution, validation authority, and scientific responsibility*:

- **L0** human-only · **L1** human-led, AI-assisted · **L2** *human-verified, AI-executed* ·
  **L3** AI-led, human-assisted · **L4** AI-autonomous.
- The survey's **L2**: *"AI begins to execute substantive parts of the research workflow, but the
  scientific authority for verification, acceptance, and accountability remains human-held."* It
  subdivides into **L2-S** (single-step), **L2-I** (interactive workflow), **L2-P** (pipeline under
  human verification). L1–L2 is the survey's "human-steered / Vibe Research" region; L3–L4 is where
  routine stepwise human verification is progressively removed.

**Verdict on the source statement ("differs greatly").** *Partially true, and the precise shape of
the difference matters more than the verdict.*

1. **The claim is TRUE at the level of axis, modality, and telos.**
   - *Axis.* The survey grades **workflow coverage / who executes** (how much of the pipeline the AI
     runs). This framework grades **who authors belief** — the `T_m` / `T_h` boundary (Definition 2).
     Different measured quantities.
   - *Modality.* The survey's L2 is a **descriptive, empirical waypoint**: human verification is the
     *current practical ceiling* that L3/L4 are expected to lift. This framework's L2 is a
     **normative, architectural invariant**: human settlement is *permanent* (Theorem 1, and the §6
     "architecturally incapable" clause), not a ceiling awaiting removal.
   - *Telos.* For the survey, L2 is a **way-station toward L4 autonomy**. For this framework, L2 is a
     **terminal design commitment** — explicitly "not a compromise toward full automation."

2. **But the claim is FALSE if read as "Chimera escapes the survey's L2 box."** By the survey's own
   criteria, Chimera Lite *classifies* as **L2 — specifically L2-P** (pipeline automation under human
   verification): the harness (W1 verbatim verification, W2 breadth mapping) executes substantive
   research labor, while verification, acceptance, and accountability stay human-held. Chimera does
   not sit *outside* the survey's L2; it **reinterprets what being at L2 means and why** —
   coverage-waypoint (survey) vs authorship-invariant (this framework). *Same classification,
   incompatible semantics.*

3. **Numbering caveat.** This document's internal "**L3 = full automation** (`T_h` absent/simulated)"
   corresponds to the survey's **L4** (AI-autonomous, no structural human necessity). The survey's
   **L3** (AI-led, *human-assisted*) has **no counterpart** in this framework's binary — the binary
   collapses the survey's L3/L4 into one "full automation" pole. When citing "L2/L3" across the two
   documents, use this mapping, not the bare number.

**Net.** Keep the label **L2**; drop the assumption that it means the same thing. The survey answers
*"how much does the AI do?"*; this framework answers *"can the AI author a belief?"* — and its
answer, by construction, is **no**.

**Sources:**
- [arXiv 2605.23204 — AutoResearch AI: Towards AI-Powered Research Automation for Scientific Discovery](https://arxiv.org/abs/2605.23204) ([HTML](https://arxiv.org/html/2605.23204))
- [Levels of Autonomy for AI Agents (working paper, arXiv 2506.12469)](https://arxiv.org/html/2506.12469v1) — corroborating L1–L5 register
- [From Automation to Autonomy: A Survey on LLMs in Scientific Discovery (arXiv 2505.13259)](https://arxiv.org/html/2505.13259v3) — Tool/Analyst/Scientist three-level taxonomy

---

## 9. Reconciliation with the repo's operational authorities

This section is the drift-guard: every formal object above, mapped to the file that *enforces* it, so
a future session can never mistake this doc for the definition.

| Formal object (this doc) | Enforced by | Note on any divergence |
|---|---|---|
| `type ∈ {K,T,I,D}` + edge vocabulary (§1) | `NODE_ONTOLOGY.md` | §1 lists a 4-edge subset for illustration; the canonical set is 7 edges. Authority wins. |
| `[V]/[P]/[U]`, Tier 1/2/3, `U<P<V` (§2, §3, §5-status) | `TAG_SYSTEM.md §3–§4` | The confession's "…therefore robust" inference lands at **`[P]`**, not `[U]` (`TAG_SYSTEM.md §5`); §3's "reasoned with `[U]` as `[V]`" refers to the general cosmetic-flag failure, not that specific number. |
| Gate 1 monotonicity as structural refusal (§3) | `TAG_SYSTEM.md §6` + `phase-K.md` K.1 | Identical arithmetic; phase-K adds the schema-reject mechanism. |
| Gate 2 (multi-framing, not in the source statements) | `phase-K.md` K.2–K.3 | §2's Separation Principle is *why* Gate 2 exists: a `[V]` number must not inherit a single (author) frame. |
| Lifecycle `PENDING→PROMOTED→SUPERSEDED/MERGED/STALE`; decay (§4, §5) | `phase-L.md` (`write_result`) | Decay (§4) has no enforced gate yet — see the Phase H open debt (§4 note, §10). |
| `criteria(field, t)`, brain–machine consistency (§7) | `vault/criteria/**` + `TAG_SYSTEM.md §8` | Zero-git vault edit surface; §8 is the doubt-signal → tag bridge both lenses and criteria reference. |

---

## 10. Open theoretical debts

- **Phase H is unhomed.** §4 (Provenance Decay) is fully specified here but enforced nowhere. It is
  the natural **Phase H** (temporal belief revision; backward-of-M → epistemology register). Until
  opened, decay is advisory — and by this project's own standard, advisory decay is negative value.
- **Phase I (Isostheneia) is referenced, not built.** §5's "settled positions only the Architect can
  reverse" is single-shot; iterative adversarial re-settlement (advocate ⇄ skeptic with
  entropy-collapse management) is Phase I, deferred (`phase-K.md`, Out of Scope).
- **The market metaphor (§5) is descriptive, not enforced.** "Hallucination is permitted on the
  machine-side" is a *permission*, not a mechanism; what makes it safe is Gate 1 + human-only
  settlement, not the metaphor. Do not let the metaphor stand in for the gate.

---

*Conceptual authority for the L/K/H/I arc. Operational truth lives in `TAG_SYSTEM.md`,
`NODE_ONTOLOGY.md`, `phase-K.md`, and `phase-L.md`. This document formalizes the reasons those files
must exist — and forfeits its own authority the moment it contradicts them.*
