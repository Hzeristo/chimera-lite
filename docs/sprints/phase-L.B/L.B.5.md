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
