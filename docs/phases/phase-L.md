# Phase L — Locus: The Research Harness

**Status:** Active
**Sealed predecessor:** Phase Q (ARA-Disciplined Knowledge Extraction)
**Superseded/absorbed:** Phase R (vault-aware reasoning) — R.5's intent (reasoning
  consults the vault) is delivered through L's subagent judgment path; R.1/R.2
  (`convert_pdf_to_md`, markdown cleaner) become L primitives; R.3 (triage criteria)
  is superseded by L's vault-criteria mechanism. Phase R is retired into Phase L.
**Deferred successor:** Phase S (ambient / hook / north star) — unchanged.

**Driving frictions:**
- **The manual harness is at capacity** (GPT diagnosis 2026-07-12). The Architect
  is hand-orchestrating cold-reviewer / warm-prover / verbatim-verifier / domain-verifier,
  synchronously, on biological bandwidth. The orchestrator is overloaded — "Claude
  hallucinates and I can't catch it, GPT converges early and I can't suppress it."
  Not a model failure; an orchestrator-saturation failure.
- **Cannot produce a semi-proposal.** The bottleneck is survey production, not reasoning.
  A conversation yields a direction-map; a semi-proposal needs survey + gap analysis +
  method commitment (30-60 papers, performance numbers, 7 subfields). The Architect
  has read 4 papers by hand; the gap is unbuilt survey, and no model writes scholar-state
  documents without survey support.
- **friction arc terminus** (lens-in-skill → prompt-in-code → prompt-in-repo → now):
  verdict criteria change daily during the doing-PhD → researching-PhD transition.
  Every prior exposure mechanism (skill body, `prompts/*.j2`, `prompts/*.md`) requires
  git-commit-level editing friction, which exceeds the frequency of criteria change.
- **friction-260709 fork-subagent appetite:** judgment belongs in isolated Claude
  workers with clean context, not in deepseek-in-MCP.

## VISION — Why This Is the Center

> **This section governs how every decision below is evaluated — not the reverse.**

The Architect has been running a harness by hand: GPT as cold reviewer, Claude as warm
prover, manual verbatim reading as verifier, domain expertise as final gate. Skill Loader,
Actor/Critic/Theorist, verifier gate, temperament routing — all executed manually these
past days.

Phase L does not build a NEW capability. It AUTOMATES the loop the Architect is already
running, because that loop has exceeded biological scheduling bandwidth. The Architect
moves from ORCHESTRATOR to VERIFIER.

Success metric: the Architect produces survey material they would actually feed into a
semi-proposal — without hand-scheduling every fetch, read, verdict, and merge. The harness
schedules; the Architect judges the output, not every step.

This is **Locus** because every prior phase was a part. Migration moved the body; Locus
builds the mind's loop. If the harness works, Chimera Lite stops being a filing system and
becomes a research organ.

### Two failure classes Locus counters — capability + disposition

Locus counters TWO classes of Claude failure. Grounding fixes one; it is not enough.

**CAPABILITY (grounding-precedes-role — already specified).** Claude lacks the domain map and
taste for a given field and reasons in a vacuum. The fix is to load that map from the knowledge
graph *before* the role is applied — the vault-criteria mechanism (L.1).

**DISPOSITION (new axis).** Claude's *behavioral* biases persist even with correct knowledge —
grounding a subagent does not remove them:
- **Over-denigrate** under "criticize a paper" — harsh on the absent object.
- **Over-defer** under "critique my proposal" — soft on the present interlocutor; over-protects
  the established cited paper.
- **Early-stop / premature convergence.**
- **Binary verdicts** instead of graded calibration.
- **Role-capture** — literal instruction-following collapses nuance.

**KEY GEOMETRY: over-denigrate and over-defer point in OPPOSITE directions.** Claude is harsh on
the absent, soft on the present. A single "be calibrated" cannot fix biases that point opposite
ways — disposition correction MUST be **direction-aware**: target = paper → counter denigration;
target = the user's proposal → counter deference.

## Mission

Automate the manual research harness into two workflows that spawn Claude subagents
for judgment, load paper-type-specific criteria dynamically from the vault, and
produce the survey material semi-proposals require.

- **W1 — Claim Verbatim Verification:** a claim → fetch its cited papers → classify
  paper type → load type-matched criteria from the vault → a Claude subagent performs
  a verbatim check → produce a [V]/[P]/[U] tag with grounding quotes. Automates the
  20-30-minute prefrontal loop the Architect has run N times by hand.
