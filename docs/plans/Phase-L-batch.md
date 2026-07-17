# Batch Plan: Phase L — Locus: The Research Harness

**Output location:** `docs/plans/Phase-L-batch.md`
**Audit reference:** `docs/audits/L.0.md` (date: 2026-07-16)
**Phase doc:** `docs/phases/phase-L.md` (sparse manifest — distinct from this batch plan)
**Driving frictions:** GPT diagnosis 2026-07-12 (harness-at-capacity; phase-declared, no `docs/logs/` entry —
same footing as Phase N.A's `friction-chimera-lite-01`), `friction-260709` (fork-subagent appetite —
judgment belongs in isolated Claude workers), `friction-260710-01` (triage tunability — partially
realized via the vault-criteria mechanism).

This document is a single unit. User approves the whole sequence or rejects the whole sequence. After
approval, hand off to `chimera-code-taste` batch_execution mode. **W1 (L.2) must run and prove value
before L.3 (W2) executes** — a go/no-go gate, per the phase's GPT-directive.

---

## Settled design decisions (locked in phase-L.md, ST 2026-07-16) + audit facts

| # | Decision | Effect on plan |
|---|---|---|
| **D1** | **Criteria is a `[type × field]` matrix, decomposed 4+N (not 4×N).** Compose `type/{type}.md` + `field/{field}.md` at runtime. `type` = verification shape, **4-class closed** {benchmark, method, theory, survey}; `field` = domain taste, **open, KG-anchored**. | L.1b classifier does TWO classifications. L.1a's `load_criteria` composes N+4 files, never an N×4 product. |
| **D2** | **Disposition is a THIRD criteria axis, loaded before role** — `disposition/{role}.md` + `disposition/_general.md`. Over-denigrate and over-defer point OPPOSITE ways → correction is direction-aware (role encodes direction). | Every judgment subagent (L.2c, L.3b) loads disposition before applying role. New phase-wide red line. |
| **D3** | **W1 claim input: all three sources** (conversation-claim / K-node / raw text); **conversation-claim is the first L.2 target** (GPT-diagnosis core). | L.2c builds the conversation-claim path first; K-node / raw-text are follow-on inputs to the same subroutine. |
| **D4** | **W2 artifact = recon + nomination ("option C")** — light survey map; high-relevance papers marked promote-candidate; the Architect selects a few for full ingest. | L.3b nominates, never auto-ingests. Bridges to the existing `ingest_paper` on the Architect's selection. |
| **D5** | **Citation input: cheap-first** — bare arXiv id + already-in-vault; the reference parser is deferred to an increment (record a friction if coverage is insufficient). | L.2a/L.3b reuse `_cited_arxiv_ids` + `grounding.resolve_citations` as-is (audit D3); no new parser this batch. |
| **D6** | **`write_result` is a lifecycle manager, not a sink** — W1 verdict = identity-based SUPERSEDE (reuse Phase Q supersede); W2 map = MERGE preserving human annotations. Artifacts live IN the vault (two curation paths: harness + Obsidian). | Split across L.2b (write + supersede) and L.3a (merge + mark_stale). |

### Forward-compatibility with Phase K (locked ST 2026-07-16)

Phase K will layer two interpretation gates on the harness's output — **K-gate-1 (monotonicity: the
"weakest dependency")** and **K-gate-2 (framing: N framings over a number before a hand-written I node)**.
The harness must therefore record **raw verifiable structure, never baked interpretation**, or Phase K is
forced into a rewrite. Three constraints follow, each pinned to a sprint:

- **C1 → L.2b.** The W1 verdict artifact records its **dependency structure**, not just the verdict:
  `{verdict, quotes, depends_on: [claim_ids]}`. K-gate-1 needs the dependency edges to compute the weakest
  dependency; a verdict-only artifact would force a retrofit.
- **C2 → L.2c.** W1 **stops at verification** — the verdict answers "is the claim supported?", NOT "what does
  the claim mean?". No single framing is baked into the verdict (framing is K-gate-2's job); a baked
  interpretation would have to be un-baked later.
- **C3 → L.3b.** The W2 per-paper artifact stores **number + verbatim source + a descriptive gap sentence**,
  never a single-framing "therefore this proves X" conclusion. K-gate-2 applies N framings to each number
  before the Architect hand-writes an I node; a pre-concluded row would have to be unwrapped.

### Planner reconciliation (read before approving)

1. **The two death-order preconditions PASS (audit).** A subagent CAN call MCP tools (`L.0.md` A1, live-probe:
   `vault_query`→108 nodes) and `read_vault_file` reaches `criteria/{type}.md` with **zero code change**
   (`vault_read_adapter.py:181-220`, no subfolder allowlist). The architecture rests on solid ground.
2. **Subagent MCP tools arrive DEFERRED.** The live probe had to `ToolSearch`-load the schema before calling
   (`L.0.md` A1). Every W1/W2 subagent prompt (L.1b, L.2c, L.3b) MUST either pre-declare needed `mcp__*` tools
   in its agent-type frontmatter or instruct the worker to load them first.
