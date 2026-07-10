"""Q.2b: single-paper disciplined extraction (Phase Q) — the ``extract_paper`` orchestration.

ARA *discipline*, not ARA *format*: reuse the paper's already-converted markdown, distill it into
ONE Knowledge node of 1-5 MECHANISM-LEVEL claims, and attach ``derives_from`` edges minted ONLY by
citation-resolution (grounding). Writes NO Insight/Thought/Decision node (HSC 4), never fabricates an
edge (no citation resolves → ``grounded: no_prior_match``, edgeless), and only ever writes to the
staging area — the operator promotes. The new node supersedes the paper's prior node on promotion.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from core.config import ChimeraConfig, get_config
from core.schemas import KClaimExtraction, Paper
from grounding import resolve_citations
from ports.prompts.jinja_prompt_manager import PromptManager
from staging_service import StagingService

logger = logging.getLogger(__name__)

_ARXIV_ID_RE = re.compile(r"\d{4}\.\d{4,5}")
_NONVAULT_DIRS = {".obsidian", ".migration_backup", "templates"}


def _arxiv_id(text: str) -> str:
    """The first arxiv id in ``text`` (else the stripped text) — normalizes a paper id/reference."""
    m = _ARXIV_ID_RE.search(text or "")
    return m.group(0) if m else (text or "").strip()


def _cited_arxiv_ids(text: str, *, exclude: str) -> list[str]:
    """Distinct arxiv ids cited in the paper text, minus the paper's own id. These are the ONLY
    edge candidates — a ``derives_from`` edge is licensed only by a resolved citation (Decision D3)."""
    self_id = _arxiv_id(exclude)
    seen: dict[str, None] = {}
    for m in _ARXIV_ID_RE.finditer(text or ""):
        cid = m.group(0)
        if cid != self_id and cid not in seen:
            seen[cid] = None
    return list(seen)


def _find_superseded_stem(paper_id: str, vault_root: Path) -> str | None:
    """Stem of an existing K node for this paper — the node the new one supersedes — or None.
    Excludes ``.obsidian`` / ``.migration_backup`` / ``templates`` (same guard as grounding)."""
    self_id = _arxiv_id(paper_id)
    if not vault_root.is_dir():
        return None
    for path in sorted(vault_root.rglob("*.md")):
        try:
            rel = path.relative_to(vault_root)
        except ValueError:
            continue
        if _NONVAULT_DIRS & set(rel.parts):
            continue
        if self_id in path.stem:
            return path.stem
    return None


def _render_claims_body(extraction: KClaimExtraction) -> str:
    """Render the extracted claims into a reviewable markdown body (no I/T/D content)."""
    lines = [
        "> **ai-suggested — review before promotion.** Mechanism-level claims extracted from the",
        "> paper; edges are citation-grounded (or `no_prior_match`). No Insight/Thought/Decision"
        " node was created.",
        "",
        "## Claims",
    ]
    for i, claim in enumerate(extraction.claims, start=1):
        lines.append(f"\n### C{i:02d}")
        lines.append(f"- **Statement:** {claim.statement}")
        lines.append(f"- **Falsification:** {claim.falsification}")
        lines.append(f"- **Status:** {claim.status}")
        if claim.sources:
            lines.append(f"- **Sources:** {'; '.join(claim.sources)}")
        if claim.tags:
            lines.append(f"- **Tags:** {', '.join(claim.tags)}")
        if claim.flags:
            lines.append(f"- **Flags:** {', '.join(f.value for f in claim.flags)}")
    return "\n".join(lines) + "\n"


def _extract_claims(
    paper: Paper, *, llm_client: object, prompt_manager: PromptManager
) -> KClaimExtraction:
    """The LLM call: paper markdown → ``KClaimExtraction`` (mechanism claims). Mirrors
    ``FilterService.evaluate_paper``. Raises on failure — the caller returns an error rather than
    staging a degraded node."""
    system_prompt = prompt_manager.render("chimera_sys/extract_claims.j2")
    schema_str = json.dumps(
        KClaimExtraction.model_json_schema(), ensure_ascii=False, indent=2
    )
    user_prompt = prompt_manager.render(
        "tasks/extract_task.j2", paper=paper, json_schema=schema_str
    )
    result = llm_client.generate_structured_data(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=KClaimExtraction,
    )
    if isinstance(result, KClaimExtraction):
        return result
    return KClaimExtraction.model_validate(result)


def _resolve_markdown(paper_id: str, settings: ChimeraConfig) -> Path:
    """Reuse the paper's already-converted clean markdown (NO MinerU). Backfill relies on this —
    the Schema-C nodes point ``source_md`` at ``papers/md_papers/<id>.md``."""
    pm = settings.paper_miner_or_default
    md_dir = pm.md_papers_dir
    if not md_dir.is_absolute():
        md_dir = (settings.project_root / md_dir).resolve()
    candidate = md_dir / f"{paper_id}.md"
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(
        f"No converted markdown for {paper_id!r} at {candidate}. extract_paper reuses source_md; "
        f"fetch+MinerU for a genuinely new paper is a later extension."
    )


def extract_single_paper(
    *,
    paper_id: str,
    settings: ChimeraConfig | None = None,
    llm_client: object | None = None,
    staging_service: StagingService | None = None,
    paper: Paper | None = None,
    markdown_path: Path | None = None,
) -> Path:
    """Extract ONE paper into a STAGED Knowledge node: 1-5 mechanism claims + citation-grounded
    ``derives_from`` edges (or ``no_prior_match``), superseding the paper's existing node on
    promotion. Writes NO I/T/D node (HSC 4). Returns the staging path; never touches the live vault.

    Dependencies (``settings`` / ``llm_client`` / ``staging_service`` / ``paper`` / ``markdown_path``)
    are injectable for testing; when omitted they are resolved from config lazily.
    """

    def cfg() -> ChimeraConfig:
        nonlocal settings
        if settings is None:
            settings = get_config()
        return settings

    vault_root = (
        staging_service.vault_root
        if staging_service is not None
        else cfg().require_path("vault_root")
    )

    if paper is None:
        from ports.papers.paper_loader import PaperLoader

        md_path = markdown_path or _resolve_markdown(paper_id, cfg())
        paper = PaperLoader().load_paper(md_path)

    if llm_client is None:
        from bootstrap import build_openai_client

        llm_client = build_openai_client(cfg())

    extraction = _extract_claims(
        paper, llm_client=llm_client, prompt_manager=PromptManager()
    )

    # Edges: citation-resolution ONLY (D3). Empty resolution ⇒ no_prior_match, edgeless.
    edge_props = resolve_citations(
        _cited_arxiv_ids(paper.raw_text, exclude=paper_id), vault_root
    )
    edges: dict[str, list[str]] = {}
    if edge_props:
        edges["derives_from"] = [p.target_stem for p in edge_props]
    superseded = _find_superseded_stem(paper_id, vault_root)
    if superseded:
        edges["supersedes"] = [superseded]

    metadata = {
        "provenance": "ai-suggested",
        "grounded": "citation_resolved" if edge_props else "no_prior_match",
    }

    staging = staging_service or StagingService(cfg().system.staging_dir, vault_root)
    path = staging.create_staging_node(
        type="knowledge",
        title=paper_id,
        body=_render_claims_body(extraction),
        edges=edges or None,
        metadata=metadata,
    )
    logger.info(
        "[Extract] Staged K node for %s: %s (edges=%s grounded=%s)",
        paper_id,
        path.name,
        sorted(edges),
        metadata["grounded"],
    )
    return path
