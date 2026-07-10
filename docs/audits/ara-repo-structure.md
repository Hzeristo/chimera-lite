# ARA Repository — Ground-Truth Structure Audit (v2, from local clone)

**Repo:** `github.com/ARA-Labs/Agent-Native-Research-Artifact` (paper arXiv 2604.24658).
**Source of truth:** the user's local clone at `D:\MAS\Agent-Native-Research-Artifact`, read **directly**
off disk. **This v2 supersedes the WebFetch-based v1** and corrects it (see "Corrections" below).
**Date:** 2026-07-09. Companion to `docs/audits/ara-2604.24658-structure.md` (paper-level).

---

## Corrections to v1 (what reading the real files changed)

1. **A schema doc DOES exist** — v1 said "no schema." Wrong. `skills/compiler/references/ara-schema.md`
   is a complete field-level spec (+ `exploration-tree-spec.md`, `validation-checklist.md`), and there is
   a real validator `docs/the-ara-of-ara/src/seal/seal.py` ("Seal Level 1"). It is still **not a typed
   schema** (no Pydantic/JSON Schema) — but "no schema at all" was inaccurate.
2. **Trace node enum is `question | experiment | dead_end | decision | pivot`** (per `exploration-tree-spec.md`)
   — so the paper's "pivot" was right; **the ResNet example's `insight` node is off-spec**.
3. **The repo's own example diverges from its own spec** (see Q2) — a material finding about enforcement.

---

## Step 1 — Actual repository tree (from disk)

```
Agent-Native-Research-Artifact/
  README.md  CONTRIBUTING.md  LICENSE  .gitignore
  .github/workflows/  (publish-ara-skills.yml, validate.yml)
  skills/                       # six agent skills (SKILL.md + references/ each)
    compiler/   research-manager/   rigor-reviewer/
    research-visualizer/   research-foresight/   submit-ara/
  examples/
    minimal-artifact/   resnet-ara-example/   resnet-paper.pdf   resnet-walkthrough.md
  packages/
    ara-skills/    (npx installer: package.json, bin/, src/)
    ara-viewer/    (build_manifest.py, viewer.js, index.html)
  docs/
    the-ara-of-ara/   # the paper dogfooding itself as an ARA (full src/eval harness + src/seal/seal.py)
    figures/  poster.pdf
```

**The `/logic /src /trace /evidence` are the per-artifact anatomy** (inside each ARA), not repo top-level.
Canonical anatomy (`ara-schema.md`; `✓` = mandatory core):

```
PAPER.md ✓                 frontmatter (title/authors/year/venue/doi/ara_version/domain/keywords/
                           claims_summary/abstract) + Layer Index
logic/
  problem.md ✓  claims.md ✓  concepts.md ✓  experiments.md ✓  related_work.md ✓
  solution/constraints.md ✓  + solution/{architecture,algorithm,heuristics,…}.md  (as warranted)
src/
  environment.md ✓  + artifacts.md / configs/ / execution/*.{py,…} / prompts/  (as warranted)
trace/exploration_tree.yaml ✓
evidence/README.md ✓  + tables/{tableN.md+tableN.png}  figures/{figureN.md+figureN.png}  (every numbered obj)
```

**Manifest:** `PAPER.md` (~200 tokens) — progressive disclosure Level 1 (agent reads only this to judge
relevance). **Install:** `npx @ara-commons/ara-skills`; skills follow the Agent Skills open standard
(Claude Code / Codex / Cursor / …). ARA is a **skill bundle + file convention**, not a Python library.

---

## Q1 — Concrete node/edge types (the real ontology)

Atoms are typed by **ID prefix + field set** (per `ara-schema.md`). Not "sources/methods/experiments/outputs."

**Claim (`logic/claims.md`, `C##`) — schema fields:** `Statement` (the *mechanism/takeaway*, subject must
be a mechanism not a recipe, **carries no numbers**) · `Conditions` (mandatory regime + untested boundary) ·
`Sources` (per load-bearing number: `<value> ← <ref> «verbatim line» [input|result]`) · `Status`
(`hypothesis|supported|refuted`) · `Falsification criteria` · `Proof` (`[E##]`) · `Evidence basis` ·
`Dependencies` (`[C##]`) · `Tags`.

