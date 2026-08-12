# Phase Review Verdict: Phase L.B — Integratio

**Audit reference:** `docs/audits/workflow-drift-audit.md` (2026-07-20, the L.B.0 sprint)
**Batch plan reference:** `docs/plans/Phase-L.B-batch.md`
**Sprints in batch:** L.B.0, L.B.1, L.B.2, L.B.3, L.B.4, L.B.5, L.B.6
**Sprints completed:** 7 of 7
**Batch history source:** sprint summaries (`docs/sprints/phase-L.B/`, 6 files) + git log
**Date:** 2026-08-12

> **Read this first.** L.B was reported sealed on 2026-07-21 with all five paths green. That
> report was wrong, and the reason it was wrong is the most useful thing in this document:
> every path had been exercised through in-process imports against an unmerged worktree
> (L.B.6 Finding 1), so the live client was never touched. When it finally was, two judgment
> workers turned out to have been dead since 2026-07-21, a resolver could not read a paper
> its own triage had filed, and the verifier guarding the phase's central invariant was
> testing a substring. This verdict rests on live-client execution, not on that record.

---

## Per-Sprint Verdicts

| Sprint | Status | Evidence | Action |
|---|---|---|---|
| L.B.0 | Pass | `docs/audits/workflow-drift-audit.md` — the audit that drove the phase | - |
| L.B.1 | Pass | `chimera_tier` present and queryable; scout card `inbox/Skim/2608.08883-AquiLLM.md` carries `chimera_tier: scout`, ascended node carries `deep_read`; `vault_query(type="thought")` returns 7 T nodes | - |
| L.B.2 | Pass | `filter_service.py` / `single_paper_extract.py` make **no** LLM call; judgment runs in pinned subagents, both of which spawned live this session | - |
| L.B.3 | Pass **after in-review repair** | Sole-writer property was **false** at review (`promote_node` reached `Knowledge/` for any K node not tiered `deep_read`); fixed `48786a0`, `2b72978` | Repaired in-review, not deferred |
| L.B.4 | Pass | `chimera-deep-extract` surfaced a `w1_offer`; `vault_query` returns `chimera_tier` | - |
| L.B.5 | Pass | `docs/ARCHITECTURE/ARCHITECTURE.md` regenerates byte-identically; `test_architecture_dataflow` passes | - |
| L.B.6 | Pass **after in-review repair** | Five components ran live end-to-end; 4 defects found and fixed in-sprint (`3dd58a8`) | Test-fix-confirm, per the sprint's own contract |

---

## Phase-Wide Red Lines

| Red Line | Status | Verification |
|---|---|---|
| Nothing enters `Knowledge/` without `chimera_tier=deep_read` + `ascend_node` | **Held** (repaired) | `_ascend_write` refuses every destination but `Knowledge/` and has exactly one caller; probe: `promote` with tier absent/`scout`/`deep_read` all REFUSED, `ascend`+`deep_read` writes. Was VIOLATED at review start. |
| Scout tier stays in `inbox/`, never auto-promoted | **Held** | `write_scout_card` writes only `inbox/<verdict>/`; `ascend_node` refuses non-`deep_read` |
| No LLM call of any kind inside any MCP server | **Held** | `ARCHITECTURE.md` I1.1 **PASS**: 4 call sites exist but **none reachable** from any registered tool (`optics_service.py:134`, `openai_compatible_client.py:113,118`, `task_service.py:467`) — dead oligo-era code. Presence is not reachability; recorded explicitly rather than reported as zero. |
| `ingest_paper` docstring must not claim "Knowledge base" or "deep read" | **Held** | `Select-String 'Knowledge base|deep read'` over `chimera-papers/server.py` → **0 hits** |
| L.B.6 does not seal if any path fails silently on the seed fixtures | **Held** | 4 defects surfaced loudly and were fixed before seal; none silent at seal |
| L.B.6 does not gate on volume | **Held** | Sealed on 4 seed papers + 1 fresh pipeline paper; no N-at-scale bar applied |
| The architecture diagram is generated from code, not hand-drawn | **Held** | `scripts/gen_architecture_diagram.py`; staleness is a test failure |

---

## Hard Sealing Conditions

| Condition | Status | Verification |
|---|---|---|
| **HSC1 (L.B.1)** scout vs deep_read machine-distinguishable | **Pass** | Both tiers observed on disk this session; `vault_query` surfaces `tier=` |
| **HSC2 (L.B.2)** no deepseek in either judgment path | **Pass** | Stronger than written — neither module calls any LLM; pins live in `.claude/agents/` (`chimera-paper-triager` haiku, `chimera-deep-extractor` sonnet) |
| **HSC3 (L.B.3)** `ascend_node` the only path into `Knowledge/` | **Pass** (repaired in-review) | Verified by execution, and the R3 verifier is **negative-controlled** — run against `67cba2c` and `48786a0` it returns VIOLATED |
| **HSC4 (L.B.5)** diagram generated from code, matches reality | **Pass** | 213→210 test suite green including the staleness test; regenerated at seal |
| **HSC5 (L.B.6)** five components e2e on real fixtures | **Pass, no exclusions** | See below |

**HSC5 evidence (live client, one session):**

