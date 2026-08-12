# friction-260810-01 — every convert reloads MinerU's models from scratch; half a convert's wall clock is setup

**Date:** 2026-08-10
**Status:** RESOLVED for the performance gap (supervisor + batch-scoped lifecycle wired and
verified). One non-code item remains open: this work's phase home is the operator's call.
**Phase context:** Phase L (branch `phase-L`). **Not an L deliverable** — L is the research
harness (W1/W2). This is an ingest-performance gap surfaced while building
`scripts/debug_mineru.py` to instrument the MinerU seam, and it needs a phase home.

## The friction

`MineruClient.convert` shells out to the `mineru` CLI once per paper. MinerU 3.x answers each
invocation by spawning a **throwaway** `mineru-api` service, loading every model into VRAM,
parsing, and tearing the whole thing down. Nothing is reused between papers.

Measured on a `pipeline` convert (`playground/mineru_debug/.../pipeline-auto/_mineru.log`):

```
20:23:29.858  local mineru-api started
20:23:32.910  batch submitted          <- 3.1s service spawn
20:23:48.756  batch complete           <- 15.8s actual parsing
                                          32.4s total wall
```

Roughly **half of a convert is setup**, and it is paid again for every paper. Under the
`hybrid` backend the model-load share was worse (~14.1s of a 46.9s run). The faster the
backend, the more the reload dominates — flipping to `pipeline`
(`docs/incidents/2026-08-10-mineru-backend-flip.md`) *increased* this friction's share of
wall time rather than reducing it.

Cost scales with batch size: a 20-paper `daily_paper_pipeline` spends ~10 minutes doing
nothing but re-introducing the GPU to models it already loaded.

## Why it is friction and not an incident

Nothing is broken. No defect, no crash, no wrong output — conversion is correct, just
wasteful. Per `.claude/skills/_shared/incident_protocol.md:6-8` that is workflow pain, which
is friction. Filed here so the sidecar work is **evidence-driven rather than anticipatory**
(`chimera-sprint-discipline:122` — sprints without a friction reference require operator
override).

## What was implemented (same session, operator-directed)

`ports/ingest/mineru_sidecar.py` — a **supervisor**, not a server. MinerU already ships the
service (`mineru.cli.fast_api`) and its CLI already accepts `--api-url`; this module only
starts / health-probes / stops that process.

Design constraints it holds:

- **No state in the MCP process.** A fixed port is the discovery mechanism, so two server
  instances (an `/mcp` reconnect) converge on one sidecar instead of racing to spawn two.
- **The health probe is the only liveness truth.** The runfile carries a pid as a *kill
  handle* and is never read as evidence of life — deliberately not repeating the shape of
  the known `TaskService.has_active_long_task` bug, which trusts disk status and reads a
  crashed task as "busy". The probe also verifies the responder is MinerU, so a foreign
  process holding the port cannot be mistaken for the sidecar.
- **Blast radius bounded to speed.** `ensure_running()` never raises; returning `None` is a
  valid outcome that makes `convert` omit `--api-url` and behave exactly as before. A broken
  sidecar costs wall time, never a conversion.
- **Spawn discipline** per `chimera-mcp-taste`: venv interpreter via `sys.executable`,
  `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP`, `stdin=DEVNULL`, stdout to a file that is
  truncated on start (a resident uvicorn would otherwise grow it without bound).
- **The device pin moved to the right process.** With `--api-url` the client only uploads a
  PDF; the sidecar does the inference, so `MINERU_DEVICE_MODE` is set in the sidecar's env.
  Pinning it on the client would configure the wrong process.
- `MINERU_API_MAX_CONCURRENT_REQUESTS=1` — one GPU, 8 GB; concurrent parses OOM, the same
  reasoning as the single-worker `convert_queue_worker`.
- `MINERU_API_SHUTDOWN_ON_STDIN_EOF` explicitly unset — the sidecar is detached and has no
  stdin owner, so that watcher would kill it at birth.

