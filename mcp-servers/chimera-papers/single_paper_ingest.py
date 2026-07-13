"""Single-paper ingest: one PDF (or arXiv id) → MinerU convert → triage → Knowledge node.

Migrates project_chimera's ``run_ingest`` single-paper path, which Phase M did not wire to
MCP (only the batch daily pipeline was). This is the SAME per-paper logic as
``batch_filter_workflow`` (load → FilterService.evaluate_paper → write_knowledge_node) run
for exactly one paper, over the Rule-10-compliant MinerU convert in ``ports.ingest``.

Deliberately does NOT invoke ``OpticsService.irradiate`` (oligo-era deep-read LLM, retired).
Deep reading is now: ``ingest_paper`` → ``read_vault_file`` → an N.A lens skill → ``create_node``.
This path stops at convert → triage → K node.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

import requests

from bootstrap import build_openai_client
from core.config import ChimeraConfig, get_config
from filter_service import FilterService
from ports.arxiv.arxiv_fetch import ArxivFetcher
from ports.ingest.mineru_pipeline import ingest_to_papers
from ports.papers.paper_loader import PaperLoader
from ports.prompts.jinja_prompt_manager import PromptManager
from ports.vault.vault_note_writer import VaultNoteWriter

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
    """Ingest ONE paper into a vault Knowledge node; return the written K-node path.

    ``arxiv_id`` → fetch the PDF first; ``pdf_path`` → convert directly. Always writes the
    K node (explicit ingest — no verdict gate). Never calls OpticsService.irradiate.

    Async so the MCP tool can stream stage progress via ``progress`` (``None`` in a direct call).
    The blocking steps (download, MinerU convert, triage LLM, vault write) run in worker threads so
    the event loop stays free; stage labels ALSO go to stderr (chimera-mcp-taste Rule #4 fallback).
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
    await report(0.15, "Converting PDF (MinerU)...")
    _staged_pdf, _raw_dir, clean_md = await asyncio.to_thread(
        ingest_to_papers, pdf_path=src_pdf, settings=settings
    )

    # Load → triage (FilterService, NOT OpticsService) → write the Knowledge node.
    await report(0.7, "Triaging (LLM)...")
    prompt_manager = PromptManager()
    paper = await asyncio.to_thread(PaperLoader().load_paper, clean_md)
    engine = FilterService(
        llm_client=build_openai_client(settings), prompt_manager=prompt_manager
    )
    result = await asyncio.to_thread(engine.evaluate_paper, paper)

    await report(0.9, "Writing node...")
    writer = VaultNoteWriter(settings=settings, prompt_manager=prompt_manager)
    out_path = await asyncio.to_thread(writer.write_knowledge_node, paper, result)
    await report(1.0, "Done")
    logger.info("[Ingest] Knowledge node written: %s", out_path)
    return out_path
