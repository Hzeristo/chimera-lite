# Batch Plan: Phase Q — Disciplined Knowledge Extraction

**Output location:** `docs/plans/Phase-Q-batch.md`
**Audit reference:** `docs/audits/Q.0.md` + `docs/audits/Q.0-reaudit.md` (date: 2026-07-09)
**Phase doc:** `docs/phases/phase-Q.md` (sparse manifest — distinct from this batch plan)
**Driving frictions:** `friction-260709-01` (vault absent from the loop → explicit extraction), `friction-260708-01`
(prose→typed-edge filling). Phase-declared; user-authorized anticipatory work per the phase spec.

This document is a single unit. User approves the whole sequence or rejects the whole sequence. After
approval, hand off to `chimera-code-taste` batch_execution mode.

---

## Settled design decisions (confirmed with user, 2026-07-09)

| # | Decision | Effect on plan |
|---|---|---|
| **D1** | **`extract_paper` stages a NEW Schema-C K node that SUPERSEDES the old** (all 392 papers already have a K node). | One path for new-paper + backfill. Q.2b stages a fresh node carrying the paper's identity; on user-approved promotion it replaces the prior node (records `supersedes`). Resolves reaudit #2. |
| **D2** | **Q.4 backfill target = the 13 clean Schema-C nodes** (reusable `source_md`; NO MinerU). The ~379-node A/B schema migration is a separate later effort, NOT a Phase-Q blocker. | Q.4 scoped to 13 named nodes. HSC: each gets ≥1 grounded edge OR explicit `no_prior_match`. Resolves reaudit #1. |
| **D3** | **A `derives_from` edge is licensed by citation-resolution** — the paper's `related_work`/references resolve to an existing vault K node (arxiv-id / title); proposed `ai-suggested`; **the human review is the confirmation**. | Q.2a grounding = citation-resolution, not topic-match. Fabrication-safe. Resolves reaudit #4. |
| **D4** | **Extend `create_staging_node` with an optional metadata passthrough** (provenance dict + `grounded` field), backward-compatible. | Q.1b. Enables HSC 2 (`no_prior_match`) + HSC 3 (provenance). Resolves reaudit #3. |

### Planner reconciliation (read before approving)

1. **Host = chimera-papers; `extract_paper` is a NEW `@mcp.tool` (not a new server).** It mirrors
   `ingest_paper` (`chimera-papers/server.py:85-108`): thin dispatcher → delegate in `miner_tools.py` →
   a new `single_paper_extract.py` orchestration. `.mcp.json` stays 2 servers; zero new dependencies
   (reuses MinerU, `generate_structured_data`, `StagingService`, `VaultReadAdapter`).
2. **Backfill reuses `source_md` — no GPU.** The 13 Schema-C nodes point `source_md` at
   `chimera-lite/papers/md_papers/<id>.md` (Scout-2). `extract_paper` reads that markdown directly; MinerU
   runs ONLY for a genuinely new, not-yet-ingested paper.
3. **Supersede = same-identity replacement on promotion.** The staged node carries the paper's
   `arxiv_id`/stem; on promotion it replaces the prior node for that paper and records `supersedes`.
   `promote_node` (`staging_service.py:95-111`) may need a small same-identity-replace guard — flagged in Q.2b.
4. **Grounding matches against 392 K nodes but 0 have K→K edges today** (Scout-2). That's fine —
   citation-resolution (D3) needs the prior node to *exist*, not to already have edges.
5. **Total new code ≈ 140–170 lines** across Q.1a/Q.1b/Q.2a/Q.2b; Q.3 is test-only, Q.4 is run+verify.
6. **`create_staging_node` extension is additive** — existing `create_node`/`link_nodes` callers pass no
   metadata and are unaffected (reaudit D4).

---

## Sprint Sequence

```
Q.1a  KClaimExtraction model (schemas.py)          ┐
Q.1b  create_staging_node metadata passthrough     ┤  (parallel-eligible prep)
Q.2a  grounding: citation-resolution sub-routine   ┘
                    │  (all three feed Q.2b)
                    ▼
Q.2b  extract_paper orchestration (new @mcp.tool; stage new K node + edges, supersede)
                    │
                    ▼
Q.3   Test: fixtures over Schema A/B/C + duplicate-migration; discipline assertions
                    │
                    ▼
Q.4   Backfill the 13 Schema-C nodes (reuse source_md) → staging → verify
                    │
                    ▼
seal (chimera-sprint-discipline phase_review)
```

