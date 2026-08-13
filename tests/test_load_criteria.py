"""Unit tests for ``compose_criteria`` (L.1a): pure three-axis criteria composition.

Uses an injected fake ``read_file`` over a ``tmp_path`` directory tree — never touches the
real vault, never builds a full ``ChimeraConfig``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vault_tools import compose_criteria


def _make_read_file(root: Path):
    def read_file(rel_path: str) -> str:
        p = root / rel_path
        if not p.is_file():
            raise FileNotFoundError(f"file not found: {rel_path}")
        return p.read_text(encoding="utf-8")

    return read_file


def _write(root: Path, rel_path: str, content: str) -> None:
    p = root / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_composition_order_type_field_disposition_general(tmp_path: Path) -> None:
    _write(tmp_path, "criteria/type/benchmark.md", "TYPE-CONTENT")
    _write(tmp_path, "criteria/field/nlp.md", "FIELD-CONTENT")
    _write(tmp_path, "criteria/disposition/paper-critic.md", "ROLE-CONTENT")
    _write(tmp_path, "criteria/disposition/_general.md", "GENERAL-CONTENT")

    out = compose_criteria(
        _make_read_file(tmp_path), type="benchmark", role="paper-critic", field="nlp"
    )

    type_idx = out.index("TYPE-CONTENT")
    field_idx = out.index("FIELD-CONTENT")
    role_idx = out.index("ROLE-CONTENT")
    general_idx = out.index("GENERAL-CONTENT")
    assert type_idx < field_idx < role_idx < general_idx, out


def test_missing_field_file_yields_marker_and_does_not_crash(tmp_path: Path) -> None:
    _write(tmp_path, "criteria/type/method.md", "TYPE-CONTENT")
    _write(tmp_path, "criteria/disposition/proposal-evaluator.md", "ROLE-CONTENT")
    _write(tmp_path, "criteria/disposition/_general.md", "GENERAL-CONTENT")
    # criteria/field/robotics.md deliberately absent

    out = compose_criteria(
        _make_read_file(tmp_path),
        type="method",
        role="proposal-evaluator",
        field="robotics",
    )

    assert "[no criteria file: criteria/field/robotics.md]" in out
    assert "TYPE-CONTENT" in out
    assert "ROLE-CONTENT" in out
    assert "GENERAL-CONTENT" in out


def test_present_files_content_appears_verbatim(tmp_path: Path) -> None:
    _write(tmp_path, "criteria/type/survey.md", "SURVEY-TYPE-BODY\nline2")
    _write(tmp_path, "criteria/disposition/paper-critic.md", "CRITIC-BODY")
    _write(tmp_path, "criteria/disposition/_general.md", "GENERAL-BODY")

    out = compose_criteria(
        _make_read_file(tmp_path), type="survey", role="paper-critic"
    )

    assert "SURVEY-TYPE-BODY\nline2" in out
    assert "CRITIC-BODY" in out
    assert "GENERAL-BODY" in out
    # field omitted entirely (no field kwarg) -> no field section/marker at all
    assert "criteria/field/" not in out


def test_field_none_omits_field_section(tmp_path: Path) -> None:
    _write(tmp_path, "criteria/type/theory.md", "T")
    _write(tmp_path, "criteria/disposition/paper-critic.md", "R")
    _write(tmp_path, "criteria/disposition/_general.md", "G")

    out = compose_criteria(
        _make_read_file(tmp_path), type="theory", role="paper-critic", field=None
    )

    assert "[field:" not in out


def test_missing_type_and_role_files_also_marker(tmp_path: Path) -> None:
    # Nothing exists at all under tmp_path/criteria — every section should degrade gracefully.
    out = compose_criteria(
        _make_read_file(tmp_path), type="benchmark", role="paper-critic", field="cv"
    )

    assert "[no criteria file: criteria/type/benchmark.md]" in out
    assert "[no criteria file: criteria/field/cv.md]" in out
    assert "[no criteria file: criteria/disposition/paper-critic.md]" in out
    assert "[no criteria file: criteria/disposition/_general.md]" in out


@pytest.mark.parametrize(
    "header",
    [
        "## [type: benchmark]",
        "## [disposition: paper-critic]",
        "## [disposition: _general]",
    ],
)
def test_section_headers_present(tmp_path: Path, header: str) -> None:
    out = compose_criteria(
        _make_read_file(tmp_path), type="benchmark", role="paper-critic"
    )
    assert header in out
