# Phase Q — Deterministic ARA Workflow & Subagent Orchestration

**Status:** Active (Follows Phase N truncation)
**Sealed predecessor:** Phase N (Truncated)
**Driving frictions:**
- Probabilistic skill activation fails under long-context load (DeepSeek/Claude forgets to check Vault).
- Vault graph lacks depth (N.B.0 audit: no K->K edges, no deep T nodes).
- Need a rigid, deterministic pipeline to enforce ARA (Agentic Reproducibility Assessment) structure on ingested papers.

## Mission

Replace the probabilistic "read and maybe use a lens" approach with a deterministic, multi-subagent pipeline. Every paper reading MUST extract a structured ARA graph (Sources → Methods → Experiments → Outputs). The main agent's role shifts from doing the reading to orchestrating subagents and presenting the final distilled knowledge.

## Design Decisions (Architect Authorized)

1. **Custom CLI Command over Hooks**: We will NOT use Claude Code background hooks (`PreToolUse` etc.) because they obscure the control flow. We will create a discrete MCP tool or a specific CLI entry point (e.g., `run_ara_pipeline(paper_id)`) that the user explicitly invokes.
2. **Subagent Isolation (The Execution Tree)**:
   - **Grounding Subagent**: Queries Vault for context. Fast, cheap model.
   - **Extraction Subagent**: Reads the heavy PDF markdown + Grounding summary. Produces rigid JSON/XML ARA structure. Expensive model.
   - **Main Agent**: Receives structured output, never sees the full paper text.
3. **Lens Demotion**: Lenses (Forensic, Math, etc. from Phase N.A) are no longer proactive skills. They are applied *reactively* by the Main Agent only if the ARA Extraction flags a specific section (e.g., "Math section is highly dense" -> apply Math Lens).
4. **Graph Edges via ARA**: The ARA extraction output maps directly to `create_staging_node` calls with predefined `derives_from` and `contradicts` edges, solving the empty-graph problem.

## Sprint Sequence

| Sprint | One-line goal |
|---|---|
| Q.0 | Audit: Current subagent capabilities (from Phase III.E) and how to pass complex JSON payloads between them. |
| Q.1 | Subagent 1 (Grounding): Build the lightweight Vault-querying sub-routine. |
| Q.2 | Subagent 2 (Extraction): Build the ARA structural extraction prompt and force rigid schema output. |
| Q.3 | Pipeline Orchestrator: Wire Subagent 1 -> Subagent 2 -> Main Agent summary. |
| Q.4 | Staging Integration: Convert ARA output into `create_staging_node` calls for the Vault. |

## Cross-Sprint Red Lines
- ❌ Do NOT rely on the Main Agent to "read" the paper text. Full text stays in Subagent 2.
- ❌ Do NOT use probabilistic prompts ("Please try to check the vault"). Use hard code execution.
- ❌ Do NOT overwrite existing K/T/I/D node schemas; map ARA outputs to the existing ontology.

## Hard Sealing Conditions
1. Invoking the ARA pipeline on a new paper produces a staged Knowledge/Thought node with at least one `derives_from` edge pointing to a prior Vault node.
2. The Main Agent context window does NOT contain the full paper markdown during the final summary phase.