- **W2 — Breadth Mapping:** seed papers → parallel Claude subagents expand the
  reference network (bounded BFS) → each paper classified, criteria-loaded, reduced
  to one gap sentence + one performance number → merged into a classified map across
  subfields. The survey-production pipeline that semi-proposals lack.

Judgment moves from deepseek-in-MCP to Claude-in-subagent. Criteria move from
repo files to vault files. The Architect moves from orchestrator to verifier.

## Sprint Sequence

| Sprint | One-line goal | Status |
|---|---|---|
| L.0 | Audit: Claude Code subagent (Task) lifecycle + parallelism limits, vault criteria loading path, paper fetch/convert primitives, which current deepseek-judgment paths move to subagents | Pending |
| L.1 | Dynamic criteria infrastructure — `criteria/{type,field,disposition}/*.md` matrix loading + dual classification (subagent: type 4-class closed + field, KG-anchored) + `load_criteria(type, field, role)` MCP primitive | Pending |
| L.2 | **W1 — Claim Verbatim Verification** — claim → fetch → classify → load criteria → subagent verbatim check → [V]/[P]/[U] + grounding quotes (highest ROI, built FIRST) | Pending |
| L.3 | **W2 — Breadth Mapping** — seed papers → parallel subagent bounded-BFS → per-paper gap + performance number → merged classified map | Pending |
| L.4 | (Optional) HTML panel — render the breadth map to an HTML file openable in a browser (display layer only, NOT criteria) | Pending |
| seal | phase_review — verify HSCs, assess the vision gate (real survey material produced) | Pending |

**Dependencies:** L.0 precedes all. L.1 (criteria infra) precedes L.2 and L.3 —
both consume dynamic criteria. L.2 precedes L.3 — W1 is the ROI-first automation, and
W2's per-paper processing REUSES W1's classify → load-criteria → verify sub-routine.
L.4 is optional, after L.3. Do NOT build the whole harness at once; W1 must run and
prove value before W2 is built (GPT's directive, Architect-confirmed).

## Criteria Architecture (L.1)

`criteria/` is a matrix with three axes — two for capability, one for disposition:

- `criteria/type/{benchmark,method,theory,survey}.md` — verification shape (capability).
- `criteria/field/{N}.md` — domain taste (capability).
- `criteria/disposition/{role}.md` — anti-bias calibration (disposition). **[NEW]**
- `criteria/disposition/_general.md` — anti-early-stop, graded-confidence. **[NEW]**

**Subagent load sequence (mandatory, ordered):**
1. **Capability** — KG neighborhood + `type/{type}.md` + `field/{field}.md`.
2. **Disposition** — `disposition/{role}.md` + `disposition/_general.md`.
3. **Apply role.**
4. **High-stakes only** (e.g. proposal eval) — adversarial pair: an advocate subagent + a
   skeptic subagent → a reconcile subagent. This recreates the manual GPT-cold / Claude-warm
   disposition split *inside all-Claude subagents*. Disposition diversity, not capability
   diversity.

## Artifact Lifecycle (write_result)

`write_result` is not just a sink — it is a **lifecycle manager**. W1 and W2 artifacts have
different identities and different re-run semantics:

- **W1 verdict** (identity = `claim_hash` / `arxiv_id`): identity-based **SUPERSEDE** (reuse the
  Phase Q supersede path). A re-run replaces, never duplicates.
- **W2 breadth map** (identity = topic / seed-set): **MERGE, not supersede.** A re-run adds new
  papers and **preserves human annotations** (`[My Critique]`, manual verdicts). Merge-not-clobber
  is why the map can *live* rather than be regenerated from scratch.

**Lifecycle states:**

```
PENDING_REVIEW → PROMOTED | REJECTED
PROMOTED → SUPERSEDED (W1 re-run) | MERGED (W2 re-run) | STALE (source changed,
           reuse Phase Q detection) | edited-in-Obsidian
```

The `write_result` primitive supports: **write / supersede / merge (preserve annotations) /
reject / mark_stale**.

Artifacts live **in the vault**, so they have TWO curation paths: the harness (`write_result`)
AND Obsidian (manual edit / prune). Artifacts are **living KG tissue, not frozen output.**

## Cross-Sprint Red Lines

- ❌ **Judgment happens in Claude subagents, not deepseek.** W1/W2's verdicts (V/P/U,
  gap identification, type classification) are Claude reasoning inside forked Task
  subagents. No `generate_structured_data` deepseek call in the W1/W2 judgment path.
  (Phase Q's `extract_paper` deepseek path is NOT reopened — it is a separate sealed
  use case; migrating it is future work, not L scope.)
