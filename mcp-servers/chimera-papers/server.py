"""chimera-papers MCP server — arXiv mining + daily pipeline (long-running, poll model).

Long-running tools return a task_id immediately; poll check_task_status. A process-wide
lock + TaskService.has_active_long_task() reject a second pipeline while one runs — the one
place this thin adapter intentionally holds logic (Phase M cross-finding #4).
"""

from __future__ import annotations

import asyncio
import logging
import sys

from mcp.server.fastmcp import FastMCP

import miner_tools
from task_service import get_task_service

# Logs MUST go to stderr — stdout is the MCP JSON-RPC channel; printing there corrupts the
# protocol. Without this handler the entire pipeline (progress + background-task tracebacks)
# is invisible to the user. Bracket-prefixed format matches the project logging standard.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

mcp = FastMCP("chimera-papers")

# Serialize the check-and-start critical section so two concurrent calls cannot both pass
# the busy check. TaskService persists PENDING synchronously, so the guard is race-free.
_start_lock = asyncio.Lock()


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
    ``check_task_status``. Subject to the same single-pipeline concurrency guard.

    Args:
        arxiv_query: Optional override for the configured arXiv query.
        arxiv_max_results: Optional cap on arXiv results (1–2000).
        skip_telegram: If true, skip the Telegram broadcast step.
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
        return await miner_tools.daily_paper_pipeline(
            arxiv_query=arxiv_query,
            arxiv_max_results=arxiv_max_results,
            skip_telegram=skip_telegram,
        )


@mcp.tool()
async def ingest_paper(arxiv_id: str | None = None, pdf_path: str | None = None) -> str:
    """Ingest a SINGLE paper into a vault Knowledge node — the single-paper counterpart to
    the batch daily pipeline. Pass an arXiv id (fetched) OR a local PDF path (converted
    directly). Converts via MinerU (GPU), triages (FilterService), writes the K node, and
    returns its path. Synchronous (no task_id). Deep reading is a separate step:
    ``read_vault_file`` + an N.A lens skill.

    Rejected while a long-running arXiv/pipeline job is active (they share the GPU / MinerU).

    Args:
        arxiv_id: arXiv identifier to fetch + ingest (e.g. "2604.14004").
        pdf_path: Path to a local PDF to ingest directly (absolute, or project-relative).
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
    return await miner_tools.ingest_paper(arxiv_id=arxiv_id, pdf_path=pdf_path)


@mcp.tool()
async def check_task_status(task_id: str) -> str:
    """Return status or result for a background task (read-only poll).

    Args:
        task_id: Identifier returned when starting a long-running task.
    """
    return await miner_tools.check_task_status(task_id)


if __name__ == "__main__":
    mcp.run()
