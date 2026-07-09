# Phase Q — Deterministic ARA Workflow & Subagent Orchestration

**Status:** Active (Follows Phase N truncation)
**Sealed predecessor:** Phase N (Truncated)
**Driving frictions:**
- Probabilistic skill activation fails under long-context load (DeepSeek/Claude forgets to check Vault).
- Vault graph lacks depth (N.B.0 audit: no K->K edges, no deep T nodes).
- Need a rigid, deterministic pipeline to enforce ARA (Agent-Native Research Artifact, arXiv 2604.24658) structure on ingested papers.

## VISION — Why We Build This

> **This section governs how every decision below is evaluated — not the reverse.**

The ultimate goal is **NOT** to build the most technically elegant system. The ultimate goal is to
build a system that **YOU** (the Architect, a working PhD researcher) actually **WANT TO USE** for daily
research.

Technical metrics are means, not ends:
- "HSC ≥ 20" is a proxy for "the graph has real value to traverse"
- "ARA structure" is a proxy for "the vault captures real knowledge"
- "Deterministic workflow" is a proxy for "I can trust it to work"

If the system is technically perfect but you don't reach for it when you sit down to read papers — **it
has failed.**

This means:
- If a simpler tool gets 80% of the value with 20% of the complexity, **choose simplicity** (user
  adoption > architectural purity).
- If a feature requires you to remember too many commands or rituals, **cut it** (the friction of the
  tool > the friction of not using it).
- If something works in demo but fails in your actual research flow, **it fails** (test against real
  use, not synthetic scenarios).

The system earns its place in your workflow only if it makes research **faster, deeper, or more
connected** — not if it makes you a better systems builder.

**Success metric: you open this tool without being reminded to.**

## Mission

Replace the probabilistic "read and maybe use a lens" approach with a deterministic, multi-subagent pipeline. Every paper reading MUST extract a structured **ARA artifact** — the four layers `/logic` (claims, heuristics, experiments), `/src`, `/trace` (exploration: decisions, dead_ends, pivots), and `/evidence` — per arXiv 2604.24658 (Agent-Native Research Artifact). This is NOT a linear `sources → methods → experiments → outputs` graph (that schema came from the mis-cited 2605.02651). The main agent's role shifts from doing the reading to orchestrating subagents and presenting the final distilled knowledge.

**Design goal (R1) — zero new dependencies.** ARA extraction is an ADDITION to the existing `ingest_paper` pipeline, not a parallel construction. Reuse MinerU (PDF → markdown), the LLM client, vault tools, and `create_staging_node`.

**Scope note (M1).** ARA's reconstructability / reproducibility score is deliberately out of scope — a triage signal, not a vault-enrichment signal. It may be surfaced to the user but does not affect node creation.

## Design Decisions (Architect Authorized)

1. **Path B — Claude Code Workflow**: We will NOT use Claude Code background hooks (`PreToolUse` etc.) because they obscure the control flow. A `/read`-style command triggers the main agent to run a Workflow: `pipeline(Grounding → Extraction)`. The Grounding agent calls vault MCP tools. The Extraction agent returns schema-constrained JSON. Staging via `create_node`. This is the ONLY viable path — MCP tools cannot spawn Claude Code subagents (B1 audit).
2. **Subagent Isolation (The Execution Tree)**:
   - **Grounding Subagent**: Queries Vault for context. Fast, cheap model.
   - **Extraction Subagent**: Reads the heavy PDF markdown + Grounding summary. Produces rigid JSON/XML ARA structure. Expensive model.
   - **Main Agent**: Receives structured output, never sees the full paper text.
3. **Lens Demotion (function-triggered, not type-triggered)**: Lenses are NOT triggered by content TYPE (e.g., "this paper has math, use Math Lens"). They are triggered by content FUNCTION (e.g., "ARA extraction flagged this section as EVIDENCE for a claim without ablation → Forensic Leakage"). The ARA extraction schema must include a flag vocabulary: `[suspicious_dependency, no_ablation, math_decoration, method_orphaned, result_ungrounded, ...]` that maps to lens triggers. This changes N.A lens skills' activation model (auto-select-by-type → reactive-on-flag) — document this as touching N.A deliverables. (Function-based abstraction confirmed by the ARA audit Q4, §2.1/§2.2.)
4. **Graph Edges via ARA (the key unresolved design item)**: ARA's four-layer artifact (`/logic` `/src` `/trace` `/evidence`) is **INTRA-paper** structure (how THIS paper is assembled — the `claims → experiments → evidence` forensic bindings, the `/trace` DAG). Vault typed edges are **INTER-node** (how THIS paper relates to OTHER vault nodes). They are not the same graph.

   Primitive mapping (per `docs/audits/ara-2604.24658-structure.md` Q3): `/logic` claims + `/evidence` → **K**; `/logic` heuristics (trick / sensitivity / bounds) → **I**; `/trace` `decision` nodes → **D**; `/trace` `dead_end` / `pivot` / `question` + reader interpretation → **T**.

   A `derives_from` edge to a prior vault node comes from the **GROUNDING** step (which found the prior node) via ARA's `related_work.md` / imports — NOT from the intra-paper extraction step.

   This mapping (B2) is the single most important unresolved design item and MUST be specified before Q.1 begins.

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| Q.0 | Audit: Claude Code native Task/Workflow primitives (schema-constrained agent output, model/effort overrides, context isolation, `pipeline()` returning validated objects) + existing `ingest_paper` pipeline as the substrate to EXTEND, not replace. Phase III.E `fork_agent`/`fork_subagent` is RETIRED — do NOT audit it. |
| Q.1 | Subagent 1 (Grounding): Build the lightweight Vault-querying sub-routine. |
| Q.2 | Subagent 2 (Extraction): Build the ARA structural extraction prompt and force rigid schema output. |
| Q.3 | Pipeline Orchestrator: Wire Subagent 1 -> Subagent 2 -> Main Agent summary. |
| Q.4 | Staging Integration: Convert ARA output into `create_staging_node` calls for the Vault. |

## Cross-Sprint Red Lines
- ❌ Do NOT rely on the Main Agent to "read" the paper text. Full text stays in Subagent 2.
- ❌ Do NOT use probabilistic prompts ("Please try to check the vault") for CONTROL FLOW. Use hard-coded control flow for orchestration. Schema-constrained LLM extraction (Q.2) is permitted and necessary — "deterministic" refers to the workflow steps being forced, not to the extraction being non-LLM.
- ❌ Do NOT overwrite existing K/T/I/D node schemas; map ARA outputs to the existing ontology.

## Hard Sealing Conditions
1. Grounding attempt succeeds. The pipeline STAGES a node for every run. If a prior Vault node was found in grounding → the staged node has ≥1 `derives_from` edge. If no prior match found → the staged node carries an explicit `grounded: no_prior_match` field, no fabricated edges. Zero fabrication of K→K edges to hit a number. (First papers into an empty graph stage edgeless — that is valid, not a failure.)
2. Under Path B (Workflow fork), context isolation is guaranteed by construction — the fork keeps paper text out of the main context. Tool output stays in the subagent; only the schema-constrained JSON crosses the boundary. This is architecturally verified, not empirically measured.

## Explicit Scope Cuts

- This phase does NOT address ambient-observe (`friction-260709`'s second face — the always-on observer during ordinary conversation). `/read` is an explicit invocation; ambient activation is deferred.
