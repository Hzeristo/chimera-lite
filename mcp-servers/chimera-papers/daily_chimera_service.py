"""Daily Chimera pipeline: fetch → convert → notify (Phase L.B.2 externalized — TRIAGE half,
commit 2/2).

The LLM triage stage (formerly ``batch_filter_workflow.filter_queue_worker``) is RETIRED — this
pipeline makes NO LLM call and writes NO Knowledge node. It fetches arXiv PDFs and MinerU-converts
them to Markdown, then tells the Architect how many landed and points at the explicit
``chimera-triage-paper`` skill (Haiku subagent → ``write_scout_card``) to turn them into scout-tier
inbox cards. Judgment lives in Claude Code skills, never here (D2).
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import NamedTuple

from core.config import ChimeraConfig, get_config, PaperMinerSettings
from core.schemas import ToolOutput
from ports.notify.telegram_notifier import TelegramNotifier
from ports.arxiv.arxiv_fetch import ArxivFetcher
from ports.ingest.mineru_pipeline import convert_queue_worker
from task_service import TaskService

logger = logging.getLogger(__name__)


class DailyPipelineStage:
    ARXIV_FETCH = ("arxiv_fetch", "Fetching from arXiv")
    PDF_INGESTION = ("pdf_ingestion", "Converting PDF → Markdown via MinerU")
    TELEGRAM_NOTIFY = ("telegram_notify", "Sending Telegram digest")


class PipelineCounts(NamedTuple):
    """Fetch/convert tallies. L.B.2 dropped the triage verdict tallies (must_read/skim/reject
    counts, per-item titles) — this pipeline no longer judges papers, so there is nothing beyond
    fetch/convert left to count."""

    new_pdfs: int
    ingested: int
    convert_failures: int


def _merge_arxiv_overrides(
    settings: ChimeraConfig,
    arxiv_query: str | None,
    arxiv_max_results: int | None,
) -> ChimeraConfig:
    """Return config with paper_miner arxiv_query / arxiv_max_results overridden when set."""
    if arxiv_query is None and arxiv_max_results is None:
        return settings
    pm: PaperMinerSettings = settings.paper_miner_or_default
    updates: dict[str, str | int] = {}
    if arxiv_query is not None:
        q = str(arxiv_query).strip()
        if q:
            updates["arxiv_query"] = q
    if arxiv_max_results is not None:
        try:
            n = int(arxiv_max_results)
            updates["arxiv_max_results"] = max(1, min(n, 2000))
        except (TypeError, ValueError):
            pass
    if not updates:
        return settings
    new_pm = pm.model_copy(update=updates)
    return settings.model_copy(update={"paper_miner": new_pm})


def _update_task_progress(
    task_service: TaskService | None,
    task_id: str | None,
    progress: float,
    message: str,
) -> None:
    if task_service is not None and task_id is not None:
        task_service.update_progress(task_id, progress, message)


async def _drain_md_queue(md_queue: asyncio.Queue[Path | None]) -> None:
    """Drain ``md_queue`` to its sentinel.

    L.B.2 removed the ``filter_queue_worker`` consumers that used to drain this bounded queue
    (maxsize=5). Without a drain, ``convert_queue_worker`` would block on ``put()`` once the
    queue fills, deadlocking any batch of more than 5 PDFs — this coroutine is the queue's only
    remaining consumer, and does nothing else (no triage, no LLM call).
    """
    while True:
        md_path = await md_queue.get()
        if md_path is None:
            break


def run_daily_pipeline(
    settings: ChimeraConfig | None = None,
    *,
    arxiv_query: str | None = None,
    arxiv_max_results: int | None = None,
    skip_telegram: bool = False,
    task_id: str | None = None,
    task_service: TaskService | None = None,
) -> str:
    """Full Chimera daily path with producer-consumer pipelining.

    Two concurrent stages joined by bounded queues:
      download (semaphore=3) → pdf_queue → convert (single GPU worker) → md_queue → drain

    Writes NO Knowledge node and makes NO LLM call (L.B.2) — triage is a separate, explicitly
    invoked step (the ``chimera-triage-paper`` skill). Returns a short text summary.
    """
    summary, _counts = asyncio.run(
        _run_pipelined_async(
            settings=settings,
            arxiv_query=arxiv_query,
            arxiv_max_results=arxiv_max_results,
            skip_telegram=skip_telegram,
            task_id=task_id,
            task_service=task_service,
        )
    )
    return summary


async def run_daily_pipeline_with_stage_events(
    *,
    task_id: str,
    task_service: TaskService,
    settings: ChimeraConfig | None = None,
    arxiv_query: str | None = None,
    arxiv_max_results: int | None = None,
    skip_telegram: bool = False,
) -> str:
    """Async path for task bus + SSE consumers. Delegates to the same pipelined core."""
    if settings is None:
        settings = get_config()
    summary, _counts = await _run_pipelined_async(
        settings=settings,
        arxiv_query=arxiv_query,
        arxiv_max_results=arxiv_max_results,
        skip_telegram=skip_telegram,
        task_id=task_id,
        task_service=task_service,
    )
    # L.B.2: no verdict-tagged K nodes come out of this pipeline anymore, so there is nothing to
    # surface as a side-channel Artifact — the converted papers await the chimera-triage-paper
    # skill, which writes its own inbox cards later.
    return ToolOutput(text=summary).model_dump_json()


async def _run_pipelined_async(
    settings: ChimeraConfig | None,
    *,
    arxiv_query: str | None,
    arxiv_max_results: int | None,
    skip_telegram: bool,
    task_id: str | None,
    task_service: TaskService | None,
) -> tuple[str, PipelineCounts]:
    """Core pipeline: download → convert → notify, two concurrent stages via asyncio.Queue.

    L.B.2 dropped the third (filter) stage entirely — nothing judges the converted papers here;
    the ``chimera-triage-paper`` skill does that afterwards, explicitly invoked, via its own
    Haiku subagent + ``write_scout_card``.

    Returns ``(summary_str, PipelineCounts)`` so both the sync wrapper and the stage-events
    wrapper can build their own return value from the same data.
    """
    if settings is None:
        settings = get_config()
    settings = _merge_arxiv_overrides(settings, arxiv_query, arxiv_max_results)
    settings.ensure_directories()

    logger.info("[Service] === Chimera Daily Pipeline Started (pipelined) ===")
    pm = settings.paper_miner_or_default

    if task_service is not None and task_id is not None:
        await task_service.start_stage(
            task_id,
            stage_id=DailyPipelineStage.ARXIV_FETCH[0],
            stage_label=DailyPipelineStage.ARXIV_FETCH[1],
            overall_progress=0.0,
        )

    fetcher = ArxivFetcher(settings=settings)
    paper_records = await asyncio.to_thread(fetcher.fetch_metadata)
    new_pdfs_count_holder: list[int] = [0]
    logger.info("[Service] Arxiv metadata fetched. records=%s", len(paper_records))
    _update_task_progress(
        task_service, task_id, 0.1, f"Metadata fetched ({len(paper_records)} records). Starting pipeline..."
    )

    pdf_queue: asyncio.Queue[Path | None] = asyncio.Queue(maxsize=5)
    md_queue: asyncio.Queue[Path | None] = asyncio.Queue(maxsize=5)
    download_sem = asyncio.Semaphore(3)

    normalized_raw = pm.md_papers_raw_dir.resolve()
    normalized_clean = pm.md_papers_dir.resolve()

    async def _download_stage() -> None:
        count = await fetcher.download_pdfs_to_queue(
            paper_records=paper_records,
            target_dir=pm.arxivpdf_dir,
            pdf_queue=pdf_queue,
            semaphore=download_sem,
        )
        new_pdfs_count_holder[0] = count
        _update_task_progress(
            task_service, task_id, 0.2, f"Downloads done ({count} new PDFs). Converting..."
        )

    if task_service is not None and task_id is not None:
        await task_service.start_stage(
            task_id,
            stage_id=DailyPipelineStage.PDF_INGESTION[0],
            stage_label=DailyPipelineStage.PDF_INGESTION[1],
            overall_progress=0.2,
        )

    drain_task = asyncio.create_task(_drain_md_queue(md_queue), name="md-drain")
    convert_task = asyncio.create_task(
        convert_queue_worker(pdf_queue, md_queue, normalized_raw, normalized_clean),
        name="convert-worker",
    )
    download_task = asyncio.create_task(_download_stage(), name="download-stage")

    await asyncio.gather(download_task, convert_task, drain_task)

    ingested_count, convert_failures = convert_task.result()
    new_pdfs_count = new_pdfs_count_holder[0]

    logger.info(
        "[Service] Pipeline stages done. new_pdfs=%s ingested=%s convert_failed=%s",
        new_pdfs_count, ingested_count, convert_failures,
    )

    # I-5 anti-hollow-success guard: a run that downloaded PDFs but converted NONE is a
    # failure, not a clean completion. Raise so the task is marked FAILED (was: silently
    # reported ingested=0 errors=0 completed). Preserved verbatim across the L.B.2 rewrite.
    if new_pdfs_count > 0 and ingested_count == 0:
        raise RuntimeError(
            f"MinerU converted 0 of {new_pdfs_count} downloaded PDFs "
            f"({convert_failures} failed) — pipeline aborted. See [Ingest] logs for cause."
        )

    _update_task_progress(
        task_service,
        task_id,
        0.7,
        f"Convert done: ingested={ingested_count} convert_failed={convert_failures}. "
        f"Awaiting triage.",
    )

    counts = PipelineCounts(
        new_pdfs=new_pdfs_count, ingested=ingested_count, convert_failures=convert_failures
    )

    if not skip_telegram:
        if task_service is not None and task_id is not None:
            await task_service.start_stage(
                task_id,
                stage_id=DailyPipelineStage.TELEGRAM_NOTIFY[0],
                stage_label=DailyPipelineStage.TELEGRAM_NOTIFY[1],
                overall_progress=0.9,
            )
        report_message = _render_daily_report(counts)
        notifier = TelegramNotifier(settings=settings)
        await asyncio.to_thread(notifier.send_summary, html_message=report_message)
        _update_task_progress(task_service, task_id, 0.99, "Telegram sent.")
    else:
        _update_task_progress(task_service, task_id, 0.99, "Telegram skipped.")

    summary = (
        f"Daily pipeline completed. new_pdfs={new_pdfs_count} ingested={ingested_count} "
        f"convert_failed={convert_failures} telegram={'no' if skip_telegram else 'yes'}. "
        f"{ingested_count} paper(s) converted, awaiting triage — run the chimera-triage-paper skill."
    )
    logger.info("[Service] %s", summary)
    return summary, counts


def _render_daily_report(counts: PipelineCounts) -> str:
    """Minimal convert-count Telegram digest.

    L.B.2 dropped the verdict digest (must_read/skim links, per-item score lines) — this
    pipeline no longer judges anything, so notify only reports what converted and points at the
    explicit ``chimera-triage-paper`` skill for the next step.
    """
    lines: list[str] = [
        "🚨 <b>[BB Channel] Chimera Morning Broadcast</b> 🚨",
        "━━━━━━━━━━━━━━━━━━━━",
        '"Good morning, Senpai~ ♡ Here is today\'s freshly-converted haul — awaiting triage."',
        "",
        f"📥 New PDFs fetched: <b>{int(counts.new_pdfs)}</b>",
        f"📄 Converted → Markdown: <b>{int(counts.ingested)}</b>",
    ]
    if counts.convert_failures:
        lines.append(f"⚠️ Convert failures: <b>{int(counts.convert_failures)}</b>")
    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🧪 {int(counts.ingested)} paper(s) ready — run the <code>chimera-triage-paper</code> "
        f"skill to screen them into scout-tier Knowledge cards.",
    ]
    return "\n".join(lines).strip()
