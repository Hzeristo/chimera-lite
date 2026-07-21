"""Phase L.B.2 externalized triage — ``single_paper_ingest.py``:

- ``ingest_single_paper`` is now fetch+convert ONLY (no LLM call, no vault write) — returns the
  converted markdown path.
- ``write_scout_card`` is the deterministic write half, called AFTER a subagent has already
  produced a ``PaperAnalysisResult`` verdict (the ``chimera-triage-paper`` skill's job) — writes
  ONE inbox card at ``chimera_tier="scout"``, never to ``Harness/``.

Heavy I/O (download, MinerU convert) is mocked throughout — no real network, no real MinerU/GPU
run. Paper ids used here are deliberately NOT arxiv-shaped (e.g. "DemoPaper") so
``PaperLoader.load_paper`` takes its no-metadata branch and never attempts a real arXiv network
fetch.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import single_paper_ingest
from core.schemas import PaperAnalysisResult
from ports.vault.vault_note_writer import VaultNoteWriter


class _StubPaperMiner:
    def __init__(self, tmp_path: Path) -> None:
        self.arxivpdf_dir = tmp_path / "arxivpdf"
        self.md_papers_dir = tmp_path / "md_papers"
        self.md_papers_raw_dir = tmp_path / "md_papers_raw"


class _StubSettings:
    """Duck-typed ``ChimeraConfig`` stand-in — only the attributes the delegates read."""

    def __init__(self, tmp_path: Path) -> None:
        self.project_root = tmp_path
        self._pm = _StubPaperMiner(tmp_path)
        self._inbox = tmp_path / "inbox"

    @property
    def paper_miner_or_default(self) -> _StubPaperMiner:
        return self._pm

    def require_path(self, field_name: str) -> Path:
        if field_name == "inbox_folder":
            return self._inbox
        raise ValueError(field_name)


# --- ingest_single_paper: fetch + convert only, no vault write ------------------------------


async def test_ingest_single_paper_arxiv_id_returns_markdown_no_vault_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_pdf = tmp_path / "arxivpdf" / "2604.14004.pdf"
    fake_pdf.parent.mkdir(parents=True, exist_ok=True)
    fake_pdf.write_bytes(b"%PDF-fake")
    fake_md = tmp_path / "md_papers" / "2604.14004.md"

    fetch_calls: list[str] = []
    convert_calls: list[Path] = []

    def _fake_fetch(arxiv_id, settings):  # noqa: ANN001
        fetch_calls.append(arxiv_id)
        return fake_pdf

    def _fake_ingest_to_papers(*, pdf_path, settings):  # noqa: ANN001
        convert_calls.append(pdf_path)
        return (fake_pdf, tmp_path / "md_papers_raw", fake_md)

    def _boom(self, paper, analysis):  # noqa: ANN001
        raise AssertionError("ingest_single_paper must never write a Knowledge node")

    monkeypatch.setattr(single_paper_ingest, "_fetch_arxiv_pdf", _fake_fetch)
    monkeypatch.setattr(single_paper_ingest, "ingest_to_papers", _fake_ingest_to_papers)
    monkeypatch.setattr(VaultNoteWriter, "write_knowledge_node", _boom)

    progress_calls: list[tuple[float, str]] = []

    async def _progress(frac: float, msg: str) -> None:
        progress_calls.append((frac, msg))

    result = await single_paper_ingest.ingest_single_paper(
        arxiv_id="2604.14004", settings=_StubSettings(tmp_path), progress=_progress
    )

    assert result == fake_md
    assert fetch_calls == ["2604.14004"]
    assert convert_calls == [fake_pdf]
    assert progress_calls[0][0] == 0.0
    assert progress_calls[-1] == (1.0, "Done")
    # no markdown / vault artifact actually created anywhere under tmp_path (mocked convert)
    assert list(tmp_path.rglob("*.md")) == []


async def test_ingest_single_paper_pdf_path_skips_fetch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = tmp_path / "local.pdf"
    pdf.write_bytes(b"%PDF-fake")
    fake_md = tmp_path / "md_papers" / "local.md"

    def _fake_ingest_to_papers(*, pdf_path, settings):  # noqa: ANN001
        return (pdf_path, tmp_path / "md_papers_raw", fake_md)

    def _boom_fetch(arxiv_id, settings):  # noqa: ANN001
        raise AssertionError("pdf_path ingest must never fetch")

    monkeypatch.setattr(single_paper_ingest, "_fetch_arxiv_pdf", _boom_fetch)
    monkeypatch.setattr(single_paper_ingest, "ingest_to_papers", _fake_ingest_to_papers)

    result = await single_paper_ingest.ingest_single_paper(
        pdf_path=str(pdf), settings=_StubSettings(tmp_path)
    )
    assert result == fake_md


async def test_ingest_single_paper_requires_arxiv_id_or_pdf_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires either"):
        await single_paper_ingest.ingest_single_paper(settings=_StubSettings(tmp_path))


def test_ingest_single_paper_makes_no_generate_structured_data_call() -> None:
    import inspect

    source = inspect.getsource(single_paper_ingest)
    assert "generate_structured_data" not in source
    assert "FilterService" not in source
    assert "build_openai_client" not in source


# --- write_scout_card: deterministic write half, called AFTER a subagent verdict -------------


def _analysis(verdict: str = "Skim") -> PaperAnalysisResult:
    return PaperAnalysisResult(
        verdict=verdict,
        short_moniker="DemoNet",
        score=6,
        novelty_delta="Modest gain over the baseline.",
        mechanism_summary="A gating mechanism routes tokens by relevance.",
    )


def test_write_scout_card_writes_inbox_scout_card(tmp_path: Path) -> None:
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    (md_dir / "DemoPaper.md").write_text("# Demo Paper\nBody text.\n", encoding="utf-8")

    out_path = single_paper_ingest.write_scout_card(
        "DemoPaper", _analysis("Skim"), settings=_StubSettings(tmp_path)
    )

    assert out_path.exists()
    assert out_path.parent.name == "Skim"
    assert out_path.parent.parent == tmp_path / "inbox"
    text = out_path.read_text(encoding="utf-8")
    assert "chimera_tier: scout" in text
    assert "DemoNet" in text


def test_write_scout_card_accepts_dict_analysis(tmp_path: Path) -> None:
    # The subagent's structured output arrives as JSON -> a plain dict through the MCP tool
    # boundary; write_scout_card must validate it into a PaperAnalysisResult itself.
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    (md_dir / "DemoPaper.md").write_text("# Demo Paper\n", encoding="utf-8")

    analysis = {
        "verdict": "Must Read",
        "short_moniker": "DemoNet",
        "score": 9,
        "novelty_delta": "Large gain.",
        "mechanism_summary": "Dense retrieval with a learned gate.",
    }

    out_path = single_paper_ingest.write_scout_card(
        "DemoPaper", analysis, settings=_StubSettings(tmp_path)
    )
    assert out_path.parent.name == "Must_Read"


def test_write_scout_card_missing_paper_raises(tmp_path: Path) -> None:
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        single_paper_ingest.write_scout_card(
            "Missing", _analysis(), settings=_StubSettings(tmp_path)
        )
