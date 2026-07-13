"""Phase Q (rebuilt — friction-260710-02): single-paper disciplined extraction — ``extract_paper``.

ARA *discipline*, not ARA *format*: reuse the paper's already-converted markdown, distill it into
ONE reader's Knowledge node — a human-readable synthesis + the single most-relevant critical lens +
an offensive attack read, with 1-5 ARA-disciplined mechanism claims as the epistemic FLOOR (a
section, not the whole output). Attach ``derives_from`` edges minted ONLY by citation-resolution
(grounding). Writes NO Insight/Thought/Decision node (HSC 4), never fabricates an edge (no citation
resolves → ``grounded: no_prior_match``, edgeless), and only ever writes to the staging area — the
operator promotes. The new node supersedes the paper's prior node on promotion.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from core.config import ChimeraConfig, get_config
from core.schemas import KNodeExtraction, Paper
from grounding import resolve_citations
from ports.prompts.jinja_prompt_manager import PromptManager
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
        f"> 🤖 **BB's Analysis**: {syn.bb_analysis}",
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
        "> **[My Critique]**: <INSTRUCTION: BB 说得对吗？有什么漏洞？> _[User fills this during review]_",
        "",
        "---",
        "",
        f"## Lens Critique — {node.lens.lens_name}",
        "",
        f"**Triggered by:** {node.lens.triggered_by}",
    ]
    for finding in node.lens.findings:
        lines += ["", f"### {finding.heading}", "", finding.body]
    lines += [
        "",
        f"**Verdict:** {node.lens.verdict}",
        "",
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


def _load_lens_catalog(template_path: Path) -> str:
    """Concatenate the canonical lens definitions (``prompts/lenses/*.md``) — the SINGLE source the
    extraction LLM reads to apply ONE lens by paper function (friction-260710-03). The same files
    back the interactive ``chimera-lens-*`` skills; there is no second copy to drift."""
    lens_dir = template_path / "lenses"
    if not lens_dir.is_dir():
        return ""
    parts = [p.read_text(encoding="utf-8").strip() for p in sorted(lens_dir.glob("*.md"))]
    return "\n\n---\n\n".join(parts)


def _extract_node(
    paper: Paper, *, llm_client: object, prompt_manager: PromptManager
) -> KNodeExtraction:
    """The LLM call: paper markdown → ``KNodeExtraction`` (synthesis + lens + attack + claims).
    Selects ONE lens by paper FUNCTION from the canonical ``prompts/lenses/*.md`` catalog. Raises on
    failure — the caller returns an error rather than staging a degraded node."""
    lenses = _load_lens_catalog(prompt_manager.template_path)
    system_prompt = prompt_manager.render("chimera_sys/extract_node.j2", lenses=lenses)
    schema_str = json.dumps(
        KNodeExtraction.model_json_schema(), ensure_ascii=False, indent=2
    )
    user_prompt = prompt_manager.render(
        "tasks/extract_task.j2", paper=paper, json_schema=schema_str
    )
    result = llm_client.generate_structured_data(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=KNodeExtraction,
    )
    if isinstance(result, KNodeExtraction):
        return result
    return KNodeExtraction.model_validate(result)


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

    extraction = _extract_node(
        paper, llm_client=llm_client, prompt_manager=PromptManager()
    )

    # Edges: citation-resolution ONLY (D3/D4). Empty resolution ⇒ no_prior_match, edgeless.
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
        "arxiv_id": paper_id,
    }

    staging = staging_service or StagingService(cfg().system.staging_dir, vault_root)
    path = staging.create_staging_node(
        type="knowledge",
        title=extraction.title,
        body=_render_node_body(extraction),
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
