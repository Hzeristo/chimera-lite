"""L.2a: unit tests for the ``fetch_paper`` / ``convert_pdf_to_md`` bare primitives.

Both delegates lift existing node-coupled logic (``single_paper_ingest._fetch_arxiv_pdf`` and
``ports.ingest.paper2md.MineruClient.convert``) into standalone, node-free tools. Heavy I/O is
mocked throughout — no real network download, no real MinerU/GPU run. A stub ``settings`` object
is injected so ``MineruClient``'s output_root stays under ``tmp_path`` (never a real project dir).

Also asserts no vault node is ever written: ``VaultNoteWriter.write_knowledge_node`` and
``StagingService.create_staging_node`` are patched to raise if invoked — neither delegate imports
them, so this proves the "no vault node" contract rather than merely assuming it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import miner_tools
import single_paper_ingest
from ports.ingest.paper2md import MineruClient
from ports.vault.vault_note_writer import VaultNoteWriter
from staging_service import StagingService


class _StubPaperMiner:
    def __init__(self, raw_dir: Path) -> None:
        self.md_papers_raw_dir = raw_dir


class _StubSettings:
    """Duck-typed ``ChimeraConfig`` stand-in — only the attributes the delegates read."""

    def __init__(self, tmp_path: Path) -> None:
        self.project_root = tmp_path
        self.paper_miner_or_default = _StubPaperMiner(tmp_path / "md_papers_raw")


@pytest.fixture(autouse=True)
def _forbid_vault_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Neither primitive should ever reach the vault-write layer. Patch both writers to blow up
    loudly if a code path tries — a strong, behavioral proof of "writes NO vault node"."""

    def _boom_knowledge(self, paper, analysis):  # noqa: ANN001
        raise AssertionError("fetch_paper/convert_pdf_to_md must never write a Knowledge node")

    def _boom_staging(self, **kwargs):  # noqa: ANN001
        raise AssertionError("fetch_paper/convert_pdf_to_md must never write a staging node")

    monkeypatch.setattr(VaultNoteWriter, "write_knowledge_node", _boom_knowledge)
    monkeypatch.setattr(StagingService, "create_staging_node", _boom_staging)


async def test_fetch_paper_returns_pdf_path_no_node(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_pdf = tmp_path / "arxivpdf" / "2604.14004.pdf"
    fake_pdf.parent.mkdir(parents=True, exist_ok=True)
    fake_pdf.write_bytes(b"%PDF-fake")

    calls: list[tuple[str, object]] = []

    def _fake_fetch(arxiv_id, settings):  # noqa: ANN001
        calls.append((arxiv_id, settings))
        return fake_pdf

    monkeypatch.setattr(single_paper_ingest, "_fetch_arxiv_pdf", _fake_fetch)

    result = await miner_tools.fetch_paper("2604.14004", settings=_StubSettings(tmp_path))

    assert str(fake_pdf) in result
    assert calls and calls[0][0] == "2604.14004"
    # no markdown / vault artifact created anywhere under tmp_path
    assert list(tmp_path.rglob("*.md")) == []


async def test_fetch_paper_requires_arxiv_id() -> None:
    result = await miner_tools.fetch_paper("")
    assert "requires" in result and "arxiv_id" in result


async def test_fetch_paper_surfaces_fetch_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _fake_fetch(arxiv_id, settings):  # noqa: ANN001
        raise RuntimeError("network unreachable")

    monkeypatch.setattr(single_paper_ingest, "_fetch_arxiv_pdf", _fake_fetch)

    result = await miner_tools.fetch_paper("2604.14004", settings=_StubSettings(tmp_path))
    assert "[Fetch Error]" in result and "network unreachable" in result


async def test_convert_pdf_to_md_with_pdf_path_no_node(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-fake")
    fake_md = tmp_path / "md_papers_raw" / "paper" / "paper.md"

    calls: list[Path] = []

    def _fake_convert(self, pdf_path):  # noqa: ANN001
        calls.append(pdf_path)
        return fake_md

    monkeypatch.setattr(MineruClient, "convert", _fake_convert)

    result = await miner_tools.convert_pdf_to_md(
        pdf_path=str(pdf), settings=_StubSettings(tmp_path)
    )

    assert str(fake_md) in result
    assert calls == [pdf]  # converted the given pdf_path directly — no fetch involved
    assert list(tmp_path.rglob("*.md")) == []  # nothing actually written to disk (mocked convert)


async def test_convert_pdf_to_md_with_arxiv_id_fetches_then_converts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fetched_pdf = tmp_path / "arxivpdf" / "2604.14004.pdf"
    fetched_pdf.parent.mkdir(parents=True, exist_ok=True)
    fetched_pdf.write_bytes(b"%PDF-fake")
    fake_md = tmp_path / "md_papers_raw" / "2604.14004" / "2604.14004.md"

    fetch_calls: list[str] = []
    convert_calls: list[Path] = []

    def _fake_fetch(arxiv_id, settings):  # noqa: ANN001
        fetch_calls.append(arxiv_id)
        return fetched_pdf

    def _fake_convert(self, pdf_path):  # noqa: ANN001
        convert_calls.append(pdf_path)
        return fake_md

    monkeypatch.setattr(single_paper_ingest, "_fetch_arxiv_pdf", _fake_fetch)
    monkeypatch.setattr(MineruClient, "convert", _fake_convert)

    result = await miner_tools.convert_pdf_to_md(
        arxiv_id="2604.14004", settings=_StubSettings(tmp_path)
    )

    assert str(fake_md) in result
    assert fetch_calls == ["2604.14004"]
    assert convert_calls == [fetched_pdf]  # converted the FETCHED pdf, not something else


async def test_convert_pdf_to_md_requires_pdf_path_or_arxiv_id() -> None:
    result = await miner_tools.convert_pdf_to_md()
    assert "requires" in result
    assert "pdf_path" in result and "arxiv_id" in result


async def test_convert_pdf_to_md_surfaces_convert_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-fake")

    def _fake_convert(self, pdf_path):  # noqa: ANN001
        raise RuntimeError("mineru exploded")

    monkeypatch.setattr(MineruClient, "convert", _fake_convert)

    result = await miner_tools.convert_pdf_to_md(
        pdf_path=str(pdf), settings=_StubSettings(tmp_path)
    )
    assert "[Convert Error]" in result and "mineru exploded" in result
