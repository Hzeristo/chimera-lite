"""L.C.3a: the ``promote`` lifecycle transition (PENDING_REVIEW -> PROMOTED).

`docs/phases/phase-L.md` declares the harness-artifact lifecycle
``PENDING_REVIEW -> PROMOTED | REJECTED``, but until this sprint no mode ever reached
``PROMOTED`` — Route 3 of the phase VISION ("review [V] claims, batch-promote") had no
terminal operation. ``promote`` is reached only by an explicit caller-supplied mode; nothing
auto-promotes.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from result_service import ResultService

W1 = "w1_verdict"
CLAIM = "claim-hash-abc123"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fm(path: Path) -> dict:
    return yaml.safe_load(_read(path).split("---", 2)[1])


def test_promote_flips_pending_review_to_promoted(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    p = svc.write_result(
        kind=W1,
        identity=CLAIM,
        title="claim verdict",
        body="[V] the model does X.\n> verbatim quote",
        metadata={"verdict": "V"},
    )
    assert _fm(p)["status"] == "PENDING_REVIEW"

    svc.write_result(kind=W1, identity=CLAIM, title="", body="", mode="promote")
    assert _fm(p)["status"] == "PROMOTED"


def test_promote_preserves_body_and_frontmatter_byte_identical(tmp_path: Path) -> None:
    """The only thing allowed to change across the transition is the ``status:`` line."""
    svc = ResultService(tmp_path / "Harness")
    p = svc.write_result(
        kind=W1,
        identity=CLAIM,
        title="claim verdict",
        body="[V] the model does X.\n> verbatim quote\n",
        metadata={"verdict": "V", "depends_on": ["q-1", "q-2"]},
    )
    before = _read(p)

    svc.write_result(kind=W1, identity=CLAIM, title="", body="", mode="promote")
    after = _read(p)

    before_lines = before.splitlines()
    after_lines = after.splitlines()
    assert len(before_lines) == len(after_lines)
    for b_line, a_line in zip(before_lines, after_lines):
        if b_line.startswith("status:"):
            assert b_line == "status: PENDING_REVIEW"
            assert a_line == "status: PROMOTED"
        else:
            assert b_line == a_line

    # body (everything after the frontmatter's second `---`) is untouched
    before_body = before.split("---", 2)[2]
    after_body = after.split("---", 2)[2]
    assert before_body == after_body


def test_promote_on_missing_artifact_raises(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    with pytest.raises(FileNotFoundError):
        svc.write_result(kind=W1, identity="nope", title="", body="", mode="promote")


def test_unknown_mode_still_rejected(tmp_path: Path) -> None:
    svc = ResultService(tmp_path / "Harness")
    with pytest.raises(ValueError):
        svc.write_result(kind=W1, identity=CLAIM, title="t", body="b", mode="approve")
