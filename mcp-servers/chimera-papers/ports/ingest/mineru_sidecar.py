"""Supervisor for a persistent MinerU parse server (the "sidecar").

WHAT THIS IS NOT: a server. MinerU ships its own FastAPI service (`mineru.cli.fast_api`,
the `mineru-api` entry point) and its CLI already knows how to talk to one via `--api-url`.
This module only **supervises** that process — start it, prove it is healthy, stop it.
Nothing here serves HTTP, and no inference runs in this process.

WHY: every `MineruClient.convert` currently spawns a throwaway MinerU service and reloads
every model. Measured on a pipeline convert: 3.1s server spawn + full model load against
15.8s of actual parsing, inside a 32.4s wall — roughly half the wall clock is setup that a
resident server pays once. See docs/logs/friction-260810.md.

## Statelessness — the design constraint

The MCP server is a thin, restartable adapter; it must not hold a server handle in memory.
So the sidecar's state lives in the OS, not in this process:

- **A fixed port is the discovery mechanism.** No singleton, no module global. Two MCP
  server instances (e.g. after an `/mcp` reconnect) converge on the same sidecar instead of
  racing to spawn two.
- **The health probe is the ONLY liveness truth.** The runfile is a *kill handle*, never
  evidence that anything is alive. This repo already has one bug of that shape —
  `TaskService.has_active_long_task` trusts disk status, so a crashed task reads as "busy"
  until cleared (CLAUDE.md, known deferred issues). Not repeating it here.
- **The probe validates that the thing answering is MinerU**, so a foreign process that
  grabbed the port cannot be mistaken for the sidecar.
- **A missing kill handle is recovered from the OS, not surrendered.** A sidecar started by
  the operator or by a previous MCP instance leaves no runfile here. `_pid_on_port` asks the
  OS who holds the port (only ever after `probe()` has confirmed the responder is MinerU), so
  adoption and `stop` work regardless of who started it. Refusing instead — the old
  behaviour — stranded a resident GPU process that only manual intervention could free.
- **Losing a start race is not a failure.** If our spawned child exits because a concurrent
  batch won the port, `ensure_running` re-probes and adopts the winner rather than dropping
  this batch to standalone alongside a perfectly healthy service.

## Disk

The log APPENDS across runs — truncate-on-start destroyed exactly the evidence needed to
diagnose a convert that failed earlier — and rolls to `.log.1` past `LOG_MAX_BYTES`. The
service's `MINERU_API_OUTPUT_ROOT` is pruned at spawn and after stop: every parse leaves a
task-uuid directory holding a full duplicate of the paper, whose authoritative copy lives in
`papers/md_papers_raw/<id>/`. Nothing used to remove it (60 MB across 7 parses).

## Blast radius

`ensure_running()` NEVER raises and never blocks conversion. If the sidecar cannot start,
`MineruClient.convert` simply omits `--api-url` and MinerU spawns its own per-run service
exactly as before. The worst case is *slow*, never *broken* — the sidecar is an
optimization, not a dependency.

Spawn discipline follows chimera-mcp-taste: the venv interpreter via `sys.executable`
(never a bare PATH lookup), `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP` with
`stdin=DEVNULL` for the headless parent, and stdout sunk to a FILE rather than a pipe.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from core.platform import get_project_root

logger = logging.getLogger(__name__)

SIDECAR_HOST = "127.0.0.1"
# Fixed by configuration, not chosen at random: the port IS how a stateless caller finds
# the sidecar. A random port would need a registry, and a registry would need to be trusted.
SIDECAR_PORT = int(os.getenv("CHIMERA_MINERU_SIDECAR_PORT", "8765"))
SIDECAR_ENABLED = os.getenv("CHIMERA_MINERU_SIDECAR", "1").lower() not in {"0", "false", "off"}

STARTUP_TIMEOUT_SECONDS = float(os.getenv("CHIMERA_MINERU_SIDECAR_STARTUP", "300"))
POLL_INTERVAL_SECONDS = 2.0
PROBE_TIMEOUT_SECONDS = 5.0
SHUTDOWN_GRACE_SECONDS = 30
# The log appends across runs (forensics), so it needs a ceiling: past this, roll to .log.1.
LOG_MAX_BYTES = int(os.getenv("CHIMERA_MINERU_SIDECAR_LOG_MAX", str(8 * 1024 * 1024)))

HEALTH_ENDPOINT = "/health"
# Keys MinerU's /health payload carries (mineru/cli/fast_api.py). Used as an identity check:
# something else listening on our port will not answer with this shape.
REQUIRED_HEALTH_KEYS = (
    "status",
    "protocol_version",
    "max_concurrent_requests",
    "processing_window_size",
)


@dataclass(frozen=True)
class SidecarStatus:
    running: bool
    base_url: str
    port: int
    pid: int | None
    detail: str
    queued_tasks: int | None = None
    processing_tasks: int | None = None
    mineru_version: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def base_url() -> str:
    return f"http://{SIDECAR_HOST}:{SIDECAR_PORT}"


def _state_dir() -> Path:
    # .chimera/ is already gitignored — runtime state, never a repo artifact.
    path = get_project_root() / ".chimera" / "mineru-sidecar"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _runfile() -> Path:
    return _state_dir() / "sidecar.json"


def log_path() -> Path:
    return _state_dir() / "sidecar.log"


# --------------------------------------------------------------------------- liveness

# Built once: the sidecar is always on loopback, so every request must bypass proxies.
_DIRECT_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def probe(timeout: float = PROBE_TIMEOUT_SECONDS) -> dict | None:
    """Return MinerU's /health payload, or None. Never raises.

    This is the single source of truth for "is the sidecar up". A payload that does not
    carry MinerU's health shape is rejected — the port may be held by something else.
    """
    url = f"{base_url()}{HEALTH_ENDPOINT}"
    try:
        # Proxy-free opener: urllib honours the system/env proxy by default, and this box
        # has one configured. Routing a 127.0.0.1 health check through an HTTP proxy makes
        # the probe slow at best (measured ~2s per call to a dead port) and wrong at worst —
        # a proxy answering for our loopback URL. An empty ProxyHandler pins it to a direct
        # connection, which fails in microseconds when nothing is listening.
        with _DIRECT_OPENER.open(url, timeout=timeout) as response:  # noqa: S310 — fixed localhost URL
            if response.status != 200:
                return None
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None
    if payload.get("status") != "healthy":
        return None
    if any(key not in payload for key in REQUIRED_HEALTH_KEYS):
        logger.warning(
            "[Sidecar] Something is listening on %s but it is not a MinerU service", base_url()
        )
        return None
    return payload


def _read_runfile() -> dict | None:
    """The recorded pid — a KILL HANDLE ONLY. Never treat its existence as liveness."""
    try:
        return json.loads(_runfile().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _pid_on_port() -> int | None:
    """Ask the OS which pid is LISTENING on the sidecar port. Never raises.

    The runfile only exists for a sidecar THIS process started. A sidecar started by the
    operator, or by another MCP instance after an `/mcp` reconnect, left no kill handle —
    and `stop()` used to give up and say "stop it manually", stranding a resident GPU
    process. The OS already knows the owner; ask it instead of holding state.

    Only ever used AFTER `probe()` has confirmed a MinerU service answers on this port, so
    the pid owning the port is that service.
    """
    try:
        if sys.platform == "win32":
            completed = subprocess.run(
                ["netstat", "-ano", "-p", "tcp"],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                check=False,
            )
            needle = f"{SIDECAR_HOST}:{SIDECAR_PORT}"
            for line in completed.stdout.splitlines():
                parts = line.split()
                # proto local foreign state pid
                if len(parts) >= 5 and parts[1].endswith(needle) and parts[3].upper() == "LISTENING":
                    return int(parts[4])
            return None
        completed = subprocess.run(
            ["lsof", "-t", f"-iTCP:{SIDECAR_PORT}", "-sTCP:LISTEN"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        first = completed.stdout.strip().splitlines()
        return int(first[0]) if first else None
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        logger.warning("[Sidecar] Could not resolve the pid holding port %s: %s", SIDECAR_PORT, exc)
        return None


def _kill_handle() -> int | None:
    """The pid to kill: the runfile's if we started it, else whoever the OS says owns the port."""
    record = _read_runfile()
    pid = record.get("pid") if record else None
    return pid if pid is not None else _pid_on_port()