- ❌ **Criteria live in the vault, not the repo.** The `vault/criteria/` matrix
  (`type/`, `field/`, `disposition/` — see **Criteria Architecture**) is the single source.
  Editing any axis in Obsidian changes W1/W2 behavior on the next run with zero git commit.
  No criteria in repo prompts, no criteria in skill bodies, no criteria in code.
- ❌ **Disposition-correction precedes role, alongside grounding.** Every judgment subagent
  loads `disposition/{role}.md` before applying its role. A role without disposition correction
  reverts to Claude's default bias (over-denigrate / over-defer / early-stop). Same class as
  "role without grounding is vacuum reasoning" — this is "role without disposition is biased
  reasoning".
- ❌ **W1/W2 are Claude Code orchestration, not MCP tools.** MCP cannot spawn subagents
  (the Phase Q B1 constraint holds). W1/W2 are the main agent spawning Task subagents;
  MCP provides only PRIMITIVES (`fetch_paper`, `convert_pdf_to_md`, `read_vault_file`,
  `load_criteria(type, field, role)`, `write_result`). Judgment never lives in an MCP tool.
- ❌ **Verbatim grounding is mandatory (W1).** A [V]/[P]/[U] tag MUST cite a verbatim
  quote from the paper. "[pending] beats a guess; an unverified path is fabrication"
  (stolen from ARA compiler discipline). No tag without a quote.
- ❌ **Bounded BFS (W2).** Reference expansion has a hard depth cap and a hard paper
  cap (per L.3 design). No unbounded network crawl.
- ❌ **HTML panel is display-only.** L.4 visualizes W2 output; it never carries criteria
  or judgment. Criteria go via vault md (necessary); panel via html (optional).
- ❌ **No new dependency.** Reuse arxiv fetch, MinerU convert, StagingService, vault
  adapter. Claude Code Task is native. `.mcp.json` stays two servers.
- ❌ **No opportunistic refactoring.**

## Hard Sealing Conditions

1. **(L.1 — the friction-arc terminus) Criteria are vault-dynamic.** Editing
   `vault/criteria/benchmark.md` in Obsidian changes W1's verdict behavior on the next
   run, with zero git commit. Verified: add a criterion, re-run W1 on the same paper,
   observe a changed verdict. The criteria file is named by paper type; classification
   selects the file.

2. **(L.2 — W1) Verbatim-grounded verdicts.** Given a claim and its cited paper, W1
   produces a [V]/[P]/[U] tag, each backed by a verbatim quote with location, using the
   type-matched criteria. Verified on ≥3 claims spanning ≥2 paper types. A claim with no
   supporting quote receives [U] or [P], never a fabricated [V].

3. **(Architecture) Judgment is subagent-borne.** W1/W2 verdicts are produced by Claude
   Task subagents, not deepseek. Verified by inspecting the W1/W2 path: zero deepseek
   judgment calls; the paper text stays in the subagent's context (isolation by construction).

4. **(L.3 — W2) Breadth map with numbers.** Given ≥3 seed papers, W2 produces a classified
   map of ≥20 papers (bounded), each carrying a one-sentence gap identification and one
   performance number, distributed across ≥3 subfields. Verified on a real seed set from
   the Architect's domain.

5. **(The VISION gate — assessed by the Architect) Real survey material.** After running
   W1+W2 on a real research direction, the Architect confirms the output is material they
   would actually feed into a semi-proposal — not a direction-map, but survey + gaps +
   numbers. Assessed on real use, not a fixture. This is the seal gate, like Phase M's
   Test 2 and Phase Q's discipline check.

## Design Decisions

- **Locus retires Phase R (ST 2026-07-12).** Phase R's core (R.5, reasoning consults
  the vault) is delivered as byproduct: W1/W2 subagents consult the vault (criteria +
  prior nodes) as their normal operation. R.1/R.2 tooling (`convert_pdf_to_md`, markdown
  cleaner) become L primitives. R.3 (triage criteria) is superseded by the vault-criteria
  mechanism (L.1) — a strictly better realization of the same friction-260710-01 ask.
  Phase R is absorbed, not run separately.

- **W1 before W2, and don't build the whole harness at once (GPT + ST 2026-07-12).**
  W1 (verbatim verification) is the most painful manual loop — the Architect has run it
  N times at 20-30 min each. It is the highest-ROI automation and W2's per-paper subroutine.
  Prove W1 works before building W2's parallel orchestration. Start from the most painful
  manual link, not the grandest architecture.

- **Criteria in vault is the friction arc's terminus, not another compromise (ST 2026-07-12).**
  The arc: lens-in-skill → prompt-in-code → prompt-in-repo-md. Each prior fix left editing
  behind a git commit. The Architect's verdict criteria change daily; git-commit friction
  exceeds change frequency. The repo is code's home; the vault is the Architect's judgment
  home. Criteria live where they are edited — in Obsidian, zero git, instant effect.
  This is why chimera-lite does not "去死": vault-md criteria is exactly what it can do.

