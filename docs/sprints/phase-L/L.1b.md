# Sprint L.1b — Dual-classification subagent

**Phase:** L (Locus) · **Risk:** 🟡 MED · **Date:** 2026-07-16
**Plan:** `docs/plans/Phase-L-batch.md` · **Audit:** `docs/audits/L.0.md` (C1, A1/A3)
**Executed by:** Opus main session (prompt authoring — reasoning-shaped, not delegated) + a Sonnet smoke test.

## What was built
- `.claude/agents/chimera-paper-classifier.md` — a Claude Code subagent definition. Given a paper,
  it returns TWO labels: a closed-4-class `type` (benchmark/method/theory/survey) and a KG-anchored
  `field` slug — the pair that selects `criteria/` files for `load_criteria` (L.1a).
- Field-anchoring convention (in the body): `ToolSearch`-load the deferred `mcp__chimera-vault__*`
  tools → extract salient terms → probe the vault (`vault_query` / `obsidian_graph_query`) → choose a
  slug matching an existing vault neighborhood, else mint + flag `field-unanchored: true`.
- Isolation: returns only `{type, field}`; the paper text stays in the subagent.

## Verification (smoke test — 1 paper)
- Spawned the classifier on **LongMemEval** (a real benchmark, already in the vault).
- Result: `{type: benchmark, field: agentic-memory}` — correct type; field anchored to the vault's
  real agent-memory cluster (it read the vault's `AgentMemSurvey` ontology note to anchor it).
- Tools called: `ToolSearch` → `vault_query`, `obsidian_graph_query`, `read_vault_file`. No deepseek.
- **Decision: PASS** (correct classification + genuine KG-anchoring + Claude-not-deepseek + isolation).

## Red-line check
- ✅ Classification is Claude-in-subagent — no `generate_structured_data`.
- ✅ `type` stays the closed 4-class.
- ✅ `field` anchored to a real KG neighborhood (observed, not invented).
- ✅ No new dependency; no MCP server change.

## Notes
- Full acceptance (≥3 papers across ≥2 types) is a seal-time / L.2c-integration check; the 1-paper
  smoke test confirms the procedure works end-to-end.
- The agent may need a session reload for `subagent_type="chimera-paper-classifier"` to be spawnable;
  the body doubles as a copy-usable spawn prompt (as the smoke test used it), so W1/W2 (L.2c/L.3b)
  can use it either way.

**Delivers:** the classify step feeding `load_criteria`. **Next:** L.2a (`fetch_paper` + `convert_pdf_to_md`).
