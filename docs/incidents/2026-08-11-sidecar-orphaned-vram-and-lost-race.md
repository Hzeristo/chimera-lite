# Incident — sidecar could strand a resident GPU process, and lost a start race silently

**Date:** 2026-08-11
**Surfaced by:** a white-box read of `ports/ingest/mineru_sidecar.py` after the Phase L.B.6 gate
run, prompted by MinerU failing hard during that run (operator-directed review).
**Severity:** Medium-High (a healthy sidecar could hold VRAM on an 8 GB card with no code path able
to stop it; no data loss, no wrong output) / Fix difficulty: minor (contained to one module).
**Status:** fixed; 16 unit tests, negative-controlled.

## Context — why the sidecar exists

MinerU 3.x answers each `mineru` CLI invocation by spawning a throwaway `mineru-api`, loading every
model into VRAM, parsing, and tearing it down. Measured on one `pipeline` convert: 3.1s service
spawn + model load against 15.8s of actual parsing inside a 32.4s wall — roughly half of every
convert is setup, paid again per paper. Like-for-like on the same paper (`2602.02369`, 14 pages):
**31.9s standalone → 13.0s on a warm sidecar = 2.4x**. The supervisor (`mineru_sidecar.py`) starts,
health-probes, and stops MinerU's own service so a batch pays that setup once.

Its blast-radius contract: `ensure_running()` never raises, `None` is a valid outcome, and
`convert` then omits `--api-url` and behaves exactly as before. A broken sidecar costs wall time,
never a conversion. That contract held throughout and is why neither defect below ever corrupted
output.

## Defect 1 — orphaned VRAM, no kill handle

`stop()` read the pid solely from the runfile this process writes when it starts the service. A
sidecar started by the operator (via the `mineru_sidecar` tool) or by a previous MCP instance — a
scenario the design **explicitly supports**, since a fixed port exists so two instances converge on
one sidecar — leaves no runfile here. `stop()` then returned `"running but no runfile pid — stop it
manually"` and did nothing, stranding a resident GPU process holding VRAM on an 8 GB card that only
manual intervention could free.

**Fix.** `_pid_on_port()` asks the OS who is LISTENING on the port (`netstat -ano` on Windows,
`lsof` on POSIX), consulted only *after* `probe()` has confirmed the responder is MinerU — so a
port squatter can never be killed by mistake. `_kill_handle()` prefers the runfile and falls back
to the OS. `status()` now reports which of three states holds: owned, `adopted — kill handle N
resolved from the OS`, or `no kill handle — cannot be stopped by this process`. That last string is
the monitorable one.

## Defect 2 — a lost start race read as a failure

If two batches started together, one child won the port and the other exited. `ensure_running` saw
`proc.poll() is not None` and returned `None` **without re-probing**, so that batch ran every
convert standalone alongside a perfectly healthy sidecar — paying the full 2.4x penalty the sidecar
exists to remove.

**Fix.** `_adopt_if_healthy()` re-probes on that path (and on spawn failure); if a healthy MinerU
answers, it adopts it and records the OS-resolved pid, so an adopted sidecar is also stoppable.

## Two more found in the same read

- **Log truncation destroyed forensics.** `_spawn` opened the log `"w"`, so every start erased the
  previous run's log — during the L.B.6 gate run the sidecar's history was unrecoverable for
  exactly this reason (299 bytes showing only the last startup). Now appends with a UTC start
  banner, rolling to `.log.1` past `LOG_MAX_BYTES` (8 MB), which preserves what truncation was
  protecting against.
- **Unbounded duplicate output.** `MINERU_API_OUTPUT_ROOT` pointed at `.chimera/mineru-sidecar/
  output` and nothing pruned it. Every parse left a task-uuid directory holding a FULL second copy
  of the paper (`origin.pdf`, `middle.json`, markdown, images) whose authoritative home is
  `papers/md_papers_raw/<id>/`. Measured at **60.1 MB across 7 parses**. `prune_output()` now runs
  at spawn and after stop — both points where no parse can be in flight — and the backlog was
  reclaimed through that code path after confirming the service was down.

## Verification

- 16 unit tests pass; full suite 210 passed.
- **Negative control on the race fix:** with `_adopt_if_healthy` disabled, `ensure_running` returns
  `None` and the new test fails. The test is sensitive to the thing it claims to check.
- Two new tests initially asserted nothing: `tests/conftest.py` disables the sidecar for *every*
  test, so without `monkeypatch.setattr(sc, "SIDECAR_ENABLED", True)` they only proved the kill
  switch returns `None` — one was passing falsely. Both now opt in explicitly.

## Not fixed — inherent, not a defect

The sidecar holds VRAM *between* papers by design, and `MINERU_API_MAX_CONCURRENT_REQUESTS=1`
bounds concurrency, never a single parse's appetite. On an 8 GB card shared with desktop
applications this makes CUDA OOM more likely, not less — the honest counter-pressure to the 2.4x.
Residency is the price of the speedup; the fixes above ensure the process can always be killed to
reclaim it.

## Lesson

Both defects are the same mistake: ownership state was held only in a file this process writes,
while the OS already knew the answer. The module's own docstring warned against exactly this shape
("the runfile is a kill handle, never evidence of life") and got liveness right — then used the
same file as the sole source of *ownership*, where it is equally untrustworthy.
