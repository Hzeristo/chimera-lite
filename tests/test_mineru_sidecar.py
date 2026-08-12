"""The sidecar's two load-bearing contracts: liveness comes from the probe, and it degrades quietly.

1. A runfile is a KILL HANDLE, never evidence of life. This repo already has one bug of that
   shape — `TaskService.has_active_long_task` trusts disk status, so a crashed task reads as
   "busy" until cleared (CLAUDE.md, known deferred issues). These tests pin that the sidecar
   does not repeat it.
2. The sidecar is an accelerator, so every unavailable path must return None rather than
   raise — a broken sidecar costs wall time, never a conversion.

Nothing here spawns a process; the probe is pointed at a closed port or a faked response.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ports.ingest import mineru_sidecar as sc

# A port nothing serves; probe() must fail fast and quietly rather than raise.
DEAD_PORT = 59_999

HEALTHY_PAYLOAD = {
    "status": "healthy",
    "protocol_version": 1,
    "max_concurrent_requests": 1,
    "processing_window_size": 64,
    "version": "3.4.0",
    "queued_tasks": 0,
    "processing_tasks": 0,
}


@pytest.fixture
def isolated_state(monkeypatch, tmp_path: Path):
    """Keep runfile/log writes inside tmp_path — never the real .chimera/ state dir."""
    monkeypatch.setattr(sc, "_state_dir", lambda: tmp_path)
    monkeypatch.setattr(sc, "SIDECAR_PORT", DEAD_PORT)
    return tmp_path


def _fake_probe(monkeypatch, payload):
    monkeypatch.setattr(sc, "probe", lambda *a, **k: payload)


def test_probe_returns_none_on_a_closed_port(isolated_state) -> None:
    assert sc.probe(timeout=0.25) is None


def test_stale_runfile_does_not_read_as_running(isolated_state, monkeypatch) -> None:
    """THE regression guard: a crashed sidecar must not look alive because a file survived."""
    (isolated_state / "sidecar.json").write_text(
        json.dumps({"pid": 4242, "port": DEAD_PORT}), encoding="utf-8"
    )
    state = sc.status()
    assert state.running is False
    assert state.pid == 4242  # still surfaced — it is a kill handle
    assert "stale" in state.detail


def test_status_reports_running_only_when_the_probe_answers(isolated_state, monkeypatch) -> None:
    _fake_probe(monkeypatch, HEALTHY_PAYLOAD)
    state = sc.status()
    assert state.running is True
    assert state.mineru_version == "3.4.0"


def test_probe_rejects_a_foreign_process_holding_the_port(isolated_state, monkeypatch) -> None:
    """Port squatting: something answering 200 that is not MinerU must not count as healthy."""

    class _Response:
        status = 200

        def read(self):
            return json.dumps({"status": "healthy", "hello": "not mineru"}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    # Patch the opener probe() actually uses. Patching urllib.request.urlopen would silently
    # miss — probe() goes through a proxy-free opener — and the test would then pass merely
    # because nothing is listening, asserting nothing about rejection.
    monkeypatch.setattr(sc._DIRECT_OPENER, "open", lambda *a, **k: _Response())
    assert sc.probe(timeout=1.0) is None


def test_api_url_is_none_when_disabled(isolated_state, monkeypatch) -> None:
    monkeypatch.setattr(sc, "SIDECAR_ENABLED", False)
    _fake_probe(monkeypatch, HEALTHY_PAYLOAD)  # healthy, but the switch is off
    assert sc.api_url_if_healthy() is None


def test_api_url_never_starts_the_sidecar(isolated_state, monkeypatch) -> None:
    """convert() calls this on every paper; if it could start, a broken sidecar would cost
    every convert the full startup timeout before falling back."""

    def _boom(*_a, **_k):
        raise AssertionError("api_url_if_healthy must never spawn")

    monkeypatch.setattr(sc, "_spawn", _boom)
    assert sc.api_url_if_healthy() is None


def test_stop_refuses_while_work_is_in_flight(isolated_state, monkeypatch) -> None:
    busy = dict(HEALTHY_PAYLOAD, queued_tasks=1, processing_tasks=1)
    _fake_probe(monkeypatch, busy)
    monkeypatch.setattr(sc, "_kill_tree", lambda *_a: pytest.fail("must not kill mid-parse"))
    state = sc.stop(force=False)
    assert state.running is True
    assert "refused" in state.detail


def test_stop_on_a_dead_sidecar_clears_the_runfile(isolated_state) -> None:
    runfile = isolated_state / "sidecar.json"
    runfile.write_text(json.dumps({"pid": 4242, "port": DEAD_PORT}), encoding="utf-8")
    state = sc.stop()
    assert state.running is False
    assert not runfile.exists()


# --------------------------------------------------------------- orphaned VRAM / lifecycle


def test_stop_recovers_a_kill_handle_from_the_os(isolated_state, monkeypatch) -> None:
    """A sidecar started elsewhere leaves no runfile — it must still be stoppable.

    Refusing here is what stranded a resident GPU process: healthy, unowned, unkillable.
    """
    _fake_probe(monkeypatch, HEALTHY_PAYLOAD)
    monkeypatch.setattr(sc, "_pid_on_port", lambda: 7777)
    killed: list[int] = []
    monkeypatch.setattr(sc, "_kill_tree", lambda pid: killed.append(pid))
    # After the kill, the port must read dead so stop() can confirm shutdown.
    monkeypatch.setattr(sc, "probe", lambda *a, **k: None if killed else HEALTHY_PAYLOAD)

    state = sc.stop(force=True)

    assert killed == [7777]
    assert state.running is False


def test_stop_reports_honestly_when_no_handle_exists(isolated_state, monkeypatch) -> None:
    _fake_probe(monkeypatch, HEALTHY_PAYLOAD)
    monkeypatch.setattr(sc, "_pid_on_port", lambda: None)
    monkeypatch.setattr(sc, "_kill_tree", lambda *_a: pytest.fail("nothing to kill"))
    state = sc.stop(force=True)
    assert state.running is True
    assert "no kill handle" in state.detail


def test_status_surfaces_an_adopted_kill_handle(isolated_state, monkeypatch) -> None:
    _fake_probe(monkeypatch, HEALTHY_PAYLOAD)
    monkeypatch.setattr(sc, "_pid_on_port", lambda: 7777)
    state = sc.status()
    assert state.running is True
    assert state.pid == 7777
    assert "adopted" in state.detail


def test_losing_the_spawn_race_adopts_instead_of_falling_back(isolated_state, monkeypatch) -> None:
    """Our child exits because a concurrent batch won the port — that is a win, not a failure."""

    class _DeadChild:
        pid = 1234
        returncode = 1

        def poll(self):
            return 1

    # conftest disables the sidecar for every test; these two exercise ensure_running itself,
    # so they must opt back in or they only prove the disabled short-circuit returns None.
    monkeypatch.setattr(sc, "SIDECAR_ENABLED", True)
    monkeypatch.setattr(sc, "_spawn", lambda: _DeadChild())
    monkeypatch.setattr(sc, "_pid_on_port", lambda: 7777)
    # Nothing on the port when we decide to spawn; healthy by the time our child dies.
    calls = {"n": 0}

    def _probe(*_a, **_k):
        calls["n"] += 1
        return None if calls["n"] == 1 else HEALTHY_PAYLOAD

    monkeypatch.setattr(sc, "probe", _probe)

    assert sc.ensure_running(timeout=5) == sc.base_url()
    # The adopted sidecar's handle is recorded, so it can be stopped later.
    assert json.loads((isolated_state / "sidecar.json").read_text())["pid"] == 7777


def test_spawn_failure_with_a_dead_port_still_returns_none(isolated_state, monkeypatch) -> None:
    monkeypatch.setattr(sc, "SIDECAR_ENABLED", True)  # else this asserts only the kill switch
    monkeypatch.setattr(sc, "_spawn", lambda: None)
    monkeypatch.setattr(sc, "probe", lambda *a, **k: None)
    assert sc.ensure_running(timeout=1) is None


# ------------------------------------------------------------------------------ disk


def test_prune_output_reclaims_duplicate_parse_dirs(isolated_state) -> None:
    task = isolated_state / "output" / "task-uuid" / "2603.02096" / "auto"
    task.mkdir(parents=True)
    (task / "2603.02096.md").write_text("x" * 500, encoding="utf-8")
    (task / "origin.pdf").write_bytes(b"y" * 1500)

    freed = sc.prune_output()

    assert freed == 2000
    assert not (isolated_state / "output" / "task-uuid").exists()
    assert (isolated_state / "output").is_dir()  # root survives; MinerU writes into it


def test_prune_output_is_safe_when_nothing_exists(isolated_state) -> None:
    assert sc.prune_output() == 0


def test_log_appends_across_runs(isolated_state, monkeypatch) -> None:
    """Truncate-on-start erased the evidence of the run you actually need to diagnose."""
    sc.log_path().write_text("=== previous run ===\n", encoding="utf-8")
    monkeypatch.setattr(sc.subprocess, "Popen", lambda *a, **k: pytest.fail("no real spawn"))
    with pytest.raises(BaseException):
        sc._spawn()
    assert "previous run" in sc.log_path().read_text(encoding="utf-8")
