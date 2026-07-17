# Phase R — Vault-Aware Reasoning & Tooling Completion

> ⛔ **RETIRED / ABSORBED INTO PHASE L 2026-07-16.** Phase R was never batch-planned or sealed. Its
> intent is absorbed by **Phase L — Locus** (`docs/phases/phase-L.md`), the reverse-ordered successor:
> R.5 (reasoning consults the vault) is delivered as a byproduct of L's W1/W2 subagents consulting the
> vault (criteria + prior nodes) as normal operation; R.1/R.2 (`convert_pdf_to_md`, heuristic markdown
> cleaner) become L primitives; R.3 (tunable triage criteria) is superseded by L.1's vault-criteria
> mechanism — a strictly better realization of the same `friction-260710-01` ask. The harness-reality
> audit (`docs/audits/phase-R-harness-reality.md`) remains valid lineage — Phase L references its F4
> semantic-search gap (DEBT-019). **Everything below is retired intent / lineage.**

**Status:** ⛔ Retired / absorbed into Phase L (2026-07-16) — see `docs/phases/phase-L.md`
**Superseded status (pre-retirement):** Active
**Sealed predecessor:** Phase Q (ARA-Disciplined Knowledge Extraction — sealedwith post-seal incidents: shape rebuild, progress notifications, motivation/results
  synthesis fields)
**Driving frictions:**
- `friction-260709-01` face 2 (RECURRING) — reasoning does not consult the vault.Phase Q made the vault worth consulting (rich K nodes, typed edges, grounded claims).
  Phase R makes the vault reach the agent's reasoning — skill-directed in R.5;
  hook-injected in Phase S if that ceiling is too low.
- `friction-260710-01` real ask — `ingest_paper` verdict/score quality is poor;
  the triage criteria are not tunable for your domain("memory-benchmark → auto must_read" is impossible to configure).
- Tooling gaps noted post-Phase Q: no standalone PDF→markdown path, no structural
  markdown cleaner, no in-session vault graph shortcut.

## What Phase Q resolved (not in Phase R scope)

- ✅ Single-source canonical lens files (`prompts/lenses/*.md`) — done in Phase Q rebuild.
- ✅ Progress notifications on extract_paper / ingest_paper — done as post-seal incident.
- ✅ motivation + results fields in K node synthesis — done as post-seal incident.
- ✅ Six chimera-lens-* skills thinned to canonical pointers — done in Phase Q rebuild.
- ✅ convert_pdf_to_md as functionality — ingest_paper's MinerU path already handles this;
  a dedicated thin wrapper may still be added (see R.1) but is low priority.

## Mission

Vault content reaches the agent before it reasons — via skill-directed tool calling
(R.5). If insufficient, Phase S upgrades to hook-injected content. (No tier makes the
agent *volitionally* consult the vault; that ideal is not harness-enforceable — see
`docs/audits/phase-R-harness-reality.md` F3.)

Phase Q built rich K nodes and grounded typed edges. A vault of mechanism-level
claims and citation-derived relationships has zero value if the agent never walks
the graph during reasoning. Today, asking "what's the failure mode of MemGPT's
eviction?" yields a generic answer even though the vault holds a Thought node
stating "recency ≠ importance." Phase R closes this gap.

Secondary: complete the ingest toolchain gaps left open by Phase Q (tunable triage
criteria, structural markdown cleaning, vault browser shortcut).

This is an activation phase, not an extraction phase. The vault is built;
Phase R makes it legible to the agent's own reasoning process.

## Sprint Sequence

| Sprint | One-line goal | Status |
|---|---|---|
| R.0 | Audit: current academic-observe skill body, vault tool surface, what specific changes would force a lookup before reasoning about a paper/method | Pending |
| R.1 | convert_pdf_to_md MCP tool — standalone PDF→markdown, no vault write, reuses existing MinerU path | Pending |
| R.2 | clean_markdown_heuristic() — non-LLM structural cleaner (page numbers, repeated headers, sub-3-word orphan lines); reused by ingest and extract paths | Pending |
| R.3 | Tunable triage criteria — expose the judgment criteria in `prompts/triage_criteria.md` so domain-specific rules ("memory-benchmark → auto must_read") can be configured without code changes (the real fix for friction-260710-01) | Pending |
| R.4 | open_vault_in_browser MCP tool — returns Cloudflare-tunneled Obsidian graph URL; no iframe, no auto-open | Pending |
| **R.5** | **Rewrite academic-observe: MUST call obsidian_graph_query/vault_query before answering about any paper/method; state "no prior vault entry" when absent** | **Pending — THE phase gate** |

**Dependencies:** R.0 precedes R.5(must read actual skill body before rewriting it).
R.1/R.2/R.3/R.4 are parallel-eligible and independent of R.5. R.5 is the seal gate.

## Cross-Sprint Red Lines

- ❌ **No hook-based injection in Phase R.** settings.json UserPromptSubmit hooks that
  force vault lookup on every turn are Phase S. R.5 uses skill-level forced lookup first;
  if it proves insufficient under context load, that becomes the friction driving Phase S.
- ❌ **No LLM in markdown cleaning (R.2).** Heuristic and explicitly imperfect. LLM
  cleaning belongs to a later phase.
