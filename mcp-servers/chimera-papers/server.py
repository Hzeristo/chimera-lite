"""chimera-papers MCP server — arXiv mining + daily pipeline (long-running, poll model).

Long-running tools return a task_id immediately; poll check_task_status. A process-wide
lock + TaskService.has_active_long_task() reject a second pipeline while one runs — the one
place this thin adapter intentionally holds logic (Phase M cross-finding #4).
"""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

import miner_tools
from task_service import get_task_service

mcp = FastMCP("chimera-papers")

# Serialize the check-and-start critical section so two concurrent calls cannot both pass
# the busy check. TaskService persists PENDING synchronously, so the guard is race-free.
_start_lock = asyncio.Lock()

_PIPELINE_NOT_WIRED = (
    "[chimera-papers] daily_paper_pipeline is not wired yet (migration sprint M.2b)."
)


def _busy_message() -> str:
    return (
        "[Busy] A long-running task is already in progress. Poll check_task_status "
        "first — only one arXiv/pipeline job runs at a time."
    )


@mcp.tool()
async def arxiv_miner(query: str, max_results: int = 5) -> str:
    """Fetch papers from arXiv and process them into Markdown.

    Long-running: returns a ``task_id`` immediately. Poll with ``check_task_status``.

    Args:
        query: arXiv / literature search query string (non-empty).
        max_results: How many papers to fetch (1–2000; default 5).
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
        return await miner_tools.arxiv_miner(query, max_results=max_results)


@mcp.tool()
async def daily_paper_pipeline(
    arxiv_query: str | None = None,
    arxiv_max_results: int | None = None,
    skip_telegram: bool = False,
) -> str:
    """Run the full daily paper pipeline (long-running). Returns a ``task_id``; poll
    ``check_task_status``. Wired in M.2b (under the same concurrency guard).

    Args:
        arxiv_query: Optional override for the configured arXiv query.
        arxiv_max_results: Optional cap on arXiv results (1–2000).
        skip_telegram: If true, skip the Telegram broadcast step.
    """
    return _PIPELINE_NOT_WIRED


@mcp.tool()
async def check_task_status(task_id: str) -> str:
    """Return status or result for a background task (read-only poll).

    Args:
        task_id: Identifier returned when starting a long-running task.
    """
    return await miner_tools.check_task_status(task_id)


if __name__ == "__main__":
    mcp.run()
