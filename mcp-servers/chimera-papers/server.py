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
    """Run the full BATCH daily paper pipeline — arXiv sweep by query → fetch → convert → notify
    (long-running). Returns a ``task_id``; poll ``check_task_status``. Subject to the
    single-pipeline concurrency guard.

    Writes NO Knowledge node and makes NO LLM call (L.B.2) — triage of the converted papers is a
    separate, explicitly invoked step: the ``chimera-triage-paper`` skill.

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
    """Fetch + convert ONE specific, already-known paper to Markdown (single-paper ingest).

    WHEN: you have a particular paper to bring in for triage — identified by an arXiv id
    (e.g. "2604.14004") OR a local PDF path. Fits requests like "pull in paper 2604.14004",
    "convert this PDF", "get <paper> ready for triage".
    WHAT: PDF → Markdown (MinerU on GPU); returns the converted markdown path. Synchronous
    (no task_id). CONTRAST: writes NO Knowledge node and makes NO LLM call (L.B.2) — screening
    a converted paper into a scout-tier card is the separate, explicitly invoked
    ``chimera-triage-paper`` skill (its Haiku subagent reads the markdown itself, then calls
    ``write_scout_card``).

    For the BATCH daily arXiv sweep — many papers pulled by a search query, not one known paper —
    use ``daily_paper_pipeline`` instead, NOT this tool.

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
async def fetch_paper(arxiv_id: str) -> str:
    """Download ONE arXiv paper's PDF; writes NO vault node (bare fetch primitive).

    WHEN: you want the raw PDF for a specific, already-known arXiv paper without converting it —
    e.g. inspecting it first, or as a manual fetch step paired with ``convert_pdf_to_md``.
    Contrast with ``ingest_paper``, which fetches AND converts (fetch+convert only, no Knowledge
    node — L.B.2). WHAT: downloads the PDF via arXiv (or reuses an already-downloaded local copy)
    and returns its local path. Synchronous (no task_id). Rejected while a long-running
    arXiv/pipeline job is active (shared GPU / network discipline — same guard as
    ``ingest_paper``).

    Args:
        arxiv_id: arXiv identifier to fetch (e.g. "2604.14004").
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
    return await miner_tools.fetch_paper(arxiv_id)


@mcp.tool()
async def convert_pdf_to_md(pdf_path: str | None = None, arxiv_id: str | None = None) -> str:
    """Convert ONE PDF to Markdown via MinerU (GPU); writes NO vault node (standalone convert
    primitive).

    WHEN: you want just the converted markdown for a PDF or arXiv paper, with no triage and no
    vault write — e.g. a manual fetch→convert flow paired with ``fetch_paper``. Contrast with
    ``ingest_paper``, which also fetches for you (fetch+convert only, no Knowledge node — L.B.2).
    WHAT: PDF → Markdown via the same MinerU convert ``ingest_paper`` uses. If ``arxiv_id`` is
    given and ``pdf_path`` is not, fetches the PDF first. Returns the markdown path. Synchronous
    (no task_id). Rejected while a long-running arXiv/pipeline job is active (shared GPU / MinerU
    — same guard as ``ingest_paper``).

    Args:
        pdf_path: Path to a local PDF to convert directly (absolute, or project-relative).
        arxiv_id: arXiv identifier to fetch + convert (e.g. "2604.14004"), when pdf_path is not
            given.
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
    return await miner_tools.convert_pdf_to_md(pdf_path=pdf_path, arxiv_id=arxiv_id)


@mcp.tool()
async def get_paper_markdown(paper_id: str) -> str:
    """Return the path to ONE already-ingested paper's converted Markdown (no MinerU) — a bare
    read primitive for a judgment skill to consume.

    WHEN: the ``chimera-deep-extract`` skill needs a paper's text to hand to its Sonnet subagent
    for deep-read extraction. WHAT: resolves ``paper_id``'s already-converted markdown path and
    returns it as a string; an error string if the paper has not been converted yet (fetch +
    convert first). CONTRAST: makes NO judgment call and writes NO node — judgment happens ONLY in
    the ``chimera-deep-extract`` skill's subagent, never here.

    Args:
        paper_id: arXiv identifier of an already-ingested paper (e.g. "2305.16291").
    """
    return await miner_tools.get_paper_markdown(paper_id)


@mcp.tool()
async def stage_deep_read_node(ctx: Context, paper_id: str, extraction: dict) -> str:
    """Stage a subagent-produced deep-read extraction into a reviewable Knowledge node — the
    DETERMINISTIC back-half of Phase Q disciplined extraction (Phase L.B externalized the LLM
    judgment out of this server).

    WHEN: the ``chimera-deep-extract`` skill's Sonnet subagent has already produced a
    ``KNodeExtraction`` (synthesis + lens critique + attack vectors + mechanism claims) from a
    paper's markdown; call this to ground its citations into ``derives_from`` edges, detect
    supersede, render the node body, and write it to ``docs/staging/`` at
    ``chimera_tier="deep_read"``. WHAT: takes ``extraction`` as a JSON-serializable dict (the
    subagent's structured output) and returns the staging path. Writes NO
    Insight/Thought/Decision node and never auto-promotes — the operator promotes via
    ``ascend_node``. CONTRAST: makes NO judgment call itself; ``extraction`` is already-judged
    input and this tool is purely deterministic (grounding, render, write) — never deepseek, never
    an Anthropic client inside this server.

    Args:
        paper_id: arXiv identifier of the paper the extraction is about (e.g. "2305.16291").
        extraction: The subagent's ``KNodeExtraction`` payload as a JSON-serializable dict.
    """
    async with _start_lock:
        if get_task_service().has_active_long_task():
            return _busy_message()
    return await miner_tools.stage_deep_read_node(paper_id, extraction, progress=_reporter(ctx))


@mcp.tool()
async def write_scout_card(paper_id: str, analysis: dict) -> str:
    """Write a scout-tier Knowledge card from an already-decided triage verdict — the
    DETERMINISTIC write half of Phase L.B.2 externalized triage.

    WHEN: the ``chimera-triage-paper`` skill's Haiku subagent (``chimera-paper-triager``) has
    already produced a ``PaperAnalysisResult`` (verdict + score + mechanism summary + critical
    flaws) from a paper's markdown; call this to write it into the vault. WHAT: takes
    ``analysis`` as a JSON-serializable dict (the subagent's structured output) and returns the
    written card's path, always under ``inbox/<verdict>/`` at ``chimera_tier="scout"`` — never
    ``Harness/``. CONTRAST: makes NO judgment call itself; ``analysis`` is already-judged input
    and this tool is purely a deterministic render + write — never deepseek, never an Anthropic
    client inside this server.

    Args:
        paper_id: arXiv identifier of the paper the analysis is about (e.g. "2604.14004").
        analysis: The subagent's ``PaperAnalysisResult`` payload as a JSON-serializable dict.
    """
    return await miner_tools.write_scout_card(paper_id, analysis)


@mcp.tool()
async def check_task_status(task_id: str) -> str:
    """Return status or result for a background task (read-only poll).

    Args:
        task_id: Identifier returned when starting a long-running task.
    """
    return await miner_tools.check_task_status(task_id)


if __name__ == "__main__":
    mcp.run()