**Trace node (`trace/exploration_tree.yaml`, `N##`) — canonical enum `question | experiment | dead_end |
decision | pivot`** (`exploration-tree-spec.md`). Common: `id`, `type`, `title`, `support_level`
(`explicit|inferred`), `source_refs`, `description`, `children` (nesting), `also_depends_on: [N##]`
(DAG cross-edges). Type-specific **per spec**:
- `experiment` → req `result`, opt `evidence: [C##/refs]`
- `dead_end` → req `hypothesis`, `failure_mode`, `lesson`; **no children** ("THE MOST VALUABLE NODE TYPE")
- `decision` → req `choice`, `alternatives`, opt `evidence`
- `pivot` → req `from`, `to`, `trigger`

**Other typed atoms:** experiments (`E##`: Verifies/Evidence/Run/Setup/Procedure/Metrics/Expected-outcome,
**no exact numbers**), heuristics (`H##`: Rationale/Sensitivity/Bounds/Code-ref/Source), concepts
(Notation/Definition/Boundary/Related), related_work (`RW##`: DOI/Type∈`imports|bounds|baseline|extends|refutes`/Delta/Claims-affected).

**"Edges" = cross-layer forensic bindings, all INTRA-artifact:** `claim.Proof→E##`,
`experiment.Verifies→C##`, `experiment.Evidence→evidence/`, `heuristic.Code-ref→src/execution/`,
`tree.evidence→C##`, `claim.Dependencies→C##`, `also_depends_on→N##`.

**vs our assumption "sources→methods→experiments→outputs":** confirmed **wrong** — that was the mis-cited
reproducibility paper (2605.02651). Real ARA has no "sources"/"outputs" node type; it is a 4-layer tree of
`C/E/H/N/RW`-coded atoms bound by references.

---

## Q2 — Pydantic / JSON schema?

**No typed schema — a markdown field spec + a structural validator, loosely enforced.**
- The spec is `skills/compiler/references/ara-schema.md` (per-file mandatory fields, quoted in Q1),
  `exploration-tree-spec.md`, `validation-checklist.md`. **No Pydantic model, no JSON Schema.** Enforcement
  is `Seal Level 1` (`docs/the-ara-of-ara/src/seal/seal.py` + the validation checklist), a structural/
  reference-integrity check, not type validation.
- **Decisive evidence it is a loose convention: the authors' own ResNet example violates their own spec.**
  `trace/exploration_tree.yaml` uses a node `type: insight` (**not in** the canonical `question|experiment|
  dead_end|decision|pivot` enum), and its `dead_end` nodes carry `why_failed` while the spec requires
  `hypothesis`/`failure_mode`/`lesson`; its `decision` nodes carry `rationale` while the spec requires
  `choice`/`alternatives`. Likewise `logic/claims.md` uses an `Interpretation` field and lacks the spec's
  now-mandatory `Conditions`/`Sources`. The example predates / drifts from the spec, and Seal L1 did not
  catch it.

**Net:** *"ARA is a documented file-system convention with a markdown field spec and a structural validator
— not a typed schema, and not strictly enforced even inside its own repo."* If we adopt it we author our
**own** Pydantic `response_model` mirroring these conventions (and can enforce it more strictly than they do).

---

## Q3 — Extraction, or only a prescription for authoring?

