# Phase Audit: Phase L — Locus: The Research Harness

**Scope:** Read-only audit prerequisite for batch_planning of Phase L (sprints L.1–L.4).
**Output location:** `docs/audits/L.0.md` (named for the L.0 sprint that authors it).
**Date:** 2026-07-16
**Mode:** Read-only w.r.t. source — no fix proposals, no code modifications. The one write is this report.
**Method:** Direct full reads of the death-order-critical files (vault adapter, staging, config) + four
fan-out scouts: one `claude-code-guide` pass (official Task docs, Area A), one **live subagent probe**
(empirical A1), two Haiku repo scouts (fetch/convert/citation; deepseek-judgment/taxonomy). Area A was
verified empirically per the phase's own directive ("Do NOT assume from this spec — verify against the
harness").

---

## Files read

| Path | Lines | Notes |
|---|---|---|
| `mcp-servers/chimera-papers/ports/vault/vault_read_adapter.py` | 598 | full read (B1) |
| `mcp-servers/chimera-papers/staging_service.py` | 235 | full read (F2) |
| `mcp-servers/chimera-vault/server.py` | 226 | full read (primitive surface) |
| `mcp-servers/chimera-papers/server.py` | 164 | full read (primitive surface) |
| `.mcp.json` | 19 | full read (F1) |
| `pyproject.toml` | 60 | full read (F1) |
| `mcp-servers/chimera-papers/single_paper_ingest.py` | scout | D1/D2/E2 |
| `mcp-servers/chimera-papers/single_paper_extract.py` | scout | D3/E1/E2 |
| `mcp-servers/chimera-papers/ports/ingest/paper2md.py` | scout | D2 |
| `mcp-servers/chimera-papers/grounding.py` | scout | D3 |
| `mcp-servers/chimera-papers/filter_service.py` | scout | E1/E2 |
| `mcp-servers/chimera-papers/optics_service.py` | scout | E1/E2 |
| `mcp-servers/chimera-papers/optics_lens_registry.py` | scout | C1 |
| `mcp-servers/chimera-papers/core/schemas.py` | scout | C1 |
| `mcp-servers/chimera-papers/batch_filter_workflow.py` | scout | E2 |
| Claude Code docs: `sub-agents.md`, `agents.md`, `costs.md`, `desktop.md` | — | A1–A4, F3 |
| Live subagent probe (empirical) | — | A1 |

---

## Findings

