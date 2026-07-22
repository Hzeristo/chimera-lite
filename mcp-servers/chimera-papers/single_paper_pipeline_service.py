"""Single PDF/MD pipeline — RETIRED (Phase L.B.2).

``FilterService.evaluate_paper`` is removed; the LLM judgment that lived here now lives in the
``chimera-triage-paper`` skill's ``chimera-paper-triager`` Haiku subagent. The ingest half is
``ingest_paper`` (MCP tool) or ``single_paper_ingest.ingest_single_paper``; the scout-card write
half is ``write_scout_card`` (MCP tool) / ``single_paper_ingest.write_scout_card``.

DEBT: delete this module. Nothing under the current MCP path imports it; it is only retained so
that any external reference to ``SinglePaperPipelineService`` fails loudly at instantiation
rather than silently at import-time (ImportError on the removed ``filter_service.FilterService``).
"""

from __future__ import annotations

import logging
from pathlib import Path

from core.config import ChimeraConfig

logger = logging.getLogger(__name__)


class SinglePaperPipelineService:
    """RETIRED — raises ``NotImplementedError`` on ``run_single``.

    L.B.2 removed ``FilterService.evaluate_paper`` (the structured-output LLM judgment call this
    service used to orchestrate). The replacement path is:
      1. ``ingest_paper`` (MCP tool) — fetch + convert to markdown; no LLM call.
      2. ``chimera-triage-paper`` skill — spawns a Haiku subagent for the verdict.
      3. ``write_scout_card`` (MCP tool) — deterministic write of the scout-tier inbox card.
    """

    def __init__(self, settings: ChimeraConfig) -> None:  # noqa: ARG002
        raise NotImplementedError(
            "SinglePaperPipelineService is retired (L.B.2). "
            "Use ingest_paper → chimera-triage-paper skill → write_scout_card instead."
        )

    def run_single(
        self,
        *,
        pdf: Path | None,
        md: Path | None,
        raw_output_root: Path | None,
        force: bool,
    ) -> int:  # pragma: no cover
        raise NotImplementedError("See __init__.")
