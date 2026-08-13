"""Q.2a: citation-resolution grounding (Decision D3).

A `derives_from` edge is licensed ONLY by a resolved citation — the paper's own
references/related-work resolving to an EXISTING vault K node. Never a topic/keyword
"similarity" guess (fabrication guard: `[[vault-graph-edges-empty]]`).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from core.schemas import EdgeProposal

logger = logging.getLogger(__name__)

_ARXIV_ID_RE = re.compile(r"\d{4}\.\d{4,5}")
# Directories excluded from citation-resolution scan: backups, user-synced templates,
# Obsidian internals. Mirrors vault_read_adapter._NONVAULT_DIRS — this is the fix for the
# reaudit Q2.2 gap, where `query_graph` excludes only `.obsidian`.
_NONVAULT_DIRS = {".obsidian", ".migration_backup", "templates"}


def _knowledge_note_type(path: Path) -> str | None:
    """Return the note's frontmatter `type` (lowercased), or None if unreadable/malformed."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError, LookupError):
        return None
    except Exception:
        return None
    norm = raw.replace("\r\n", "\n").replace("\r", "\n")
    m = re.match(r"^---\n(.*?)\n---", norm, re.DOTALL)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception:
        logger.warning("[Vault] Skipping note with malformed frontmatter: %s", path)
        return None
    if not isinstance(fm, dict):
        return None
    return str(fm.get("type", "")).strip().lower()


def _iter_knowledge_stems(vault_root: Path) -> list[str]:
    """Stems of every `type: knowledge` note under `vault_root`, excluding
    `.obsidian` / `.migration_backup` / `templates`. Read-only; skips unreadable notes."""
    stems: list[str] = []
    if not vault_root.is_dir():
        return stems
    for path in vault_root.rglob("*.md"):
        try:
            rel = path.relative_to(vault_root)
        except ValueError:
            continue
        if _NONVAULT_DIRS & set(rel.parts):
            continue
        if _knowledge_note_type(path) == "knowledge":
            stems.append(path.stem)
    return stems


def resolve_citations(references: list[str], vault_root: Path) -> list[EdgeProposal]:
    """Resolve each reference to an existing vault K node and propose a `derives_from`
    edge (Decision D3: citation-resolution ONLY, never topic/keyword similarity).

    Resolution: extract an arxiv id from the reference (regex `\\d{4}\\.\\d{4,5}`) and
    match it against K-node stems (preferred); if the reference carries no arxiv id,
    fall back to an exact match of the (stripped) reference string against a K-node stem.
    A reference that resolves to nothing contributes no proposal.

    NOTE: `contradicts` is OUT of Q.2a scope — it requires semantic claim-conflict
    detection, not citation-resolution; only `derives_from` is emitted here.

    Read-only over the vault. Returns a list de-duplicated by (target_stem, source_citation).
    """
    stems = _iter_knowledge_stems(vault_root)
    proposals: list[EdgeProposal] = []
    seen: set[tuple[str, str]] = set()

    for reference in references:
        ref = str(reference).strip()
        if not ref:
            continue

        target_stem: str | None = None
        id_match = _ARXIV_ID_RE.search(ref)
        if id_match:
            arxiv_id = id_match.group(0)
            target_stem = next((s for s in stems if arxiv_id in s), None)
        else:
            target_stem = next((s for s in stems if s == ref), None)

        if target_stem is None:
            continue

        key = (target_stem, ref)
        if key in seen:
            continue
        seen.add(key)
        proposals.append(
            EdgeProposal(
                target_stem=target_stem,
                edge_type="derives_from",
                source_citation=ref,
            )
        )

    return proposals
