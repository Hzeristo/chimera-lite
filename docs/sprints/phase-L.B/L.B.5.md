# Modification Summary: L.B.5

**Phase:** L.B — Consolidation
**Sprint:** L.B.5 — Living architecture diagram (code-generated) 🟡
**Batch position:** 7 of 7 in the parallel band (runs concurrently with L.B.4; generated after L.B.2 so it reflects the migrated model boundaries)
**Date:** 2026-07-21
**Executed by:** Sonnet subagent (`chimera-sprint-executor`); review + commit by main session (Opus).
**Commit:** `7db9e3b`

---

## Objective

Add a generator that INTROSPECTS the codebase and emits a living architecture diagram marking the
model boundaries (Haiku / Sonnet / subagent) and the four ingestion/write paths — a first-class
artifact regenerated at every phase seal, describing what the code does, never aspiration.

---

## Files touched

| Path | Change |
|---|---|
| `scripts/gen_architecture_diagram.py` | **New** (~135 lines). Parses the `@mcp.tool()` inventory of both servers (regex over decorator/`async def` pairs), the pinned worker model of every `.claude/agents/*.md` (regex over YAML frontmatter `name:`/`model:`), and renders a mermaid flowchart of the four ingestion/write paths + the judgment-never-in-MCP boundary. Writes `docs/ARCHITECTURE/ARCHITECTURE.md` with `newline="\n"`. |
| `docs/ARCHITECTURE/ARCHITECTURE.md` | **New** — the generated artifact, produced by running the generator (not hand-written). |

---

## Key design facts / decisions

1. **Inventories are introspected; only the path SHAPE is a literal.** The drift-prone parts (which
   tools exist, which model each agent is pinned to) are read from source on every run, so the
   diagram tracks reality. The four-path structure — which is the canonical four-path statement (F8:
   it exists nowhere else in prose) — is a small explicit data literal in the script, since its
   shape does not change per-run. This is the split the batch plan sanctions (task 1).

2. **Deterministic by construction.** All lists sorted; no timestamps, no randomness; `newline="\n"`
   on write so Windows CRLF translation cannot perturb output. Verified: two consecutive runs
   produce a byte-identical file (SHA256 match), and re-running on the committed tree yields no git
   diff.

3. **No new dependency.** Stdlib `re` + `pathlib` only — the tiny agent frontmatter is regex-parsed
   rather than pulling `pyyaml` into the diagram path. Reuses the L.4 self-contained-artifact
   pattern (mermaid-in-markdown, no server).

