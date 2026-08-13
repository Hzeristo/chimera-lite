"""Shared test guards.

Currently one: no test may start the MinerU sidecar.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_sidecar_spawn_in_tests(monkeypatch):
    """Disable the MinerU sidecar for every test.

    `daily_paper_pipeline` starts a batch-scoped sidecar, so without this the pipeline tests
    spawn a REAL `mineru-api` process — loading models onto the GPU and adding ~10s per test
    (measured: 41s across four tests). A unit test that reaches for the GPU is not a unit
    test, and it fails on any machine without the ML stack.

    Autouse and blanket rather than per-test patching, so a future test cannot reintroduce
    the spawn by forgetting. A test that genuinely needs the real thing can undo it with
    `monkeypatch.setattr(mineru_sidecar, "SIDECAR_ENABLED", True)`.
    """
    try:
        from ports.ingest import mineru_sidecar
    except ImportError:  # chimera-vault-only test runs
        return
    monkeypatch.setattr(mineru_sidecar, "SIDECAR_ENABLED", False)
