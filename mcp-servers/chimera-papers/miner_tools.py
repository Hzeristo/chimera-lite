"""Background miner tools — arXiv async fetch + task status (poll model).

Long-running tools return a ``task_id`` immediately; callers poll ``check_task_status``.
``daily_paper_pipeline`` is added in M.2b.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from core.config import ChimeraConfig, get_config
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
    """Start the full daily pipeline (fetch → convert → notify); return task_id.

    Makes NO LLM call and writes NO Knowledge node (L.B.2) — triage of the converted papers is a
    separate, explicitly invoked step: the ``chimera-triage-paper`` skill.
    """
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
    arxiv_id: str | None = None,
    pdf_path: str | None = None,
    progress: Callable[[float, str], Awaitable[None]] | None = None,
) -> str:
    """Fetch + convert ONE paper (arXiv id or local PDF); returns its markdown path.

    Writes NO Knowledge node and makes NO LLM call (L.B.2) — this is a fetch+convert primitive
    only. Contrast with the retired ingest→triage→K-node path: triage is now the explicitly
    invoked ``chimera-triage-paper`` skill, which reads this markdown itself (isolation) and, on
    a verdict, calls ``write_scout_card`` to write the inbox card. The heavy download / MinerU
    convert each run in a worker thread inside the domain function so the event loop is not
    blocked; ``progress`` (from the MCP tool wrapper) streams stage labels to the client.
    """
    has_arxiv = bool(arxiv_id and str(arxiv_id).strip())
    has_pdf = bool(pdf_path and str(pdf_path).strip())
    if not has_arxiv and not has_pdf:
        return "[Tool Error]: ingest_paper requires arxiv_id or pdf_path."

    # Lazy import: keep the heavy MinerU chain out of module load (matches the
    # daily-pipeline lazy import).
    from single_paper_ingest import ingest_single_paper

    try:
        md_path = await ingest_single_paper(
            arxiv_id=(str(arxiv_id).strip() if has_arxiv else None),
            pdf_path=(str(pdf_path).strip() if has_pdf else None),
            progress=progress,
        )
    except FileNotFoundError as exc:
        return f"[Ingest Error] PDF not found: {exc}"
    except Exception as exc:  # network / MinerU
        return f"[Ingest Error] {exc}"
    return f"[✔] Markdown converted (no Knowledge node written): {md_path}"


async def write_scout_card(paper_id: str, analysis: dict) -> str:
    """Write ONE scout-tier Knowledge card from an already-decided triage verdict.

    ``analysis`` is a ``PaperAnalysisResult``-shaped dict — the ``chimera-triage-paper`` skill's
    ``chimera-paper-triager`` subagent's verdict, judged elsewhere. This tool makes NO judgment
    call of its own; it validates + writes. The card always lands in ``inbox/<verdict>/`` (never
    ``Harness/``) at ``chimera_tier="scout"``, for the Architect to review before promotion.
    """
    pid = (paper_id or "").strip()
    if not pid:
        return "[Tool Error]: write_scout_card requires a non-empty paper_id."

    # Lazy import: keep the vault-write chain out of module load.
    from single_paper_ingest import write_scout_card as _write_scout_card

    try:
        out_path = await asyncio.to_thread(_write_scout_card, pid, analysis)
    except FileNotFoundError as exc:
        return f"[Triage Error] {exc}"
    except Exception as exc:  # validation / vault write
        return f"[Triage Error] {exc}"
    return f"[✔] Scout card written (review before promotion): {out_path}"


async def _fetch_pdf(arxiv_id: str, settings: ChimeraConfig) -> Path:
    """Download one arXiv PDF; the primitive shared by ``fetch_paper`` and the ``arxiv_id`` path
    of ``convert_pdf_to_md``. Runs the blocking download in a worker thread. Raises on failure —
    callers format the error message."""
    # Lazy import: keeps single_paper_ingest's chain (requests / filter_service / vault writer)
    # out of module load, matching the daily-pipeline / ingest_paper lazy-import convention.
    from single_paper_ingest import _fetch_arxiv_pdf

    return await asyncio.to_thread(_fetch_arxiv_pdf, arxiv_id, settings)


async def fetch_paper(
    arxiv_id: str,
    settings: ChimeraConfig | None = None,
) -> str:
    """Download ONE arXiv paper's PDF; writes NO vault node — a bare fetch primitive.

    Pairs with ``convert_pdf_to_md`` for a manual fetch-then-convert flow. Contrast with
    ``ingest_paper``, which always writes a Knowledge node. ``settings`` is injectable for
    testing; resolved from config when omitted.
    """
    aid = (arxiv_id or "").strip()
    if not aid:
        return "[Tool Error]: fetch_paper requires a non-empty arxiv_id."

    cfg = settings or get_config()
    try:
        pdf_path = await _fetch_pdf(aid, cfg)
    except Exception as exc:  # network / filesystem
        return f"[Fetch Error] {exc}"
    return f"[✔] PDF fetched (no vault node written): {pdf_path}"


async def convert_pdf_to_md(
    pdf_path: str | None = None,
    arxiv_id: str | None = None,
    settings: ChimeraConfig | None = None,
) -> str:
    """Convert ONE PDF to Markdown via MinerU; writes NO vault node — a standalone convert
    primitive over ``MineruClient.convert``.

    ``pdf_path`` converts directly; ``arxiv_id`` fetches first (reusing the ``fetch_paper``
    download primitive, ``_fetch_pdf``) then converts — exactly one of the two must be given.
    Contrast with ``ingest_paper``, which converts AND writes a Knowledge node. ``settings`` is
    injectable for testing; resolved from config when omitted.
    """
    has_pdf = bool(pdf_path and str(pdf_path).strip())
    has_arxiv = bool(arxiv_id and str(arxiv_id).strip())
    if not has_pdf and not has_arxiv:
        return "[Tool Error]: convert_pdf_to_md requires pdf_path or arxiv_id."

    cfg = settings or get_config()

    if has_pdf:
        src_pdf = Path(str(pdf_path).strip()).expanduser()
    else:
        try:
            src_pdf = await _fetch_pdf(str(arxiv_id).strip(), cfg)
        except Exception as exc:  # network / filesystem
            return f"[Convert Error] Fetch failed: {exc}"

    if not src_pdf.is_absolute():
        src_pdf = (cfg.project_root / src_pdf).resolve()

    pm = cfg.paper_miner_or_default
    output_root = pm.md_papers_raw_dir
    if not output_root.is_absolute():
        output_root = (cfg.project_root / output_root).resolve()

    # Lazy import: ports.ingest.paper2md itself is stdlib-only, but keep the same lazy-import
    # shape as the other domain delegates in this file.
    from ports.ingest.paper2md import MineruClient

    try:
        client = MineruClient(output_root=output_root)
        md_path = await asyncio.to_thread(client.convert, src_pdf)
    except FileNotFoundError as exc:
        return f"[Convert Error] PDF not found: {exc}"
    except Exception as exc:  # MinerU subprocess / conversion failure
        return f"[Convert Error] {exc}"
    return f"[✔] Markdown converted (no vault node written): {md_path}"


async def get_paper_markdown(paper_id: str) -> str:
    """Return the path to ONE already-ingested paper's converted Markdown (no MinerU) — a bare
    read primitive. The ``chimera-deep-extract`` skill reads this path directly with its own
    subagent (isolation: this MCP layer never sees paper content, and makes NO LLM call).
    """
    pid = (paper_id or "").strip()
    if not pid:
        return "[Tool Error]: get_paper_markdown requires a non-empty paper_id."

    # Lazy import: keep the vault/config chain out of module load.
    from single_paper_extract import get_paper_markdown as _get_paper_markdown

    try:
        path = _get_paper_markdown(pid)
    except FileNotFoundError as exc:
        return f"[Extract Error] {exc}"
    return str(path)


async def stage_deep_read_node(
    paper_id: str,
    extraction: dict,
    progress: Callable[[float, str], Awaitable[None]] | None = None,
) -> str:
    """Stage a subagent-produced extraction (a ``KNodeExtraction`` dict from the
    ``chimera-deep-extract`` skill) into a reviewable deep_read Knowledge node: deterministic
    citation-grounding + supersede-detection + render + write to ``docs/staging/``. All judgment
    already happened in the skill's subagent — this is the deterministic back-half, making NO LLM
    call itself. Staging-only — never auto-promoted. ``progress`` streams stage labels; the domain
    function runs its blocking steps in worker threads.
    """
    pid = (paper_id or "").strip()
    if not pid:
        return "[Tool Error]: stage_deep_read_node requires a non-empty paper_id."

    # Lazy import: keep the grounding / vault chain out of module load.
    from single_paper_extract import stage_deep_read_node as _stage_deep_read_node

    try:
        out_path = await _stage_deep_read_node(
            paper_id=pid, extraction=extraction, progress=progress
        )
    except FileNotFoundError as exc:
        return f"[Extract Error] {exc}"
    except Exception as exc:  # validation / grounding / staging
        return f"[Extract Error] {exc}"
    return f"[✔] Staged K node (review before promotion): {out_path}"


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