MCP surface: `mineru_sidecar(action="status"|"start"|"stop", force=False)` — a thin
`server.py` contract delegating to `miner_tools`. `stop` refuses while parses are in flight
unless forced.

**Violation Detector** (mandatory pre-change, `ARCHITECTURE_RULES.md:40`): R2–R6 untouched
(no truth advance, no `Knowledge/` write, no `chimera_tier`, no `[V]/[P]/[U]`, no T/I/D
body). R1 is the only row in play and is **defused by ordering** — the backend flip landed
first, so `pipeline` runs no VLM at all and the sidecar hosts layout/OCR/table CV models
only. Had hybrid or vlm-engine remained pinned, this would have made the MCP server the
supervisor of a *resident* vision-language model.

## Verification (done)

Driven through the production `MineruClient.convert` path, not a mock:

```
ensure_running()                              6.1s   -> http://127.0.0.1:8765 (pid, mineru 3.4.0)
convert #1 with sidecar (cold models)        18.9s
convert #2 with sidecar (warm)               11.9s
convert #3 standalone (sidecar disabled)     31.9s
stop()                                       clean; probe() -> None, no process on the port
```

Like-for-like on the **same** paper (`2602.02369`, 14 pages), since the three above differ in
length: **31.9s standalone -> 13.0s on a warm sidecar = 2.4x**. Output path is unchanged
(`<stem>/auto/<stem>.md`), which also confirms the `pipeline` flip end to end.

A first attempt reported "0.0s / 7895x" — an artifact of two verification scripts racing on
one output directory, where the second run's timed convert hit the skip cache the first had
just populated. Recorded because the failure mode is instructive: a speedup that looks too
good is usually a cache, and this harness has a skip cache by design.

Unit coverage: `tests/test_mineru_sidecar.py` (8 cases) pins the two load-bearing contracts —
a stale runfile must NOT read as running, and `api_url_if_healthy` must never spawn.

## Open

- **Phase home.** This work does not belong to Phase L's intent. `docs/phases/*` is
  human-authored, so where it lives is the operator's call. **Still open.**

## Closed since

- **Batch-level ownership — DONE.** `daily_chimera_service.py:224` calls `start_for_batch`
  and `:238` calls `stop_after_batch` inside a `finally`, ownership-gated so a sidecar the
  operator brought up by hand outlives the batch. This is where the N-paper win lives and
  what bounds VRAM residency to the batch.
- **Log growth — resolved differently than planned.** Truncate-on-start bounded the file by
  destroying the previous run's log, which is precisely the evidence needed to diagnose a
  convert that failed earlier — during the L.B.6 gate run the sidecar's history was
  unrecoverable for exactly this reason. The log now APPENDS with a start banner and rolls to
  `.log.1` past `LOG_MAX_BYTES` (8 MB default).
- **Orphaned VRAM — closed.** `stop()` used to refuse when the service was healthy but no
  runfile pid existed, stranding a resident GPU process that only manual intervention could
  free — reachable whenever the operator or a reconnected MCP instance started it.
  `_pid_on_port` now recovers the kill handle from the OS (only after `probe()` has confirmed
  the responder is MinerU), `_adopt_if_healthy` records it, and `status()` reports whether a
  handle exists at all.
- **Lost spawn race — closed.** A child that exited because a concurrent batch won the port
  read as "failed to start" and dropped that batch to standalone beside a healthy sidecar.
  `ensure_running` now re-probes and adopts the winner.

## Found while fixing — not in the original friction

- **Unbounded duplicate output.** `MINERU_API_OUTPUT_ROOT` points at
  `.chimera/mineru-sidecar/output` and nothing pruned it. Every parse leaves a task-uuid
  directory holding a FULL second copy of the paper (`origin.pdf`, `middle.json`, the
  markdown, images) whose authoritative home is `papers/md_papers_raw/<id>/`. Measured at
  **60.1 MB across 7 parses** — two orders of magnitude larger than the log growth this doc
  worried about. `prune_output()` now runs at spawn and after stop; the 60.1 MB backlog was
  reclaimed through that code path.