- **Subagent-primacy: deepseek dies as judge, MCP lives as primitive (ST 2026-07-12).**
  V/P/U tagging and gap identification are judgment — Claude > deepseek. Judgment moves to
  Task subagents. MCP demotes from "the layer that runs deepseek" to "the leaf tools a
  subagent calls" (fetch / read / convert / load-criteria / write). Context isolation (paper
  text stays in the subagent) is precisely what friction-260709's fork-subagent appetite
  wanted. Cost profile shifts (40-60 papers = batched-parallel Claude subagents, not one
  deepseek call) — covered by Claude Max, bounded by Task parallelism limits (audit in L.0).

- **The Architect becomes verifier, not orchestrator (ST 2026-07-12).**
  The manual harness put the Architect at the center of scheduling. Locus moves scheduling
  into the main Claude agent (spawns subagents, merges results). The Architect's role
  compresses to judging the harness's output — the verifier gate that biological bandwidth
  is actually good at, freed from the scheduling that saturated it.

- **HTML panel: input vs output, do not conflate (ST 2026-07-12).**
  Two mechanisms were named together but are orthogonal. vault-md criteria = INPUT (how
  judgment standards arrive) — the load-bearing death-order. HTML panel = OUTPUT (how the
  breadth map is viewed) — optional display. L.1 delivers the input mechanism; L.4 (optional)
  delivers the display. The panel never carries criteria.

- **Criteria is a [type × field] matrix, decomposed 4+N — not 4×N (locked ST 2026-07-16).**
  Compose `type/{type}.md` + `field/{field}.md` at runtime. `type` = verification shape
  (cross-field, 4-class closed); `field` = domain taste (field-specific, anchored to the KG
  topic structure, open set). The classifier does TWO classifications: type (4-class closed) +
  field (open, anchored to the KG neighborhood).

- **W1 claim input: all three sources supported (locked ST 2026-07-16).** conversation-claim /
  K-node / raw text. The conversation-claim is the first L.2 target — it is the core of the GPT
  diagnosis.

- **W2 artifact: recon + nomination — "option C" (locked ST 2026-07-16).** The survey map is
  light; high-relevance papers are marked promote-candidate; the Architect reviews and selects a
  few for full ingest. W2 nominates; the Architect promotes.

- **Citation input: cheap-first (locked ST 2026-07-16).** Bare arXiv id + already-in-vault; the
  reference parser is deferred to a later increment. Record as a friction if coverage proves
  insufficient (the L.0 audit's D3 risk).

## Out of Scope (→ Phase S / later)

- **Ambient activation** (research discussion without naming a specific paper/direction)
  — Phase S north star. Phase L is explicitly invoked (run W1 on this claim, W2 on this seed).
- **Hook-based deterministic injection** — Phase S, only if invocation friction proves it
  necessary.
- **Parallel vault + web with <30s interleaved synthesis** — the full north star, Phase S.
- **Migrating `extract_paper`'s deepseek judgment to subagents** — Phase Q is sealed; L
  establishes the subagent-judgment pattern but does not reopen Q. Future consideration.
- **Semantic vault search (embeddings)** — the F4 gap. W1/W2 use classification + typed-edge
  walk + keyword; embedding search remains deferred (the `semantic_vault_search` mock interface
  from the Phase R audit — DEBT-019 — can be introduced here as a stub if W1/W2 grounding needs
  it, but its implementation is Phase S).
- **Schema-A/B node migration (~379 nodes)** — still the separate later effort.

## Notes

- L.0 MUST verify Claude Code Task lifecycle empirically: max concurrent subagents,
  whether subagents can call MCP tools, how results return to the main agent, context
  isolation guarantees. The entire phase rests on Task doing what friction-260709 assumed.
  Do NOT assume from this spec — verify against the harness.
- L.0 MUST confirm the vault-criteria loading path: can an MCP primitive read
  `vault/criteria/{type}.md` at runtime, and can a subagent receive that content? This is
  the death-order's technical precondition.
- **L.3 — disposition cost.** High-stakes adversarial pairing (load-sequence STEP 4) is 3× the
  subagents. Scope it to proposal-evaluation and contested claims, NOT routine W1/W2 verification.
  Routine verification uses a single subagent + `disposition/{role}.md` (prompt-level correction);
  the adversarial pair is reserved for where over-defer is most dangerous — evaluating the
  Architect's own proposals.