**Both; extraction is first-class.** Two of the six skills bracket it: `research-manager` **authors**
(capture during work) and `compiler` **extracts** (`/compiler <path>` — "convert an existing paper, repo,
or notes into a structured ARA"). The `resnet-ara-example/` is a real legacy PDF (ResNet 2015) compiled
into ARA — proof of a PDF→ARA path. Extraction is **agent-driven + human-review-disciplined** (Rule 16:
on repo-vs-paper conflict, "do NOT pick one silently — surface the conflict to the user"), not a packaged
deterministic parser (`resnet-walkthrough.md`: "not a standalone binary… a skill specification for an
agent").

---

## Q4 — What the Ara Compiler actually does

**A multi-stage LLM agent skill — not a simple extractor.** `skills/compiler/SKILL.md` frontmatter:
`allowed-tools: Read, Write, Edit, Bash(python *|git clone *|…), Glob, Grep, Task`; body: "You are the ARA
Universal Compiler… operate as a first-class Claude Code agent." Workflow:

> READ inputs → 4-stage epistemic protocol → GENERATE files → COVERAGE CHECK loop (max 3) → VALIDATE (Seal
> Level 1) → FIX/re-validate → REPORT.

4 stages: **(1) Semantic Deconstruction** (extract atoms + an *evidence ledger* over every numbered
table/figure + a *visual pass* that **renders PDF regions to PNG via PyMuPDF/`fitz`/`pdf2image` and reads
the figures as images**); **(2) Cognitive Mapping** → `/logic`; **(3) Artifact Layer** → `/src` (grounded/
transcribed code only, never fabricated); **(4) Exploration Graph Extraction** → `/trace` DAG.

It is governed by **16 Critical Rules** — exact numbers (never round), no hallucination, `Proof`→E-IDs,
cross-layer bindings must resolve, dead-ends mandatory, "Not specified in paper" over guessing,
source-bounded (never invent nodes to hit a count), the **name-deletion test** (a claim Statement that only
names your components is attribution, not knowledge), and **grounding-by-verbatim-quote** for every
load-bearing number. It **requires an LLM** and is **explicitly human-review-gated**. (`pdf_extract.py`
exists as a deterministic text/render helper the agent *uses* — it is not itself the compiler.)

---

## Notable ground-truth observations (for Phase Q)

1. **ARA's provenance/trust layer is rich** and maps to our vault's need to separate human-confirmed from
   AI-inferred: entry tags `user | ai-suggested | ai-executed | user-revised`; trace `support_level:
   explicit|inferred`; code `# Grounding: transcribed|reconstructed`; numbers grounded by verbatim «quote».
2. **ARA's *own* "make capture automatic" is the pattern that failed us.** The README tells you to append to
   `CLAUDE.md`: *"At the END of every coding session, invoke the `/research-manager` skill…"* — i.e. hope the
   agent remembers to fire a skill. That is exactly `friction-260709`'s probabilistic-activation failure.
   Only the **explicit `/compiler <path>`** invocation is deterministic — which is precisely what
   `ingest_paper(mode='ara')` emulates. Independent validation of Decision 1.
3. **The claim-as-mechanism discipline == our lens taste.** ARA's "Statement is a takeaway, not a record" +
   name-deletion test is the same standard as our lenses' "mechanism + evidence + falsifiability." We can
   lift it wholesale for K/I node quality.

---

## Verdict — Is ARA usable as a single-paper extraction method for our vault?

**YES — adopt the *ontology + agent-extraction protocol*, re-expressed as our own (more strictly enforced)
Pydantic `response_model`; extract a deliberate SUBSET; route to staging.** Unchanged from v1, now
evidence-hardened.

- **What we extract → K/T/I/D:** claims (as *mechanism* Statements + Conditions + Falsification) → **K**;
  heuristics (`H##`: trick/sensitivity/bounds) → **I**; trace `dead_end`/`decision`/`pivot` (with
  `lesson`/`why_failed`/`rationale`) → **T/D** (the failure & judgment knowledge keyword search can't reach);
  `related_work` (`imports/extends/refutes`) → the **seed** for a `derives_from`/`contradicts` edge minted by
  the **Grounding** step against a prior vault node (not by extraction).
- **What we skip (80/20, per VISION):** the reproduction cathedral — `evidence/tables|figures` PNG sweep,
  `src/execution/*` code + `artifacts.md`, the full 8-14-node DAG, Seal L1. Those serve agent *reproduction*;
  we are a reader/triager.
- **Borrow for free:** the provenance tags (explicit/inferred, user/ai) and the claim-as-mechanism discipline.
- **Honest expectation:** it is an **LLM judgment call requiring review** (ARA says so; its own example is
  hand-curated *and* off-spec) — so size `mode='ara'` to a curated subset → **staging**, exactly where
  Decision 1 + the two-write-paths cross-finding already point.

---

*Research task — no code written. Read from the local clone `D:\MAS\Agent-Native-Research-Artifact`.*