3. **Isolation is free (audit A3).** Subagents return only a summary in their own context window, no leak to
   parent — HSC #3 satisfied by construction. Keep worker returns tiny (verdict+quote / gap+number).
4. **Concurrency/cost ceilings are undocumented (audit A2/A4)** → self-bounding is mandatory. L.3b runs bounded
   BFS + hard paper cap and batches in waves, not one 60-wide blast.
5. **W1's build surface is three thin primitives, not a rewrite.** Bare-fetch (split `_fetch_arxiv_pdf`,
   `single_paper_ingest.py:34-59,87,111`), `convert_pdf_to_md` (thin wrapper over live
   `MineruClient.convert`, `paper2md.py:56-159`), and `write_result` (new). Convert is essentially free.
6. **Subagent-primacy holds by construction (audit E1/E2).** The three existing `generate_structured_data`
   sites (`filter_service.py:45`, `optics_service.py:134`, `single_paper_extract.py:186`) are ALL outside the
   greenfield W1/W2 path. As long as the new primitives carry no LLM call, the red line holds.
7. **Type axis ≠ lens registry.** The locked `type` is the closed 4-class {benchmark, method, theory, survey}
   (D1), NOT the existing lens names (`optics_lens_registry.py:84-169`: math_arch/eval_rigor/memory_physics/
   survey_*). The lens registry is a *reuse candidate for the CONTENT of `type/*.md`* (verification-shape
   prose), not the type labels. Keep them distinct.
8. **Thin-adapter watch.** `chimera-vault/server.py` is already 225 lines (Accepted Partial O.seal.1). Adding
   `load_criteria` + `write_result` grows it — new tool bodies stay lazy-import dispatchers; the lifecycle
   logic lives in a domain module (extend `StagingService` or a new `result_service.py`). Consider the
   O.seal.1 follow-up (move write tools to `write_tools.py`) if the file bloats.
