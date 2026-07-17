"""W1/W2 harness result artifacts: write into the vault under a review status, identity-superseding.

Unlike ``StagingService`` (writes ``docs/staging/`` → explicit promote), harness results live
directly IN the vault (``<vault>/Harness/``) so the Architect curates them in Obsidian — the "two
curation paths" (harness + Obsidian) of the Phase L artifact lifecycle. Re-running for the same
identity (claim_hash / arxiv_id) SUPERSEDES the prior artifact — the filename is identity-keyed, so
the same identity always maps to the same file: a re-run replaces, never duplicates.

For a W1 verdict, the caller passes ``metadata={"verdict": ..., "depends_on": [...]}``; the
``depends_on`` dependency structure lands in frontmatter (Phase K Gate 1 reads it — the verdict is
never recorded bare). This is the C1 forward-compat constraint.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import yaml

_SLUG_RE = re.compile(r'[\\/:*?"<>|\s]+')


def _slug(text: str, limit: int = 80) -> str:
    return _SLUG_RE.sub("_", str(text)).strip("_")[:limit].rstrip("_")


class ResultService:
    """Write review-gated harness artifacts into the vault, identity-superseding on re-run."""

    def __init__(self, results_dir: Path) -> None:
        self.results_dir = results_dir
        results_dir.mkdir(parents=True, exist_ok=True)

    def write_result(
        self,
        *,
        kind: str,
        identity: str,
        title: str,
        body: str,
        metadata: dict | None = None,
    ) -> Path:
        """Write one harness artifact; a re-run with the same ``(kind, identity)`` replaces it.

        The filename is derived from ``kind`` + ``identity`` so the same identity always maps to the
        same file — the supersede is a deterministic overwrite, never a duplicate. Frontmatter carries
        the fixed keys plus any ``metadata`` (e.g. ``verdict`` + ``depends_on`` for a W1 verdict — the
        dependency structure Phase K Gate 1 reads). Returns the artifact path.
        """
        ident = str(identity).strip()
        if not ident:
            raise ValueError("write_result requires a non-empty identity")

        path = self.results_dir / f"{_slug(kind)}__{_slug(ident)}.md"
        fm: dict = {
            "type": kind,
            "status": "PENDING_REVIEW",
            "identity": ident,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "superseded_prior": path.exists(),
        }
        if metadata:
            fm.update(metadata)
        content = (
            f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)}"
            f"---\n\n# {title}\n\n{body}\n"
        )
        path.write_text(content, encoding="utf-8")
        return path