- **Q.1a / Q.1b / Q.2a are parallel-eligible** (different files, no interdependency). **Q.2b consumes all
  three.** Q.3 needs Q.2b; Q.4 needs Q.2b + Q.3.
- **Split analysis (process step 3):** phase-doc Q.1 → **Q.1a** (model, `schemas.py`) + **Q.1b** (staging
  extension, `staging_service.py`) — different concerns, >50 lines combined. Phase-doc Q.2 → **Q.2a**
  (grounding, independently testable) + **Q.2b** (orchestration, the 🔴 sprint). Q.3/Q.4 unchanged.

---

## Sprint Q.1a: KClaimExtraction — the mechanism-claim response_model

**Friction reference:** `friction-260709-01` (OPEN).

**Predecessor assumptions:** None — independent. **Produces** the `response_model` Q.2b validates the LLM against.

**Risk level:** 🟡 MED (code < 30 lines, schema-validated; design-bearing — the model IS the discipline).

### Objective
Define `KClaimExtraction` in `core/schemas.py` so a paper's claims are captured as 1–5 mechanism-level
statements (no numbers), each with provenance and proposed citation-grounded edges — mirroring ARA's
claim discipline, never its file format.

### Design notes (audit-derived)
- Reuse the existing pattern: `class KClaimExtraction(BaseModel)` + `model_config = ConfigDict(extra="forbid")` — audit ref: `schemas.py:69-72`.
- Fields per claim (from `ara-repo-structure.md` Q1, minus reproduction): `statement` (mechanism, no run-numbers), `falsification`, `sources` (grounding-by-quote: `value ← «verbatim line»`), `status`, `tags`; plus lens `flags` from Decision 3 (`[no_ablation, math_decoration, result_ungrounded, …]`).
- Top-level: `claims: list[…]` (1–5), `proposed_edges: list[{target_stem, edge_type, source_citation}]`, `provenance` default `ai-suggested`. NO I/T/D fields — audit ref: `phase-Q.md` HSC 4.

### Task scope
1. Add `KClaimExtraction` (+ any nested claim model) to `core/schemas.py` (~35 lines) — audit ref: Q1.1/Q1.2.
2. `Field(description=…)` on every field (fed to the LLM via `model_json_schema()`) — audit ref: `filter_service.py:36`.

### Acceptance
- `KClaimExtraction.model_json_schema()` renders; `extra="forbid"` rejects unknown keys — verify via a unit test.
- Name-deletion check in the test: a fixture claim whose `statement` names a recipe FAILS a lint assertion; a mechanism statement passes.
- No field admits an I/T/D node.

### Red lines
- ❌ No numbers in `statement` (numbers live in `sources`/evidence) (phase-wide)
- ❌ No new dependency; model lives in `schemas.py` only (sprint-specific)
- ❌ No I/T/D fields (phase-wide)
- ❌ No opportunistic refactoring

### Output locations
- Code: `mcp-servers/chimera-papers/core/schemas.py`
- Tests: `tests/test_kclaim_schema.py`
- Docs: deferred to seal.

---

## Sprint Q.1b: create_staging_node — metadata passthrough (D4)

**Friction reference:** `friction-260709-01` (OPEN); reaudit #3.

**Predecessor assumptions:** None — independent. **Produces** the staging write that carries provenance + `grounded:`.

**Risk level:** 🟡 MED (< 20 lines, must stay backward-compatible; has tests).

### Objective
Extend `create_staging_node` with an optional `metadata: dict | None` passthrough so a staged K node can
carry provenance tags and a `grounded: no_prior_match` field — without breaking existing callers.

### Design notes (audit-derived)
- Current frontmatter is a fixed dict (`type/status/title/created_at/tags/graph_edges`) — audit ref: `staging_service.py:80-92`. Add `if metadata: fm.update(metadata)` after the fixed keys.
- Signature: `create_staging_node(type, title, body, edges=None, metadata=None)`. Existing `create_node`/`link_nodes` callers pass nothing → unchanged — audit ref: `mcp-architecture-review.md` Q3.

