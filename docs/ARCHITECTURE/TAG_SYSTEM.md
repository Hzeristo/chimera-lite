# TAG_SYSTEM — Chimera Lite [V]/[P]/[U] verdict authority

**Status:** 🟡 DRAFT — canonical authority. The core algebra (partial order, `[V]/[P]/[U]`
definitions, monotonicity) is ported faithfully from `docs/scratch/tag.txt` (the prior scratch ground truth). The
three **completions** — §4 tier taxonomy, §5 "robust" P/U resolution, §7 crosswalk — are proposed
design decisions marked **⚖ RATIFY** and pending the Architect's sign-off (like `NODE_ONTOLOGY.md`'s
two renames).
**Authored:** 2026-07-18 · **Supersedes:** `docs/scratch/tag.txt` (scratch, relocated from repo root 2026-07-21) — retire it once this is ratified.
**Audit:** `docs/audits/tag-system-consistency.md` (closes CRITICAL-1/2 and HIGH-4/5).
**§8 added** for lens-criteria reconciliation Option C (`docs/audits/lens-criteria-reconciliation.md`):
the doubt-signal → tag bridge is the single source both `prompts/lenses/*.md` and `criteria/**` reference.

> This is the single source of truth for what `[V]`, `[P]`, `[U]` MEAN and how their status
> propagates. Every consumer — the W1 verifier agent, the vault `criteria/`, `write_result`,
> Phase K's Gate 1, Phase L's W1 HSC — must **reference** this file, never restate the definition
> (§8). It is the definitional floor Phase K's Gate 1 makes load-bearing; it must exist and be
> complete **before** Gate 1 hardens monotonicity over it, or the gate guarantees the propagation
> of a mis-defined tag (`phase-K.md:25-28`).

---

## 1. Why this doc exists

`[V]/[P]/[U]` had **no canonical referenced definition**. The one formal statement (`tag.txt`) was a
root scratch file cited by nobody; five consumers each restated or merely used the tags, one used a
different vocabulary (`supported/refuted`), and the runtime `[V]` (verifier agent + criteria) silently
**dropped the Tier1/Tier2 requirement** the formal `[V]` mandates. Same multi-site-drift shape that
`NODE_ONTOLOGY.md` resolved for typed edges — resolved here the same way: one authority, all consumers
reference it.

---

## 2. Partial order and numeric encoding

The three statuses form a total order (a chain, the trivial Hasse diagram):

```
U < P < V           (U weakest, V strongest)
numeric: U = 0, P = 1, V = 2      (used ONLY for monotonicity arithmetic — §6)
```

---

## 3. The three verdicts

### [V] — Verified

```
V(claim c) ⟺
  ∃ source s ∈ Tier1 ∪ Tier2,  ∃ verbatim quote q extracted from s,
  such that q ⊢ c   (q directly entails c)
  AND q is explicitly cited in the claim record.
```

*Plain:* the paper contains a line that **literally** supports the claim, drawn from **primary
evidence** (Tier 1 or Tier 2 — §4), **not** the authors' framing, and the quote is on record.

*Worked case (confession):* the reported figure "99.8% compression / 96.8% retained" is a Tier-1
number → the **numeric** claim is `[V]`. The **inference** "…therefore robust" is a separate claim and
is **not** `[V]` (see §5). Score the number and the inference separately (the split-scoring rule).

### [P] — Partial

```
P(claim c) ⟺
  ∃ source s that partially supports c, BUT one of:
    - s ∈ Tier3 only        (author framing, no primary data), OR
    - the evidence is confounded   (e.g. a delta over a weak baseline; an
                                     insensitivity number equally consistent
                                     with a rival reading), OR
    - the quote supports the DIRECTION but not the MAGNITUDE.
```

*Plain:* there is support, but with a **known hole** — or only the authors' own say-so.

*Worked case (confession):* "Table 3 proves the tree works" — the `+0.2` margin is citable (Tier 1),
but `+0.2` is within noise → confounded → `[P]`, not `[V]`.

### [U] — Unverified

```
U(claim c) ⟺
  ¬∃ checked source satisfying V or P,
  OR  a source exists but c is OUTSIDE the scope of what that source asserts.
```

*Plain:* no primary support found, or the paper is asserting something else.

*Worked case (confession):* "the merge-count penalty is anti-recurrence" — Eq. 2 defines it as an
anti-**degradation** (fidelity) term, and alone it behaves like content-blind uniform downsampling →
the paper asserts the opposite kind of thing → `[U]`.

---

## 4. ⚖ RATIFY — the source-tier taxonomy (`[V]` depends on it; it was defined nowhere)

`[V]` requires a `Tier1 ∪ Tier2` source and `[P]`'s first branch turns on `Tier3`. Those tiers were
named in `tag.txt` and **defined nowhere**. Definition (confession-grounded — the whole confession is
"read the table/equation, not the abstract"):