def prune_output(reason: str = "") -> int:
    """Delete the sidecar's server-side output tree. Returns bytes reclaimed. Never raises.

    `MINERU_API_OUTPUT_ROOT` accumulates one task-uuid directory per parse, each holding a
    FULL duplicate of the paper (origin.pdf, middle.json, the markdown, images) — a second
    copy of material whose authoritative home is `papers/md_papers_raw/<id>/`. Nothing used
    to remove it; it had already reached 60 MB across 7 parses. Safe to call only when no
    parse is in flight: at spawn (before the service exists) and after it has stopped.
    """
    root = _state_dir() / "output"
    if not root.is_dir():
        return 0
    freed = 0
    try:
        for entry in root.iterdir():
            try:
                size = sum(f.stat().st_size for f in entry.rglob("*") if f.is_file())
            except OSError:
                size = 0
            try:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    entry.unlink(missing_ok=True)
                freed += size
            except OSError as exc:
                logger.warning("[Sidecar] Could not prune %s: %s", entry, exc)
    except OSError as exc:
        logger.warning("[Sidecar] Could not read the output root: %s", exc)
        return freed
    if freed:
        logger.info(
            "[Sidecar] Pruned %.1f MB of duplicate parse output%s",
            freed / (1024 * 1024),
            f" ({reason})" if reason else "",
        )
    return freed