### Task scope
1. Add `metadata` param + merge in `create_staging_node` (`staging_service.py:61-93`, ~8 lines).
2. Optionally thread it through the `create_node` MCP tool (chimera-vault) IF Q.2b routes through it; else Q.2b calls `StagingService` directly (precedent: `scripts/seed_hsc3.py:84`) — decide in Q.2b.

### Acceptance
- `create_staging_node(..., metadata={"provenance":"ai-suggested","grounded":"no_prior_match"})` emits those frontmatter keys; `model` unchanged when `metadata=None` (byte-identical to today) — unit test.

### Red lines
- ❌ Must not change output for existing `metadata=None` callers (phase-wide: backward-compat)
- ❌ No new frontmatter key when metadata absent (sprint-specific)
- ❌ Still staging-only — no live-vault write (phase-wide)
- ❌ No opportunistic refactoring

### Output locations
- Code: `mcp-servers/chimera-papers/staging_service.py`
- Tests: `tests/test_staging_metadata.py`

---

## Sprint Q.2a: Grounding — citation-resolution sub-routine (D3)

**Friction reference:** `friction-260708-01` (OPEN); reaudit #4.

**Predecessor assumptions:** None — uses existing vault tools. **Produces** the edge-proposal function Q.2b calls.

**Risk level:** 🟡 MED (~40 lines; independently testable; the fabrication guard lives here).

### Objective
Given a paper's references/`related_work`, resolve each to an existing vault K node (arxiv-id / title) and
return proposed `derives_from`/`contradicts` edges — matches only, never topic-guesses.

### Design notes (audit-derived)
- Seed via `VaultReadAdapter` / ripgrep over vault K nodes; **exclude `.migration_backup` + `templates`** (fix the reaudit Q2.2 gap — `query_graph` excludes only `.obsidian`, `vault_read_adapter.py:496`).
- Resolution key = arxiv-id first, then title stem (Schema-A titles ARE the arxiv id, Scout-2). Return `{target_stem, edge_type: derives_from, source_citation}` per match; empty list ⇒ caller stages `no_prior_match`.
- No LLM "similarity" — a match is a resolved citation, full stop (D3). Fabrication guard: `[[vault-graph-edges-empty]]`.

### Task scope
1. New `grounding.py` (`resolve_citations(references, vault_root) -> list[EdgeProposal]`, ~40 lines) — audit ref: Q2.2.
2. Its own dir-exclusion set (`.obsidian`, `.migration_backup`, `templates`).

### Acceptance
- Given a references list containing an arxiv id present in the vault → returns a `derives_from` proposal to that stem; an id NOT in the vault → no proposal — unit test with fixtures.
- Never returns a proposal for a `.migration_backup`/`templates` file.

### Red lines
- ❌ No topic/keyword "similarity" edges — resolved citations only (phase-wide: no fabrication)
- ❌ Must exclude `.migration_backup` + `templates` (sprint-specific)
- ❌ Read-only over the vault (phase-wide)
- ❌ No opportunistic refactoring

### Output locations
- Code: `mcp-servers/chimera-papers/grounding.py`
- Tests: `tests/test_grounding.py`

---

## Sprint Q.2b: extract_paper — orchestration + new @mcp.tool 🔴

**Friction reference:** `friction-260709-01` (OPEN). **Requires explicit per-sprint approval before execution.**

**Predecessor assumptions:**
- Q.1a `KClaimExtraction` exists; Q.1b `metadata` passthrough exists; Q.2a `resolve_citations` exists — re-plan trigger if any signature differs.

**Risk level:** 🔴 HIGH (> 50 lines, multiple files, stages a superseding node).

### Objective
Implement `extract_paper(paper_id)` end-to-end: reuse `source_md` (or MinerU for a new paper) → extract
`KClaimExtraction` → ground edges via citation-resolution → stage ONE new Schema-C K node (provenance +
edges or `no_prior_match`) that supersedes the paper's prior node on promotion.