1. `daily_paper_pipeline` → `new_pdfs=1 ingested=1 convert_failed=0`, fetched + converted `2608.08883` on the batch-scoped sidecar
2. triage → `inbox/Skim/2608.08883-AquiLLM.md`, `chimera_tier: scout`, verdict Skim/5, via the Haiku triager
3. `chimera-deep-extract` → `docs/staging/20260810_052117-FluxMem….md`, `chimera_tier: deep_read`, 1 lens + 5 ARA claims, `grounded: no_prior_match`
4. W1 → `Harness/w1_verdict__2605.17065.md`, verdict **[P]**, 4 verbatim quotes, `depends_on` in frontmatter
5. W2 → `Harness/w2_breadth_map__topic_streaming-video-memory.md` merged (`merged_added: 0, merged_skipped: 4`)
6. `ascend_node` → `Knowledge/FluxMem_….md`, `status: active`, `chimera_tier: deep_read`; staging emptied

Seed set: StreamForest `2509.24871`, PyraVid `2605.17065`, MemDreamer `2606.07512`, FluxMem `2603.02096`, plus `2608.08883` fresh from the pipeline.

---

## Driving Friction Resolution

| Friction | Original | Current | Evidence |
|---|---|---|---|
| **C-1** `type: knowledge` overloaded, `status` inert | CRITICAL | **RESOLVED** | `chimera_tier` axis live and observed on both tiers (L.B.1) |
| **H-1** Paths 1-2 use deepseek | HIGH | **RESOLVED** | No LLM call in either module; both pinned subagents spawned live (L.B.2, and the CRLF repair that made them reachable at all) |
| **H-2/H-3** no single deep-read path; `ingest_paper` over-promises | HIGH | **RESOLVED** | `chimera-deep-extract` ran end-to-end; docstring scan 0 hits |
| **Structural** no living architecture diagram | — | **RESOLVED** | Generated from source, with per-invariant verifiers and declared coverage (L.B.5) |
| `friction-260811` registration class | — | **OPEN, deferred** | Escalated during this review (3 instances ≥ threshold); needs a phase home, not an L.B sprint |

---

## Sealing Decision

⚠️ **Functionally Sealed.** 7 of 7 sprints Pass (two repaired in-review), all 7 red lines Held,
all 5 hard sealing conditions met with no exclusions. Moving forward with 1 Accepted Partial
and 2 Technical Debt items filed.

The phase is sealed on what it claimed: the four-path infrastructure runs correctly on real
fixtures through the live client. It is **not** sealed on scale — that is L.C+ scope by the
phase's own definition.

---

## State File Updates

### Auto-applied (written + staged by phase_review; no approval needed)

- `docs/ACCEPTED_PARTIALS.md` — appended **L.B.6.1** (MinerU images pre-existing dangling links)
- `docs/TECHNICAL_DEBT.md` — appended **DEBT-022** (`informed_by` not emittable) and
  **DEBT-023** (server-side changes invisible to a running MCP server), in the **Open** table.
  Note: DEBT-021 was already taken by Phase L.3, so the first draft's ids collided and were
  renumbered before staging.
- Friction status: `friction-260810` already RESOLVED and superseded (deleted; content preserved
  in `docs/incidents/2026-08-11-sidecar-orphaned-vram-and-lost-race.md`)

### Proposed for approval (decision-bearing)

#### `docs/ROADMAP.md`

```diff
- Phase L.B — Integratio: Active
+ Phase L.B — Integratio: ⚠️ Functionally Sealed 2026-08-12
+   Four-path infrastructure verified live end-to-end. 1 Accepted Partial, DEBT-021/022 filed.
+   Not sealed on scale (L.C+ scope). I0.4 contradiction recorded in ENFORCEMENT_DEBT D-1.
```

*(Exact anchor left to the operator — the ROADMAP lists phases by descriptive header and the
codename-prefix sync is itself an open item in `CODENAMES.md`.)*

---

## Findings carried out of the phase — not waived

1. **I0.4 is contradicted by the sealed path.** `_unlink_superseded` deletes superseded
   committed nodes; I0.4 (Tier 0) says they are "never deleted, only superseded and marked
   STALE". Verified by execution. Inherited from repo-init, not created by L.B — but it now
   sits behind `ascend_node`, the gate this phase built, which concentrates it. Recorded as
   `ENFORCEMENT_DEBT` **D-1(b)**, homed to Phase H.
2. **Three verifiers were found guarding nothing**, each returning PASS: R3 tested a substring;
   R6 defended against the server authoring a T/I/D body when the threat is the caller; R2
   chained on a symbol that had been renamed, so it found nothing and reported clean. All three
   rewritten; R2 now refuses a vacuous result, R3 is negative-controlled.
3. **MCP restarts hid results three times** (agent registry, `stage_deep_read_node` guard,
   `paper_loader`). A running server is a snapshot of code that no longer exists; server-side
   verification is provisional until restart.

---

## Audit-to-Implementation Trace

| Audit Finding | Outcome |
|---|---|
| C-1: tier overload | Addressed by L.B.1 |
| H-1: deepseek in Paths 1-2 | Addressed by L.B.2 (+ the CRLF repair that made the replacement reachable) |
| H-2/H-3: no deep-read path, docstring over-promise | Addressed by L.B.2 / L.B.4 |
| Structural: no living diagram | Addressed by L.B.5 |
| Sole-writer guarantee | Addressed by L.B.3, **repaired in-review** (`48786a0`, `2b72978`) |

---

*Generated by chimera-sprint-discipline phase_review mode.*
