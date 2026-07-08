"""Background miner tools — arXiv async fetch + task status (poll model).

Long-running tools return a ``task_id`` immediately; callers poll ``check_task_status``.
``daily_paper_pipeline`` is added in M.2b.
"""

from __future__ import annotations

import asyncio

from core.schemas import ToolOutput
from fetch_arxiv_workflow import fetch_and_process_arxiv
from task_service import TaskStatus, get_task_service


async def arxiv_miner(query: str, max_results: int = 5) -> str:
    """Start a background arXiv fetch+process task; return its task_id message."""
    if not (query and str(query).strip()):
        return "[Tool Error]: arxiv_miner requires a non-empty query string."
    try:
        n = int(max_results)
    except (TypeError, ValueError):
        n = 5
    n = max(1, min(n, 2000))

    task_service = get_task_service()
    task_id = task_service.create_task("arxiv_fetch")
    await task_service.emit_created(task_id)
    work = fetch_and_process_arxiv(
        str(query).strip(), n, task_id=task_id, task_service=task_service
    )
    asyncio.create_task(task_service.run_task(task_id, work))
    return (
        f"[Task Started] Arxiv mining task created: {task_id}\n"
        f"Use check_task_status({task_id!r}) to track progress."
    )


async def _run_daily_with_progress(
    task_id: str,
    arxiv_query: str | None,
    arxiv_max_results: int | None,
    skip_telegram: bool,
) -> str:
    # Lazy import: keep the heavy filter/ingest (MinerU) chain out of module load.
    from daily_chimera_service import run_daily_pipeline_with_stage_events

    task_service = get_task_service()
    return await run_daily_pipeline_with_stage_events(
        task_id=task_id,
        task_service=task_service,
        settings=None,
        arxiv_query=arxiv_query,
        arxiv_max_results=arxiv_max_results,
        skip_telegram=skip_telegram,
    )


async def daily_paper_pipeline(
    arxiv_query: str | None = None,
    arxiv_max_results: int | None = None,
    skip_telegram: bool = False,
) -> str:
    """Start the full daily pipeline (fetch → ingest → filter → notify); return task_id."""
    n: int | None
    if arxiv_max_results is None:
        n = None
    else:
        try:
            n = int(arxiv_max_results)
        except (TypeError, ValueError):
            n = None

    q_override: str | None = None
    if arxiv_query is not None and str(arxiv_query).strip():
        q_override = str(arxiv_query).strip()

    task_service = get_task_service()
    task_id = task_service.create_task("daily_pipeline")
    await task_service.emit_created(task_id)
    work = _run_daily_with_progress(task_id, q_override, n, bool(skip_telegram))
    asyncio.create_task(task_service.run_task(task_id, work))
    return (
        f"[Task Started] Daily pipeline: {task_id}\n"
        f"Use check_task_status({task_id!r}) to track progress."
    )


async def ingest_paper(
    arxiv_id: str | None = None, pdf_path: str | None = None
) -> str:
    """Ingest ONE paper (arXiv id or local PDF) into a vault Knowledge node.

    Synchronous — returns the written K-node path. The heavy MinerU convert + triage runs
    in a worker thread so the event loop is not blocked.
    """
    has_arxiv = bool(arxiv_id and str(arxiv_id).strip())
    has_pdf = bool(pdf_path and str(pdf_path).strip())
    if not has_arxiv and not has_pdf:
        return "[Tool Error]: ingest_paper requires arxiv_id or pdf_path."

    # Lazy import: keep the heavy MinerU / LLM chain out of module load (matches the
    # daily-pipeline lazy import).
    from single_paper_ingest import ingest_single_paper

    try:
        out_path = await asyncio.to_thread(
            ingest_single_paper,
            arxiv_id=(str(arxiv_id).strip() if has_arxiv else None),
            pdf_path=(str(pdf_path).strip() if has_pdf else None),
        )
    except FileNotFoundError as exc:
        return f"[Ingest Error] PDF not found: {exc}"
    except Exception as exc:  # network / MinerU / LLM / vault write
        return f"[Ingest Error] {exc}"
    return f"[✔] Knowledge node written: {out_path}"


async def check_task_status(task_id: str) -> str:
    """Return persisted status / progress / result for a background task."""
    tid = (task_id or "").strip()
    if not tid:
        return "[Tool Error]: check_task_status requires a non-empty task_id."
    task_service = get_task_service()
    try:
        task = task_service.get_task_status(tid)
    except FileNotFoundError:
        return f"[Task Error] Unknown task_id: {tid!r}"

    if task.status == TaskStatus.COMPLETED:
        body = task.result or ""
        try:
            return ToolOutput.model_validate_json(body).text
        except Exception:
            return f"[Task Completed] {body}"
    if task.status == TaskStatus.FAILED:
        return f"[Task Failed] {task.error}"
    if task.status == TaskStatus.RUNNING:
        msg = (task.progress_message or "").strip() or "Processing..."
        return f"[Task Running] Progress: {task.progress * 100:.0f}% - {msg}"
    if task.status == TaskStatus.PENDING:
        return "[Task Pending] Waiting to start..."
    label = str(task.status.value).upper()
    return f"[Task {label}] Progress: {task.progress * 100:.0f}%"
