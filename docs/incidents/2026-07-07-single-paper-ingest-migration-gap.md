# Incident — single-paper ingest missing from chimera-lite MCP (migration gap)

**Date:** 2026-07-07
**Surfaced by:** DR6 grounding (`Thought-trajectory-pattern grounding (DR6)`): 0/13 cited
references had a Knowledge node, and there was **no way to ingest one paper** to close the gap.
**Severity:** Medium (capability gap, no data loss) / Fix difficulty: minor (thin adapter over
existing, sealed primitives).
**Status:** fixed; static-verified (imports, tool registration, no-irradiate, Rule-10 reuse).
Live end-to-end pending (see Verification).

## Symptom
`daily_paper_pipeline` does the full arXiv sweep + **batch** ingest, and `arxiv_miner` fetches
metadata — but there is no tool to ingest a **single** paper you already know (by arXiv id) or
already have (a local PDF). A user reading a specific paper could not get it into the vault as a
K node without running the whole daily sweep.

## Root cause
project_chimera's `run_ingest` single-paper path was **not migrated to MCP**. Phase M wired only
the batch daily pipeline (`daily_paper_pipeline`). The single-paper *service*
(`single_paper_pipeline_service.py`) was copied into the repo during migration but left
**unwired** — no MCP tool exposed it (same shape as the orphaned `StagingService` before Phase O).

## Fix
Added `ingest_paper(arxiv_id: str | None, pdf_path: str | None)` to the chimera-papers server —
a thin adapter that composes the **same per-paper logic the sealed batch already uses**, for one
paper:

- `mcp-servers/chimera-papers/single_paper_ingest.py` (new, ~95 lines incl. docstrings):
  `_fetch_arxiv_pdf` (direct download by id, reusing `ArxivFetcher.REQUEST_HEADERS`, bypassing
  the batch *seen-filter* since this is an explicit ingest) → `ingest_to_papers` (the Rule-10
  MinerU convert) → `PaperLoader.load_paper` → `FilterService.evaluate_paper` (triage) →
  `VaultNoteWriter.write_knowledge_node`. Returns the K-node path. Always writes (no verdict gate).
- `miner_tools.ingest_paper` — synchronous wrapper; runs the heavy MinerU/LLM work in
  `asyncio.to_thread`; returns the path (no task_id).
- `server.py` `@mcp.tool() ingest_paper` — delegates; rejected while a long-running arXiv/pipeline
  job is active (shared GPU / MinerU) via the existing `has_active_long_task()` guard.

**Reuse, not reimplementation:** the convert is `MineruClient.convert` (creationflags +
`stdin=DEVNULL` + temp-file output — Rule 10, from incidents `2026-07-01` / `2026-07-02`), reached
via `ingest_to_papers`; the K-node writer already existed; triage is the batch's `FilterService`.

## Scope boundary — DELIBERATELY NOT migrated: `OpticsService.irradiate`
`irradiate` is the oligo-era **deep-read LLM in the pipeline** (paper → full DeepReadAtlas). It is
**not** part of this path, by design:
- The 6 Phase-N.A lens skills replaced it. Migrating `irradiate` would 架空 (hollow out) those
  skills and revive reasoning-in-pipeline.
- Deep read is now: **`ingest_paper` → `read_vault_file` → an N.A lens skill → `create_node`.**
- `ingest_paper` stops at convert → **triage** (FilterService, a lighter verdict/summary the batch
  already runs) → K node. Triage ≠ deep read.

Confirmed: `OpticsService` / `irradiate` are referenced **only** inside `optics_service.py`
(grep across the server → 0 matches elsewhere); the new path and its whole call chain
(`ingest_to_papers`, `paper_loader`, `filter_service`, `vault_note_writer`, `arxiv_fetch`,
`bootstrap`) never import or call it.

## Verification
Static (DONE):
- `single_paper_ingest` imports clean; `ingest_paper` registers on the chimera-papers server
  (`arxiv_miner`, `daily_paper_pipeline`, `ingest_paper`, `check_task_status`).
- `.irradiate(` calls in the new module: **0** (the 3 `OpticsService` mentions are the explanatory
  comments above). Grep across the server confirms no `irradiate` outside `optics_service.py`.
- Convert path = `MineruClient.convert` (Rule-10 flags), reused via `ingest_to_papers`.

Live end-to-end (pending a real run — MinerU GPU + LLM + arXiv download, ~1–3 min, writes a K node):
- `ingest_paper("2604.14004")` → PDF fetched → converted → K node written.
- `ingest_paper(pdf_path="<local>.pdf")` → converted → K node written.
- `nvidia-smi` shows MinerU on the GPU, no headless freeze (Rule 10 holds).

## Follow-ups (deferred, not blockers)
- **GPU guard is one-directional.** `ingest_paper` refuses to start while a batch runs, but is not
  itself a tracked long task, so a batch *started during* a synchronous ingest would contend on the
  8 GB GPU. Single-user, low-risk; revisit if it bites (register a lightweight GPU lease).
- **MinerU raw output is not auto-cleaned** by this path (`ingest_to_papers` returns the raw dir for
  the caller to clean; the batch cleans via the archive router). Minor disk residual per ingest.
- **arXiv id → PDF URL** is built as `https://arxiv.org/pdf/{id}` (versionless, latest). If a
  specific version is needed, pass the versioned id or a local `pdf_path`.
