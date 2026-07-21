# Batch Plan: Phase L.B — Consolidation: Tier Integrity + Model Migration + Unified Ascension

**Output location:** `docs/plans/Phase-L.B-batch.md`
**Audit reference:** `docs/audits/workflow-drift-audit.md` (2026-07-20) — **VERIFIED against `phase-L` code this session** (every code claim's line numbers match live files; two corrections carried below).
**Phase doc:** `docs/phases/phase-L.B.md` (sparse manifest — distinct from this batch plan)
**Driving frictions:** C-1 (CRITICAL — tier indistinguishable), H-1 (HIGH — deepseek judgment), H-2/H-3 (HIGH — no single deep-read path; `ingest_paper` over-promises), Structural (no living architecture diagram). All audit-declared (workflow-drift-audit.md).

This document is a single unit. The user approves the whole sequence or rejects the whole sequence. After approval, hand off to `chimera-code-taste` batch_execution mode. **L.B.1 is the load-bearing sprint and must seal before L.B.2/L.B.3 begin.**

---

## Settled design decisions (locked in phase-L.B.md) + verified audit facts

| # | Decision | Effect on plan |
|---|---|---|
| **D1** | **`chimera_tier`, not status alone, is the tier marker.** Status = lifecycle (`unverified`/`PENDING_REVIEW` → `active`); tier = origin/depth (`scout` / `deep_read` / `harness_candidate`). Orthogonal axes. | L.B.1 adds a NEW frontmatter field across every write path + templates; it does not overload `status`. |
| **D2** | **Haiku for triage, Sonnet for synthesis, subagents for judgment.** deepseek retired as a judgment engine (may remain for cheap data extraction only). | L.B.2 routes `filter_service` → Haiku, `single_paper_extract` → Sonnet. Because both share one config slot today (fact F1), this is a config-slot SPLIT, not a string swap. |
| **D3** | **`ascend_node` is the single ascension gate.** All promotion into `Knowledge/` goes through one code path; a direct `Knowledge/` write is impossible by code constraint. | L.B.3 builds `ascend_node` on the existing `promote_node` seed; `Knowledge/` is a new committed-tier folder with `ascend_node` as its sole writer. |
| **D4** | **L.B.6 is verify+rebuild, not test-then-seal.** Reserve in-sprint time to fix any failing path before seal. | L.B.6 scope explicitly includes fix-in-sprint; a silent path failure blocks the seal. |
| **D5** | **The architecture diagram is a first-class, code-generated artifact.** Regenerated at every phase seal; describes what the code does, never aspiration. | L.B.5 is a generator script + its committed output, not a hand-drawn picture. |

### Verified audit facts (the recon this batch rests on)

| # | Fact | Evidence (file:line — `D:/MAS/chimera-lite`) |
|---|---|---|
| **F1** | **The judgment model is config-resolved, NOT hardcoded, and both Path-1/Path-2 judgment calls share ONE slot.** `build_openai_client(settings)` → `OpenAICompatibleClient(model=settings.default_llm_model, base_url=…)`; `default_llm_model` = `llm.working.model`. | `bootstrap.py:108-125`; `config.py:472-474`; call sites `filter_service.py:45`, `single_paper_extract.py:186,257-260` |
| **F2** | **Live working model = `deepseek-v4-pro`** (audit said `deepseek-chat`; that is only the code fallback at `config.py:182,222,230`). An **anthropic slot exists but is stale/unused**: `claude-3-5-sonnet-20241022`. | `~/.chimera/config.toml [llm.working]`; `config.py:174,182,190,222,230,643` |
| **F3** | **All three K writers emit `type: knowledge`** — tier is indistinguishable by `type`. | `prompts/obsidian_tpl/knowledge_node.j2:2` (daily+ingest); `single_paper_extract.py:288`; `staging_service.py:88` |
| **F4** | **Status machinery already partially exists.** Inbox cards' `status: unverified` is inert; the STAGING path already writes `PENDING_REVIEW` and transitions to `active` on promotion. The real C-1 gap = uniform `type` + inert *inbox* status, not total absence of transitions. | inbox `knowledge_node.j2:3`; staging `staging_service.py:89`; transition `staging_service.py:110` (`promote_node`) |
| **F5** | **`ingest_paper` + `daily_pipeline` write DIRECTLY to `inbox/<verdict>/`, bypassing `docs/staging/`.** No path writes to `Knowledge/` today (only `inbox/` and `Harness/` are non-staging in-vault writes). | `vault_note_writer.py:24,40,43`; Q6.1 `create_node`/`extract_paper` → `docs/staging/`; Harness `result_service.py:136` |
| **F6** | **`vault_query` already filters by ANY `type` string (no allowlist); `search_vault`/`search_vault_attribute` have NO type filter (body/attr only).** | `vault_query.py:70-71` (`if type and fm.get("type") != type: continue`); `vault_read_adapter.py:425-430,432-443`; graph filter `:518-521` |
| **F7** | **`chimera_tier` appears nowhere in the repo** — clean net-new field. | grep: 0 hits repo-wide |
| **F8** | **The "four-path model" is the audit's own synthesis** — there is no `CLAUDE.md § Knowledge Ingestion Paths` (never existed per `git log -S`); `THEORETICAL_FRAMEWORK.md` describes the manifold bifurcation but does not enumerate a named four-path model. | `CLAUDE.md` headings; `git log -S "Ingestion Path"` empty; `THEORETICAL_FRAMEWORK.md:222` |
| **F9** | **`_resolve_markdown` raises `FileNotFoundError`; `extract_paper` needs pre-converted markdown (no MinerU in-path); the deep-read chain lives in two docstrings.** Intersects DEBT-016. | `single_paper_extract.py:196-209`; chain `single_paper_ingest.py:8-9` + `server.py:117` |

### Planner reconciliation (read before approving)

1. **Audit core claims CONFIRMED against live `phase-L` code** — C-1 (uniform `type: knowledge`, F3), H-1 (deepseek judgment on Paths 1-2, F1/F2), H-2/H-3 (`ingest_paper` over-promises + no single deep-read path, F9), all four entry points exist, no auto-promotion. The batch may build on the audit.
2. **L.B.2 is bigger than a string swap (F1/F2).** The model is config-resolved and both judgment paths share the ONE `llm.working` slot. Giving `filter_service` Haiku and `single_paper_extract` Sonnet needs (a) two new config slots (or repurpose the stale anthropic slot), (b) per-call-site client construction in `bootstrap.py`, and (c) an Anthropic API base_url/key path (today the client points at deepseek's OpenAI-compatible endpoint). **→ split L.B.2 into L.B.2a (config slots + client path) and L.B.2b (wire call sites + docstring).**
3. **L.B.1 EXTENDS existing status machinery, does not rebuild it (F4).** The staging `PENDING_REVIEW → active` path stays; L.B.1 adds the orthogonal `chimera_tier` axis and closes the inert-*inbox*-status gap. Do not touch the staging transition logic beyond adding the tier field.
4. **L.B.1's query fix is lighter than the phase-doc phrasing implies (F6).** `vault_query` already returns any `type` — so HSC "vault_query with `type=thought` returns T nodes" holds today *if T nodes exist*. The real deliverables are: (a) the vault-tool contract docstrings must advertise `thought`/`insight` as valid `type` args, and (b) `vault_query` rows must carry `chimera_tier` (this is the L.B.4 return-field work; keep it there, don't duplicate in L.B.1). `search_vault` gaining a type filter is out of scope unless a friction demands it.
5. **`ascend_node` "impossible by code constraint" is structural, and `Knowledge/` is NEW (F5).** No writer targets `Knowledge/` today, so making `ascend_node` its sole writer is enforceable: L.B.3 introduces `Knowledge/` and a test asserts no other code path writes it. The Cross-Sprint red line "scout tier (`inbox/`) stays as-is, NOT auto-promoted" means `ingest_paper`/`daily_pipeline` KEEP writing scout cards to `inbox/` — `ascend_node` governs only the `inbox|staging → Knowledge/` gate.
6. **`ascend_node` is the structural backstop DEBT-018 lacks.** DEBT-018 (grounding-by-quote unverified; human staging-review is the ONLY check) is exactly the "advisory rigor" risk; `ascend_node`'s validation makes "human commits truth" a code constraint. L.B.3's validation SHOULD substring-verify grounding (or explicitly defer to DEBT-018's fix) rather than pass blindly.
7. **L.B.5's diagram is the first canonical four-path statement (F8).** Since the model is nowhere asserted canonically, the generated diagram becomes ground truth. Consider (sprint-internal) whether a pointer belongs in `CLAUDE.md`/`THEORETICAL_FRAMEWORK.md` — but the diagram is generated, not the prose.
8. **Thin-adapter watch (O.seal.1).** `chimera-vault/server.py` was 225 lines at O.seal.1 and has grown (tool inventory now spans to `:255`). `ascend_node` (L.B.3) grows it further — new tool body stays a lazy-import dispatcher; ascension logic lives in a domain module (`result_service.py`/`staging_service.py` or a new `ascend_service.py`). Consider the O.seal.1 follow-up (move write tools to `write_tools.py`) if it bloats.
9. **No reopening Phase Q judgment beyond what L.B.2 states.** L.B.2 migrates the `filter`/`extract` judgment models — this DOES touch `single_paper_extract.py`, which Phase Q sealed. That is in-scope for L.B by explicit phase intent (H-1). Grounding-verification (DEBT-018) and `_resolve_markdown`/backfill (DEBT-016/017, F9) are NOT reopened here unless L.B.6 surfaces them as a path failure.

---

## Sprint Sequence

```
L.B.0  workflow-drift audit                    ✅ DONE (docs/audits/workflow-drift-audit.md)
   │
   ▼
L.B.1  chimera_tier + status vocabulary  🔴  ◄── LOAD-BEARING — must seal before L.B.2/L.B.3
   │
   ├─────────────────────────────┬───────────────────────────────┐
   ▼                             ▼                                 │
L.B.2a config slots + client   L.B.3  ascend_node + unified     (parallel-eligible
L.B.2b wire filter→Haiku,             write path            🔴    after L.B.1)
       extract→Sonnet + docstring 🟡
   │                             │
   └─────────────┬───────────────┘
                 ▼
L.B.4  K-node lifecycle integration 🟡  ──┐
L.B.5  living architecture diagram  🟡  ──┤ (L.B.5 runs concurrently with L.B.4)
                 │                         │
                 ▼ (requires L.B.1-L.B.4) ─┘
L.B.6  Verify + Rebuild (test-fix-confirm) 🔴
                 ▼
seal (chimera-sprint-discipline phase_review + regenerate the L.B.5 diagram)
```

- **L.B.1 precedes all.** L.B.2 (a/b) and L.B.3 are **parallel-eligible after L.B.1** (different files: L.B.2 = config/bootstrap/filter/extract; L.B.3 = vault write surface). L.B.4 needs L.B.1 (tier field) + L.B.3 (`ascend_node` for the e2e). **L.B.5 runs concurrently with L.B.4.** **L.B.6 requires L.B.1-L.B.4 complete.**
- **Split analysis (process step 3):** phase-doc **L.B.2** → **L.B.2a** (config slots + Anthropic client path) + **L.B.2b** (wire the two call sites + fix `ingest_paper` docstring) — the config split is the design-bearing half; wiring is mechanical. All other phase-doc sprints map 1:1. No expansion beyond the phase manifest.

---

## Sprint L.B.1: `chimera_tier` field + status vocabulary 🔴

**Friction reference:** C-1 (CRITICAL — scout vs deep_read tiers indistinguishable).

**Predecessor assumptions:** None — independent. **Produces** the tier field + status-transition vocabulary that every later sprint depends on (this is why it is load-bearing).

**Risk level:** 🔴 HIGH (touches the schema authority + every write path + all node templates + the query contract — >3 files).

### Objective
Add an orthogonal `chimera_tier` frontmatter field ∈ `{scout, deep_read, harness_candidate}` to the node schema, all write paths, and all templates, and codify the `status` lifecycle — so a scout-tier triage card and a deep_read node are machine-distinguishable in the vault.

### Design points (audit-derived)
- `chimera_tier` is a NEW field, orthogonal to `status` (D1) — F7 confirms it exists nowhere, so no migration collision.
- EXTEND, do not rebuild, status machinery (F4): the staging `PENDING_REVIEW → active` path stays (`staging_service.py:89,110`); the gap is the inert **inbox** `status` (`knowledge_node.j2:3`) + the uniform `type: knowledge` (F3).
- Tier assignment by writer: `ingest_paper`/`daily_pipeline` inbox cards → `scout`; `extract_paper` staging → `deep_read`; W1/W2 harness artifacts → `harness_candidate` (or leave harness `kind`-keyed and document the mapping — decide in-sprint, cite it).
- Schema authority is `docs/ARCHITECTURE/NODE_ONTOLOGY.md` (129 lines) — the tier axis + status lifecycle table land here.
- Query contract (F6): `vault_query` already accepts any `type`; this sprint only ensures the vault-tool docstrings advertise `thought`/`insight` as valid `type` args. Returning `chimera_tier` in rows is L.B.4 (reconciliation #4) — do NOT duplicate here.

### Task scope
1. `docs/ARCHITECTURE/NODE_ONTOLOGY.md` — add the `chimera_tier` axis {scout/deep_read/harness_candidate} + a status-lifecycle table (orthogonal axes; ~20 lines).
2. `prompts/obsidian_tpl/knowledge_node.j2:2-17` — add `chimera_tier: scout` (inbox/ingest/daily card).
3. `prompts/obsidian_tpl/{thought,insight,decision,deep_read,deep_read_survey}_node.j2` — add the `chimera_tier` field.
4. `staging_service.py:61-102` (`create_staging_node`) — accept + write `chimera_tier` (caller supplies; ~6 lines).
5. `single_paper_extract.py:280-288` — pass `chimera_tier=deep_read`.
6. Vault-tool contract docstrings (`chimera-vault/server.py` `vault_query`/`search_vault_attribute`) — advertise `thought`/`insight` as valid `type` values (docstring only, F6).

### Acceptance
- A scout K node (from `ingest_paper`) and a deep_read K node (from `extract_paper`) differ by `chimera_tier` in frontmatter — verifiable by reading two produced nodes.
- **HSC #1 live:** `vault_query(type="thought")` returns T nodes (holds via F6 once a T node exists — verify against the live vault).
- `NODE_ONTOLOGY.md` documents the `chimera_tier` axis + status lifecycle; the inert-inbox-status gap is closed or explicitly deferred with a reason.

### Red lines
- ❌ `chimera_tier` lives in frontmatter only, never baked into the body (sprint-specific)
- ❌ EXTEND the existing `PENDING_REVIEW → active` machinery — do not rebuild it (sprint-specific: F4)
- ❌ Do not overload `status` to carry tier — the axes stay orthogonal (phase-wide: D1)
- ❌ Thin adapter — no query/tier logic in `server.py` (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-papers/staging_service.py`, `mcp-servers/chimera-papers/single_paper_extract.py`, `prompts/obsidian_tpl/*.j2`, `mcp-servers/chimera-vault/server.py` (docstrings)
- Architecture: `docs/ARCHITECTURE/NODE_ONTOLOGY.md`
- Tests: `tests/test_chimera_tier.py` (a scout write and a deep_read write differ by tier)
- Docs: deferred to seal

---

## Sprint L.B.2a: Model config slots + Anthropic client path 🟡

**Friction reference:** H-1 (deepseek judgment where ST specifies Claude).

**Predecessor assumptions:** L.B.1 sealed. Independent of L.B.3.

**Risk level:** 🟡 MED (config surface + one client path; design-bearing because it splits the single working slot).

### Objective
Add distinct Haiku and Sonnet judgment slots to the config and a client-construction path that can target the Anthropic API — so downstream call sites can select different models per role instead of sharing the one `llm.working` slot.

### Design points (audit-derived)
- Today one slot feeds both judgment calls (F1): `build_openai_client(settings)` → `default_llm_model` = `llm.working.model` (`bootstrap.py:108-125`, `config.py:472-474`).
- A stale anthropic slot exists (`config.py:190` = `claude-3-5-sonnet-20241022`, F2) — repurpose or add fresh `haiku`/`sonnet` slots. **Use current-generation ids per the `claude-api` skill (Haiku 4.5 / Sonnet 5), not the stale `claude-3-5-*` string.**
- Anthropic uses a different base_url/key than deepseek's OpenAI-compatible endpoint — the client path must route Claude models to the Anthropic endpoint (or an OpenAI-compatible gateway if one is configured).
- No hardcoded model strings in judgment code — models stay config-resolved (the F1 pattern is preserved, just multi-slot).

### Task scope
1. `config.py:174-190` — add/curate `haiku` + `sonnet` judgment slots with current model ids (consult `claude-api` skill) + base_url/key (~15 lines).
2. `bootstrap.py:108-125` — a role-parameterized client builder (`build_client(role)` selecting the slot) alongside the existing `build_openai_client` (~15 lines); add the Anthropic endpoint path.

### Acceptance
- The config exposes resolvable `haiku` and `sonnet` slots with current ids; `bootstrap` can build a client for each.
- No behavior change at call sites yet (that is L.B.2b) — this sprint is the substrate.

### Red lines
- ❌ Models stay config-resolved — no hardcoded model string in judgment code (phase-wide)
- ❌ No new dependency; reuse the existing client stack / Anthropic SDK already available (phase-wide)
- ❌ Thin adapter — slot logic in config/bootstrap, not in tool bodies
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-papers/core/config.py`, `mcp-servers/chimera-papers/.../bootstrap.py`
- Tests: `tests/test_model_slots.py` (haiku/sonnet slots resolve)

---

## Sprint L.B.2b: Wire filter→Haiku, extract→Sonnet + fix `ingest_paper` docstring 🟡

**Friction reference:** H-1 (deepseek retired as judge); H-3 (`ingest_paper` over-promise).

**Predecessor assumptions:** L.B.2a slots exist with the planned `build_client(role)` signature — re-plan trigger if it differs.

**Risk level:** 🟡 MED (two call-site swaps + a docstring; mechanical once L.B.2a exists).

### Objective
Route `filter_service` (bulk triage classification/verdict) to Haiku and `single_paper_extract` (synthesis) to Sonnet, and correct the `ingest_paper` docstring so it stops claiming "Knowledge base"/"deep read" — it produces a scout-tier triage card.

### Design points (audit-derived)
- `filter_service.py:45` = classification/verdict → Haiku (cheap bulk). `single_paper_extract.py:186,257-260` = synthesis → Sonnet.
- deepseek MAY remain for cheap data extraction (e.g. citation parsing) but NOT for verdict/synthesis/classification — verify by grep after the swap.
- `ingest_paper` docstring (`server.py:106,110,111,117`) — replace "into my Knowledge base" / deep-read framing with "scout-tier triage card"; keep the separate-deep-read-step pointer honest (F9).

### Task scope
1. `filter_service.py:45` (+ its client construction via `batch_filter_workflow.py:120-122,189-190` / `daily_chimera_service.py:261`) — use the Haiku slot.
2. `single_paper_extract.py:186,257-260` — use the Sonnet slot.
3. `mcp-servers/chimera-papers/server.py:106-117` — rewrite the `ingest_paper` docstring (scout-tier triage card; no "Knowledge base"/"deep read").

### Acceptance
- **HSC #2:** `grep` shows no deepseek in the `filter`/`extract` JUDGMENT paths; `filter_service` uses Haiku, `single_paper_extract` uses Sonnet.
- `ingest_paper`'s docstring makes no "Knowledge base"/"deep read" claim.
- Existing filter/extract tests still pass with the new models (or are updated to assert the slot).

### Red lines
- ❌ deepseek retired as a JUDGMENT model (verdict/synthesis/classification); cheap data-extraction use only, if any (phase-wide)
- ❌ `ingest_paper` docstring: scout-tier triage card, never "Knowledge base"/"deep read" (phase-wide)
- ❌ No hardcoded model strings — use L.B.2a slots (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-papers/filter_service.py`, `.../single_paper_extract.py`, `.../server.py` (docstring), wiring in `batch_filter_workflow.py`/`daily_chimera_service.py`
- Tests: extend `tests/test_model_slots.py` / existing filter+extract tests

---

## Sprint L.B.3: `ascend_node` MCP tool + unified write path 🔴

**Friction reference:** C-1 (tier integrity); realizes D3 (single ascension gate); structural backstop for DEBT-018.

**Predecessor assumptions:** L.B.1 sealed (`chimera_tier=deep_read` exists to gate on) — re-plan trigger if the tier vocabulary differs.

**Risk level:** 🔴 HIGH (new committed-tier folder + new lifecycle tool + a code-enforced write constraint; touches the vault write surface).

### Objective
Add an `ascend_node` MCP tool (+ backing service) as the SOLE path into a new committed-tier `Knowledge/` folder: it validates `chimera_tier=deep_read` (+ status/grounding) and promotes; a direct file write to `Knowledge/` by any other code path is impossible by construction.

### Design points (audit-derived)
- Build on the existing `promote_node` seed (`staging_service.py:104-121`: staging → vault, `status:=active`) — `ascend_node` generalizes it with tier validation for the `Knowledge/` destination.
- `Knowledge/` is NEW (F5 — no writer targets it today), so "only `ascend_node` writes `Knowledge/`" is enforceable and testable from a clean baseline.
- Scout tier stays put (Cross-Sprint red line): `ingest_paper`/`daily_pipeline` keep writing `scout` cards to `inbox/<verdict>/` (`vault_note_writer.py:40`); `ascend_node` governs only `inbox|staging → Knowledge/`.
- Validation is the DEBT-018 backstop (reconciliation #6): substring-verify grounding quotes against source before ascension, or explicitly defer to DEBT-018 with a cited reason — do not pass blindly.
- Thin adapter (reconciliation #8): tool body in `server.py` stays a lazy-import dispatcher; ascension logic in a domain module.

### Task scope
1. An ascension service `ascend_node(identity|path)` — validate `chimera_tier=deep_read` + status + grounding, write to `Knowledge/`, record provenance/`supersedes` (~40 lines; reuse `promote_node`/`_unlink_superseded`).
2. Thin `ascend_node` `@mcp.tool` in `chimera-vault/server.py` (~15 lines) with a WHEN/WHAT/CONTRAST docstring.
3. A guard test asserting NO code path other than `ascend_node` writes under `Knowledge/`.

### Acceptance
- **HSC #3:** `ascend_node` promotes a `deep_read` node into `Knowledge/`; a non-deep_read tier is refused; a direct write to `Knowledge/` without `ascend_node` is impossible (test-asserted — no other writer targets it).
- Scout cards still land in `inbox/` and are NOT auto-promoted.

### Red lines
- ❌ `ascend_node` is the ONLY writer of `Knowledge/` — code-enforced, not convention (sprint-specific: D3, HSC #3)
- ❌ Only `chimera_tier=deep_read` ascends; scout stays in `inbox/`, never auto-promoted (phase-wide)
- ❌ Reuse the Phase Q supersede/promote path — no new supersede logic (phase-wide)
- ❌ Thin adapter — ascension logic in a domain module, not `server.py` (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-vault/server.py` + `ascend_service.py` (or extend `staging_service.py`)
- Tests: `tests/test_ascend_node.py` (deep_read promotes; scout refused; `Knowledge/` sole-writer guard)

---

## Sprint L.B.4: K-node lifecycle integration 🟡

**Friction reference:** H-2 (no single deep-read arc); C-1 (tier-aware retrieval).

**Predecessor assumptions:** L.B.1 (`chimera_tier` field) + L.B.3 (`ascend_node`) exist — re-plan trigger if either interface differs.

**Risk level:** 🟡 MED (a return-field addition + a completion hint; no new tool).

### Objective
Close the deep-read arc: `extract_paper` surfaces a W1 offer on completion, and `vault_query` returns `chimera_tier` in its rows so callers can filter by tier.

### Design points (audit-derived)
- MCP cannot spawn subagents (Phase Q B1) — so the "W1 offer" is a return-value hint (candidate claim(s) for W1) the calling agent/skill acts on; `extract_paper` does NOT auto-run W1 (W1 is explicitly invoked).
- `vault_query.py:70-71` returns rows post-filter — add `chimera_tier` to the emitted dict (reconciliation #4; this is where the query-tier work belongs, not L.B.1).

### Task scope
1. `single_paper_extract.py` — on completion, include a `w1_offer` hint (claim candidates) in the result (~10 lines).
2. `vault_query.py` — include `chimera_tier` in each result row (~5 lines).

### Acceptance
- `extract_paper`'s result surfaces a W1 offer (a hint, not an auto-run).
- `vault_query` rows carry `chimera_tier`; a caller can filter deep_read vs scout.

### Red lines
- ❌ `extract_paper` does NOT auto-run W1 — offer only; W1 stays explicitly invoked (sprint-specific)
- ❌ No deepseek in the offer/hint path (phase-wide)
- ❌ Thin adapter (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `mcp-servers/chimera-papers/single_paper_extract.py`, `mcp-servers/chimera-vault/vault_query.py`
- Tests: `tests/test_lifecycle_integration.py`

---

## Sprint L.B.5: Living architecture diagram (code-generated) 🟡

**Friction reference:** Structural (no living architecture diagram; phase complexity exceeds friction-driven management).

**Predecessor assumptions:** None hard — but generate AFTER L.B.2 so the diagram reflects the migrated model boundaries. Runs concurrently with L.B.4.

**Risk level:** 🟡 MED (a generator script + committed output; no runtime code path).

### Objective
Add a generator that introspects the codebase and emits a living architecture diagram marking the deepseek/sonnet/haiku/subagent boundaries and the four ingestion paths — a first-class artifact regenerated at every phase seal.

### Design points (audit-derived)
- Generated FROM code (red line: not hand-drawn, not aspirational): introspect the MCP tool inventory (`chimera-papers/server.py`, `chimera-vault/server.py` `@mcp.tool` lists), the model slots (L.B.2a), and the write paths (`vault_note_writer.py`, `staging_service.py`, `result_service.py`, `ascend_service.py`).
- This is the FIRST canonical statement of the four-path model (F8) — the generated artifact is ground truth; a prose pointer in `CLAUDE.md`/`THEORETICAL_FRAMEWORK.md` is optional and sprint-internal.
- Reuse the L.4 self-contained-artifact pattern (mermaid-in-markdown or a self-contained HTML) — no new dependency, no server.

### Task scope
1. `scripts/gen_architecture_diagram.py` — introspect tool inventory + model slots + write paths → emit the diagram artifact (~60 lines).
2. The generated artifact committed at `docs/ARCHITECTURE/ARCHITECTURE.md` (mermaid) or `.html`.
3. Document the seal-time regeneration step in the phase seal record.

### Acceptance
- **HSC #4:** the diagram exists, is generated from code, shows model boundaries (Haiku/Sonnet/subagent) + the four paths, and matches code reality on every item the drift audit flagged.
- Re-running the generator reproduces the artifact (deterministic; no manual edits).

### Red lines
- ❌ Code-generated, never hand-drawn; describes actual code, never aspiration (phase-wide: D5)
- ❌ No new dependency; self-contained artifact (phase-wide)
- ❌ No opportunistic refactoring

### Output location
- Code: `scripts/gen_architecture_diagram.py`
- Architecture: `docs/ARCHITECTURE/ARCHITECTURE.{md,html}` (committed, regenerated at seal)

---

## Sprint L.B.6: Verify + Rebuild (test-fix-confirm) 🔴

**Friction reference:** the VISION gate (D4) — end-to-end four-path integrity.

**Predecessor assumptions:** L.B.1-L.B.4 complete. This is a verify+rebuild sprint, NOT test-then-seal.

**Risk level:** 🔴 HIGH (full end-to-end on real papers; may require in-sprint fixes to any path).

### Objective
Run the full four-path model end-to-end on real papers in one session; if any path fails, fix it in-sprint before seal.

### Design points (audit-derived)
- Five checks, one session (HSC #5): `daily_pipeline` → a scout K node; `extract_paper` → a deep_read K node in staging; W1 on a real claim → a harness verdict; W2 on 3 seeds → a breadth map; `ascend_node` → a deep_read node promoted to `Knowledge/`.
- No silent failures (red line): silent wrong behavior (no error, wrong output) blocks the seal and is worse than an error.
- Fix-in-sprint discipline (D4): a failing path is repaired here, not deferred, before the seal.

### Task scope
1. Execute the five-path e2e on a real seed set (Architect-run where judgment is required).
2. For each failing path: root-cause + fix in-sprint (or log an incident if it is a clear-cut defect).
3. Record the run + outcomes in the phase seal record; regenerate the L.B.5 diagram.

### Acceptance
- **HSC #5:** all five paths run in one session with correct, non-silent outputs; `ascend_node` promotes a deep_read node to `Knowledge/`.
- Any path that failed was fixed in-sprint and re-confirmed.

### Red lines
- ❌ No seal if ANY of the four paths fails silently (phase-wide: D4)
- ❌ Fix in-sprint — do not defer a failing path past the seal (sprint-specific)
- ❌ No opportunistic refactoring

### Output location
- Docs: the phase seal record (`docs/sprints/phase-L.B/…`) + regenerated `docs/ARCHITECTURE/ARCHITECTURE.*`
- Code: in-sprint fixes as needed (scoped to the failing path)

---

## Phase-wide Red Lines

Violation in any sprint halts the batch:

- ❌ **Nothing enters `Knowledge/` without `chimera_tier=deep_read` + `ascend_node`.** No exceptions. The scout tier (`inbox/`) stays as-is — NOT auto-promoted.
- ❌ **deepseek is retired as a JUDGMENT model** (verdict/synthesis/classification). It may remain for cheap data extraction only.
- ❌ **`ingest_paper`'s docstring produces a "scout-tier triage card"** — never "Knowledge base" or "deep read".
- ❌ **L.B.6 does not seal if ANY of the four paths fails silently.** Silent wrong behavior is worse than an error.
- ❌ **The architecture diagram is code-generated, describing actual code** — not hand-drawn, not aspirational.
- ❌ **`chimera_tier` and `status` stay orthogonal** — tier is not folded into status.
- ❌ **Thin adapter** — new tool bodies are lazy-import dispatchers; logic in domain modules (mind O.seal.1).
- ❌ **No new dependency, no new server** — `.mcp.json` stays 2; reuse StagingService / vault adapter / Phase Q supersede / the existing client stack.
- ❌ **No opportunistic refactoring.**

---

## Hard Sealing Conditions (carried from phase doc)

MUST Pass at phase_review:

1. **(L.B.1)** A scout-tier K node and a deep_read-tier K node are machine-distinguishable: `chimera_tier` exists, status transitions are defined, and `vault_query` with `type=thought` returns T nodes.
2. **(L.B.2)** `filter_service` uses Haiku; `single_paper_extract` uses Sonnet. No deepseek call in either judgment path — verified by grep.
3. **(L.B.3)** `ascend_node` is the only path into `Knowledge/`. A direct file write to `Knowledge/` without `ascend_node` is impossible by code constraint.
4. **(L.B.5)** The architecture diagram exists, is generated from code, shows model boundaries (Haiku/Sonnet/subagent), and matches code reality on all drift-audit-flagged items. Generated at seal time, committed.
5. **(L.B.6 — the VISION gate)** Full end-to-end: `daily_pipeline` → scout K node; `extract_paper` → deep_read K node in staging; W1 on a real claim → harness verdict; W2 on 3 seeds → breadth map; `ascend_node` → deep_read node promoted to `Knowledge/`. All five in one session. No silent failures.

---

## Approval

The user approves the whole sequence or rejects the whole sequence.

Upon approval, hand off to `chimera-code-taste`:
> "Execute batch for Phase L.B per `docs/plans/Phase-L.B-batch.md`."

Gate notes: **L.B.1 must seal before L.B.2/L.B.3 begin** (load-bearing). **L.B.1 / L.B.3 / L.B.6 are 🔴** — gate their execution explicitly even after batch approval. L.B.2 (a/b) and L.B.3 are parallel-eligible after L.B.1; L.B.5 runs concurrently with L.B.4; L.B.6 requires L.B.1-L.B.4 complete.

---

*Generated by chimera-sprint-discipline batch_planning mode.*
