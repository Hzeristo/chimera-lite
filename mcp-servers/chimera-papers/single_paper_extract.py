"""Phase Q (rebuilt — friction-260710-02), externalized L.B.2: single-paper disciplined
extraction — the DETERMINISTIC back-half behind the ``get_paper_markdown`` /
``stage_deep_read_node`` MCP tools (the former single ``extract_paper`` tool, split by L.B.2).

ARA *discipline*, not ARA *format*: the human-readable synthesis + the single most-relevant
critical lens + an offensive attack read + 1-5 ARA-disciplined mechanism claims is now judged by
a pinned-Sonnet subagent (the ``chimera-deep-extract`` skill), never here — the MCP server makes
NO LLM call (D2). This module keeps only the two deterministic primitives the skill calls:
``get_paper_markdown`` (read — resolves the paper's already-converted markdown path) and
``stage_deep_read_node`` (write — given the subagent's ``KNodeExtraction``, grounds its citations
into ``derives_from`` edges minted ONLY by citation-resolution, detects supersede, renders the
node body, and stages it). Writes NO Insight/Thought/Decision node (HSC 4), never fabricates an
edge (no citation resolves → ``grounded: no_prior_match``, edgeless), and only ever writes to the
staging area at ``chimera_tier="deep_read"`` — the operator promotes (via ``ascend_node``). The
new node supersedes the paper's prior node on promotion.
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Awaitable, Callable
from pathlib import Path

from core.config import ChimeraConfig, get_config
from core.schemas import KNodeExtraction, Paper
from grounding import resolve_citations
from staging_service import StagingService

logger = logging.getLogger(__name__)

_ARXIV_ID_RE = re.compile(r"\d{4}\.\d{4,5}")
_NONVAULT_DIRS = {".obsidian", ".migration_backup", "templates"}
# Strip an LLM-supplied leading enumerator ("1.", "2)", "3:") so the renderer doesn't double it.
_STEP_ENUM_RE = re.compile(r"^\s*\d+[.):]\s*")
# Strip LLM-supplied leading 💥 markers (+ variation selectors) so the renderer doesn't double them.
_ATTACK_MARK_RE = re.compile(r"^[\s💥️]+")


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


def _render_node_body(node: KNodeExtraction) -> str:
    """Render the extracted node into the reader's markdown body: Synthesis + Lens Critique +
    Attack Vectors + ARA-disciplined Mechanism Claims (the epistemic floor), with human-fill
    ``[My Critique]`` review hooks. No Insight/Thought/Decision content (HSC 4)."""
    syn = node.synthesis
    lines: list[str] = [
        "> **ai-suggested — review before promotion.** Distilled synthesis with BB's analysis,",
        "> mechanism walkthrough, lens critique, attack vectors, and explicit human correction hooks.",
        "",
        "## Synthesis",
        "",
        f"**Motivation (the gap):** {syn.motivation}",
        "",
        f"> 🤖 **BB's Analysis**: {syn.bb_analysis}",
        "",
        "**Mechanism:**",
        "",
        syn.mechanism,
    ]
    if syn.algorithm_steps:
        lines += ["", "**Core Algorithm Steps:**", ""]
        lines += [
            f"{i}. {_STEP_ENUM_RE.sub('', step).strip()}"
            for i, step in enumerate(syn.algorithm_steps, start=1)
        ]
    lines += [
        "",
        "**Results (did it work):**",
        "",
        syn.results,
        "",
        "> **[My Critique]**: <INSTRUCTION: BB 说得对吗？有什么漏洞？> _[User fills this during review]_",
        "",
    ]
    for lens in node.lenses:
        lines += [
            "---",
            "",
            f"## Lens Critique — {lens.lens_name}",
            "",
            f"**Triggered by:** {lens.triggered_by}",
        ]
        for finding in lens.findings:
            lines += ["", f"### {finding.heading}", "", finding.body]
        lines += ["", f"**Verdict:** {lens.verdict}", ""]
    lines += [
        "---",
        "",
        "## 💥 Attack Vectors (Offensive Perspective)",
        "",
    ]
    for vector in node.attack.vectors:
        clean = _ATTACK_MARK_RE.sub("", vector).strip()
        lines += [f"> 💥 {clean}", ""]
    lines += [
        "**Actionable Attack:**",
        "",
        f"- [ ] Beat this baseline by: {node.attack.beat_baseline}",
        f"- [ ] Exploit the flaw: {node.attack.exploit_flaw}",
        "",
        "> **[My Critique on Attack Vectors]**: <INSTRUCTION: 我能用什么方法打败这个 baseline？> _[User fills during review]_",
        "",
        "---",
        "",
        "## Mechanism Claims (ARA-Disciplined)",
    ]
    for i, claim in enumerate(node.claims, start=1):
        status = f"{claim.status} ({claim.status_note})" if claim.status_note else claim.status
        lines += [
            "",
            f"### C{i:02d}: {claim.title}",
            "",
            f"**Statement:** {claim.statement}",
            "",
            f"**Falsification:** {claim.falsification}",
            "",
            f"**Status:** {status}",
        ]
        if claim.sources:
            rendered = "; ".join(f'"{s.quote}" ← {s.location}' for s in claim.sources)
            lines += ["", f"**Sources:** {rendered}"]
        if claim.tags:
            lines += ["", f"**Tags:** {', '.join(claim.tags)}"]
        if claim.flags:
            lines += ["", f"**Flags:** {', '.join(f.value for f in claim.flags)}"]
    return "\n".join(lines) + "\n"


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
        f"No converted markdown for {paper_id!r} at {candidate}. get_paper_markdown reuses "
        f"source_md; fetch+MinerU for a genuinely new paper is a later extension."
    )


def get_paper_markdown(paper_id: str, settings: ChimeraConfig | None = None) -> Path:
    """Resolve ``paper_id``'s already-converted markdown path (no MinerU) — the READ primitive the
    ``chimera-deep-extract`` skill calls so its Sonnet subagent can read the paper itself
    (isolation: the MCP layer never sees paper content). Raises ``FileNotFoundError`` if the paper
    has not been converted yet. ``settings`` is injectable for testing; resolved from config when
    omitted."""
    cfg = settings or get_config()
    return _resolve_markdown(paper_id, cfg)


async def stage_deep_read_node(
    *,
    paper_id: str,
    extraction: KNodeExtraction | dict,
    settings: ChimeraConfig | None = None,
    staging_service: StagingService | None = None,
    paper: Paper | None = None,
    markdown_path: Path | None = None,
    progress: Callable[[float, str], Awaitable[None]] | None = None,
) -> Path:
    """Stage a subagent-produced ``KNodeExtraction`` into a STAGED Knowledge node — the
    DETERMINISTIC back-half of Phase Q disciplined extraction (L.B.2 externalized the LLM judgment
    to the ``chimera-deep-extract`` skill's subagent; this function makes NO LLM call). Grounds the
    paper's citations into ``derives_from`` edges (or ``no_prior_match``), detects supersede, and
    renders + writes the node at ``chimera_tier="deep_read"``. Writes NO I/T/D node (HSC 4).
    Returns the staging path; never touches the live vault.

    ``extraction`` is the subagent's structured output — accepted as a ``KNodeExtraction`` or a
    plain dict (validated via ``KNodeExtraction.model_validate``; a JSON payload arriving through
    the MCP tool boundary is a dict).

    Async so the MCP tool can stream stage progress via ``progress`` (``None`` in tests). The
    blocking work (grounding walk, file writes) runs in worker threads so the event loop stays
    free; stage labels ALSO go to stderr (chimera-mcp-taste Rule #4 fallback) so a no-ctx run is
    never silent.

    Dependencies (``settings`` / ``staging_service`` / ``paper`` / ``markdown_path``) are
    injectable for testing; when omitted they are resolved from config lazily.
    """
    node = (
        extraction
        if isinstance(extraction, KNodeExtraction)
        else KNodeExtraction.model_validate(extraction)
    )

    def cfg() -> ChimeraConfig:
        nonlocal settings
        if settings is None:
            settings = get_config()
        return settings

    async def report(frac: float, msg: str) -> None:
        logger.info("[Extract] %s %.0f%% — %s", paper_id, frac * 100, msg)
        if progress is not None:
            await progress(frac, msg)

    await report(0.0, "Resolving markdown...")
    vault_root = (
        staging_service.vault_root
        if staging_service is not None
        else cfg().require_path("vault_root")
    )
    if paper is None:
        from ports.papers.paper_loader import PaperLoader

        md_path = markdown_path or _resolve_markdown(paper_id, cfg())
        paper = await asyncio.to_thread(PaperLoader().load_paper, md_path)

    await report(0.4, "Grounding citations...")
    # Edges: citation-resolution ONLY (D3/D4). Empty resolution ⇒ no_prior_match, edgeless.
    edge_props = await asyncio.to_thread(
        resolve_citations, _cited_arxiv_ids(paper.raw_text, exclude=paper_id), vault_root
    )
    edges: dict[str, list[str]] = {}
    if edge_props:
        edges["derives_from"] = [p.target_stem for p in edge_props]
    superseded = await asyncio.to_thread(_find_superseded_stem, paper_id, vault_root)
    if superseded:
        edges["supersedes"] = [superseded]

    await report(0.85, "Staging node...")
    metadata = {
        "provenance": "ai-suggested",
        "grounded": "citation_resolved" if edge_props else "no_prior_match",
        "arxiv_id": paper_id,
    }
    staging = staging_service or StagingService(cfg().system.staging_dir, vault_root)
    path = await asyncio.to_thread(
        staging.create_staging_node,
        type="knowledge",
        title=node.title,
        body=_render_node_body(node),
        edges=edges or None,
        metadata=metadata,
        chimera_tier="deep_read",
    )
    await report(1.0, "Done")
    logger.info(
        "[Extract] Staged K node for %s: %s (edges=%s grounded=%s)",
        paper_id,
        path.name,
        sorted(edges),
        metadata["grounded"],
    )
    return path