| Tier | What it is | Admits |
|---|---|---|
| **Tier 1 — Primary in-paper evidence** | The paper's own measured/computed data and formal objects: results tables, figures, reported numbers, **defining equations with their indices/subscripts**, ablation rows, measured cost/latency. *What the paper did and got, as recorded.* | `[V]` |
| **Tier 2 — Verbatim factual self-report + external primary sources** | (a) The paper's **non-interpretive, checkable** descriptions of its own method/architecture/setup — e.g. *"all root nodes … are fed into the LLM"*, *"the backbone VLM remains frozen"*, *"we assume features are already extracted"* — structural facts falsifiable against the paper's own equations/code. (b) External primary artifacts: the paper's own repo/README, another paper's Tier-1 data, an official benchmark spec. | `[V]` |
| **Tier 3 — Author framing / inference** | The authors' **interpretation** of their own evidence: *"demonstrates robustness"*, *"high perceptual error tolerance"*, superlatives, narrative gloss. **Inadmissible for `[V]`.** This tier is *the adversary* — the layer a claim under test usually leans on. | `[P]` at most |

**Rule:** a `[V]` quote must come from Tier 1 or Tier 2. A quote from Tier 3 supports **at most `[P]`**,
regardless of how confident the authors sound. This is the exact clause the current runtime `[V]`
(verifier agent, criteria) omits — CRITICAL-2 in the audit.

---

## 5. ⚖ RATIFY — the split-scoring rule and the "robust" P/U resolution

**Split-scoring.** A compound claim decomposes into its factual part and its inferential part; each is
scored on its **own** admissible evidence, and one part's status never bleeds onto the other.

**Resolution of the "robust" ambiguity** (audit HIGH-4). `tag.txt`'s `[V]`-example labels the "robust"
inference `[U]` — but that is loose shorthand for "not `[V]`," and it conflicts with `[P]`'s own
"Tier3-only" branch. Precise landing:

- The **number** (99.8% / 96.8%) is Tier 1 → **`[V]`**.
- The **inference** ("…therefore robust") is supported by a Tier-3 author-framing source **and** is
  confounded (equally consistent with "the benchmark is fidelity-blind"). Both are `[P]` triggers →
  the inference is **`[P]`**, *not* `[U]`.
- **`[U]` is reserved** for a claim with **no admissible support at all** (Tier 1/2/3 silent) or
  out-of-scope. An author-asserted-but-primary-unsupported inference is `[P]`; an
  unasserted/unsupported claim is `[U]`.

Under monotonicity (§6), a composite "robust *because* 99.8%→96.8%" = `min([V] number, [P] inference)`
= **`[P]`**. This matches the vault `criteria/` and the Phase-L eval gold; it supersedes the
`[V]`-example's shorthand `[U]`.

---

## 6. Monotonicity (Phase K Gate 1's formal basis)

For any synthesis/artifact node `n` with dependency set `D = {d₁, …, dₖ}`:

```
status(n) ≤ min_{dᵢ ∈ D} status(dᵢ)        where V→2, P→1, U→0
```

*Meaning:* a conclusion's status cannot exceed its **weakest** dependency. Depends on one `[U]` →
`n` is at most `[U]`. Depends on `[V]` + `[P]` → `n` is at most `[P]`.

