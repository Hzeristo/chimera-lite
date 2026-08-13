"""Phase L.B.2 externalized triage — ``filter_service.py`` is now a bare data primitive: NO LLM
call, no ``FilterService`` class. ``analyze_paper_data`` resolves an already-converted paper's
markdown path + a small metadata dict for the ``chimera-triage-paper`` skill's Haiku subagent to
read directly. All deps injected (a stub settings object) — no real config/vault/network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from filter_service import analyze_paper_data


class _StubPaperMiner:
    def __init__(self, md_papers_dir: Path) -> None:
        self.md_papers_dir = md_papers_dir


class _StubSettings:
    """Duck-typed ``ChimeraConfig`` stand-in — only the attributes ``analyze_paper_data`` (via
    ``get_paper_markdown``) actually reads."""

    def __init__(self, md_papers_dir: Path) -> None:
        self.project_root = md_papers_dir
        self._pm = _StubPaperMiner(md_papers_dir)

    @property
    def paper_miner_or_default(self) -> _StubPaperMiner:
        return self._pm


def test_analyze_paper_data_returns_markdown_path_and_metadata(tmp_path: Path) -> None:
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    (md_dir / "DemoPaper.md").write_text("# Demo Paper\nBody text.\n", encoding="utf-8")

    result = analyze_paper_data("DemoPaper", settings=_StubSettings(md_dir))

    assert result["markdown_path"] == str(md_dir / "DemoPaper.md")
    assert result["metadata"]["id"] == "DemoPaper"
    assert result["metadata"]["title"] == "DemoPaper"
    assert "content_path" in result["metadata"]


def test_analyze_paper_data_missing_raises(tmp_path: Path) -> None:
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        analyze_paper_data("DemoPaper", settings=_StubSettings(md_dir))


def test_filter_service_has_no_filterservice_class() -> None:
    # L.B.2 retired the FilterService class + its generate_structured_data LLM call entirely —
    # only the deterministic analyze_paper_data primitive remains (H-1 friction resolved).
    import filter_service

    assert not hasattr(filter_service, "FilterService")


def test_filter_service_makes_no_generate_structured_data_call() -> None:
    import inspect

    import filter_service

    source = inspect.getsource(filter_service)
    assert "generate_structured_data" not in source
