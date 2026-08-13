# Phase Q — Quiddity: Disciplined Knowledge Extraction

> ✅ **REOPENED 2026-07-10 (`friction-260710-02`) → REBUILT 2026-07-10.** The output shape has been rebuilt
> per the Architect's authored target (an ideal reader's K node) and the approved **A-refined** lens
> architecture. `extract_paper` now stages a human-readable node — **Synthesis** (BB's analysis + mechanism
> walkthrough + algorithm steps) +
> **Lens Critique** (1-2 function-selected lenses — a second only on independent hybrid detection) +
> **Attack Vectors** (offensive read) + **Mechanism Claims** (ARA-disciplined — the epistemic FLOOR, not the
> whole output) — with `[My Critique]` human-fill review hooks and the citation-grounded edges kept. ARA's
> claim-as-mechanism discipline is applied as a **prose QUALITY BAR**, never as the output shape. Lens
> methodology is single-sourced in `prompts/lenses/*.md` (read by both this server's extraction and the
> interactive `chimera-lens-*` skills; `friction-260710-03`). The prior functional seal
> (`docs/sprints/phase-Q/phase-review.md`) remains **superseded**; the rebuild record is
> `docs/sprints/phase-Q/Q.R-rebuild.md`. **Pending re-seal:** a live re-extraction reviewed by the operator.

**Status:** REBUILT 2026-07-10 (`friction-260710-02`) — output shape rebuilt (synthesis + lens + attack + claims); pending live re-extraction + re-seal
**Sealed predecessor:** Phase N (Truncated)
**Driving frictions:**
- Probabilistic skill activation fails under long-context load (DeepSeek/Claude forgets to check Vault).
- Vault graph lacks depth (N.B.0 audit: no K->K edges, no deep T nodes).
- Need disciplined extraction that enforces ARA's *epistemic discipline* (claim-as-mechanism, falsification, grounding-by-quote), NOT ARA's file-system format, on ingested papers (ARA = Agent-Native Research Artifact, arXiv 2604.24658).

## VISION — Why We Build This

> **This section governs how every decision below is evaluated — not the reverse.**

The ultimate goal is **NOT** to build the most technically elegant system. The ultimate goal is to
build a system that **YOU** (the Architect, a working PhD researcher) actually **WANT TO USE** for daily
research.

Technical metrics are means, not ends:
- "HSC ≥ 20" is a proxy for "the graph has real value to traverse"
- "ARA discipline" is a proxy for "the vault captures real knowledge"
- "A deterministic pipeline" is a proxy for "I can trust it to work"

If the system is technically perfect but you don't reach for it when you sit down to read papers — **it
has failed.**

This means:
- If a simpler tool gets 80% of the value with 20% of the complexity, **choose simplicity** (user
  adoption > architectural purity).
- If a feature requires you to remember too many commands or rituals, **cut it** (the friction of the
  tool > the friction of not using it).
- If something works in demo but fails in your actual research flow, **it fails** (test against real
  use, not synthetic scenarios).

The system earns its place in your daily work only if it makes research **faster, deeper, or more
connected** — not if it makes you a better systems builder.

**Success metric: you open this tool without being reminded to.**

## Mission

Extract structured knowledge from an existing paper into a vault K node the
Architect actually wants to read — a human-readable SYNTHESIS + CRITIQUE. ARA's
epistemic discipline is a QUALITY BAR on the prose, NOT the output shape.

The key distinction (from ARA repo analysis):
  - ARA's FORMAT (4 layers, /trace DAG, exploration_tree.yaml) is for WRITING
    artifacts — you cannot extract a git log from someone else's paper. Wrong.
  - ARA's DISCIPLINE (claim-as-mechanism, name-deletion, falsification,
    grounding-by-verbatim-quote, provenance) is EXCELLENT — applied as the
    quality bar on the synthesis prose and made explicit in the claims section.