Phase K's **Gate 1 (K.1)** implements this as a *structural refusal* — a `[U]`-dependent synthesis is
structurally blocked, a `[P]`-dependent conclusion is force-downgraded (`phase-K.md:52-55, :76`). Gate 1
**reads the recorded `depends_on`** (Phase L's `write_result` writes it) and never re-infers
dependencies with an LLM (`phase-K.md:100-101`).

---

## 7. ⚖ RATIFY — crosswalk: `[V]/[P]/[U]` ↔ `hypothesis/supported/refuted`

Two vocabularies answer two different questions, and must not be silently merged (audit HIGH-5):

- **`hypothesis/supported/refuted`** (`ExtractedClaim.status`, `schemas.py:310`, Phase Q `extract_paper`
  K-nodes) = the claim's epistemic state **as the paper frames it** — the paper's own verdict on its
  own claim.
- **`[V]/[P]/[U]`** (W1) = the **harness's verification verdict** on a specific assertion, at a specific
  evidential strength (with a tier requirement the Q vocabulary has no notion of).

**Rule: Gate 1 operates ONLY on `[V]/[P]/[U]`.** A Phase-Q K-node claim status is **not** a valid Gate-1
dependency until **explicitly re-expressed** as a V/P/U verdict — the tier information `[V]` needs is
absent from the Q schema, so the mapping is a sanctioned re-expression, **never automatic**:

| Q status | → re-express as | Condition |
|---|---|---|
| `supported` | `[V]` | a Tier 1/2 `ClaimSource` (verbatim quote + location) is present |
| `supported` | `[P]` | support is framing-only / confounded (no Tier 1/2 quote) |
| `hypothesis` | `[U]` | proposed, not yet grounded (→ `[P]` only if partial grounding is separately shown) |
| `refuted` | `[U]` | for the claim **as stated** — not supported, actively contradicted. Record a `contradicts` edge; do **not** read it as `[V]` of the negation unless the negation is itself W1-verified. |

---

## 8. Doubt-signal → tag translation (the lens ↔ W1 bridge)

Lens analytical signals (`prompts/lenses/*.md`) and W1/W2 `[V]/[P]/[U]` tags are **the same
judgment in two vocabularies**: a lens NAMES a doubt-signal; W1 TRANSLATES it to a tag. *The doubt
is why a claim is `[P]` and not `[V]`* — a lens's doubt and a `[P]` tag do not conflict; the tag is
the doubt's calibrated form.

This table is the **single source** both the lens files and the vault `criteria/**` reference. A
lens never sets a tag directly — it emits a signal, and W1 assigns the tag using this table plus the
§3–5 definitions. **Add a new signal HERE first, then reference it** — this is what keeps the two
edit surfaces (git-tracked lenses, zero-git criteria) from drifting.

| Doubt-signal (lens vocabulary) | → W1 tag | Why (per §3–5) |
|---|---|---|
| `self-evaluation-only` — judge model == judged family (LLM-as-judge mirror) | **[U]** | no admissible source; a self-graded score is not a measurement (§3) |
| `unfalsifiable` — no test could break the claim | **[U]** | decoration, not evidence (§3) |
| `decorative-math` — equation survives the deletion test / scaling in Greek clothing, no ablation shows it matters | **[U]** | the "formalism drives behavior" claim is unverified (§3) |
| `mechanism-from-name` — a mechanism's function asserted from its noun phrase, defining equation unread | **[U]** | Tier 1/2 unread → direction unverifiable (§3, §4) |
| `human-ceiling-anomaly` — a baseline ≈ human where others floor, undiscussed | **[U]** | metric broken; nothing on it verifies (§3) |
| `experiment-design-leak` — asymmetric prompting / contamination / cherry-picked seeds | **[P]** | the number is Tier-1 `[V]`; the "gain is earned" inference is confounded (§5) |
| `endpoint-only-metric` — final accuracy / win-rate, no process evidence | **[P]** | the number is `[V]`; the validity inference is confounded (§5) |
| `mock-not-streaming` — batch-fed static log, not turn-by-turn recall | **[P]** | recall claim inflated; the number ≠ what is claimed (§5) |
| `margin-within-noise` — delta ≤ noise, no reported variance | **[P]** (`[U]` for a "significant" claim) | confounded (§5); "significant" is unresolvable (§3) |
| `insensitivity-as-robustness` — massive reduction, tiny accuracy cost, read as "robust" | **[P]** | equally consistent with benchmark-blindness; author framing (§5) |

**Signals mapping to `[V]` are intentionally absent.** A lens produces *doubt*; `[V]` is earned by
the **presence of a Tier-1/2 verbatim quote** (§3), never by the **absence** of a doubt-signal. "No
lens fired" is not evidence — it is silence.

---

## 9. Consumers — reference this file, do not restate it

Descriptive convergence targets (this doc does **not** execute them — like `NODE_ONTOLOGY.md` §4/§5):

| Consumer | Current state | Convergence needed |
|---|---|---|
| `.claude/agents/chimera-verbatim-verifier.md` | own `[V]/[P]/[U]` rubric; **no Tier clause** | cite §3–4; add the Tier 1/2 requirement to `[V]` (CRITICAL-2) |
| `<vault>/criteria/**/*.md` | pattern-triggers, tag-consistent by shared origin | header pointer to this file; the stub files (`type/{method,theory,survey}`, `_general`) author against §3–5 |
| `chimera-vault` `write_result` | `verdict: str` unvalidated | `Literal["V","P","U"]` (schema-reject, per Phase K K.1); docstring links here (HIGH-3) |
| `docs/phases/phase-K.md` (Gate 1) | monotonicity design | implements §6 + §7 against this file |
| `docs/phases/phase-L.md` (W1 HSC) | uses the tags | references §3 for the semantics |
| `mcp-servers/chimera-papers/core/schemas.py` | `ExtractedClaim.status` (other vocab) | document the §7 crosswalk at the field |
| `CLAUDE.md` | silent | one line pointing here |
| `prompts/lenses/*.md` (lens canonical sources) | free-text `verdict`, outside the tag system | carry a `## W1 epistemic translation` block that references §8 (doubt-signal → tag); never restate a mapping |

---

## 10. Provenance

Content ported and completed from `docs/scratch/tag.txt` (relocated from repo root — the prior scratch ground truth), translated to
en-US per repo convention (`rg \p{Han}` doc-only check). §2/§3/§6 are faithful ports; §4/§5/§7 are the
completions the audit flagged as required and are marked **⚖ RATIFY**. On ratification, retire `tag.txt`
and flip this doc's status to ✅ RATIFIED.
