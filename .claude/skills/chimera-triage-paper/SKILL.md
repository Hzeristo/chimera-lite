---
name: chimera-triage-paper
description: Screen ONE already-converted paper into a scout-tier Knowledge card (Phase L.B externalized triage). Activate when the Architect wants a fast verdict on a specific paper — "triage <paper>", "screen <arxiv id>", "is this paper worth reading", or after a `daily_paper_pipeline` / `ingest_paper` run has converted papers awaiting triage. Orchestrates markdown+metadata resolution → classify → load criteria → an isolated Haiku triage subagent → the deterministic scout-card write, producing an inbox-only scout node the operator reviews before promoting to a deep read. Judgment is Claude-in-subagent, never deepseek, never an Anthropic client inside the MCP server. Explicitly invoked (not ambient).
---

# Triage Paper — Externalized Scout-Tier Screening

<expected_model>
**Run this orchestration loop at Sonnet.** The loop is glue — resolve the paper, sequence the MCP
primitives (`analyze_paper_data` / `load_criteria` / `write_scout_card`), assemble the report.
Every unit of *judgment* is delegated to **pinned workers** (`chimera-paper-classifier` at
sonnet, `chimera-paper-triager` at haiku — deliberately CHEAP, this is bulk screening, not deep
extraction), so the loop itself carries no reasoning that needs Opus
(`docs/audits/model-routing-gaps.md`).

If the session model is Opus, follow the recommendation procedure (detect → inform → wait, never
auto-switch): see `../_shared/expected_model.md`. Do NOT upgrade `chimera-paper-triager` past
haiku — triage is deliberately cheap bulk judgment; if a paper's verdict is ambiguous, that is a
signal for the Architect to run `chimera-deep-extract` on it, not a reason to spend a bigger
model on the screen.
</expected_model>

You (the main agent) **orchestrate**; the triage judgment happens in an **isolated subagent**.
Never synthesize the paper yourself in the main context — the paper's full text must stay in the
worker (isolation by construction). The MCP server (`chimera-papers`) makes NO LLM call anywhere
in this path (L.B.2) — `analyze_paper_data` is a bare read primitive and `write_scout_card` is a
deterministic validate + render + write primitive; the server is never the judge.

## The loop

1. **Resolve the paper's data.** Normalize `paper_id` (an arXiv id, e.g. "2604.14004"). Call
   `analyze_paper_data(paper_id)` → `{markdown_path, metadata}`. A `[Extract Error]` /
   `FileNotFoundError` (not yet converted) means the paper needs `fetch_paper` +
   `convert_pdf_to_md` (or `ingest_paper`) FIRST — report that back rather than guessing at
   content.

2. **Classify.** Spawn the `chimera-paper-classifier` subagent on `markdown_path` → `{type,
   field}` (isolation: it reads the paper itself, returns only the two labels).

3. **Load criteria.**
   - `load_criteria(type, role="paper-critic", field=field)` → the composed criteria block
     (capability: `type` + `field`, THEN disposition: `paper-critic` + `_general`). Do NOT
     reorder it.

4. **Triage (in a subagent).** Spawn the `chimera-paper-triager` subagent with: the paper's
   markdown **path** (it reads the paper itself — isolation), the `metadata` dict, and the
   composed criteria block. It returns ONE JSON object matching `PaperAnalysisResult` — verdict +
   score + mechanism summary + critical flaws. This is a fast SCREEN (haiku-cheap), not a deep
   extraction — no lens critique, no attack vectors, no ARA-disciplined claims.

5. **Write the scout card.** Call `write_scout_card(paper_id, analysis=<the subagent's JSON as a
   dict>)`. This is the deterministic back-half: validates the payload against
   `PaperAnalysisResult`, resolves the paper via `PaperLoader`, and writes it to
   `<inbox>/<verdict>/` at `chimera_tier="scout"` (never `Harness/`). Returns the written path.

6. **Report** to the Architect: the written path, the verdict + score, and a one-line pointer —
   `Must Read` verdicts are a candidate for `chimera-deep-extract`; `Reject`/`Skim` verdicts stay
   scout-tier until the Architect decides otherwise. The node is inbox-only; nothing here writes
   to the live vault or promotes automatically.

## Red lines

- ❌ The triage judgment happens in the `chimera-paper-triager` subagent — NEVER in the main
  context (isolation), and NEVER via deepseek or an Anthropic client inside the MCP server
  (`chimera-papers/server.py` makes NO LLM call, period).
- ❌ The scout card always lands under `inbox/<verdict>/`, at `chimera_tier="scout"` — NEVER
  `Harness/`, and NEVER auto-promoted to `Knowledge/`. Promotion is a separate, later Architect
  decision.
- ❌ Criteria are loaded via `load_criteria` (vault-dynamic), disposition after capability — never
  inline criteria in this skill or the subagent prompt.
- ❌ `chimera-paper-triager` stays pinned `haiku` — never upgraded for a "hard" paper; a
  genuinely hard verdict is a signal to escalate to `chimera-deep-extract`, not to spend a bigger
  model on the screen itself.
- ❌ No lens critique, attack vectors, or ARA-disciplined mechanism claims here — that is
  `chimera-deep-extract`'s job on promotion, never this skill's.
