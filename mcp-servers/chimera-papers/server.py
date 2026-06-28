"""chimera-papers MCP server — arXiv mining and the daily paper pipeline.

AUTHORITATIVE tool contract for the paper-mining surface migrated from oligo's
``miner_tools.py``. The heavy work is long-running and runs through ``TaskService``
(already copied into this package): the start tools return a ``task_id`` immediately;
``check_task_status`` polls it. This is the poll model — Claude Code re-engages on a
later turn, rather than the old in-request AWAITING_TASK suspension.

Migration status (see CLAUDE.md): the copied domain code still imports
``from src.crucible…`` / ``from src.oligo…`` and references not-yet-ported modules
(config, schemas, naming). Each tool lazy-imports its implementation; until sprint 1
rewires those imports, calls return ``_NOT_WIRED`` and the server still starts.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("chimera-papers")

_NOT_WIRED = (
    "[chimera-papers] Tool contract is live, but the domain implementation is not "
    "wired yet (migration sprint 1). Pending: rewrite src.crucible/src.oligo imports "
    "to the flat package layout and port config/schemas/naming."
)


def _papers_root() -> str:
    """Papers output dir from the env var set in .mcp.json (empty string if unset)."""
    return os.environ.get("CHIMERA_PAPERS_ROOT", "")


def _as_text(out: object) -> str:
    """Normalize a domain return (str or ToolOutput-like) to a string."""
    return getattr(out, "text", None) or str(out)


@mcp.tool()
async def arxiv_miner(query: str, max_results: int = 5) -> str:
    """Fetch papers from arXiv and process them into Markdown.

    Long-running: returns a ``task_id`` immediately. Poll with ``check_task_status``.

    Args:
        query: arXiv / literature search query string (non-empty).
        max_results: How many papers to fetch (1–2000; default 5).
    """
    try:
        from miner_tools import arxiv_miner as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(query, max_results=max_results))


@mcp.tool()
async def daily_paper_pipeline(
    arxiv_query: str | None = None,
    arxiv_max_results: int | None = None,
    skip_telegram: bool = False,
) -> str:
    """Run the full daily paper pipeline (long-running).

    Returns a ``task_id`` immediately. Poll with ``check_task_status``. Do not start
    a second run while one is in progress — check status first.

    Args:
        arxiv_query: Optional override for the configured arXiv query.
        arxiv_max_results: Optional cap on arXiv results (1–2000).
        skip_telegram: If true, skip the Telegram broadcast step.
    """
    try:
        from miner_tools import daily_paper_pipeline as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(
        await _impl(
            arxiv_query=arxiv_query,
            arxiv_max_results=arxiv_max_results,
            skip_telegram=skip_telegram,
        )
    )


@mcp.tool()
async def check_task_status(task_id: str) -> str:
    """Return status or result for a background task (read-only poll).

    Args:
        task_id: Identifier returned when starting a long-running task.
    """
    try:
        from miner_tools import check_task_status as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(task_id))


if __name__ == "__main__":
    mcp.run()
