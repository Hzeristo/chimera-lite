"""Paper data primitive (Phase L.B.2 externalized — TRIAGE half, commit 2/2).

``FilterService.evaluate_paper`` (the retired structured-output LLM judgment call) is GONE —
verdict judgment now lives in the ``chimera-triage-paper`` skill's Haiku subagent
(``chimera-paper-triager``), never in the MCP server (D2). ``analyze_paper_data`` is the
deterministic data primitive that skill calls first: it resolves + loads an already-converted
paper's markdown and a small metadata dict for the subagent to read directly (isolation — this
module never sees the paper's content beyond materializing the ``Paper`` for its own id/title
fields). Makes NO LLM call of any kind.
"""

from __future__ import annotations

import logging
from typing import Any

from core.config import ChimeraConfig, get_config
from ports.papers.paper_loader import PaperLoader
from single_paper_extract import get_paper_markdown

logger = logging.getLogger(__name__)


def analyze_paper_data(paper_id: str, settings: ChimeraConfig | None = None) -> dict[str, Any]:
    """Resolve ONE already-converted paper's markdown path + metadata — a data primitive, NO LLM
    call (L.B.2 retired ``FilterService.evaluate_paper``'s structured-output judgment call).

    Reuses ``single_paper_extract.get_paper_markdown`` for the exact same md-dir resolution the
    deep-read path uses (one resolution scheme, not two), then materializes a ``Paper`` via
    ``PaperLoader`` purely to surface its id/title/authors/year — never to judge it.

    Returns ``{"markdown_path": str, "metadata": {"id", "title", "authors", "year",
    "content_path"}}``. Raises ``FileNotFoundError`` if the paper has not been converted yet
    (``fetch_paper`` / ``convert_pdf_to_md`` / ``ingest_paper`` first). ``settings`` is injectable
    for testing; resolved from config when omitted.
    """
    cfg = settings or get_config()
    markdown_path = get_paper_markdown(paper_id, settings=cfg)
    paper = PaperLoader().load_paper(markdown_path)
    return {
        "markdown_path": str(markdown_path),
        "metadata": {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "content_path": str(paper.content_path),
        },
    }
