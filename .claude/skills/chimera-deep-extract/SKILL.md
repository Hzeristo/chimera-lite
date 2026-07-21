---
name: chimera-deep-extract
description: Distill ONE already-ingested paper into a staged deep_read Knowledge node (Phase L.B disciplined extraction). Activate when the Architect wants a fresh deep-read of a specific paper already in the vault — "deep-read <paper>", "extract <arxiv id> into a Knowledge node", "distill this paper's mechanism claims", or when backfilling the graph with citation-grounded edges. Orchestrates markdown resolution → classify → load criteria + the applicable lens(es) → an isolated Sonnet extraction subagent → the deterministic grounding/render/stage back-half, producing a staging-only deep_read node the operator reviews before promotion (via ascend_node). Judgment is Claude-in-subagent, never deepseek, never an Anthropic client inside the MCP server. Explicitly invoked (not ambient).
---

# Deep Extract — Disciplined Single-Paper Extraction

<expected_model>
**Run this orchestration loop at Sonnet.** The loop is glue — resolve the paper, sequence the MCP
primitives (`get_paper_markdown` / `load_criteria` / `stage_deep_read_node`), concatenate the lens
catalog, assemble the report. Every unit of *judgment* is delegated to **pinned-Sonnet** workers
(`chimera-paper-classifier`, `chimera-deep-extractor`), so the loop itself carries no reasoning
that needs Opus (`docs/audits/model-routing-gaps.md`).

If the session model is Opus, follow the recommendation procedure (detect → inform → wait, never
auto-switch): see `../_shared/expected_model.md`. The pinned workers stay Sonnet regardless of the
session model — do NOT downgrade `chimera-deep-extractor`; it is the fidelity-critical judgment,
so if anything spend UP there, never down.
</expected_model>

You (the main agent) **orchestrate**; the extraction judgment happens in an **isolated subagent**.
Never synthesize the paper yourself in the main context — the paper's full text must stay in the
worker (isolation by construction). The MCP server (`chimera-papers`) makes NO LLM call anywhere
in this path (L.B.2) — `get_paper_markdown` is a bare read primitive and `stage_deep_read_node` is
a deterministic grounding + render + write primitive; the server is never the judge.

## The loop

1. **Resolve the paper.** Normalize `paper_id` (an arXiv id, e.g. "2305.16291"). Call
   `get_paper_markdown(paper_id)` → the paper's already-converted markdown path. A `[Extract
   Error]` (not yet converted) means the paper needs `fetch_paper` + `convert_pdf_to_md` (or
   `ingest_paper`) FIRST — report that back rather than guessing at content.

2. **Classify.** Spawn the `chimera-paper-classifier` subagent on the markdown path → `{type,
   field}` (isolation: it reads the paper itself, returns only the two labels).

3. **Load criteria + the lens catalog.**
   - `load_criteria(type, field, role="paper-critic")` → the composed criteria block (capability:
     `type` + `field`, THEN disposition: `paper-critic` + `_general`). Do NOT reorder it.
   - Read the canonical lens catalog yourself (`Glob`/`Read` over `prompts/lenses/*.md`,
     concatenated) — this is a deterministic file read in the main session, not a judgment call;
     the SAME files back the interactive `chimera-lens-*` skills, so there is no second copy to
     drift.

4. **Extract (in a subagent).** Spawn the `chimera-deep-extractor` subagent with: the paper's
   markdown **path** (it reads the paper itself — isolation), the lens catalog text, and the
   composed criteria block. It returns ONE JSON object matching `KNodeExtraction` — synthesis + 1-2
   lenses + attack + 1-5 ARA-disciplined mechanism claims. It proposes NO edges (grounding mints
   those next, deterministically) and writes NO Insight/Thought/Decision content.

5. **Stage the node.** Call `stage_deep_read_node(paper_id, extraction=<the subagent's JSON as a
   dict>)`. This is the deterministic back-half: grounds the paper's own citations into
   `derives_from` edges (or `no_prior_match`, edgeless — never fabricated), detects a superseded
   prior node (`supersedes`), renders the reader's markdown body, and writes it to
   `docs/staging/` at `chimera_tier="deep_read"`. Returns the staging path.

6. **Report** to the Architect: the staging path, the applied lens(es), the grounding outcome
   (`citation_resolved` / `no_prior_match`), and any supersede detected. The node is
   staging-only — the Architect reviews and promotes via `ascend_node` (Phase L.B.3); this skill
   never auto-promotes.

## Red lines

- ❌ The extraction judgment happens in the `chimera-deep-extractor` subagent — NEVER in the main
  context (isolation), and NEVER via deepseek or an Anthropic client inside the MCP server
  (`chimera-papers/server.py` makes NO LLM call, period).
- ❌ The staged node is `chimera_tier="deep_read"` and staging-only — never auto-promoted. Promotion
  into `Knowledge/` is the Architect's call, via `ascend_node` (Phase L.B.3), never this skill.
- ❌ Criteria are loaded via `load_criteria` (vault-dynamic), disposition after capability — never
  inline criteria in this skill or the subagent prompt.
- ❌ Edges are minted ONLY by `stage_deep_read_node`'s deterministic citation-resolution — the
  `chimera-deep-extractor` subagent proposes none; never accept an `edges` field from it.
- ❌ No `w1_offer` step here — surfacing a W1 candidate-claim hint on completion is Phase L.B.4,
  explicitly out of scope for this skill.