| Q# | Driving sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| **A1** | arch / L.2–L.3 | Can a Task subagent call the MCP tools? | **YES.** MCP tools are inherited by subagents by default; scopable via `mcpServers`/`tools` frontmatter. Live probe called `mcp__chimera-vault__vault_query` → 108 real knowledge nodes. **Nuance:** tools arrive *deferred* in a subagent — the worker must `ToolSearch`-load the schema before the first call. | docs `sub-agents.md#available-tools`; live probe (vault_query→108 hits) | Low |
| **A2** | L.3 | Max concurrent subagents / result return? | **No documented hard cap.** Docs warn cost/context scales with team size; no published max or Max-plan rate limit. (For reference, the Workflow harness caps concurrent agents at `min(16, cpu-2)`.) Bound must be self-imposed. | docs `agents.md`, `costs.md` (no limit stated) | Med |
| **A3** | arch (HSC #3) | Context-isolation guarantee? | **PASS by construction.** Subagents return **only a summary**, run in their **own context window**, and intermediate context **does not leak to the parent**. Exactly HSC #3 — the paper text stays in the worker; only the verdict + quotes return. | docs `sub-agents.md` ("returns only the summary"; "own context window") | Low |
| **A4** | L.3 | Cost/parallelism budget for 40–60 workers? | Each subagent bills tokens independently; cost ≈ proportional to team size ("keep teams small"). 40–60 fan-out **not documented**; no explicit Max rate-limit. Affordable but must be bounded + keep worker returns tiny. | docs `costs.md#agent-team-token-costs` | Med |
| **B1** | L.1 | Can an MCP primitive read `<vault_root>/criteria/{type}.md`? | **YES, zero code change.** `_resolve_path_within_vault` enforces *only* "stays inside `vault_root`" — no subfolder allowlist. `read_vault_file("criteria/x.md")` reads it (file must exist; L.1 creates the dir). The `.obsidian/templates` exclusions apply to search/graph, NOT `read_file`. | `vault_read_adapter.py:181-220`, `:206-220`; exclusions `:24-25,236,288,420` | Low |
| **B2** | L.1 | Can a subagent receive the criteria content? | **YES.** A worker either calls `read_vault_file("criteria/{type}.md")` itself (inherited tool, per A1) or gets it injected in the spawn prompt (per A3). | A1 + A3 | Low |
| **C1** | L.1 | Existing paper-TYPE taxonomy / classifier? | **No type→criteria classifier exists — must be built.** Static `SourceType` (`arxiv_paper`/…) is a *source* type, not a research type, and is set at load, not inferred. The reusable taxonomy is the **lens registry**: `math_arch`, `eval_rigor`, `memory_physics`, `survey_taxonomy`, `survey_consensus`, `survey_gaps` — the natural source for `{type}` filenames. Lens selection is LLM-judged by "paper FUNCTION"; survey/non-survey is a metadata binary, not inferred. | `core/schemas.py:13-15`; `optics_lens_registry.py:84-169`; `optics_service.py:166` | Med |
| **D1** | L.2 | Fetch by arXiv id without writing a node? | Fetch exists (`_fetch_arxiv_pdf`) but **no bare-fetch path** — only reached via `ingest_single_paper`, which always writes a K node. W1 needs a fetch that stops at the PDF. Small build (separate the concern). | `single_paper_ingest.py:34-59` (fetch), `:87` (ingest-only caller), `:111` (node write) | Med |
| **D2** | L.2 | Standalone PDF→md convert, no node? | **YES — exists and is live.** `MineruClient.convert(pdf_path)` is stateless, returns an `.md` path, writes no node. The retired R.1 "convert_pdf_to_md" is a **thin wrapper over existing logic**, not new work. | `ports/ingest/paper2md.py:56-159` | Low |
| **D3** | L.2 | Reference/citation extraction? | **Regex-only, vault-bound.** `_cited_arxiv_ids` scans markdown for bare `\d{4}.\d{4,5}` arXiv IDs; `grounding.resolve_citations` matches those to *existing vault stems* (never fabricates). No References-section / DOI / author-year parsing; new-paper fetch+convert in the *extract* path is explicitly deferred. W1's "claim → its cited papers" likely needs real reference parsing. | `single_paper_extract.py:43-52`; `grounding.py:67-113`; `single_paper_extract.py:206-209` | Med-High |
| **E1** | arch (red line) | Catalog every `generate_structured_data` judgment call. | **Three sites:** (1) `filter_service.py:45` — ingest triage verdict/score (`reviewer_zero.j2`→`PaperAnalysisResult`); (2) `optics_service.py:134` — lens/optics analysis (async); (3) `single_paper_extract.py:186` — K-node extraction (`extract_node.j2`→`KNodeExtraction`). | `filter_service.py:45`, `optics_service.py:134`, `single_paper_extract.py:186` | Low |
| **E2** | arch (red line) | Which flow reaches each deepseek call? | (1) triage → `ingest_paper` **and** `daily_paper_pipeline`; (2) optics → **unreached** by any tool flow (only `run_lens_cli`; ingest explicitly disclaims it — retired oligo deep-read); (3) extract → `extract_paper` (Phase Q, sealed). **None sits in the future W1/W2 path.** | `single_paper_ingest.py:107` (+`:8-9` disclaimer), `batch_filter_workflow.py:150,204`, `miner_tools.py:140`, `optics_service.py:232` | Low |
| **F1** | cross | Reuse targets exist, no new dep / no 3rd server? | **PASS.** `.mcp.json` = exactly two servers. `pyproject.toml` already has arxiv fetch (`requests`), MinerU (`mineru[core]`+cu128 torch), the deepseek client (`openai`); StagingService + vault adapter are in-repo. | `.mcp.json:2-17`; `pyproject.toml:6-31` | Low |
| **F2** | L.2/L.3 | Output sink for verdicts / breadth map? | **No generic result writer — must be built.** `StagingService` writes only K/T/I/D nodes + link patches. `create_staging_node` has a `metadata` passthrough (`:66`) that could carry a verdict, but a proper `write_result` primitive (the L red-line list already names it) is a build item. | `staging_service.py:12,55-102`; `create_staging_node` metadata `:66-67` | Med |
| **F3** | L.4 | Can Claude Code open a local HTML file? | **CLI: no native open** — the agent writes the `.html` and the user opens it (Desktop app can click-to-open a path). Confirms L.4 "display-only, write-to-disk"; the panel is a trivial file write. | docs `desktop.md#preview-your-app` | Low |

---

## Cross-references discovered

- **`read_file` vs. search exclusions**: the vault adapter's non-vault dir exclusion set
  (`_NONVAULT_DIRS = {.obsidian, .migration_backup, templates}`, `vault_read_adapter.py:25`) gates
  `resolve_note_path` / graph traversal / ripper search — but **not** `read_file`. So `criteria/` is
  freely readable while staying invisible to graph queries. Evidence: `vault_read_adapter.py:181-220`
  (read path, no allowlist) vs. `:420`, `:236`, `:288` (exclusions in resolve/search only).
- **Lens taxonomy ↔ criteria filenames**: `optics_lens_registry.py:84-169` already enumerates six
  functional classes (`math_arch`, `eval_rigor`, `memory_physics`, `survey_taxonomy`,
  `survey_consensus`, `survey_gaps`) that mirror the six `chimera-lens-*` skills. This is the natural,
  already-ratified vocabulary for L.1's `criteria/{type}.md` filenames — unifying W1/W2 criteria with
  the existing lens system instead of inventing a parallel type set.
- **Grounding never fabricates**: `grounding.resolve_citations` returns an edge only on a real vault-stem
  match, else `continue` (`grounding.py:67-113`). The same "no fabrication" discipline W1's verbatim red
  line demands already exists on the extract side — reusable precedent.

---

## Notable cross-findings (no fix proposals — flagging for planning)

1. **W1's build surface is three small primitives, not a rewrite.** L.2 (W1) needs exactly:
   (a) a **bare fetch** (split `_fetch_arxiv_pdf` from the node-write, D1), (b) a **thin `convert_pdf_to_md`**
   wrapper over the already-live `MineruClient.convert` (D2), and (c) a **`write_result`** sink for
   [V]/[P]/[U]+quotes (F2). Convert is essentially free; fetch-split and result-sink are small.
   Evidence: `single_paper_ingest.py:34-59,87,111`; `paper2md.py:56-159`; `staging_service.py:55-102`.

2. **Citation resolution is W1's real risk (D3), and it's not a harness problem.** "Claim → its cited
   papers" currently works only for papers cited by *bare arXiv id* AND *already in the vault*. A claim
   backed by a DOI/author-year citation, or by a paper not yet ingested, will not resolve. This is the
   quiet second boss (mirrors the Phase R audit's F4 shape: a mechanism can *fire* yet surface nothing).
   Batch planning must decide W1's citation-input contract: bare-id only (cheap, incomplete) vs. a real
   References-section parser (a MinerU-markdown post-processor). Evidence: `single_paper_extract.py:43-52`.

3. **The subagent-primacy red line is satisfiable by construction.** The W1/W2 judgment path is
   greenfield — it does not exist yet, so it starts with zero deepseek calls. All three existing
   `generate_structured_data` sites are outside it: extract (sealed, out of L scope), triage (a separate
   ingest concern), optics (retired/CLI-only, unreached). As long as the new primitives L adds
   (fetch/convert/read/load-criteria/write) carry **no LLM call**, HSC #3 holds. Evidence: E1/E2.

4. **`friction-260710-01` (triage tunability) — scope decision for batch planning.** Phase L frames
   vault-criteria as "the strictly better realization" of the untunable-triage friction. But the audit
   shows the *runtime* triage judgment (`filter_service.py:45`, deepseek) is in the `ingest_paper` /
   `daily_paper_pipeline` flow, **not** the W1/W2 path. L.1's vault-criteria mechanism serves W1/W2
   classification; whether it *also* rewires the ingest triage prompt to read `vault/criteria/` is a
   distinct decision. Recommend: keep L scoped to W1/W2 criteria; treat triage-criteria migration as a
   follow-on, or explicitly widen L.1 if the Architect wants both. Evidence: `filter_service.py:45`,
   `single_paper_ingest.py:107`, `batch_filter_workflow.py:150,204`.

5. **Concurrency/cost are undocumented ceilings → self-bounding is mandatory, and already planned.**
   A2/A4 returned "not documented." This does not block L; it *validates* the existing L.3 red lines
   (hard depth cap + hard paper cap) and W2's design (each worker returns one gap sentence + one number —
   tiny returns keep parent context and token cost bounded). Plan W2 in bounded waves, not one 60-wide
   blast. Evidence: docs `agents.md`, `costs.md`.

6. **Subagent MCP tools are deferred — W1/W2 spawn prompts must say so.** The live probe confirmed a
   worker must `ToolSearch`-load an `mcp__*` schema before its first call. Any custom agent type L defines
   for W1/W2 workers should either pre-declare the needed MCP tools in `mcpServers`/`tools` frontmatter or
   instruct the worker to load them first. Evidence: live probe (deferred-then-loaded, then 108 hits).

---

## Red-line precondition check (verified this audit)

- ✅ **`.mcp.json` stays two servers** — verified `.mcp.json:2-17`.
- ✅ **No new dependency needed** — arxiv fetch / MinerU / openai(deepseek) / staging / vault adapter all
  present, `pyproject.toml:6-31`.
- ✅ **Judgment can live in subagents, not deepseek** — W1/W2 path is greenfield; the 3 deepseek sites are
  all outside it (E1/E2).
- ✅ **Criteria can live in the vault, read at runtime** — `read_vault_file` reaches `criteria/{type}.md`
  with no code change (B1).
- ⚠️ **`write_result` / bare-fetch / citation-parser are net-new** — small, but they ARE code L must add
  (F2/D1/D3); the "reuse only" red line holds for convert/fetch-transport/staging but W1 needs thin new
  primitives on top.

---

## Audit complete

- 15 questions answered (A1–A4, B1–B2, C1, D1–D3, E1–E2, F1–F3)
- ~40 file:line references
- 3 cross-references
- 6 notable cross-findings + a red-line precondition check

**Death-order preconditions (the two the phase said MUST be confirmed): BOTH PASS.**
(1) A subagent can call MCP tools — A1, live-verified. (2) An MCP primitive can read
`vault/criteria/{type}.md` at runtime and a subagent can receive it — B1/B2. The architecture rests on
solid ground.

**Suggested next:** `batch_planning` for Phase L — starting with L.1 (criteria infra: reuse the lens
taxonomy for `{type}`; classification is a subagent step) and L.2 (W1: build the three thin primitives
+ resolve the citation-input contract from cross-finding #2).

---

*Generated by chimera-sprint-discipline phase_audit mode.*