9. **OPEN DECISION — `write_result` target (confirm before L.2b).** CHANGE 5 says "artifacts live in the vault
   (two curation paths: harness + Obsidian)" with lifecycle `PENDING_REVIEW → PROMOTED | REJECTED`. This
   implies a **dedicated vault subfolder** (e.g. `<vault>/Harness/`) with a `status:` field, Obsidian-editable
   — NOT `docs/staging/` (Phase Q's model). This does not violate "never auto-promote staging candidates":
   W1/W2 results are the harness's OWN output surface, not K/T/I/D nodes being auto-promoted. **Confirm the
   target folder + whether PENDING_REVIEW artifacts sit in-vault or in staging before L.2b codes the path.**
10. **The harness records structure; Phase K interprets it (C1/C2/C3).** W1/W2 never bake interpretation —
    verdicts carry `depends_on`, W1 stops at "supported?", W2 stores number+verbatim not conclusions. This is
    a *forward-compat* constraint, not extra scope: it changes the artifact SHAPE (add fields, withhold
    conclusions), not the work. Getting the shape right now avoids a Phase-K rewrite.

---

## Sprint Sequence

```
L.1a  criteria matrix + load_criteria()      ┐
L.1b  dual-classification subagent           ┤ (L.1b depends on L.1a's file layout)
                     │                        │
L.2a  fetch_paper + convert_pdf_to_md  ───────┤ (parallel-eligible with L.1)
L.2b  write_result: write + supersede  ───────┘ (+ depends_on structure, C1)
                     │  (L.1a+L.1b+L.2a+L.2b all feed L.2c)
                     ▼
L.2c  W1 orchestration (conversation-claim first)   ◄── PROVE-VALUE GATE (GPT directive)
                     │   Architect confirms W1 output is worth W2 before proceeding
                     ▼
L.3a  write_result: merge + mark_stale
                     ▼
L.3b  W2 orchestration (bounded BFS, parallel, option-C nomination)
                     ▼
L.4   (optional) HTML panel render
                     ▼
seal (chimera-sprint-discipline phase_review)
```

- **L.1a / L.2a / L.2b are parallel-eligible** (different files, no interdependency). **L.1b needs L.1a's
  criteria layout. L.2c consumes L.1a+L.1b+L.2a+L.2b.** L.3a extends L.2b; L.3b needs L.3a + the W1 subroutine
  from L.2c. L.4 needs L.3b.
- **Split analysis (process step 3):** phase-doc **L.1** → **L.1a** (loader + matrix, MCP) + **L.1b**
  (classifier, subagent) — different concerns (code vs orchestration). Phase-doc **L.2** → **L.2a** (input
  primitives) + **L.2b** (result lifecycle, the design-bearing supersede) + **L.2c** (orchestration, 🔴).
  Phase-doc **L.3** → **L.3a** (merge semantics, independently testable) + **L.3b** (orchestration, 🔴).
  L.4 unchanged (optional). No expansion beyond the phase manifest.

---

## Sprint L.1a: Criteria matrix scaffold + `load_criteria(type, field, role)`

**Friction reference:** friction arc terminus (phase-declared); `friction-260710-01` (OPEN — tunable criteria).

**Predecessor assumptions:** None — independent. **Produces** the criteria layout + loader that L.1b, L.2c, L.3b consume.

**Risk level:** 🟡 MED (new MCP primitive < 40 lines; vault-read only; design-bearing — this IS HSC #1).

### Objective
Add a `load_criteria(type, field, role)` MCP primitive to `chimera-vault` that composes the three-axis
criteria matrix from the vault at runtime, and establish the `criteria/` directory convention with a minimal
Architect-seeded set — so editing a criteria file in Obsidian changes W1/W2 behavior on the next run, zero git.

### Design points (audit-derived)
- `read_vault_file` reaches `criteria/{...}.md` with no code change — `_resolve_path_within_vault` enforces
  only "inside vault_root", no subfolder allowlist — audit ref: `vault_read_adapter.py:181-220`.
- `load_criteria` composes, in the mandatory order: `type/{type}.md` + `field/{field}.md` (capability) then
  `disposition/{role}.md` + `disposition/_general.md` (disposition) — phase-L.md "Criteria Architecture".
  Missing `field/{field}.md` degrades gracefully (capability = type-only) and is reported, never fabricated.
- Thin adapter: the tool body delegates to `VaultReadAdapter.read_file`; no logic in `server.py` — audit ref:
  `chimera-vault/server.py:78-86` (existing `read_vault_file` pattern). Mind O.seal.1 (server at 225 lines).
- `type` is the closed 4-class {benchmark, method, theory, survey} (D1); `role` ∈ a small vocabulary seeded
  here (e.g. `paper-critic`, `proposal-evaluator`) — see L.1b/L.2c.

### Task scope
1. `load_criteria(type, field, role)` `@mcp.tool` in `chimera-vault/server.py` (~15 lines, thin) + a
   `compose_criteria` helper in a domain module (~25 lines) — audit ref: `L.0.md` B1/B2.
2. Seed the vault `criteria/` tree (Architect authors real content; this sprint seeds minimal stubs to test):
   `criteria/type/{benchmark,method,theory,survey}.md`, `criteria/field/_example.md`,
   `criteria/disposition/{paper-critic,proposal-evaluator}.md`, `criteria/disposition/_general.md`.
3. Document the matrix + load order in the tool docstring (WHEN/WHAT).

### Acceptance
- `load_criteria("benchmark", "memory", "paper-critic")` returns the composed text of the four files in order;
  a missing `field/memory.md` returns type+disposition with an explicit "no field criteria" marker (not a crash).
- **HSC #1 live:** add a line to `criteria/type/benchmark.md` in Obsidian, re-call `load_criteria` → the new
  line appears with zero git commit.
- `chimera-vault/server.py` tool body stays a lazy-import dispatcher (thin-adapter spirit).

### Red lines
- ❌ No criteria content in repo/code/skill — only the loader + minimal test stubs; real criteria live in the vault (phase-wide)
- ❌ Disposition files load BEFORE role is applied downstream (phase-wide)
- ❌ Thin adapter — compose logic in a domain module, not `server.py` (phase-wide)
- ❌ No new dependency; `.mcp.json` stays 2 servers (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-vault/server.py` + a domain helper (`criteria_service.py` or extend an existing module)
- Vault: `<vault>/criteria/**` (seed stubs; Architect authors real content)
- Tests: `tests/test_load_criteria.py`
- Docs: deferred to seal.

---

## Sprint L.1b: Dual-classification subagent (type 4-class + field, KG-anchored)

**Friction reference:** friction arc terminus (phase-declared); `friction-260709` (judgment in Claude subagents).

**Predecessor assumptions:** L.1a criteria layout exists (the classifier's output must name a real `type/{type}.md` +
`field/{field}.md`) — re-plan trigger if the axis names change.

**Risk level:** 🟡 MED (orchestration + subagent prompt; near-zero MCP code; the classifier IS Claude judgment, not deepseek).

### Objective
Define the classification subagent that reads a paper (title/abstract/markdown) + its KG neighborhood and returns
`{type ∈ {benchmark,method,theory,survey}, field}` — type from a closed 4-class, field anchored to the vault's
existing topic structure — so `load_criteria` can select the matched criteria files.

### Design points (audit-derived)
- Classification is **Claude reasoning in a Task subagent**, NOT `generate_structured_data` — phase-wide red
  line; audit ref: `L.0.md` E1/E2 (the 3 deepseek sites are all outside this path).
- Field is anchored to the KG: seed the field candidate set from the vault via `obsidian_graph_query` /
  `vault_query` (existing tools) so `field` names a real neighborhood, not a hallucinated label — audit ref:
  `L.0.md` C1; `optics_lens_registry.py:84-169` is a *content* reuse candidate, not the type labels (reconciliation #7).
- The subagent is DEFERRED-tool aware: it `ToolSearch`-loads `mcp__chimera-vault__*` before calling
  (reconciliation #2).
- Output is a tiny structured summary `{type, field}` — isolation by construction (audit A3).

### Task scope
1. A classifier subagent definition / prompt (agent-type frontmatter naming the needed `mcp__chimera-vault__*`
   tools; or a documented spawn prompt used by L.2c/L.3b) — orchestration artifact, ~0 MCP lines.
2. The field-anchoring convention (how the KG neighborhood constrains the open field label).

### Acceptance
- Given ≥3 papers spanning ≥2 types, the classifier returns the correct `type` (4-class) and a `field` that
  resolves to a real vault neighborhood, in a subagent (verified by inspecting the spawn path — Claude, not deepseek).
- The classifier's return is a short `{type, field}` — the paper text does not leak into the parent context.

### Red lines
- ❌ Classification is Claude-in-subagent — NO `generate_structured_data` call (phase-wide)
- ❌ `type` stays the closed 4-class; do not silently widen it (sprint-specific: D1)
- ❌ `field` must anchor to a real KG neighborhood — no free-invented labels (sprint-specific)
- ❌ No opportunistic refactoring

### Output location
- Orchestration: a subagent definition (`.claude/agents/…` or a documented spawn prompt) + convention notes
- Tests: a fixture-based classification check (`tests/…` or a documented manual check — orchestration is not unit-testable like code)
- Docs: deferred to seal.

---

## Sprint L.2a: `fetch_paper` (bare) + `convert_pdf_to_md` primitives

**Friction reference:** `friction-260709` (W1 inputs); absorbs retired Phase R R.1.

**Predecessor assumptions:** None — independent. **Produces** the fetch + convert primitives L.2c/L.3b call.

**Risk level:** 🟡 MED (two thin primitives; convert is a wrapper over live code; < 40 lines total).

### Objective
Add two `chimera-papers` MCP primitives — `fetch_paper(arxiv_id)` (download the PDF only, no vault node) and
`convert_pdf_to_md(pdf_path | arxiv_id)` (MinerU → markdown path, no vault node) — by lifting the existing,
node-coupled logic into standalone, node-free tools.

### Design points (audit-derived)
- `_fetch_arxiv_pdf` already downloads by id but is bound to the node-writing ingest — split it into a bare
  fetch — audit ref: `single_paper_ingest.py:34-59` (fetch), `:87` (ingest-only caller), `:111` (node write).
- `MineruClient.convert(pdf_path)` is ALREADY a standalone, stateless, node-free converter — `convert_pdf_to_md`
  is a thin `@mcp.tool` wrapper (+ optional fetch-first when given an arxiv_id) — audit ref: `paper2md.py:56-159`.
- Both are gated by the existing `_start_lock` / `has_active_long_task` (shared GPU) — audit ref:
  `chimera-papers/server.py:124-129` (ingest_paper pattern).

### Task scope
1. Extract a bare `fetch_paper(arxiv_id) -> pdf_path` delegate in `miner_tools.py` (reuse `_fetch_arxiv_pdf`) +
   thin `@mcp.tool` (~12 lines).
2. `convert_pdf_to_md(pdf_path=None, arxiv_id=None) -> md_path` delegate wrapping `MineruClient.convert` +
   thin `@mcp.tool` (~15 lines). Writes NO vault node.

### Acceptance
- `fetch_paper("2305.16291")` returns a PDF path, creates no vault node.
- `convert_pdf_to_md(pdf_path=…)` returns a markdown path, creates no vault node; reuses the live MinerU/GPU path.
- Both rejected while a long-running arXiv/pipeline job holds the lock (shared GPU).

### Red lines
- ❌ Neither tool writes a vault node — bare primitives only (sprint-specific)
- ❌ Reuse `MineruClient` / `_fetch_arxiv_pdf`; no new fetch or convert logic (phase-wide: no new dep)
- ❌ Thin adapter — delegates in `miner_tools.py`, not `server.py` (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-papers/{server.py, miner_tools.py}`
- Tests: `tests/test_fetch_convert_primitives.py`

---

## Sprint L.2b: `write_result` — write + identity-supersede (W1 lifecycle) 🔴

**Friction reference:** `friction-260709`; realizes D6 (lifecycle manager) + C1 (dependency structure).

**Predecessor assumptions:** OPEN DECISION #9 resolved (write target = vault subfolder vs staging) — **re-plan
trigger if the target folder / status model differs from the CHANGE-5 in-vault reading.**

**Risk level:** 🔴 HIGH (new lifecycle logic; touches the vault write surface; identity-supersede is design-bearing).

### Objective
Add a `write_result` MCP primitive (+ backing service) that writes a W1 verdict artifact —
`{verdict: [V]/[P]/[U], quotes, depends_on: [claim_ids]}` (C1) — into the vault under a `PENDING_REVIEW` status,
and, on re-run for the same identity (`claim_hash` / `arxiv_id`), SUPERSEDES the prior artifact rather than
duplicating — reusing the Phase Q supersede path.

### Design points (audit-derived)
- Reuse the Phase Q supersede mechanism: `StagingService.promote_node` / `_unlink_superseded`
  (`staging_service.py:104-135`) and the `create_staging_node` `metadata` passthrough (`:66`) that already carries
  provenance/grounded fields — audit ref: `L.0.md` F2, D6.
- Identity = `claim_hash` (conversation/raw-text claims) or `arxiv_id` (K-node claims). Same identity on re-run ⇒
  supersede (records `supersedes`), never a duplicate — mirrors DEBT-017's arxiv_id-authoritative fix.
- **Record dependency structure (C1 — Phase K forward-compat).** The artifact stores `depends_on: [claim_ids]` —
  which verbatim quotes / sub-claims the verdict rests on — so K-gate-1 (monotonicity) can compute the weakest
  dependency without a retrofit. The schema is `{verdict, quotes, depends_on}`, not verdict-only.
- Target = the vault subfolder from decision #9 (Obsidian-editable, `status:` frontmatter), NOT `docs/staging/`
  unless #9 says otherwise. Lifecycle: `PENDING_REVIEW → PROMOTED | REJECTED`; `PROMOTED → SUPERSEDED`.
- Thin adapter — lifecycle logic in a domain service (`result_service.py` or extend `StagingService`), server tool
  delegates (reconciliation #8).

### Task scope
1. A result-write service: `write_result(kind="w1_verdict", identity, body, metadata)` with write + identity-supersede
   (~40 lines) — reuse `_unlink_superseded` / supersede logic. The W1 artifact schema is
   `{verdict, quotes, depends_on: [claim_ids]}` (C1).
2. Thin `write_result` `@mcp.tool` in `chimera-vault/server.py` (~15 lines).
3. Status-frontmatter convention (`PENDING_REVIEW` default) + the identity field + the `depends_on` list.

### Acceptance
- `write_result` on a new claim → one artifact in the vault result folder, `status: PENDING_REVIEW`, carrying
  `{verdict, quotes, depends_on: [claim_ids]}` (C1 — the dependency structure is present, not just the verdict).
- Re-run for the SAME identity → the prior artifact is superseded (one artifact, not two), `supersedes` recorded.
- The live vault K/T/I/D nodes are untouched; only the harness result folder is written.

### Red lines
- ❌ Identity-supersede, never duplicate on re-run (sprint-specific: D6)
- ❌ Store `depends_on` dependency structure, not verdict-only — Phase K forward-compat (sprint-specific: C1)
- ❌ Reuse Phase Q supersede — no new supersede logic (phase-wide: no opportunistic rebuild)
- ❌ Does not auto-promote or mutate K/T/I/D nodes; writes only the harness surface (phase-wide)
- ❌ Thin adapter — lifecycle in a domain module (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-vault/server.py` + `result_service.py` (or extended `staging_service.py`)
- Tests: `tests/test_write_result_supersede.py`

---

## Sprint L.2c: W1 orchestration — Claim Verbatim Verification 🔴

**Friction reference:** GPT diagnosis 2026-07-12 (the 20-30-min manual loop). **Requires explicit per-sprint approval.**

**Predecessor assumptions:** L.1a (`load_criteria`), L.1b (classifier), L.2a (fetch/convert), L.2b (`write_result`
with the `depends_on` schema) all exist with the planned signatures — re-plan trigger if any differs.

**Risk level:** 🔴 HIGH (the phase's ROI core; multi-step orchestration + subagent prompts; the PROVE-VALUE gate).

### Objective
Implement W1 end-to-end as Claude Code orchestration: a claim → fetch its cited paper(s) → classify (type+field)
→ `load_criteria(type, field, role)` (role = `paper-critic`) → a Claude subagent performs the verbatim check with
the composed criteria + disposition loaded before role → emit a [V]/[P]/[U] tag with grounding quotes **+ the
`depends_on` claim/quote ids** → `write_result`. The verdict answers "is the claim supported?", NOT "what does it
mean?" (C2). **Conversation-claim is the first input path** (D3); K-node and raw-text feed the same subroutine.

### Design points (audit-derived)
- Orchestration lives in the **main Claude agent** spawning Task subagents — NOT an MCP tool (phase-wide;
  Phase Q B1 constraint). MCP provides only the primitives called along the way.
- Load order in the verbatim subagent (mandatory): capability (KG + type + field) → disposition
  (`paper-critic` counters over-denigration on the absent paper; `_general` counters early-stop/binary verdicts)
  → THEN apply the critic role — phase-L.md red line "disposition precedes role".
- **Verification, not interpretation (C2 — Phase K forward-compat).** The verdict answers only "is the claim
  supported by a verbatim quote?" — it does NOT bake a single framing ("this number means X"). Framing is
  Phase K's K-gate-2, applied before a hand-written I node. The subagent also returns `depends_on` — which
  quotes / sub-claims the verdict rests on (feeds L.2b's C1 schema).
- Citation input cheap-first (D5): resolve the claim's cited paper via `_cited_arxiv_ids` +
  `grounding.resolve_citations` (`single_paper_extract.py:43-52`, `grounding.py:67-113`); if unresolved, the tag
  is [U]/[P], never a fabricated [V] (HSC #2). Record a friction if coverage proves too thin.
- The paper text stays in the subagent; only `{tag, quotes, location, depends_on}` returns (audit A3). Subagent
  `ToolSearch`-loads `mcp__*` first (reconciliation #2).
- Verbatim grounding mandatory: no tag without a verbatim quote + location (phase-wide red line).

### Task scope
1. W1 orchestration flow (a documented Claude Code procedure / skill or workflow): input-normalize (conversation/
   K-node/raw-text) → fetch/convert (L.2a) → classify (L.1b) → `load_criteria` (L.1a) → spawn verbatim subagent →
   `write_result` (L.2b).
2. The verbatim-check subagent prompt (criteria + disposition composition; [V]/[P]/[U] rubric; quote-or-[U] rule;
   verification-only — no framing/interpretation, C2; return `depends_on`).
3. The conversation-claim extractor (turn the Architect's in-conversation claim into `{claim_text, cited_ref}`).

### Acceptance
- **HSC #2 live:** on ≥3 claims spanning ≥2 paper types, W1 emits [V]/[P]/[U], each [V]/[P] backed by a verbatim
  quote + location; a claim with no supporting quote gets [U]/[P], never a fabricated [V].
- **HSC #3:** inspection shows zero `generate_structured_data` in the W1 path; the paper text never enters parent context.
- **C2:** the verdict contains no interpretation/framing ("means X") — only support + quotes + `depends_on`;
  framing is deferred to Phase K.
- Disposition is loaded before role (visible in the subagent prompt composition).
- **PROVE-VALUE GATE:** the Architect confirms W1 output is worth automating W2 before L.3 executes.

### Red lines
- ❌ No `generate_structured_data` / deepseek in the W1 judgment path (phase-wide)
- ❌ No [V]/[P]/[U] tag without a verbatim quote + location (phase-wide: verbatim grounding)
- ❌ W1 stops at verification — no framing/interpretation baked into the verdict; return `depends_on` (sprint-specific: C2/C1)
- ❌ Disposition (`paper-critic` + `_general`) loads before the critic role (phase-wide)
- ❌ W1 is main-agent orchestration, not an MCP tool (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Orchestration: a W1 skill/workflow + the verbatim subagent definition (`.claude/…`)
- Code: minimal glue only (input-normalize); the judgment is in the subagent prompt
- Tests: a ≥3-claim verification fixture + the HSC #2/#3 + C2 checks
- Docs: deferred to seal.

---

## Sprint L.3a: `write_result` — MERGE mode + mark_stale

**Friction reference:** realizes D6 (W2 map is living tissue).

**Predecessor assumptions:** L.2b `write_result` service exists — extends it. Re-plan trigger if its interface differs.

**Risk level:** 🟡 MED (~30 lines extending L.2b; merge-preserve-annotations is design-bearing but bounded).

### Objective
Extend `write_result` with a MERGE mode (identity = topic / seed-set) that adds new papers to an existing W2 breadth
map WHILE preserving human annotations (`[My Critique]`, manual verdicts), plus a `mark_stale` transition (reuse
Phase Q stale detection) — so the map can *live* across re-runs instead of being clobbered.

### Design points (audit-derived)
- MERGE ≠ SUPERSEDE: W1 supersedes by identity (L.2b); W2 merges by identity — audit ref: D6, phase-L.md
  "Artifact Lifecycle". Preserve any human-edited block (`[My Critique]`, manual verdict) verbatim; append only
  new-paper rows. Precedent for byte-preserving edits: `_splice_graph_edges` (`staging_service.py:31-52`).
- `mark_stale` reuses the Phase Q source-changed detection (STALE state) — audit ref: DEBT-017/Q stale path.
- Lifecycle: `PROMOTED → MERGED (W2 re-run) | STALE | edited-in-Obsidian`.

### Task scope
1. `write_result(kind="w2_map", identity, new_rows, ...)` merge path preserving annotated blocks (~25 lines).
2. `mark_stale(identity)` transition (~8 lines) reusing Phase Q detection.

### Acceptance
- Re-running W2 on the same seed-set MERGES new papers into the existing map; a hand-added `[My Critique]` line
  survives verbatim.
- `mark_stale` flips a map to STALE when its source changed, without deleting annotations.

### Red lines
- ❌ MERGE preserves human annotations verbatim — never clobbers (sprint-specific: D6)
- ❌ Reuse Phase Q stale detection + byte-preserving splice — no new mechanism (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `result_service.py` (or extended `staging_service.py`)
- Tests: `tests/test_write_result_merge.py`

---

## Sprint L.3b: W2 orchestration — Breadth Mapping 🔴

**Friction reference:** "cannot produce a semi-proposal" (survey-production bottleneck). **Requires explicit
per-sprint approval AND passing the L.2c prove-value gate.**

**Predecessor assumptions:** L.2c W1 subroutine (classify→load-criteria→verify) exists and proved value; L.3a MERGE
mode exists — re-plan trigger if the W1 subroutine's interface differs.

**Risk level:** 🔴 HIGH (parallel subagent orchestration; the phase's scale test; multi-file).

### Objective
Implement W2 as Claude Code orchestration: ≥3 seed papers → parallel Claude subagents expand the reference network
(bounded BFS — hard depth + hard paper caps) → each paper classified + criteria-loaded + REUSING W1's per-paper
subroutine → reduced to `{gap sentence, performance number, verbatim source}` — the gap sentence DESCRIBES, it does
NOT conclude "therefore this proves X" (C3) → merged (L.3a) into a classified map across ≥3 subfields, with
high-relevance papers marked promote-candidate (option-C nomination, D4).

### Design points (audit-derived)
- Reuse the W1 per-paper subroutine (classify → load_criteria → subagent read) from L.2c — the phase's stated
  reuse (phase-L.md Dependencies).
- Bounded BFS (phase-wide red line): hard depth cap + hard paper cap; batch in waves (audit A2/A4 — undocumented
  ceilings ⇒ self-bound). Each worker returns ONLY `{gap_sentence, perf_number, verbatim_source, type, field,
  promote?}` — tiny returns keep parent context + token cost bounded (audit A3/A4).
- **Number + verbatim, no single framing (C3 — Phase K forward-compat).** The `gap_sentence` describes the gap
  but draws NO "therefore this proves X" conclusion; the row stores the raw `perf_number` + its `verbatim_source`.
  Phase K's K-gate-2 applies N framings to each number before the Architect hand-writes an I node — a
  pre-concluded row would have to be unwrapped.
- Citation expansion cheap-first (D5): `_cited_arxiv_ids` + `grounding.resolve_citations`
  (`single_paper_extract.py:43-52`, `grounding.py:67-113`); papers not resolvable are noted, not fabricated.
- Disposition: routine per-paper reduction uses a single subagent + `disposition/{role}.md` (prompt-level);
  the 3× adversarial pair (advocate/skeptic/reconcile) is NOT used here — reserved for proposal-eval (Notes L.3).
- Option-C (D4): mark high-relevance papers `promote-candidate`; the Architect selects a few → hand to the
  existing `ingest_paper`. W2 never auto-ingests.

### Task scope
1. W2 orchestration flow: seed → bounded-BFS reference expansion → parallel per-paper subagents (reuse W1
   subroutine) → collect `{gap, number, verbatim_source, type, field, promote?}` → `write_result(kind="w2_map", MERGE)`.
2. The per-paper reduction subagent prompt (`{gap sentence, performance number, verbatim source}`; descriptive
   gap, NO single-framing conclusion, C3; promote-candidate flag).
3. The BFS bound config (depth cap, paper cap) — surfaced/logged, no silent truncation.

### Acceptance
- **HSC #4 live:** given ≥3 seed papers, W2 produces a classified map of ≥20 papers (bounded), each with a
  descriptive one-sentence gap + one performance number **+ its verbatim source** (C3 — no single-framing
  conclusion), across ≥3 subfields — on a real seed set from the Architect's domain.
- Re-run MERGES (L.3a) and preserves any annotations; promote-candidates are marked, none auto-ingested.
- Bounds are logged (what was capped), no silent truncation.

### Red lines
- ❌ Bounded BFS — hard depth + paper caps; no unbounded crawl (phase-wide)
- ❌ Judgment in Claude subagents, not deepseek (phase-wide)
- ❌ Store number + verbatim; NO single-framing "proves X" conclusion in the map (sprint-specific: C3)
- ❌ W2 nominates; the Architect promotes — no auto-ingest (sprint-specific: D4)
- ❌ Adversarial pair NOT used for routine reduction (sprint-specific: cost, Notes L.3)
- ❌ No opportunistic refactoring

### Output location
- Orchestration: a W2 skill/workflow + the reduction subagent definition (`.claude/…`)
- Code: minimal glue; judgment in subagent prompts
- Tests: a real-seed-set breadth-map check (HSC #4)
- Docs: deferred to seal.

---

## Sprint L.4: (Optional) HTML panel render 🟢

**Friction reference:** none — optional display; absorbs retired Phase R R.4 intent (view surface).

**Predecessor assumptions:** L.3b produces a W2 map artifact — renders it. Independent otherwise.

**Risk level:** 🟢 LOW (write-only; a self-contained HTML file; no criteria, no judgment).

### Objective
Render a W2 breadth map to a self-contained local HTML file the Architect can open in a browser — display-only.

### Design points (audit-derived)
- CLI has no native browser-open — the tool writes the `.html`; the Architect opens it (Desktop app can
  click-to-open) — audit ref: `L.0.md` F3.
- Display-only: the panel NEVER carries criteria or judgment (phase-wide red line). It reads the existing map artifact.

### Task scope
1. A render step: W2 map artifact → a self-contained `.html` (inline CSS; no external fetch) written to disk.

### Acceptance
- Running the render on a W2 map produces an `.html` that opens in a browser and shows the classified map.
- The HTML carries no criteria and no judgment — pure display of existing map data.

### Red lines
- ❌ Display-only — no criteria, no judgment in the panel (phase-wide)
- ❌ Self-contained HTML (no external fetch) (sprint-specific)
- ❌ No opportunistic refactoring

### Output location
- Code: a render helper + (optional) a thin invocation
- Output: an `.html` file on disk

---

## Phase-wide Red Lines

Violation in any sprint halts the batch:

- ❌ **Judgment in Claude subagents, not deepseek** — no `generate_structured_data` in the W1/W2 path (audit E1/E2).
- ❌ **Criteria live in the vault matrix** (`type/`, `field/`, `disposition/`), never in repo/code/skill.
- ❌ **Disposition-correction precedes role** — every judgment subagent loads `disposition/{role}.md` before its role.
- ❌ **W1/W2 are main-agent orchestration, not MCP tools** — MCP provides only primitives (fetch/convert/read/
  load_criteria/write_result); judgment never lives in an MCP tool.
- ❌ **Verbatim grounding mandatory (W1)** — no [V]/[P]/[U] tag without a verbatim quote + location.
- ❌ **Harness records raw verifiable structure, never baked interpretation (Phase K forward-compat)** — verdicts
  carry the `depends_on` dependency structure (C1), W1 stops at "is it supported?" not "what it means" (C2), W2
  stores number+verbatim not single-framing conclusions (C3). Interpretation/framing is Phase K's job (K-gate-1
  monotonicity / K-gate-2 framing); baking it in forces a rewrite.
- ❌ **Bounded BFS (W2)** — hard depth + paper caps; no unbounded crawl; no silent truncation.
- ❌ **HTML panel display-only** — never carries criteria or judgment.
- ❌ **No new dependency, no new server** — `.mcp.json` stays 2; reuse arxiv fetch / MinerU / StagingService /
  vault adapter / Phase Q supersede.
- ❌ **Thin adapter** — new tool bodies stay lazy-import dispatchers; lifecycle logic in domain modules (mind O.seal.1).
- ❌ **No opportunistic refactoring.**

---

## Hard Sealing Conditions (carried from phase doc)

MUST Pass at phase_review:

1. **HSC 1 — criteria are vault-dynamic (L.1a):** editing `criteria/type/benchmark.md` in Obsidian changes W1's
   verdict on the next run, zero git — verified by the add-criterion-then-rerun check; both capability AND
   disposition axes are vault-editable.
2. **HSC 2 — verbatim-grounded verdicts (L.2c):** [V]/[P]/[U] each backed by a verbatim quote + location, ≥3
   claims / ≥2 types, no fabricated [V] — verified on real claims.
3. **HSC 3 — judgment is subagent-borne (arch):** zero deepseek in the W1/W2 path; paper text stays in the
   subagent — verified by path inspection + audit E1/E2.
4. **HSC 4 — breadth map with numbers (L.3b):** ≥3 seeds → ≥20 papers (bounded), gap + number each, ≥3 subfields —
   verified on a real seed set.
5. **HSC 5 — the VISION gate (Architect):** after W1+W2 on a real direction, the Architect confirms the output is
   semi-proposal-grade survey material — assessed on real use, not a fixture.

**Forward-compat check (not a seal gate, but verify at review):** the harness artifacts carry raw structure —
W1 verdicts include `depends_on` (C1) and no baked framing (C2); W2 rows carry number+verbatim and no
single-framing conclusion (C3) — so Phase K (K-gate-1/K-gate-2) can layer on without a rewrite.

---

## Approval

User approves the whole sequence or rejects the whole sequence.

Upon approval, hand off to `chimera-code-taste`:
> "Execute batch for Phase L per `docs/plans/Phase-L-batch.md`."

Gate notes: **L.2b / L.2c / L.3b are 🔴** — gate their execution explicitly even after batch approval.
**Resolve OPEN DECISION #9 (`write_result` target) before L.2b.** **L.3 executes only after L.2c's prove-value
gate** (Architect confirms W1 is worth automating W2 — the GPT directive).

---

*Generated by chimera-sprint-discipline batch_planning mode.*
