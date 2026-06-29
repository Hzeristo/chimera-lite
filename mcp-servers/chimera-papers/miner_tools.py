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