def _write_runfile(pid: int) -> None:
    payload = {
        "pid": pid,
        "port": SIDECAR_PORT,
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        _runfile().write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        # A missing runfile costs us the kill handle, not correctness — probe() still works.
        logger.warning("[Sidecar] Could not write runfile: %s", exc)


def status() -> SidecarStatus:
    payload = probe()
    record = _read_runfile()
    pid = record.get("pid") if record else None
    if payload is None:
        return SidecarStatus(
            running=False,
            base_url=base_url(),
            port=SIDECAR_PORT,
            pid=pid,
            detail=(
                "not running"
                if record is None
                else f"not running (stale runfile records pid {pid})"
            ),
        )
    # Healthy: report a kill handle even when we never started it, so an operator (or Claude)
    # reading status always sees whether this sidecar can actually be stopped.
    owned = pid is not None
    if pid is None:
        pid = _pid_on_port()
    return SidecarStatus(
        running=True,
        base_url=base_url(),
        port=SIDECAR_PORT,
        pid=pid,
        detail=(
            "healthy"
            if owned
            else f"healthy (adopted — kill handle {pid} resolved from the OS)"
            if pid is not None
            else "healthy (no kill handle — cannot be stopped by this process)"
        ),
        queued_tasks=payload.get("queued_tasks"),
        processing_tasks=payload.get("processing_tasks"),
        mineru_version=payload.get("version"),
    )


# --------------------------------------------------------------------------- lifecycle


def _build_env() -> dict[str, str]:
    """The sidecar does the INFERENCE, so the device pin must land in its environment.

    With `--api-url`, the client process only uploads a PDF and downloads a zip — pinning
    the device on the client would configure the wrong process entirely.
    """
    # Lazy, and deliberately one-directional: paper2md imports this module only from inside
    # a function, so there is no module-level cycle.
    from ports.ingest.paper2md import MINERU_DEVICE, MINERU_TASK_BUDGET_SECONDS

    env = os.environ.copy()
    if MINERU_DEVICE:
        env.setdefault("MINERU_DEVICE_MODE", MINERU_DEVICE)
    env["MINERU_API_OUTPUT_ROOT"] = str(_state_dir() / "output")
    # One GPU, 8 GB: concurrent parses would OOM. Same reasoning as the single-worker
    # convert queue in mineru_pipeline.convert_queue_worker.
    env["MINERU_API_MAX_CONCURRENT_REQUESTS"] = "1"
    env["MINERU_API_DISABLE_ACCESS_LOG"] = "1"
    env.setdefault("MINERU_TASK_RESULT_TIMEOUT_SECONDS", str(MINERU_TASK_BUDGET_SECONDS))
    # MUST NOT be set: it makes the service exit on stdin EOF. The sidecar is detached and
    # has no stdin owner, so that watcher would shut it down immediately.
    env.pop("MINERU_API_SHUTDOWN_ON_STDIN_EOF", None)
    return env


def _spawn() -> subprocess.Popen | None:
    """Launch mineru-api detached from this (possibly headless) process. Never raises."""
    command = [
        sys.executable,  # the venv interpreter — never a bare PATH lookup (mcp-taste rule 1)
        "-m",
        "mineru.cli.fast_api",
        "--host",
        SIDECAR_HOST,
        "--port",
        str(SIDECAR_PORT),
    ]
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
        subprocess, "CREATE_NEW_PROCESS_GROUP", 0
    )
    # No parse can be in flight — the service does not exist yet — so this is the safe
    # moment to drop the previous run's duplicate output.
    prune_output(reason="spawn")

    try:
        # APPEND, not truncate. Truncate-on-start destroyed the evidence of every previous
        # run, which is exactly what was needed to diagnose a failed convert after the fact.
        # Unbounded growth is held off by a size cap below plus MINERU_API_DISABLE_ACCESS_LOG.
        path = log_path()
        try:
            if path.is_file() and path.stat().st_size > LOG_MAX_BYTES:
                path.replace(path.with_suffix(".log.1"))  # keep exactly one previous generation
        except OSError as exc:
            logger.warning("[Sidecar] Could not roll the sidecar log: %s", exc)
        logf = path.open("a", encoding="utf-8", errors="replace")
        logf.write(
            f"\n===== sidecar start {datetime.now(timezone.utc).isoformat(timespec='seconds')} "
            f"on {base_url()} =====\n"
        )
        logf.flush()
    except OSError as exc:
        logger.error("[Sidecar] Cannot open the sidecar log: %s", exc)
        return None

    try:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=logf,
            stderr=subprocess.STDOUT,
            creationflags=flags,
            env=_build_env(),
            cwd=str(get_project_root()),
        )
    except OSError as exc:
        logger.error("[Sidecar] Failed to spawn mineru-api: %s", exc)
        logf.close()
        return None
    finally:
        # The child holds its own duplicated handle; this process does not need ours.
        logf.close()

    logger.info("[Sidecar] Spawned mineru-api pid=%s on %s", proc.pid, base_url())
    return proc


