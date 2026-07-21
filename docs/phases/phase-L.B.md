# Phase L.B — Consolidation: Tier Integrity + Model Migration + Unified Ascension

**Status:** Active
**Predecessor:** Phase L (Locus: The Research Harness — partially sealed; W1/W2 live)
**Relationship to Phase L:** L.B completes Phase L by fixing the three-way drift the
workflow audit exposed. Phase L sealed the SKILL half (W1/W2 match ST); L.B fixes the
INGESTION half (Paths 1-2 contradict ST on judgment substrate and tier marking).

**Driving audit:** `docs/audits/workflow-drift-audit.md` (2026-07-20) — the L.B.0 sprint.

---

## Driving Frictions (from audit, 2026-07-20)

- **C-1 (CRITICAL):** `type: knowledge` is overloaded; `status: unverified` is inert.
  Scout-tier triage cards and deep-read nodes are indistinguishable. Vault read tools
  cannot retrieve meaningfully; I/T nodes built on this ground are unstable.
- **H-1 (HIGH):** Paths 1-2 use deepseek. ST's "judgment in Claude subagents" is false
  for half the system.
- **H-2/H-3 (HIGH):** No single "deep-read a fresh paper" path; `ingest_paper`
  over-promises.
- **Structural:** No living architecture diagram. Phase complexity has exceeded
  friction-driven management capacity.

---

## Mission

Fix the ingestion half of the four-path model so it matches the harness half. Make K
node tiers machine-distinguishable. Migrate deepseek to Sonnet/Haiku. Unify write paths
under a single ascension gate. Generate a living architecture diagram that becomes the
new ground truth for all future phases.

---

## Sprint Sequence

| Sprint | Risk | One-line goal |
|---|---|---|
| L.B.0 | — | **DONE** — the workflow-drift audit is this sprint (`docs/audits/workflow-drift-audit.md`) |
| L.B.1 | 🔴 | `chimera_tier` field + status vocabulary: add to schemas, templates, all write paths; fix `vault_query`/`search_vault` to include `thought`/`insight` in queryable types |
| L.B.2 | 🟡 | Model migration: `filter_service` → Haiku; `single_paper_extract` → Sonnet; update all config/bootstrap paths; fix `ingest_paper` docstring over-promise |
| L.B.3 | 🔴 | `ascend_node` MCP tool + unified write path: all K candidates go to `/Harness` first; `Knowledge/` only accepts `chimera_tier=deep_read` via `ascend_node` |
| L.B.4 | 🟡 | K node lifecycle integration: `extract_paper` triggers a W1 offer on completion; `vault_query` returns `chimera_tier` in results so callers can filter |
| L.B.5 | 🟡 | Living architecture diagram: machine-generated from the codebase; marks deepseek/sonnet/haiku/subagent boundaries; a first-class artifact updated at every phase seal |
| L.B.6 | 🔴 | Verify + Rebuild sprint: run the full four-path model end-to-end on real papers; if any path fails, fix in-sprint before seal — this is test-fix-confirm, not test-then-seal |

**Dependencies.** L.B.1 is the load-bearing sprint — everything else in L.B depends on
tier marking existing. L.B.1 must seal before L.B.2/L.B.3 begin. L.B.2 and L.B.3 are
parallel-eligible after L.B.1. L.B.5 runs concurrently with L.B.4. L.B.6 requires
L.B.1-L.B.4 complete.

---

## Cross-Sprint Red Lines

- ❌ Nothing enters `vault/Knowledge/` without `chimera_tier=deep_read` + the `ascend_node`
  path. No exceptions. The scout tier (`inbox/`) stays as-is — it is NOT promoted
  automatically.
- ❌ deepseek is retired as a JUDGMENT model. It may remain for cheap data extraction
  (citation parsing, etc.) but not for verdict/synthesis/classification.
- ❌ `ingest_paper`'s docstring must not claim "Knowledge base" or "deep read." It
  produces a scout-tier triage card. Period.
- ❌ L.B.6 does not seal if ANY of the four paths fails silently. Silent wrong behavior
  (no error, wrong output) is worse than an error.
- ❌ The architecture diagram is NOT hand-drawn. It is generated from code. It is NOT
  aspirational. It describes what the code actually does.

---

## Hard Sealing Conditions

1. **(L.B.1)** A scout-tier K node and a deep_read-tier K node are machine-distinguishable
   in the vault: the `chimera_tier` field exists, status transitions are defined, and
   `vault_query` with `type=thought` returns T nodes.

2. **(L.B.2)** `filter_service` uses Haiku; `single_paper_extract` uses Sonnet. No deepseek
   call in either judgment path. Verified by grep.

3. **(L.B.3)** `ascend_node` is the only path into `Knowledge/`. A direct file write to
   `Knowledge/` without `ascend_node` is impossible by code constraint (not just convention).

4. **(L.B.5)** The architecture diagram exists, is generated from code, shows model
   boundaries (Haiku/Sonnet/subagent), and matches code reality on all items the drift
   audit flagged. Generated at seal time, committed.

5. **(L.B.6 — the VISION gate)** Full end-to-end: `daily_pipeline` produces a scout K
   node; `extract_paper` produces a deep_read K node in staging; W1 on a real claim
   produces a harness verdict; W2 on 3 seeds produces a breadth map; `ascend_node`
   promotes a deep_read node to `Knowledge/`. All five in one session. No silent failures.

---

## Design Decisions

- **`chimera_tier`, not status alone, is the tier marker.** Status tracks lifecycle
  (`unverified → staged → promoted`). Tier tracks origin/depth (`scout` / `deep_read` /
  `harness_candidate`). They are orthogonal. Adding tier to status would conflate two
  independent axes.

- **Haiku for triage, Sonnet for synthesis, subagents for judgment.** This replaces the
  current split (deepseek for Paths 1-2, Claude for 3-4) with a consistent principle:
  cheap bulk classification = Haiku, synthesis requiring reasoning = Sonnet, isolated
  judgment requiring no framing contamination = subagent. Deepseek is retired as a
  judgment engine.

- **`ascend_node` is the single ascension gate.** All promotion into `Knowledge/` goes
  through one code path. This makes the "human commits truth" principle structural (not
  advisory) — the code physically cannot promote a node to the committed tier without
  `ascend_node`'s validation.

- **L.B.6 is a verify+rebuild sprint, not a test sprint.** Phase complexity has exceeded
  the level where "test then seal" is sufficient. L.B.6 explicitly reserves time to fix
  in-sprint if end-to-end reveals a gap. This is the "rebuild on failure" discipline the
  meta-lesson demands.

- **The architecture diagram is a first-class artifact.** It is generated from code at
  seal time. It is the canonical ground truth for all future phases. When ST vision
  diverges from it, the divergence is immediately visible. It replaces "we discussed this
  in ST" as the architectural authority.

---

## Notes

- **L.B.1 is load-bearing.** Everything downstream depends on tier marking existing; it
  must seal before the parallel-eligible sprints (L.B.2 / L.B.3) begin.
- The batch plan (`docs/plans/Phase-L.B-batch.md`) holds the file:line-anchored task
  scope, split analysis, and per-sprint red lines derived from the L.B.0 audit + the
  Phase L.B recon. This phase doc is the sparse manifest of intent.
</content>
</invoke>