### Design notes (audit-derived)
- Mirror `ingest_paper` wiring: thin `@mcp.tool` (`server.py`, gated by `_start_lock`/`has_active_long_task`) → `miner_tools.py` delegate → new `single_paper_extract.py` — audit ref: `Q.0.md` Q0.2, `single_paper_ingest.py:60-94`.
- Markdown: if the paper's node has a valid `source_md`, READ it (no MinerU); else fetch+`ingest_to_papers` (reaudit Planner #2).
- Extract: `generate_structured_data(system_prompt, user_prompt, response_model=KClaimExtraction)` (temp 0.01, 3-retry) — audit ref: `openai_compatible_client.py:163`. New `.j2` templates (system = a mechanism-claim/name-deletion persona; user injects `model_json_schema()` + paper text).
- Stage: `create_staging_node(type="knowledge", …, edges=<grounded>, metadata={provenance, grounded})`; empty grounding ⇒ `metadata={"grounded":"no_prior_match"}`, edgeless. **Supersede (D1):** carry the paper identity; note `promote_node` same-identity-replace guard (`staging_service.py:95-111`).
- Returns a **summary string** (isolation by construction; the caller never sees the markdown) — audit ref: `mcp-architecture-review.md` Q4.

### Task scope
1. `single_paper_extract.py` orchestration (~70 lines) — reuse source_md, extract, ground, stage.
2. `extract_paper` delegate in `miner_tools.py` (~15 lines); thin `@mcp.tool` in `chimera-papers/server.py` (~12 lines).
3. Two `.j2` templates under `prompts/` (system + task).
4. `promote_node` same-identity-replace guard if absent (~10 lines) — records `supersedes`.

### Acceptance
- `extract_paper("2305.16291")` on a Schema-C node → stages ONE K node in `docs/staging/` with mechanism claims, ≥0 grounded edges (or `grounded: no_prior_match`), `provenance: ai-suggested`, and NO I/T/D file created.
- The tool return is a summary string; `docs/staging/` shows the node; the live vault is untouched until promotion.
- `server.py` stays a thin dispatcher (< 200-line spirit).

### Red lines
- ❌ No I/T/D node ever written (phase-wide HSC 4)
- ❌ No fabricated edge — Q.2a proposals only; no match ⇒ `no_prior_match` edgeless (phase-wide)
- ❌ Staging-only; never auto-promote into the vault (phase-wide)
- ❌ No new MCP server / dependency; `.mcp.json` stays 2 (phase-wide)
- ❌ No opportunistic refactoring

### Output locations
- Code: `mcp-servers/chimera-papers/{single_paper_extract.py, miner_tools.py, server.py, staging_service.py}`, `prompts/…`
- Tests: `tests/test_extract_paper.py`

---

## Sprint Q.3: Test — fixtures over Schema A/B/C + discipline assertions

**Friction reference:** `friction-260709-01` (OPEN).

**Predecessor assumptions:** Q.2b `extract_paper` exists and stages a node — re-plan trigger if its output shape differs.

**Risk level:** 🟢 LOW (test-only).

### Objective
Prove the discipline holds on real inputs: mechanism-level claims, grounding-only edges, provenance
present, zero I/T/D — across all three vault K-node schemas.

### Design notes (audit-derived)
- Fixtures MUST cover Schema **A** (`score:"9/10"` string, no `arxiv_id`, no edges), **B** (`arxiv_id`+stale `source_md`), **C** (full + empty scaffold), and a duplicate-migration pair (`Memp` C vs `v2` A) — audit ref: reaudit Q3.1 (Scout-2).
- Assert name-deletion on emitted `statement`s; assert every edge traces to a Q.2a citation proposal; assert no `Insight/Thought/Decision` file written.

### Task scope
1. `tests/test_extract_discipline.py`: 5 K-node fixtures (A×2, B×1, C×2) — run `extract_paper`, assert claims mechanism-level, edges grounding-only, provenance set, no I/T/D.

### Acceptance
- All 5 fixtures pass the four assertions; a deliberately recipe-named `statement` fixture FAILS (guard works).

### Red lines
- ❌ No production code changes in this sprint (test-only) (phase-wide)
- ❌ Fixtures must include all three schemas (sprint-specific)
- ❌ No opportunistic refactoring

