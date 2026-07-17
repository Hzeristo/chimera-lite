"""L.2b: ResultService — vault harness artifacts with identity-supersede + depends_on (C1)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from result_service import ResultService


def _read_fm(path: Path) -> dict:
    fm_raw = path.read_text(encoding="utf-8").split("---", 2)[1]
    return yaml.safe_load(fm_raw)


def test_write_result_writes_pending_artifact_with_depends_on(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    path = svc.write_result(
        kind="w1_verdict",
        identity="claim-abc123",
        title="Claim: X improves Y by 3%",
        body='**Verdict:** [V]\n\n> "...3% improvement..." — p.4',
        metadata={"verdict": "V", "depends_on": ["claim-abc123", "q-1"]},
    )
    assert path.exists()
    fm = _read_fm(path)
    assert fm["type"] == "w1_verdict"
    assert fm["status"] == "PENDING_REVIEW"
    assert fm["identity"] == "claim-abc123"
    assert fm["verdict"] == "V"
    # C1 — the dependency structure is recorded, not just the bare verdict.
    assert fm["depends_on"] == ["claim-abc123", "q-1"]
    assert "3% improvement" in path.read_text(encoding="utf-8")


def test_rerun_same_identity_supersedes_not_duplicates(tmp_path: Path) -> None:
    results = tmp_path / "Harness"
    svc = ResultService(results)
    svc.write_result(
        kind="w1_verdict", identity="id-1", title="v1", body="first", metadata={"verdict": "P"}
    )
    path2 = svc.write_result(
        kind="w1_verdict", identity="id-1", title="v2", body="second", metadata={"verdict": "V"}
    )
    files = list(results.glob("*.md"))
    assert len(files) == 1  # superseded, not duplicated
    fm = _read_fm(path2)
    assert fm["verdict"] == "V"  # replaced with the new verdict
    assert fm["superseded_prior"] is True
    assert "second" in path2.read_text(encoding="utf-8")


def test_different_identity_distinct_files(tmp_path: Path) -> None:
    results = tmp_path / "Harness"
    svc = ResultService(results)
    svc.write_result(kind="w1_verdict", identity="id-A", title="a", body="a")
    svc.write_result(kind="w1_verdict", identity="id-B", title="b", body="b")
    assert len(list(results.glob("*.md"))) == 2


def test_empty_identity_rejected(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    with pytest.raises(ValueError):
        svc.write_result(kind="w1_verdict", identity="  ", title="t", body="b")