The extraction payload — a K node with FOUR reader-facing sections:
  1. Synthesis — the reader's FULL arc: motivation (the gap, grounded) →
     contribution + insight in BB's analytical voice → mechanism walkthrough →
     algorithm steps → results (headline outcomes + key numbers, grounded — the
     home for the numbers the claims strip). Connects to existing vault concepts;
     carries a `[My Critique]` hook the Architect fills at review. (`friction-260713-01`)
  2. Lens Critique — 1-2 lenses selected by paper FUNCTION (not content type):
     the single best-matching lens by default; a SECOND only when another lens's
     trigger independently scores high (a genuine hybrid — e.g. a benchmark ABOUT
     a mechanism warrants both benchmark-integrity and mechanism-depth lenses).
     Trigger + findings + verdict per lens. Canonical lens definition per lens in
     prompts/lenses/*.md, read by BOTH server and skills (one source).
  3. Attack Vectors — the offensive read: how to beat this baseline / exploit the
     flaw. Actionable, adversarial. Carries its own `[My Critique]` hook.
  4. Mechanism Claims (ARA-disciplined) — the epistemic floor: 1-5 mechanism-level
     claims (statement / falsification / verbatim-grounded sources / status /
     tags / flags). A SECTION beneath the synthesis, NEVER the whole node.

Plus:
  - Typed edges: minted ONLY from Grounding (citation resolution), never from
    extraction. derives_from / contradicts. No match → grounded: no_prior_match,
    staged edgeless. Zero fabrication.
  - Provenance (ai-suggested) + `[My Critique]` hooks make the staging review
    literal; every node is staged, never auto-promoted.

What Phase Q does NOT extract:
  - No D nodes from papers (inference, not fact)
  - No T nodes from papers (T is your interpretation, you author it)
  - No I nodes from papers. An Insight is crystallized ONLY per explicit user
    call in chat (NEVER automatic generation), from a group of T nodes that were
    reproduced, verified in direct PI discussion, or affirmed in a seminar /
    conference (ICLR/NeurIPS) invited oral.
  - No ARA /trace DAG (you don't have the git log)
  - No /src code, /evidence PNGs, full artifact

## ARA Steal Table

| ARA artifact | Steal what | Into what |
|---|---|---|
| rigor-reviewer skill | 6-dimension epistemic review (Evidence-Relevance, Falsifiability, Scope-Calibration, Argument-Coherence, Exploration-Integrity, Methodological-Rigor) | Chimera lens skill upgrade (or new chimera-rigor-review skill) |
| compiler discipline | Claim-as-mechanism, name-deletion test, grounding-by-quote, 16 anti-hallucination rules | Phase Q extraction prompt content |
| Provenance tags (ai-suggested / user-confirmed / inferred) | Trust layer for AI-extracted fields | K node frontmatter |
| research-foresight | Honesty-envelope pattern (grounded_inference / speculative_leap / confidence / falsifiable) | N.B successor — vault Q&A with honesty bounds |

SKIP (already handled by existing tools):
  - ara-viewer (Obsidian renders vault graph)
  - ara-submit (no publishing; we have our own skill system)

## Design Decisions (Architect Authorized)

1. **Extend the existing ingest infrastructure — no new pipeline.** `extract_paper(paper_id)` reuses `ingest_paper`'s MinerU (PDF→markdown), the schema-constrained LLM path (`generate_structured_data`), in-process `StagingService`, and the poll model. The paper markdown never leaves the server, so the caller only ever sees the staged result. Zero new dependencies.
2. **In-server stages (a single MCP tool, all in-process).** (1) **Grounding** — query the vault for prior nodes related to the paper. (2) **Extraction** — one schema-constrained LLM call over the markdown → K claims + provenance tags. (3) **Staging** — write to `docs/staging/`. Context isolation is automatic: the tool returns only the staged summary, never the paper text.
3. **Lens Demotion (function-triggered, not type-triggered)**: Lenses are NOT triggered by content TYPE (e.g., "this paper has math, use Math Lens"). They are triggered by content FUNCTION (e.g., "extraction flagged this section as EVIDENCE for a claim without ablation → Forensic Leakage"). The extraction schema must include a flag vocabulary: `[suspicious_dependency, no_ablation, math_decoration, method_orphaned, result_ungrounded, ...]` that maps to lens triggers. This changes N.A lens skills' activation model (auto-select-by-type → reactive-on-flag) — document this as touching N.A deliverables.
4. **Edges are INTER-node, minted by Grounding — never reconstructed from the paper.** The vault's typed edges (`derives_from` / `contradicts`) describe how THIS paper relates to OTHER vault nodes; they are minted by the **Grounding** step matching a prior vault node, NOT reconstructed from the paper's internal structure. Extraction produces the K node's content; Grounding produces its edges.

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| Q.1 | Define K Claim Pydantic model (mechanism-distilled claims, provenance tags, no numbers); verify it captures the discipline from ARA compiler |
| Q.2 | Implement extract_paper(paper_id) — ingest + grounding + disciplined extraction + staging |
| Q.3 | Test on 5 existing K nodes; verify claims are mechanism-level and edges come from grounding only (no I/T/D nodes produced) |
| Q.4 | Backfill 20 existing K nodes via extract_paper; verify ≥1 grounded edge or explicit no_prior_match |
| Q.R | **Rebuild (`friction-260710-02`):** output shape → reader's K node = Synthesis + Lens Critique + Attack Vectors + Mechanism Claims (floor); function-selected lens from single-source `prompts/lenses/*.md` (A-refined); reader-facing renderer + `[My Critique]` hooks; edges kept. See `docs/sprints/phase-Q/Q.R-rebuild.md`. |

## Cross-Sprint Red Lines
- ❌ Do NOT let the paper's full markdown reach the calling agent's context — it stays inside the in-server extraction step; only the staged summary crosses back.
- ❌ Do NOT use probabilistic prompts ("Please try to check the vault") for CONTROL FLOW — the grounding → extraction → staging steps are hard-coded and always run. Schema-constrained LLM extraction is permitted and necessary; "disciplined" refers to the steps being forced and the output schema-bound, not to the extraction being non-LLM.
- ❌ Do NOT overwrite existing K/T/I/D node schemas; map extracted output onto the existing ontology.

## Hard Sealing Conditions

1. **Mechanism-level claims (HSC 1):** The Mechanism Claims section (the epistemic FLOOR beneath the synthesis, never the whole node) holds 1-5 claims that are mechanism-distilled ("why"), not recipe ("how") or numbers. Name-deletion test passes: if the claim still makes sense after deleting the paper's name, it is mechanism-level.

2. **Grounded edges only (HSC 2):** Every derives_from / contradicts edge is minted from a confirmed grounding match. Zero fabrication. Edgeless staging is valid (grounded: no_prior_match) for cold-start papers.

3. **Provenance on every field (HSC 3):** Every AI-extracted field (claim, edge) carries a provenance tag (ai-suggested / inferred). User review can confirm or reject each.

4. **Zero I/T/D from extraction (HSC 4):** extract_paper never writes a I, T or D node.

## Explicit Scope Cuts

- This phase does NOT address ambient-observe (`friction-260709`'s second face — the always-on observer during ordinary conversation). `extract_paper` is an explicit invocation; ambient activation is deferred.

## Cross-Findings

- **Two write paths (design reconciliation, not a blocker).** `ingest_paper` writes K nodes to `inbox/`
  (immediate, no review). `create_staging_node` writes to `docs/staging/` (review required). `extract_paper`
  writes to **staging** (Architect's judgment, review-gated). See `docs/audits/Q.0.md` cross-finding #4.
