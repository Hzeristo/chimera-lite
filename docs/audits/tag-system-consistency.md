# Audit — [V]/[P]/[U] tag-system definitional consistency & MCP awareness

**Type:** read-only audit · **Date:** 2026-07-18 · **Scope:** every consumer of the
`[V]/[P]/[U]` verdict vocabulary (schema, prompts, MCP tools, static docs, vault criteria).
**Ground truth:** `docs/scratch/tag.txt` (relocated from repo root 2026-07-21) — the only formal definition that exists.

## TL;DR

**There is NO canonical, referenced single source of truth for `[V]/[P]/[U]`.** The one formal
definition (`tag.txt`) is a repo-root scratch file (same class as `GPT-confession.txt`), committed
to no `docs/` authority and **referenced by zero consumers**. Every consumer either (a) restates the
definition independently and incompletely, (b) names the tags without defining them, (c) uses them
with an implicit definition, or (d) uses a **different** three-value vocabulary entirely
(`hypothesis/supported/refuted`). Drift is not merely a future risk — **it already exists** in three
places (runtime `[V]` drops the Tier requirement; two unmapped vocabularies; a P-vs-U ambiguity that
`tag.txt` itself does not resolve).

**Phase K caveat (see Q6.1):** `Phase K — Katalepsis` (Qued) is the phase that *implements* the tags as
load-bearing gates (Gate 1 monotonicity), so a few findings here are **designed-not-yet-built** rather
than drifted — and `tag.txt` is effectively Phase K's Gate-1 design. That does **not** relax the
recommendation: because Phase K makes the *propagation* load-bearing without fixing the *definition*,
the canonical arch file is a **K.0/K.1 precondition** — build it (and converge the runtime `[V]` onto
it) *before* Gate 1 hardens monotonicity over a mis-defined input.

---

## Ground truth (`tag.txt`, root)

