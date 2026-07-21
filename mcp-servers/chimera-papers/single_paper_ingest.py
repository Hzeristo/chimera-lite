"""Single-paper ingest: one PDF (or arXiv id) → MinerU convert → Markdown path (Phase L.B.2
externalized — TRIAGE half, commit 2/2).

Migrates project_chimera's ``run_ingest`` single-paper path, which Phase M did not wire to
MCP (only the batch daily pipeline was). ``ingest_single_paper`` is now a fetch+convert
primitive ONLY — it makes NO LLM call and writes NO Knowledge node. Verdict judgment moved to
the ``chimera-triage-paper`` skill's Haiku subagent (``chimera-paper-triager``); once triaged,
that skill calls this module's ``write_scout_card`` to write the scout-tier inbox card (D2 — the
MCP server is never the judge).

Deliberately does NOT invoke ``OpticsService.irradiate`` (oligo-era deep-read LLM, retired).
Deep reading is: ``ingest_paper`` → the ``chimera-triage-paper`` skill → (promoted) →
``chimera-deep-extract``. This module stops at convert (returning a markdown path) and, once
triaged elsewhere, at writing the scout card.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

import requests

from core.config import ChimeraConfig, get_config
from core.schemas import PaperAnalysisResult
from ports.arxiv.arxiv_fetch import ArxivFetcher
from ports.ingest.mineru_pipeline import ingest_to_papers
from ports.papers.paper_loader import PaperLoader
from ports.prompts.jinja_prompt_manager import PromptManager
from ports.vault.vault_note_writer import VaultNoteWriter
from single_paper_extract import get_paper_markdown

logger = logging.getLogger(__name__)


def _fetch_arxiv_pdf(arxiv_id: str, settings: ChimeraConfig) -> Path:
    """Download one arXiv PDF by id. Explicit ingest → bypasses the batch seen-filter;
    reuses ArxivFetcher's request headers. Returns the local PDF path."""
    pm = settings.paper_miner_or_default
    target_dir = pm.arxivpdf_dir
    if not target_dir.is_absolute():
        target_dir = (settings.project_root / target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = target_dir / f"{arxiv_id}.pdf"
    if pdf_path.exists():
        logger.info("[Ingest] arXiv PDF already present: %s", pdf_path.name)
        return pdf_path

    url = f"https://arxiv.org/pdf/{arxiv_id}"
    logger.info("[Ingest] Fetching arXiv PDF: %s", url)
    with requests.get(
        url, stream=True, headers=ArxivFetcher.REQUEST_HEADERS, timeout=60
    ) as resp:
        resp.raise_for_status()
        with pdf_path.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
    logger.info("[Ingest] Downloaded arXiv PDF: %s", pdf_path.name)
    return pdf_path


async def ingest_single_paper(
    *,
    arxiv_id: str | None = None,
    pdf_path: str | None = None,
    settings: ChimeraConfig | None = None,
    progress: Callable[[float, str], Awaitable[None]] | None = None,
) -> Path:
    """Fetch + convert ONE paper; return its converted markdown path. Makes NO LLM call and
    writes NO Knowledge node (L.B.2) — triage is a separate, explicitly invoked step (the
    ``chimera-triage-paper`` skill, which calls ``write_scout_card`` once judged).

    ``arxiv_id`` → fetch the PDF first; ``pdf_path`` → convert directly. Never calls
    OpticsService.irradiate.

    Async so the MCP tool can stream stage progress via ``progress`` (``None`` in a direct call).
    The blocking steps (download, MinerU convert) run in worker threads so the event loop stays
    free; stage labels ALSO go to stderr (chimera-mcp-taste Rule #4 fallback).
    """
    settings = settings or get_config()

    async def report(frac: float, msg: str) -> None:
        logger.info("[Ingest] %.0f%% — %s", frac * 100, msg)
        if progress is not None:
            await progress(frac, msg)

    if arxiv_id and arxiv_id.strip():
        await report(0.0, "Fetching arXiv PDF...")
        src_pdf = await asyncio.to_thread(_fetch_arxiv_pdf, arxiv_id.strip(), settings)
    elif pdf_path and pdf_path.strip():
        src_pdf = Path(pdf_path.strip()).expanduser()
    else:
        raise ValueError("ingest_single_paper requires either arxiv_id or pdf_path.")

    # Convert: the Rule-10-compliant MinerU path (creationflags + stdin=DEVNULL + temp-file
    # output) lives in ports.ingest.paper2md.MineruClient.convert, reused via ingest_to_papers.
    await report(0.3, "Converting PDF (MinerU)...")
    _staged_pdf, _raw_dir, clean_md = await asyncio.to_thread(
        ingest_to_papers, pdf_path=src_pdf, settings=settings
    )

    await report(1.0, "Done")
    logger.info("[Ingest] Converted markdown ready (no Knowledge node written): %s", clean_md)
    return clean_md


def write_scout_card(
    paper_id: str,
    analysis: PaperAnalysisResult | dict,
    settings: ChimeraConfig | None = None,
) -> Path:
    """Write ONE scout-tier Knowledge card from a subagent's triage verdict — the WRITE
    primitive the ``chimera-triage-paper`` skill calls last (L.B.2). Makes NO judgment call:
    ``analysis`` is already-decided (the skill's ``chimera-paper-triager`` subagent's verdict),
    accepted as a ``PaperAnalysisResult`` or a plain dict (a JSON payload arriving through the
    MCP tool boundary is a dict; validated via ``PaperAnalysisResult.model_validate``).

    Reuses ``single_paper_extract.get_paper_markdown`` for the same md-dir resolution the
    deep-read path uses, loads the ``Paper`` via ``PaperLoader``, and writes the card via
    ``VaultNoteWriter.write_knowledge_node`` — always to ``inbox/<verdict>/`` (``chimera_tier``
    is set by the ``knowledge_node.j2`` template to ``scout``), NEVER to ``Harness/``. Raises
    ``FileNotFoundError`` if the paper has not been converted yet.
    """
    cfg = settings or get_config()
    validated = (
        analysis
        if isinstance(analysis, PaperAnalysisResult)
        else PaperAnalysisResult.model_validate(analysis)
    )
    markdown_path = get_paper_markdown(paper_id, settings=cfg)
    paper = PaperLoader().load_paper(markdown_path)
    writer = VaultNoteWriter(settings=cfg, prompt_manager=PromptManager())
    out_path = writer.write_knowledge_node(paper, validated)
    logger.info("[Triage] Scout card written for %s: %s", paper_id, out_path)
    return out_path