def api_url_if_healthy() -> str | None:
    """Base URL iff a sidecar is ALREADY serving. Never starts anything.

    This — not ``ensure_running`` — is what the convert path calls. Starting is an explicit,
    batch-level act: if ``convert`` tried to start the sidecar, a service that cannot start
    would cost every single convert the full startup timeout before falling back, turning an
    accelerator into a large regression. Probing costs a failed localhost connect (sub-ms)
    when nothing is listening.
    """
    if not SIDECAR_ENABLED:
        return None
    return base_url() if probe() is not None else None


def ensure_running(timeout: float = STARTUP_TIMEOUT_SECONDS) -> str | None:
    """Return the sidecar's base URL, starting it if needed. NEVER raises.

    Returning None is a valid, non-fatal outcome: the caller falls back to MinerU's own
    per-run service. That is the blast-radius contract — a broken sidecar costs speed only.
    """
    if not SIDECAR_ENABLED:
        return None

    if probe() is not None:
        return base_url()

    proc = _spawn()
    if proc is None:
        return _adopt_if_healthy("spawn failed")

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            # Our child died — but losing a start RACE looks identical to failing to start.
            # The likely cause is that a concurrent batch won the port, so re-probe before
            # giving up: falling straight through to standalone would run this batch slowly
            # alongside a perfectly healthy sidecar.
            adopted = _adopt_if_healthy(f"our spawn exited {proc.returncode}, port already served")
            if adopted is None:
                logger.error(
                    "[Sidecar] mineru-api exited with code %s before becoming healthy; see %s",
                    proc.returncode,
                    log_path(),
                )
            return adopted
        if probe() is not None:
            _write_runfile(proc.pid)
            logger.info("[Sidecar] Healthy at %s (pid=%s)", base_url(), proc.pid)
            return base_url()
        time.sleep(POLL_INTERVAL_SECONDS)

    logger.error("[Sidecar] mineru-api did not become healthy within %ss; stopping it", timeout)
    _kill_tree(proc.pid)
    return None


def _adopt_if_healthy(context: str) -> str | None:
    """Adopt a sidecar this process did not start: verify health, then RECORD a kill handle.

    Without the runfile write this is where orphaned VRAM came from — a healthy service with
    no recorded owner, which `stop()` refused to touch. The pid comes from the OS, so the
    handle is recorded even though we never held the child.
    """
    if probe() is None:
        return None
    pid = _pid_on_port()
    if pid is not None:
        _write_runfile(pid)
    logger.info("[Sidecar] Adopted the running sidecar at %s (pid=%s; %s)", base_url(), pid, context)
    return base_url()