| Element | Definition (tag.txt:line) |
|---|---|
| Partial order | `U < P < V`; numeric `U=0, P=1, V=2` (for monotonicity only) — tag.txt:7-9 |
| **[V]** | `∃ source s ∈ Tier1 ∪ Tier2, ∃ verbatim quote q from s, q ⊢ c, q cited in the record` — tag.txt:14-19 |
| **[P]** | partial support **but** `Tier3 only (author framing)` OR `confounded` OR `direction-not-magnitude` — tag.txt:27-31 |
| **[U]** | no checked source satisfies V or P, OR claim out of scope of what `s` asserts — tag.txt:40-42 |
| Monotonicity | `status(n) ≤ min_{dᵢ∈D} status(dᵢ)` (Gate 1's formal basis) — tag.txt:51-55 |

Two load-bearing dependencies of this definition are **undefined anywhere else in the repo**:
the **source-tier taxonomy** (`Tier1/2/3`) and the **split-scoring rule** ("99.8% = robust →
number `[V]`, inference `[U]` — 两个分开算", tag.txt:22).

---

## Q1 — Schema-level definition

**File:** `mcp-servers/chimera-papers/core/schemas.py`

| Location | What's defined | Gap? |
|---|---|---|
| `ExtractedClaim.status` — schemas.py:310 | `Literal["hypothesis","supported","refuted"]` — a **different** 3-value vocabulary, NOT V/P/U. No `Field(description=...)` mapping it to V/P/U. | ⚠️ **Different vocabulary**, unmapped to the tag system |
| `ClaimSource` — schemas.py:296-302 | `quote` (verbatim) + `location`; docstring "quote-or-drop — a reported result with no ClaimSource is invalid." Aligns with `[V]`'s verbatim clause but is **not tied to any V/P/U value**. | Partial — grounding without the tag |
| `LensCritique.verdict` — schemas.py:340 | free `str` ("bottom-line verdict"); not V/P/U. | Not a tag |
| **V/P/U field** | **Does not exist.** No Pydantic field carries `V`/`P`/`U`. The W1 verdict is never modeled in the schema — it flows as an untyped `str` into `write_result` (Q3). | 🔴 **No schema definition or type for V/P/U** |

**Q1 verdict:** The schema does not define `[V]/[P]/[U]` at all. Its only claim-status field
(`ExtractedClaim.status`) is a parallel, self-contained vocabulary (`hypothesis/supported/refuted`)
used by `extract_paper` (Phase Q), with no declared relationship to the W1 tag system.

## Q2 — Prompt-level definition (the critical one)

**Finding: no `.j2` prompt defines `[V]/[P]/[U]`.** The W1 runtime definition lives in a subagent
`.md`, independently authored and **incomplete**.

| Location | What's defined | Gap? |
|---|---|---|
| `prompts/chimera_sys/extract_node.j2` (extract_paper) | Emits `status: hypothesis/supported/refuted` (line 69) + verbatim "quote-or-drop" (71-72). **No `[V]/[P]/[U]`, no Tier requirement.** | Uses the *other* vocabulary; not a V/P/U definition |
| `.claude/agents/chimera-verbatim-verifier.md` (W1 runtime) — verdict rubric, lines 33-41 | Defines all three: "V — Verified: the paper contains a verbatim passage that DIRECTLY supports the claim"; "P — Partial…weaker scope/qualification"; "U — Unverified: no passage supports". "**MANDATORY: no [V] or [P] without a verbatim quote + location.**" | 🔴 **Independent restatement; MISSING the Tier1/Tier2 clause** and any reference to `tag.txt`. Verbatim ✔, source-tier �’ |
| `.claude/skills/chimera-w1-verify/SKILL.md` | Uses `[V]/[P]/[U]`; partial constraint "A claim you cannot ground is `[U]`"; defers the rubric to the agent. | Not a full definition |
| Optics prompts (`eval_scalpel/method_scalpel/synthesis.j2`) | Do **not** produce V/P/U. | n/a |

**Q2 verdict (CRITICAL):** The verbatim-quote requirement for `[V]` **is** specified at runtime
(verifier agent). But the agent's `[V]` **omits the Tier1/Tier2 source requirement** that `tag.txt`
makes definitional — so the `[V]` the LLM actually produces on every W1 run is *weaker* than
canonical `[V]` (a Tier3 author-framing quote can pass the agent's bar but should be `[P]` per
`tag.txt`). And because the definition is restated in the agent rather than referenced, editing the
canonical meaning does not propagate here → drift.

## Q3 — MCP tool description awareness

| Location | What's surfaced | Gap? |
|---|---|---|
| `write_result` docstring — `chimera-vault/server.py:266, 280` | **Names** the tags: "a W1 claim verdict ([V]/[P]/[U] …)"; "verdict: For `w1_verdict` — the tag `V` / `P` / `U`." | 🔴 **Names, does not define** — no machine-readable meaning of `[V]` |
| `write_result` signature — `chimera-vault/server.py:260, 288-289` | `verdict: str \| None`; stored verbatim into frontmatter (`metadata["verdict"] = verdict`). **No `Literal`, no enum, no validation.** | 🔴 Any string accepted (`"v"`, `"Verified"`, `"maybe"`) → silently enters the frontmatter Gate 1 reads |
| `load_criteria` docstring — `chimera-vault/server.py` | Describes the criteria matrix; does not define V/P/U. | Expected (criteria carry it — Q5) |
| `chimera-papers/server.py` | **No V/P/U mention** (extract path uses supported/refuted). | Consistent with Q1 |

**Q3 verdict:** When Claude Code invokes `write_result` (or reads a stored verdict), the tool surface
communicates the tag **names** but no definition, and imposes **no type constraint**. The verdict is
a free string. Nothing at the tool boundary can reject a malformed or mis-defined tag before it lands
in the frontmatter that Gate 1's monotonicity depends on.

## Q4 — Static documentation

| Location | Definition or Use? | Consistent with tag.txt? |
|---|---|---|
| `docs/phases/phase-K.md` (Gate 1) — :53-55, :76, :113-116 | **Use** + the monotonicity rule ("artifact status ≤ weakest dependency"; a `[U]` dep blocks a T/I/D node; a `[P]` dep force-downgrades). References confession examples ("the 99.8% number is [V]"). | ✅ Monotonicity matches tag.txt:51-55. But it is a phase spec using an **implicit** def; cites no canonical source. |
| `docs/phases/phase-L.md` (HSC #2) | **Use** — partial constraint: "a claim with no supporting quote receives [U] or [P], never a fabricated [V]." | ✅ Consistent; not a full def (no Tier). |
| `CLAUDE.md` | **Neither** — the string `[V]/[P]/[U]` does not appear. Only "verbatim verification" (line 39) describes W1. | ⚠️ Top-level doc is **silent** on the tag system. |
| `docs/ARCHITECTURE/NODE_ONTOLOGY.md` | About K/T/I/D typed **edges**, not V/P/U. | n/a — but see Q6: it is the **precedent** for a single-source authority. |
| `TAG_SYSTEM.md` / `tag_definitions.md` / `STAGING_PROTOCOL.md` | **Do not exist** (glob: no files). | 🔴 No dedicated tag authority in `docs/`. |

**Q4 verdict:** The docs that touch the tags (`phase-K`, `phase-L`) are **consistent** with `tag.txt`
on monotonicity and the verbatim/no-fabrication rule, but every one is a *use* under an *implicit*
definition — none is the definition, and none references one. `CLAUDE.md` omits the system entirely.

## Q5 — Criteria files (the primary runtime surface)

**Files:** `<vault>/criteria/type/benchmark.md`, `field/streaming-video-memory.md`,
`disposition/paper-critic.md` (authored 2026-07-18); `type/{method,theory,survey}.md`,
`disposition/_general.md`, `field/_example.md` (stubs).

| Aspect | Finding | Consistent? |
|---|---|---|
| Vocabulary | The three authored files use `[V]/[P]/[U]` as the **operative output** vocabulary, densely (every rule is tagged). | ✅ Same tokens |
| Worked examples | "99.8→robust = [P]", "merge-penalty anti-recurrence = [U]", "Table 3 +0.2 = [P]" — **echo `tag.txt`'s own examples verbatim** (both derive from the same confession). | ✅ Consistent **by shared origin**, not by reference |
| `[V]` bar | "quote the table row, not the abstract sentence"; oracle required for "robust". Verbatim ✔. **No Tier1/Tier2 clause; no reference to tag.txt.** | ⚠️ Same omission as the verifier agent (Q2) |
| **Second definitional axis** | The criteria assign verdicts by **failure-PATTERN** ("[U] — mechanism from a noun phrase", "[P] — robust from an insensitivity number", "force [P] on convergent evidence"). `tag.txt` assigns by **evidence-STRUCTURE** (Tier + verbatim + entailment). Each pattern-trigger *is* reducible to a tag.txt clause (noun-phrase → no source → `[U]`; robust → confounded → `[P]`), so they are consistent today — but this is a **distinct definitional surface** that can drift independently on the next criteria edit. | ⚠️ Consistent now; a second surface to keep synced |
| **"robust" → P vs U** | Criteria (and the eval gold) score the composite "robust" claim `[P]` (via `[P]`'s *confounded* clause). `tag.txt`'s `[V]` worked example labels the robustness **inference** `[U]` and scores it **separately** from the number. | ⚠️ **Divergence** — agree "not [V]", disagree on the P/U boundary (see HIGH-2) |
| Stubs (`type/{method,theory,survey}.md`, `disposition/_general.md`, `field/_example.md`) | Load as explicit `[no criteria file]`/placeholder markers — honest degradation. **But:** when the Architect authors them, there is **no canonical tag def for them to align to** → each will reinvent verdict semantics independently, exactly as `benchmark.md` inherited the Tier-omission. | 🟠 **Pending gap** — the biggest future drift surface |

**Q5 verdict:** The criteria are the **primary runtime surface** — composed into *every* W1 verify
subagent (and W2 later), across an **open, growing set** of `type × field` files. That gives them the
**widest blast radius** of any consumer: a criteria/`tag.txt` divergence propagates to every future
verification. Today the three authored files align with `tag.txt` *because both descend from the
confession*, not because either references a canonical source; they inherit the verifier agent's
Tier-omission, add a second (pattern-based) definitional axis, resolve "robust" P/U in a way `tag.txt`
does not itself settle, and — most consequentially — the **stub files have no authority to align to**
when authored. The surface that most needs a canonical anchor is the one furthest from having one.

---

## Q6 — Canonical source verdict

**Is there a single source of truth? — No.**

```
tag.txt (root, temp)  ── formal def ──   referenced by: NOBODY
   │
   ├─ verifier agent .md ...... restates independently, DROPS Tier1/Tier2
   ├─ write_result docstring .. names only, verdict: str (unvalidated)
   ├─ phase-K.md .............. uses + monotonicity (consistent, implicit)
   ├─ phase-L.md HSC .......... uses (consistent, partial)
   ├─ criteria/*.md ........... uses heavily (consistent by shared origin, DROPS Tier)
   ├─ schemas.py .............. DIFFERENT vocabulary: hypothesis/supported/refuted
   └─ CLAUDE.md ............... silent
```

Five independent expressions of the "same" tag, plus one parallel vocabulary, plus one silence — the
exact multi-site pattern that `NODE_ONTOLOGY.md` was created to end for typed edges. **Multi-site
drift is not hypothetical; it is already present** (HIGH/CRITICAL below).

### Recommendation: **Option C — `docs/ARCHITECTURE/TAG_SYSTEM.md`** (doc-canonical, referenced by all)

Port `tag.txt`'s formalism into `docs/ARCHITECTURE/TAG_SYSTEM.md` (Pure-English per repo convention —
`tag.txt` is currently bilingual), make it the single authority, and have every consumer *reference*
it rather than restate it.

**Rationale (strongest first):**
1. **The repo already solved this exact problem this way.** `NODE_ONTOLOGY.md` in `docs/ARCHITECTURE/`
   unified three disagreeing K/T/I/D edge definitions into one authority that code (`_TYPE_EDGES`)
   mirrors. The tag system is the *same shape of problem* (N disagreeing defs) and deserves the *same
   home and pattern* — precedent, not novelty.
2. **The definition is stable; the criteria are fluid — different homes.** Phase L's friction-arc
   thesis puts *criteria* in the vault precisely because they change daily. The tag *semantics* must
   NOT change daily (they are Gate 1's formal basis). A committed `docs/ARCHITECTURE/` authority is the
   right home for the stable definition; the vault criteria *reference* it and stay fluid.
3. **Rejects Option A (`schemas.py`):** V/P/U is not even in the schema today (it is a text verdict),
   and code-canonical contradicts the "edit without a git commit" spirit for the judgment layer. A
   `Literal["V","P","U"]` on `write_result` is still worth adding (HIGH-3) but as an *enforcement
   mirror* of the doc, not the definition's home.
4. **Rejects Option B (`prompts/tag_definitions.md`):** the actual runtime producer is the verifier
   **agent** (`.md`), not a `.j2`; and the criteria live in the vault. A `prompts/` home would miss both
   real consumers. Option C is reachable from agents, criteria, docs, and tool docstrings alike.

**What the canonical doc must additionally resolve** (gaps `tag.txt` leaves open):
- Define the **Tier1/2/3 source taxonomy** (currently named only in `tag.txt`, defined nowhere).
- Settle **"robust" P vs U** — its own `[V]`-example says the inference is `[U]`, its `[P]` clause says
  confounded → `[P]`. Pick one; Gate 1 depends on it.
- Declare the relationship between `V/P/U` (W1) and `hypothesis/supported/refuted` (extract_paper):
  a crosswalk, or an explicit "these are two systems and Gate 1 consumes only V/P/U."

---

## Q6.1 — Reconciliation with Phase K (the tags ARE slated for implementation)

`Phase K — Katalepsis` (status **Qued**, executes after L) is the phase that converts `[V]/[P]/[U]`
from advisory metadata into **load-bearing structural gates**. This *reframes* several findings above
from "drift" to "designed-not-yet-built" — and, crucially, makes the canonical arch file a Phase K
**precondition**, not an alternative to it.

**What Phase K implements (so it is not a gap — it is pending work):**
- **Gate 1 (K.1)** = the monotonicity rule as a *structural refusal*: "artifact status ≤ weakest
  dependency … a [U]-dependent synthesis is structurally blocked" (`phase-K.md:52-55, :76`, HSC 1
  `:112-116`) — the code form of `tag.txt:51-55`. So `tag.txt` is effectively Phase K's Gate-1 formal
  design (`tag.txt:48` names monotonicity "Gate1 的形式基础").
- The K.1 red line "**a gate is a structural refusal … schema rejects, status propagates**"
  (`phase-K.md:90-93`) is the *intended* fix for HIGH-3 (unvalidated `verdict: str`).
- **Positive / forward-compat:** Phase L's `write_result` already records `depends_on` in frontmatter
  (verified on today's two W1 nodes) — so Gate 1's input requirement (forward-compat constraint 1,
  `phase-K.md:100-101, :204-207`) is **already satisfied**. Not a gap.

**Why the arch file is STILL necessary — and must PRECEDE Phase K:**
Phase K makes the **propagation** load-bearing; it does **not** fix the **definition**. Gate 1 computes
`min` over dependency statuses — it *trusts* that each `[V]/[P]/[U]` was correctly assigned upstream.
The upstream assigner is W1 (the verifier agent), whose `[V]` **drops the Tier1/Tier2 requirement**
(CRITICAL-2). If Phase K hardens monotonicity over statuses produced by a weaker-than-canonical `[V]`,
it **structurally guarantees the propagation of a mis-defined tag** — katalepsis over an akataleptic
input, the exact "kataleptic label that does not carry the guarantee it claims" the phase's own vision
warns against (`phase-K.md:25-28`). A load-bearing gate on an undefined floor manufactures a
*guaranteed* wrong answer instead of an advisory one.

Two definitional questions Gate 1 **cannot run without**, that neither the code nor `tag.txt` resolves:
- **"robust" P vs U** (HIGH-4) — Gate 1's cap on a node depending on a "robust" claim is `[P]` or `[U]`
  by which reading; the monotonicity output differs on the phase's own seal fixture (the 99.8%/96.8%
  number).
- **`V/P/U` ↔ `supported/refuted` crosswalk** (HIGH-5) — if a Gate-1 dependency is a Phase-Q K-node
  claim (`supported/refuted`, `schemas.py:310`), Gate 1 has **no numeric to `min` over**.

**Conclusion:** `docs/ARCHITECTURE/TAG_SYSTEM.md` is a **K.0/K.1 precondition**, not a substitute for
Phase K. Sequence: promote `tag.txt` → the arch file, *complete* it (define the Tier taxonomy, resolve
"robust" P/U, declare the crosswalk), converge the verifier-agent + criteria `[V]` onto it (close
CRITICAL-2), **then** let K.1 implement Gate 1 *against it*. Building the load-bearing gate first and
the canonical definition never is how katalepsis becomes a guarantee of the wrong thing.

---

## Priority-ranked gap list

### 🔴 CRITICAL — tag drift on every W1 run
1. **No referenced canonical source.** The only formal def (`tag.txt`) is a root temp file cited by no
   consumer. Every consumer's definition can drift with no anchor. (Q6)
2. **Runtime `[V]` is weaker than canonical `[V]`.** The verifier agent (`chimera-verbatim-verifier.md:33-41`)
   **and the criteria** — the *widest* surface, composed into every W1/W2 subagent across an open
   `type × field` set — both **omit the Tier1/Tier2 source requirement** (`tag.txt:14-19`). A Tier3
   author-framing quote can earn `[V]` at runtime that should be `[P]`. Fires on *every* W1
   verification, and the criteria carry it into *every field the Architect adds next*. (Q2, Q5)

### 🟠 HIGH — K-Gate monotonicity fails silently
3. **`write_result` accepts an unvalidated `verdict: str`** (`chimera-vault/server.py:260`). A typo or a
   non-canonical string enters the frontmatter Gate 1 reads; monotonicity computes on garbage with no
   rejection. Fix mirror: `Literal["V","P","U"]` + reject-or-normalize. (Q3)
4. **"robust" composite: `[P]` (criteria) vs `[U]` (tag.txt split-scoring).** A synthesis node depending
   on a "robust" claim is capped at `[P]` under the criteria but `[U]` under `tag.txt`'s worked example —
   a different monotonicity result from the same evidence, and `tag.txt` does not resolve it internally.
   (Q5, Q6)
5. **Two unmapped vocabularies.** `extract_paper` K-nodes carry `hypothesis/supported/refuted`
   (`schemas.py:310`); W1 carries `V/P/U`. Gate 1 monotonicity is defined only over `V/P/U`. If a Gate-1
   consumer ever ingests a K-node claim status, there is **no defined crosswalk** → silent
   mis-propagation. (Q1, Q6)
6. **Criteria stubs will reinvent the tag semantics.** `type/{method,theory,survey}.md`,
   `disposition/_general.md`, and `field/*` are stubs the Architect will author into the *widest*
   runtime surface. With no canonical source to align to, each will independently restate `[V]/[P]/[U]`
   (as `benchmark.md` inherited the Tier-omission) — pre-seeding drift into every future field/type
   before those files even exist. This is the gap the canonical source (Q6) most needs to close *before*
   the stubs are filled. (Q5)

### 🟡 LOW — cosmetic / hygiene
7. `CLAUDE.md` does not mention the `[V]/[P]/[U]` system at all (Q4).
8. `tag.txt` is bilingual (Chinese formal prose); promotion to a `docs/` authority needs the Pure-English
   treatment per repo convention.
9. `phase-K.md` / `phase-L.md` use the tags under an implicit definition — harmless once a canonical
   source exists for them to link.

---

*Read-only audit. No files changed. Recommended next step (a future phase, not this audit): create
`docs/ARCHITECTURE/TAG_SYSTEM.md` from `tag.txt`, resolve the three open questions above, and convert
every consumer from a restatement to a reference — mirroring the `NODE_ONTOLOGY.md` precedent.*
