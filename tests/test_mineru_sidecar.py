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
