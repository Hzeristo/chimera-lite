"""Regression: MinerU 3.x nests a per-backend parse dir; the markdown lookup must follow it.

Bug (incident 2026-08-10-mineru-3x-drift): ``convert()`` probed the MinerU 2.x flat path
``<out>/<stem>/<stem>.md``, which never exists on 3.x — MinerU nests one level
(``mineru/cli/output_paths.py::build_parse_dir``): ``<method>`` for pipeline, ``vlm`` for
vlm-*, ``hybrid_<method>`` for hybrid-*. Nothing failed loudly: every convert limped through
the recursive fallback, and the same dead probe served as the exists-check, so conversion
silently stopped being idempotent and re-converted from scratch every call.

These tests pin the resolution ORDER against fake trees, so the next MinerU layout change
fails here instead of drifting for another few months.
"""

from __future__ import annotations

from pathlib import Path

from ports.ingest.paper2md import _resolve_output_markdown

STEM = "2606.32007"


def _write(path: Path, text: str = "# md\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_finds_markdown_in_hybrid_parse_dir(tmp_path: Path) -> None:
    target = tmp_path / STEM
    expected = _write(target / "hybrid_auto" / f"{STEM}.md")
    assert _resolve_output_markdown(target, STEM) == expected


def test_finds_markdown_in_pipeline_and_vlm_parse_dirs(tmp_path: Path) -> None:
    for parse_dir in ("auto", "txt", "ocr", "vlm", "hybrid_txt"):
        target = tmp_path / parse_dir / STEM
        expected = _write(target / parse_dir / f"{STEM}.md")
        assert _resolve_output_markdown(target, STEM) == expected


def test_still_finds_the_legacy_flat_layout(tmp_path: Path) -> None:
    """MinerU < 3 wrote the markdown flat — an older raw dir on disk must still resolve."""
    target = tmp_path / STEM
    expected = _write(target / f"{STEM}.md")
    assert _resolve_output_markdown(target, STEM) == expected


def test_nested_parse_dir_wins_over_an_unrelated_stray(tmp_path: Path) -> None:
    """A stray README must not be preferred over the real, stem-named output."""
    target = tmp_path / STEM
    _write(target / "hybrid_auto" / "README.md", "stray\n")
    expected = _write(target / "hybrid_auto" / f"{STEM}.md")
    assert _resolve_output_markdown(target, STEM) == expected


def test_falls_back_to_recursive_scan_when_no_stem_named_markdown(tmp_path: Path) -> None:
    target = tmp_path / STEM
    only = _write(target / "hybrid_auto" / "output.md")
    assert _resolve_output_markdown(target, STEM) == only


def test_returns_none_when_nothing_was_produced(tmp_path: Path) -> None:
    target = tmp_path / STEM
    target.mkdir(parents=True)
    assert _resolve_output_markdown(target, STEM) is None
    # A convert that never created the folder at all must not raise either.
    assert _resolve_output_markdown(tmp_path / "absent", STEM) is None
