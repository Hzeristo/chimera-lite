# Sprint L.3 — W2: Breadth Mapping

**Phase:** L (Locus) · **Risk:** 🔴 HIGH (new write-mode over irreplaceable human curation) · **Date:** 2026-07-18
**Plan:** `docs/plans/Phase-L-batch.md` · **Spec:** `docs/phases/phase-L.md` (W2, HSC #4)
**Approach:** TDD — the deterministic invariants were written red first (the merge-not-clobber test
failed against the supersede-only `write_result`), then the code was built to green them.

## What was built

**Deterministic core (code + tests):**
- `mcp-servers/chimera-papers/w2_breadth.py` — `plan_expansion(seeds, get_refs, bounds)`: a pure,
  bounded reference BFS. HARD `max_depth` + `max_papers` caps enforced in code (the phase-L "bounded
  BFS, no unbounded crawl" red line becomes an assertable invariant); cycles/diamonds visit once. Pure
  over an injected `get_refs` so it is testable without the (deferred) reference parser.
- `mcp-servers/chimera-papers/result_service.py` — extended with a `mode` param:
  - `supersede` (default, **W1** — unchanged): re-run REPLACES.
  - `merge` (**W2** breadth map): re-run UNIONS the body by paper key — ADDS new papers, PRESERVES the
    Architect's in-Obsidian annotations verbatim (existing blocks win), status → `MERGED`. Pure helpers
    `_parse_blocks` / `_merge_bodies` do the key-union.
  - `reject` / `mark_stale`: status transitions on an existing artifact (body untouched).
- `mcp-servers/chimera-vault/server.py` — the `write_result` MCP tool wrapper gains `mode` (threaded to
  the service) + docstring for the W2 merge / keyed-block contract.

**Orchestration (Claude Code, not MCP — the judgment layer):**
- `.claude/agents/chimera-breadth-reducer.md` — the per-paper recon worker: paper + {type, field} +
  criteria → ONE keyed block (gap sentence + performance number + verbatim anchor + promote-candidate).
  **RECON ONLY** — records the number, never frames it (Phase K Gate 2 does that; the forward-compat
  constraint K.0 checks).
- `.claude/skills/chimera-w2-map/SKILL.md` — the W2 orchestration: seeds → bounded expansion → per-paper
  classify + load-criteria + reduce → subfield-grouped map → `write_result(mode="merge")`. Reuses W1's
  classify → load-criteria subroutine; nominates promote-candidates, the Architect promotes.

## Verification

- `pytest tests/test_w2_bfs.py tests/test_w2_result.py tests/test_write_result.py`: **19 passed**, 0.17s.
  - BFS: paper-cap, depth-cap, cycle-termination, diamond-dedup, multi-seed, seeds-beyond-cap.
  - W2 lifecycle: first-write pending, **merge preserves annotations + adds papers + dedups**, status→MERGED,
    preamble preserved, reject/mark_stale transitions, missing-artifact raises, unknown-mode raises.
  - Regression: W1 supersede still overwrites (not merged).
- `uvx ruff check` on the four new/edited Python files: **All checks passed.**

## Red-line check

- ✅ **Bounded BFS** — hard caps enforced in `plan_expansion` (tested), no open-web crawl.
- ✅ **MERGE, never clobber** — the landmine (supersede-only `write_result`) is closed; annotations survive a re-run (the load-bearing test).
- ✅ **RECON, not interpretation** — the reducer records number+verbatim+gap, no single-framing conclusion (Phase K forward-compat).
- ✅ **Judgment in Claude subagents, never deepseek** — classify + reduce are forked Task subagents; paper text stays in the worker.
- ✅ **W2 nominates, Architect promotes** — no auto-ingest, no auto-K-node.
- ✅ No new MCP server; `.mcp.json` unchanged. No new dependency.

## Notes / deviations

- **Reference parser deferred (D5 cheap-first).** L.3's expansion runs over the seeds + cheaply-available
  references (bare arXiv ids in the vault or supplied); the parser is a later increment. `plan_expansion`
  is the tested engine ready for it — until then the skill applies the caps in orchestration to the
  shallow frontier. If coverage proves insufficient, record a friction (the L.0 D3 risk).
- **BFS bounds are code-spec'd, orchestration-enforced.** `plan_expansion` fixes the cap semantics
  (tested); the W2 skill mirrors them. Wiring it as an MCP primitive the skill calls directly is a clean
  future increment (would make the runtime bound-enforcement code, not prose).
- **Merge is conservative (existing-wins).** A re-run does not refresh an existing paper's machine data —
  it only adds new papers and preserves annotations. Refresh-preserving-annotations is a later option.

**Delivers:** HSC #4 (breadth map with gaps + numbers across ≥3 subfields) — structurally; the ≥20-paper /
real-seed acceptance run is the seal-time check. **Next:** L.4 (optional HTML panel) or the Phase-L seal
(vision gate — real survey material). W1 (L.2) + W2 (L.3) both built; the harness is complete.