4. **The generated diagram is now the first canonical four-path statement** (reconciliation #7). The
   mermaid correctly shows: two scout paths (`daily_paper_pipeline`, `ingest_paper` → `inbox/`), the
   deep_read path (`chimera-deep-extract` skill → Sonnet subagent → `stage_deep_read_node` →
   `docs/staging/`), and the ascension path (`ascend_node` → `Knowledge/`, sole writer), with a
   judgment subgraph annotating triage=Haiku, deep-read=Sonnet, both Claude Code subagents.

5. **Tool inventory matches live servers.** The generated MD lists all 9 `chimera-papers` tools and
   all 11 `chimera-vault` tools (including `ascend_node` from L.B.3) — verified against the two
   `server.py` files.

---

## Verification

| Check | Status | Output |
|---|---|---|
| ruff (`gen_architecture_diagram.py`) | clean | exit 0 — "All checks passed!" (via `uvx ruff`; `.venv` lacks ruff — pre-existing env gap) |
| Determinism (two runs) | PASS | byte-identical (SHA256 `BFB0F4B3…08A6D7` both runs); `git status` unchanged on 2nd run |
| Determinism (post-commit re-run on committed tree) | PASS | `git status --short` empty for the artifact |
| Pure-English (`rg \p{Han}`) | 0 hits | exit 1 (clean) |
| Tool inventory vs live `server.py` | matches | 9 papers + 11 vault tools |

---

## Red Line Status

| Red Line | Status |
|---|---|
| Code-generated, never hand-drawn; describes actual code, never aspiration | ✓ — inventories introspected from source |
| No new dependency; self-contained artifact | ✓ — stdlib `re`/`pathlib` only, mermaid-in-markdown |
| Deterministic — re-running reproduces byte-for-byte | ✓ — SHA256 match + no git diff |
| No opportunistic refactoring | ✓ — only the generator + its output |

---

## Acceptance

- ✅ HSC #4: the diagram exists, is generated from code, shows model boundaries (Haiku/Sonnet/subagent) + the four paths, and matches code reality on the drift-audit-flagged items (uniform `type` resolved, judgment externalized, `ascend_node` sole writer).
- ✅ Re-running the generator reproduces the artifact (deterministic; no manual edits).

**Note:** the diagram is regenerated at seal (L.B.6 task 3 / phase_review) so it reflects any
in-sprint fixes from the e2e run.

**Seal:** L.B.5 complete.

---

## AMENDMENT 2026-08-03 — acceptance redesigned from determinism to accuracy

The acceptance recorded above was **wrong in kind**, and the artifact it certified was **false**.

### What was wrong
The "four ingestion/write paths" were a hardcoded literal (`INGESTION_PATHS`), not introspected —
only the tool inventory and agent model pins were read from source. When L.B.2 moved scout-card
writing out of `daily_paper_pipeline` / `ingest_paper` and into the `chimera-triage-paper` skill's
`write_scout_card`, the literal kept asserting the old flow. The shipped diagram claimed:

- `daily_paper_pipeline (batch) [chimera_tier=scout]` → `inbox/<verdict>/` — **false**
- `ingest_paper (single) [chimera_tier=scout]` → `inbox/<verdict>/` — **false**
- dotted edges from both tools to `chimera-paper-triager` — **phantom**; MCP tools never spawn
  subagents, skills do

`write_scout_card` — the actual sole writer of `inbox/` (`single_paper_ingest.py:137`, the ONE caller
of `VaultNoteWriter.write_knowledge_node`) — appeared in the tool inventory and **nowhere in the
flow**. So the diagram violated its own header line and phase-wide red line D5 ("describes actual
code, never aspiration") from the moment L.B.2 sealed.

### Why the acceptance failed to catch it
Acceptance was **determinism** — that re-running reproduces the artifact byte-for-byte. A hardcoded
literal reproduces perfectly forever while being wrong. Reproducibility was measured; accuracy was
assumed. The check certified the cheap property and left the load-bearing one bare.

### The redesign
Acceptance is now **accuracy: every flow edge must map to a real write call site.**

- `scripts/gen_architecture_diagram.py` rewritten to DERIVE every write edge. It builds a reference
  graph over both server packages (references, not just call-expression targets — this codebase
  routes writes through `asyncio.to_thread(staging.create_staging_node, …)`, where the writer is an
  argument; alias-resolved, since the servers lazy-import under `as _name`), then computes which MCP
  tools transitively reach each declared write surface.
- Only the **anchor** is declared per surface (destination + module + writer symbol), and it is
  verified against source every run. A surface whose writer no longer exists is a hard `SystemExit`,
  not a stale diagram. A surface no tool reaches is reported **ORPHANED** rather than drawn.
- `tests/test_architecture_dataflow.py` (new, 13 tests) asserts the derivation: anchors exist, every
  chain terminates at its writer, every mermaid edge is a derived edge, `inbox/` is reachable ONLY
  via `write_scout_card`, neither fetch/convert tool reaches it, and no subagent name appears in the
  diagram. Determinism is retained as a secondary property, not as the proof of correctness.

### Derived result (now true)

| destination | writer | reached by |
|---|---|---|
| `inbox/<verdict>/` [scout] | `write_knowledge_node` | `write_scout_card` |
| `docs/staging/` | `create_staging_node` | `stage_deep_read_node`, `create_node` |
| `<vault>/Knowledge\|Thoughts\|Insights\|Decisions/` | `_promote_write` | `ascend_node` |
| `<vault>/Harness/` | `write_result` | `write_result` |
| `<vault>/01_Deep_Reads/` | `write_deep_read_node` | **ORPHANED** (only caller is the retired `OpticsService.irradiate`) |

### Verification
- `pytest tests/test_architecture_dataflow.py` → 13 passed; full suite → **170 passed, 0 failed**.
- ruff on both changed files → **All checks passed!** (exit 0).
- Determinism (secondary) → two runs byte-identical, SHA256 `EA916ED3…F4AD9`.
- **Negative control** — re-pointing the inbox anchor at `ingest_single_paper` (the exact rot that
  shipped) fails hard: `SystemExit` at `gen_architecture_diagram.py:202`, 1 failed + 7 errors. The
  test can fail, which the previous acceptance could not.

### Not in this change (deliberately)
- **R1-R6 conformance section** — logged as `docs/logs/friction-260803.md` (OPEN). The map checks
  topology, not invariants; bundling an unverified rules section alongside the verified edges would
  repeat the sin being fixed. Part 2, once each rule has a real check.
- **Skill → tool / skill → subagent layer** — a full dataflow map wants it, but naive backtick
  parsing of `SKILL.md` would mint false edges (red lines mention tools precisely to forbid them,
  e.g. `chimera-deep-extract` names `ascend_node` only to disclaim it). Deferred until it can be
  derived precisely rather than guessed.

**Status:** L.B.5 acceptance re-met on the accuracy criterion. **Phase L.B must NOT seal** until the
flow section matches live code — it now does, but the seal remains blocked on the L.B.6 e2e (halted:
insufficient vault nodes).
