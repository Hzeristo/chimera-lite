# Q.R — Output-Shape Rebuild (`friction-260710-02`)

**Date:** 2026-07-10
**Type:** Reopen rebuild (supersedes the 2026-07-10 functional seal).
**Driver:** `friction-260710-02` — `extract_paper` had drifted to atomic-claim dumps, violating the
founding VISION (synthesis → lens → human-readable summary + critique). The staging gate caught it;
none promoted.
**Architect authorship:** the target output shape was authored by the Architect (an ideal reader's
K node) and the lens architecture decided as **A-refined** (single-source canonical lens files). Both
gates (Mission diff + N.A skill-thinning) were explicitly approved before code.

## What changed — the output shape, not the engine

The extraction **engine** (MinerU reuse, schema-constrained LLM call, in-process staging, poll model)
and the **citation-grounded edges** (`grounding.py`, D4) were correct and are untouched. Only the
**payload shape** was rebuilt: from `KClaimExtraction` (1-5 atomic claims = the whole node) to
`KNodeExtraction` = a reader's node with four sections, claims demoted to the epistemic floor.

### Files
- `core/schemas.py` — `KClaimExtraction` → **`KNodeExtraction`** (`title`, `synthesis`, `lens`,
  `attack`, `claims`). New models: `ClaimSource{quote,location}` (grounding-by-quote enforced
  structurally), `PaperSynthesis`, `LensFinding`, `LensCritique`, `AttackVectors`. `ExtractedClaim`
  gains `title` + `status_note`; `sources` → `list[ClaimSource]`. Extraction proposes **no** edges
  (D4 — grounding mints them), so `proposed_edges`/`provenance` dropped from the LLM payload.
- `prompts/lenses/*.md` — **6 new canonical lens files** (forensic-leakage, thermodynamic-decay,
  state-collision, agentic-illusion, math-decoration, ontological-map): function-based trigger +
  method + folded-in falsifiability discipline. **Single source of truth** (`friction-260710-03`).
- `prompts/chimera_sys/extract_node.j2` (new; replaces `extract_claims.j2`) — synthesis (BB voice) +
  select-ONE-lens-by-function (catalog injected) + attack + disciplined claims. `extract_task.j2`
  updated. `extract_claims.j2` deleted.
- `single_paper_extract.py` — `_extract_claims`→`_extract_node`, `_render_claims_body`→
  `_render_node_body` (4-section reader template + `[My Critique]` hooks), `_load_lens_catalog`
  reads `prompts/lenses/`. Node staged with `title=node.title` (readable H1/filename) +
  `metadata.arxiv_id` (identity preserved).
- `.claude/skills/chimera-lens-*/SKILL.md` ×6 — **thinned** (Phase N.A deliverables, edited with
  explicit sign-off): `description` frontmatter kept verbatim; body → one-line pointer to the
  canonical `prompts/lenses/<name>.md`. No method lost — relocated to one home.
- Tests — `test_kclaim_schema.py` → **`test_knode_schema.py`** (new structural contract);
  `test_extract_paper.py` rewritten to the new shape (asserts all four sections render, quote-grounded
  sources render as `"quote" ← location`, `[My Critique]` hook present, `arxiv_id` preserved).

## Verification
- `pytest -q` — **72 passed** (incl. `test_knode_schema` 12, `test_extract_paper` 9, `test_extract_schemas`
  grounding 4 unchanged).
- `ruff check` (via `uv run --with ruff`) — **All checks passed**.
- `grep` for `KClaimExtraction` / `_extract_claims` / `_render_claims_body` in `*.py` → **0**.
- Note: the ported `check_taste.ps1` is hardwired to the old `crucible_core/` path (absent here) and
  could not run; verification rests on pytest + ruff.

## Housekeeping
- The 8 atomic-dump staged nodes in `docs/staging/` (the rejected wrong-shape output) were **cleared**.

## Accepted partials / follow-ups
- **Live re-seal pending:** unit-tested with an injected stub LLM; a real end-to-end re-extraction
  (operator reviews an actual new-shape node) is the re-seal condition. MCP servers were disconnected
  this session, so the live smoke is deferred.
- **Re-extraction supersede idempotency:** a promoted node's stem is now the paper title, not the
  arxiv id; `_find_superseded_stem` matches the old (Schema-C, id-stemmed) nodes correctly on first
  rebuild, but a *second* extraction of an already-rebuilt paper would not self-supersede. Minor;
  `arxiv_id` is preserved in frontmatter for a future metadata-based match if needed.
- **`friction-260710-01`** (ingest triage) is separate and still OPEN — the triage prompt is already
  external (`prompts/chimera_sys/reviewer_zero.j2`); the real ask is *tunable judgement criteria*, not
  relocation. Not addressed here.

## Addendum — 2026-07-13 (first live run + lens policy)

- **First live extraction** (STALE, arXiv 2605.06527) — ingest → extract produced a genuinely rich,
  readable node (synthesis, lens findings, C01–C04 with quote-grounded sources, `supersedes` the thin
  triage node, honest `no_prior_match`). `friction-260710-02` resolved in practice.
- **Incident:** the run surfaced doubled list markers (`1. 1.`, `> 💥 💥`) — the LLM prefixes them and
  the renderer also did. Fixed with defensive strips + prompt notes + regression test
  (`docs/incidents/2026-07-13-extract-node-double-markers.md`).
- **Lens policy (Architect decision):** `lens` → `lenses: list[LensCritique]` (1-2). ONE lens by
  default; a SECOND fires only when another lens's trigger scores high INDEPENDENTLY on the same paper
  (hybrid detection, prompt-managed — no override param). STALE is the exemplar: a benchmark ABOUT a
  mechanism warrants both Forensic Leakage (benchmark integrity) and State Collision (mechanism depth).
- **Live re-seal still pending** a server reconnect (the Python fixes need a process reload — prompts
  hot-reload, module code does not) + operator review of a clean re-extraction.
