# Incident — `stage_deep_read_node` carried the GPU busy-guard, making Path 2 unreachable during any pipeline run

**Date:** 2026-08-10
**Surfaced by:** the Phase L.B.6 five-path e2e. Staging the `chimera-deep-extractor` output
returned `[Busy] A long-running task is already in progress` while an unrelated
`daily_paper_pipeline` was converting.
**Severity:** Medium (Path 2's deterministic back-half could not complete whenever Path 1 was
running — the two paths could not be exercised in one session) / Fix difficulty: trivial (remove
four lines).
**Status:** fixed.

## Symptom

`stage_deep_read_node(paper_id, extraction)` refused with the concurrency-guard message while a
pipeline task held the lock. The call performs no GPU work, no network I/O, and no MinerU
invocation — it grounds citations, renders markdown, and writes one file to `docs/staging/`.

## Root cause

`mcp-servers/chimera-papers/server.py` wrapped the tool in the same guard the GPU/network tools
use:

```python
async with _start_lock:
    if get_task_service().has_active_long_task():
        return _busy_message()
```

The guard exists to serialize a single shared GPU across `arxiv_miner`, `daily_paper_pipeline`,
`ingest_paper`, `fetch_paper`, and `convert_pdf_to_md`. `stage_deep_read_node` shares none of those
resources, and its own docstring says so: *"this tool is purely deterministic (grounding, render,
write)."*

The asymmetry made the error obvious once looked at: `write_scout_card` — the identical
deterministic sibling, the write half of externalized triage — has **never** carried the guard.
Two tools of the same shape, one guarded, and the guarded one was the one that blocked a path.

## Fix

Removed the guard from `stage_deep_read_node`, with a comment recording why it does not belong
(no GPU, no MinerU, no network; matches `write_scout_card`). No change to the domain call.

## Verification

- Full suite 187 passed after the change.
- The blocked call succeeded once the lock cleared, writing
  `docs/staging/20260810_052117-FluxMem_….md` at `chimera_tier: deep_read`, which then ascended to
  `Knowledge/` — completing Paths 2 and 5 of the gate.
- **Server-level changes need an MCP restart.** Removing the guard did not take effect in-session:
  `server.py` was loaded at startup, whereas the lazily-imported domain modules (`miner_tools`,
  `single_paper_extract`) had picked up their edits. The call only went through once the pipeline
  task ended and released the lock.

## Lesson

A guard is a claim about which resource is scarce. Copied onto a tool that does not touch that
resource, it stops being protection and becomes an availability bug — and it will look like correct
defensive code in review, because the guard itself is correct everywhere else it appears. The
sibling comparison is the cheap detector: two tools with the same contract should carry the same
guards, and a difference is either a bug or a comment nobody wrote.
