"""chimera-papers MCP server — arXiv mining + daily pipeline (long-running, poll model).

Long-running tools return a task_id immediately; poll check_task_status. A process-wide
lock + TaskService.has_active_long_task() reject a second pipeline while one runs — the one
place this thin adapter intentionally holds logic (Phase M cross-finding #4).
"""

from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import Context, FastMCP

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

logger = logging.getLogger(__name__)

mcp = FastMCP("chimera-papers")

# Serialize the check-and-start critical section so two concurrent calls cannot both pass
# the busy check. TaskService persists PENDING synchronously, so the guard is race-free.
_start_lock = asyncio.Lock()


def _busy_message() -> str:
    return (
        "[Busy] A long-running task is already in progress. Poll check_task_status "
        "first — only one arXiv/pipeline job runs at a time."
    )


def _reporter(ctx: Context) -> Callable[[float, str], Awaitable[None]]:
    """Adapt the FastMCP ``ctx`` into the domain layer's ``progress(frac, msg)`` callback — emitting
    MCP progress notifications at stage boundaries. Best-effort: a notification failure never aborts
    the tool (the domain function also logs each stage to stderr, chimera-mcp-taste Rule #4)."""

    async def report(frac: float, msg: str) -> None:
        try:
            await ctx.report_progress(frac, 1.0, msg)
        except Exception:  # noqa: BLE001 — progress is decorative; never fail the tool over it
            logger.debug("progress notification failed", exc_info=True)

    return report


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
    """Run the full BATCH daily paper pipeline — arXiv sweep by query → ingest → filter → notify
    (long-running). Returns a ``task_id``; poll ``check_task_status``. Subject to the
    single-pipeline concurrency guard.

    For a SINGLE already-known paper (by arXiv id or a local PDF), use ``ingest_paper`` instead.

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
async def ingest_paper(
    ctx: Context, arxiv_id: str | None = None, pdf_path: str | None = None
) -> str:
    """Add ONE specific, already-known paper to the vault as a Knowledge node (single-paper ingest).

    WHEN: you have a particular paper to bring into the vault — identified by an arXiv id
    (e.g. "2604.14004") OR a local PDF path. Fits requests like "add paper 2604.14004 to the
    vault", "ingest this PDF into my Knowledge base", "get <paper> into the vault".
    WHAT: PDF → Markdown (MinerU on GPU) → triage → a vault Knowledge node; returns the node path.
    Synchronous (no task_id).

    For the BATCH daily arXiv sweep — many papers pulled by a search query, not one known paper —
    use ``daily_paper_pipeline`` instead, NOT this tool.

    Deep reading is a separate step afterwards: ``read_vault_file`` + an N.A lens skill.
    Rejected while a long-running arXiv/pipeline job is active (shared GPU / MinerU).

    Args:
        arxiv_id: arXiv identifier to fetch + ingest (e.g. "2604.14004").
        pdf_path: Path to a local PDF to ingest directly (absolute, or project-relative).
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
    return await miner_tools.ingest_paper(
        arxiv_id=arxiv_id, pdf_path=pdf_path, progress=_reporter(ctx)
    )


@mcp.tool()
async def extract_paper(paper_id: str, ctx: Context) -> str:
    """Extract ONE already-ingested paper into a STAGED Knowledge node — mechanism-level claims
    plus citation-grounded ``derives_from`` edges (Phase Q disciplined extraction).

    WHEN: you want to (re)distill a paper already in the vault into a reviewable Knowledge node with
    typed edges — e.g. backfilling the graph. Reuses the paper's converted markdown (no MinerU).
    WHAT: markdown → 1-5 mechanism claims + citation-resolved edges (or ``grounded: no_prior_match``)
    → a node in ``docs/staging/`` for review. Writes NO Insight/Thought/Decision node and never
    auto-promotes into the vault. Returns the staging path.

    Args:
        paper_id: arXiv identifier of an already-ingested paper (e.g. "2305.16291").
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
    return await miner_tools.extract_paper(paper_id, progress=_reporter(ctx))


@mcp.tool()
async def check_task_status(task_id: str) -> str:
    """Return status or result for a background task (read-only poll).

    Args:
        task_id: Identifier returned when starting a long-running task.
    """
    return await miner_tools.check_task_status(task_id)


if __name__ == "__main__":
    mcp.run()
