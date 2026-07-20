"""L.3: ResultService W2 breadth-map lifecycle — merge-not-clobber, reject, mark_stale.

The load-bearing invariant: a W2 re-run MERGES (adds papers, PRESERVES the Architect's
in-Obsidian annotations), it does NOT supersede. Clobbering the map would destroy irreplaceable
human curation — this is the reason W2 needs its own write mode.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from result_service import ResultService

W2 = "w2_breadth_map"
TOPIC = "topic:agentic-memory"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fm(path: Path) -> dict:
    return yaml.safe_load(_read(path).split("---", 2)[1])


def _map_body(*paper_ids: str) -> str:
    return "\n\n".join(
        f"<!-- w2:paper={pid} -->\n### {pid}\n- gap: g-{pid}\n- number: 60.{pid}"
        for pid in paper_ids
    )


def test_w2_first_write_is_pending(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    p = svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A", "B"), mode="merge")
    assert _fm(p)["type"] == W2
    assert _fm(p)["status"] == "PENDING_REVIEW"
    assert "paper=A" in _read(p) and "paper=B" in _read(p)


def test_w2_rerun_merges_and_preserves_annotations(tmp_path: Path) -> None:
    results = tmp_path / "Harness"
    svc = ResultService(results)
    p = svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A", "B"), mode="merge")
    # Architect annotates paper B in Obsidian (a manual critique inside its block)
    p.write_text(_read(p).replace("- number: 60.B", "- number: 60.B\n- [My Critique]: B is over-hyped."))
    # re-run adds a NEW paper C (and re-supplies A, B)
    svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A", "B", "C"), mode="merge")

    files = list(results.glob("*.md"))
    assert len(files) == 1  # merged in place, not duplicated
    final = _read(files[0])
    assert "[My Critique]: B is over-hyped." in final  # ANNOTATION PRESERVED
    assert "paper=C" in final  # new paper ADDED
    assert final.count("paper=A") == 1 and final.count("paper=B") == 1  # deduped, existing wins


def test_w2_merge_status_becomes_merged_on_add(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A"), mode="merge")
    p = svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A", "B"), mode="merge")
    assert _fm(p)["status"] == "MERGED"
    assert _fm(p)["merged_added"] == 1


def test_w2_preamble_preserved_on_merge(tmp_path: Path) -> None:
    results = tmp_path / "Harness"
    svc = ResultService(results)
    p = svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A"), mode="merge")
    # Architect adds a free-form notes section ABOVE the first paper block
    p.write_text(_read(p).replace("<!-- w2:paper=A -->", "## [My Notes]\nfocus on decay.\n\n<!-- w2:paper=A -->", 1))
    svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A", "B"), mode="merge")
    assert "focus on decay." in _read(p)  # preamble preserved


def test_reject_transitions_status_preserving_body(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    p = svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A"), mode="merge")
    svc.write_result(kind=W2, identity=TOPIC, title="", body="", mode="reject")
    assert _fm(p)["status"] == "REJECTED"
    assert "paper=A" in _read(p)  # body untouched


def test_mark_stale_transitions_status(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    p = svc.write_result(kind=W2, identity=TOPIC, title="map", body=_map_body("A"), mode="merge")
    svc.write_result(kind=W2, identity=TOPIC, title="", body="", mode="mark_stale")
    assert _fm(p)["status"] == "STALE"


def test_transition_on_missing_artifact_raises(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    with pytest.raises(FileNotFoundError):
        svc.write_result(kind=W2, identity="nope", title="", body="", mode="reject")


def test_unknown_mode_rejected(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    with pytest.raises(ValueError):
        svc.write_result(kind=W2, identity=TOPIC, title="t", body="b", mode="clobber")


def test_w1_supersede_still_overwrites(tmp_path: Path) -> None:
    # regression: the W1 default mode is unchanged — a re-run REPLACES, never merges.
    svc = ResultService(tmp_path / "Harness")
    svc.write_result(kind="w1_verdict", identity="id-1", title="v1", body="first", metadata={"verdict": "P"})
    p = svc.write_result(kind="w1_verdict", identity="id-1", title="v2", body="second", metadata={"verdict": "V"})
    assert "second" in _read(p) and "first" not in _read(p)
    assert _fm(p)["verdict"] == "V"
    assert _fm(p)["superseded_prior"] is True