- ❌ **No new MCP server, no new dependency.** `.mcp.json` stays two servers.
- ❌ **Thin adapter preserved.** R.1 and R.4 are thin dispatchers; logic in domain modules.
- ⚠️ **academic-observe's description MUST be rewritten in R.5 — it is the activation
  lever. Freezing it was self-defeating.** (Rescinds the prior red line; the harness
  audit — `docs/audits/phase-R-harness-reality.md` F1 — showed a frozen description
  forecloses the only fix for under-activation. The narrow-trigger rewrite is in the
  R.5 design notes below.)
- ❌ **No opportunistic refactoring.**

## Hard Sealing Conditions

1. **(R.5 — the phase gate) Reasoning consults the vault unprompted.**
   When you ask about a paper or method that has a corresponding vault node
   (K node with mechanism claims, or T/I node with your prior thinking), the agent
   queries the vault BEFORE answering, and its response references what it found.
   When no node exists, it explicitly states "no prior vault entry" rather than
   silently skipping.
   **Assessed over N≥5 questions including ≥1 long-context turn. Record two rates:**
   - **X/N = consultation rate** — the skill fired a vault tool before answering.
   - **Y/X = retrieval precision** — the RIGHT node was surfaced.

   **Seal gate: X/N ≥ 4/5 (80%). Y/X is reported but NOT gated — precision failures
   drive Phase S, not Phase R.**
   Example: ask aboutMemGPT's eviction failure mode; confirm the agent retrieves
   and cites your T node on "recency ≠ importance."

2. **(R.3) Triage criteria are tunable without code changes.**
   Editing `prompts/triage_criteria.md` changes the verdict behavior on the next
   ingest_paper call. Verified by adding "memory benchmark → must_read" and
   observing a changed verdict on a test paper.

3. **(R.1) Standalone markdown conversion.**
   convert_pdf_to_md(arxiv_id | pdf_path) returns a markdown path, creates no
   vault node, reuses existing MinerU path. Verified live.

4. **(R.2) Heuristic cleaner removes structural noise without LLM.**
   On a sample MinerU markdown, removes isolated page numbers, repeated header/
   footer lines, sub-3-word orphan lines, while preserving paragraphs.
   Documented as best-effort.

## Design Decisions

- **The activation gap is Phase R's only reason to exist (ST2026-07-12).**
  Phase Q took three re-scopes to get the write side right. Phase R has one job:
  the vault is only as useful as the agent's willingness to walk it during its
  own reasoning. Without R.5, Phase Q is a sophisticated filing system the agent
  never opens. R.5 is what makes extract_paper's output matter.

- **R.5 uses skill-level forced lookup, not a harness hook (ST 2026-07-10).**
  The skill instruction rewrite ("MUST call obsidian_graph_query before answering")
  is the cheaper, less invasive mechanism. If it proves insufficient under context
  load (the agent still ignores the vault when the paper context is very long),
  that failure is the precise friction that justifies Phase S's hook architecture.
  R.5 tests the skill ceiling; Phase S is the fallback if the ceiling is too low.

- **Triage tunable criteria vs. triage prompt relocation (ST 2026-07-12).**
  friction-260710-01 was initially diagnosed as "triage prompt buried in code."
  Claude correctly identified that reviewer_zero.j2 is already external — the
  prompt was never buried. The real ask is configurable judgment criteria for your
  research domain. R.3 introduces prompts/triage_criteria.md for this. This is
  a different file from reviewer_zero.j2 (which is the persona prompt); triage
  criteria are a separate, domain-configurable concern.

- **Phase R completes the toolchain; Phase S activates the north star.**
  R.1/R.2/R.4 are debt items, not breakthroughs. R.3 and R.5 are the phase's
  actual deliverables. The north star (ambient multi-source reasoning in<30s)
  requires Phase S after Phase R proves the skill-level ceiling.

## R.5 Design Notes

- **Dual retrieval path.** R.5 calls both, merges + dedupes:
  - (a) `obsidian_graph_query(seed=entity, depth=1)` — typed edge walk.
  - (b) `vault_query(...)` — keyword match NOW. Phase S upgrades this leg to embedding
    search behind a stable `semantic_vault_search` interface. That interface is
    **pre-defined as a mock, NOT built in R.5** (tracked as DEBT-019): R.5's skill names
    the real registered tool `vault_query` — never `semantic_vault_search`, which is not
    an MCP tool yet. Phase S swaps the body behind the interface, not the signature.

- **Narrow-trigger description rewrite.** R.5 rewrites academic-observe's description to a
  narrow trigger (replacing the broad "proactively surface connections" instruction):
  > BEFORE answering any question about a specific paper, method, or architecture by name,
  > call `obsidian_graph_query` + `vault_query`. State findings or no prior entry.

## Out of Scope (→ Phase S)

- Hook-based deterministic vault injection (settings.json UserPromptSubmit/PreToolUse)
  — only if R.5's skill-level approach proves insufficient under context load.
- Ambient activation during general research conversation (not just paper/method questions)
- Parallel vault + web query with interleaved reasoning (north star)
- Schema-A/B node migration (~379 nodes) — still the separate later effort
- Embedded vault viewer (requires web frontend) — R.4 returns a URL only