### Output locations
- Tests: `tests/test_extract_discipline.py`

---

## Sprint Q.4: Backfill the 13 Schema-C nodes (D2) → staging → verify

**Friction reference:** `friction-260708-01` (OPEN — populates the wide-and-shallow graph, honestly).

**Predecessor assumptions:** Q.2b + Q.3 pass; the 13 Schema-C `source_md` paths still resolve — re-plan trigger if a path is missing (then that node needs re-fetch, out of D2 scope).

**Risk level:** 🟡 MED (runs LLM extraction on 13 real papers; writes to `docs/staging/` only, review-gated).

### Objective
Run `extract_paper` on the 13 named Schema-C nodes (reusing `source_md`, no MinerU) and stage a superseding
K node for each, so every one carries ≥1 grounded edge OR an explicit `no_prior_match`.

### Design notes (audit-derived)
- The 13 nodes are enumerated in `Q.0-reaudit.md` / Scout-2 (VOYAGER, AWM, Memp, Skill-Pro, LiveEvo, MemTransfer, DIA, WORLDEVOLVER, AutoMem, ReContext, IterativeVibecoding, FLOORPLANVLM, MapTrace).
- Batch via the async twin + `asyncio.gather` if serial is slow — audit ref: `optics_service.py:168`. No GPU (source_md reuse).
- Do NOT touch the ~379 Schema-A/B nodes (D2 scope) — their migration is a later effort.

### Acceptance
- 13 staged K nodes appear in `docs/staging/`; each has ≥1 `derives_from`/`contradicts` edge to a real prior vault K node OR `grounded: no_prior_match`; zero fabricated (each edge traces to a citation).
- Zero I/T/D nodes created; the live vault untouched (all in staging, awaiting the Architect's review).

### Red lines
- ❌ Only the 13 Schema-C nodes — do NOT process Schema-A/B (sprint-specific: D2 scope)
- ❌ No MinerU re-conversion (reuse `source_md`) (sprint-specific)
- ❌ No fabricated edges; `no_prior_match` when citations don't resolve (phase-wide)
- ❌ Staging-only; the Architect promotes (phase-wide)
- ❌ No opportunistic refactoring

### Output locations
- Artifacts: `docs/staging/*.md` (13 nodes, awaiting review)
- Verify log: seal notes

---

## Phase-wide Red Lines

Violation in any sprint halts the batch:

- ❌ **Zero I/T/D nodes from extraction** — `extract_paper` writes K nodes only (HSC 4).
- ❌ **No fabricated edges** — citation-resolution only; no match ⇒ `grounded: no_prior_match`, edgeless.
- ❌ **Staging → review → never auto-promote** — all writes land in `docs/staging/`.
- ❌ **No new MCP server, no new dependency** — `.mcp.json` stays 2; reuse MinerU / `generate_structured_data` / `StagingService` / `VaultReadAdapter`.
- ❌ **Thin adapter** — server tool bodies stay lazy-import dispatchers; logic in domain modules.
- ❌ **Backward-compatible staging** — `create_staging_node(metadata=None)` is byte-identical to today.
- ❌ **No opportunistic refactoring.**

---

## Hard Sealing Conditions (carried from phase doc)

MUST Pass at phase_review:

1. **HSC 1 — mechanism-level claims:** extracted `statement`s pass the name-deletion test — verified by Q.3 assertions + spot-check of Q.4 output.
2. **HSC 2 — grounded edges only:** every edge traces to a Q.2a citation resolution; `no_prior_match` used when none — verified across the 13 Q.4 nodes.
3. **HSC 3 — provenance on every field:** each staged claim/edge carries a provenance tag — verified in Q.3 + Q.4 frontmatter.
4. **HSC 4 — zero I/T/D from extraction:** `extract_paper` never writes an I/T/D node — verified by test + `grep` over Q.4 staging output.

---

## Approval

User approves the whole sequence or rejects the whole sequence.

Upon approval, hand off to `chimera-code-taste`:
> "Execute batch for Phase Q per `docs/plans/Phase-Q-batch.md`."

Note: **Q.2b is 🔴** — gate its execution explicitly even after batch approval.

---

*Generated by chimera-sprint-discipline batch_planning mode.*