def start_for_batch() -> bool:
    """Start the sidecar for a batch. Returns True only if THIS caller started it.

    Ownership rule: **only the starter stops it.** A sidecar the operator brought up by hand
    (via the `mineru_sidecar` tool) must outlive the batch — a pipeline that stopped it would
    be disposing of something it does not own. Pair with ``stop_after_batch``.

    Never raises: a batch must run, slowly, rather than not at all.
    """
    try:
        if api_url_if_healthy() is not None:
            logger.info("[Sidecar] Already running; the batch will use it but not stop it")
            return False
        started = ensure_running() is not None
        if not started:
            logger.warning("[Sidecar] Unavailable; this batch converts standalone (slower)")
        return started
    except Exception as exc:  # noqa: BLE001 — an accelerator must never fail a batch
        logger.warning("[Sidecar] Could not start for the batch (%s); continuing standalone", exc)
        return False


def stop_after_batch(started_here: bool) -> None:
    """Release the sidecar's VRAM iff this batch started it. Never raises."""
    if not started_here:
        return
    try:
        # force=True: this batch owns the sidecar and its own converts are done, so any
        # in-flight count is stale bookkeeping rather than someone else's work.
        state = stop(force=True)
        logger.info("[Sidecar] Batch finished — %s", state.detail)
    except Exception as exc:  # noqa: BLE001 — teardown must not mask a batch failure
        logger.warning("[Sidecar] Could not stop after the batch (%s); it may hold VRAM", exc)


def _kill_tree(pid: int) -> None:
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            logger.error("[Sidecar] taskkill failed for pid %s: %s", pid, exc)
        return
    try:
        os.kill(pid, 9)
    except OSError as exc:
        logger.error("[Sidecar] kill failed for pid %s: %s", pid, exc)


def stop(force: bool = False) -> SidecarStatus:
    """Stop the sidecar and free its VRAM.

    Refuses while the service reports in-flight work unless ``force`` — killing mid-parse
    loses that conversion, and the caller usually does not know a batch is still running.
    """
    payload = probe()
    if payload is None:
        _runfile().unlink(missing_ok=True)
        freed = prune_output(reason="stop (already down)")
        detail = "already stopped (runfile cleared)"
        if freed:
            detail += f"; pruned {freed / (1024 * 1024):.1f} MB of duplicate parse output"
        return SidecarStatus(
            running=False,
            base_url=base_url(),
            port=SIDECAR_PORT,
            pid=None,
            detail=detail,
        )

    in_flight = int(payload.get("queued_tasks") or 0) + int(payload.get("processing_tasks") or 0)
    if in_flight and not force:
        return SidecarStatus(
            running=True,
            base_url=base_url(),
            port=SIDECAR_PORT,
            pid=(_read_runfile() or {}).get("pid"),
            detail=f"refused: {in_flight} task(s) in flight — pass force=True to kill anyway",
            queued_tasks=payload.get("queued_tasks"),
            processing_tasks=payload.get("processing_tasks"),
            mineru_version=payload.get("version"),
        )

    # A sidecar started by the operator or by another MCP instance has no runfile here; ask
    # the OS who owns the port rather than refusing and stranding its VRAM.
    pid = _kill_handle()
    if pid is None:
        return SidecarStatus(
            running=True,
            base_url=base_url(),
            port=SIDECAR_PORT,
            pid=None,
            detail=(
                "running but no kill handle — the runfile has no pid and the OS did not "
                f"report a listener on port {SIDECAR_PORT}; stop it manually"
            ),
            queued_tasks=payload.get("queued_tasks"),
            processing_tasks=payload.get("processing_tasks"),
            mineru_version=payload.get("version"),
        )

    _kill_tree(pid)
    deadline = time.monotonic() + SHUTDOWN_GRACE_SECONDS
    while time.monotonic() < deadline:
        if probe() is None:
            _runfile().unlink(missing_ok=True)
            # The service is down, so nothing can be mid-parse — safe to reclaim its scratch.
            freed = prune_output(reason="stop")
            logger.info("[Sidecar] Stopped (pid=%s)", pid)
            detail = "stopped"
            if freed:
                detail += f"; pruned {freed / (1024 * 1024):.1f} MB of duplicate parse output"
            return SidecarStatus(
                running=False,
                base_url=base_url(),
                port=SIDECAR_PORT,
                pid=pid,
                detail=detail,
            )
        time.sleep(1.0)

    return SidecarStatus(
        running=True,
        base_url=base_url(),
        port=SIDECAR_PORT,
        pid=pid,
        detail="kill issued but the port is still answering — inspect manually",
    )
