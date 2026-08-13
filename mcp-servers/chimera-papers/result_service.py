"""W1/W2 harness result artifacts: write into the vault under a review status.

Unlike ``StagingService`` (writes ``docs/staging/`` → explicit promote), harness results live
directly IN the vault (``<vault>/Harness/``) so the Architect curates them in Obsidian — the "two
curation paths" (harness + Obsidian) of the Phase L artifact lifecycle.

Write modes (keyed off ``(kind, identity)`` — the filename is identity-derived, so the same
identity always maps to the same file):

- ``supersede`` (default — **W1 verdict**): a re-run REPLACES the artifact. Identity = claim_hash /
  arxiv_id; the ``depends_on`` dependency structure lands in frontmatter (Phase K Gate 1 reads it —
  the verdict is never recorded bare; the C1 forward-compat constraint).
- ``merge`` (**W2 breadth map**): a re-run UNIONS the map by paper key — it ADDS new papers and
  PRESERVES the Architect's in-Obsidian annotations verbatim (existing blocks win). Clobbering the
  map would destroy irreplaceable human curation, which is why W2 does not supersede. Status moves
  to ``MERGED`` when papers were added.
- ``promote`` / ``reject`` / ``mark_stale``: status transitions on an EXISTING artifact (body
  untouched) — ``PROMOTED`` / ``REJECTED`` / ``STALE`` respectively. Raise if the artifact does
  not exist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml


@dataclass(frozen=True)
class WriteOutcome:
    """What a ``write_result`` call actually did (L.B.6 F6).

    ``merged_*`` are meaningful only for ``mode="merge"``; a supersede/first write reports
    ``merged_added=0, merged_skipped=0`` with ``total`` = the artifact's block count. Returning
    these to the caller is the point: a merge that adds nothing looks identical to a successful
    update unless the counts come back.
    """

    path: Path
    merged_added: int = 0
    merged_skipped: int = 0
    total: int = 0

    def as_dict(self) -> dict:
        return {
            "path": str(self.path),
            "merged_added": self.merged_added,
            "merged_skipped": self.merged_skipped,
            "total": self.total,
        }

_SLUG_RE = re.compile(r'[\\/:*?"<>|\s]+')
_PAPER_KEY_RE = re.compile(r"<!--\s*w2:paper=(?P<id>\S+?)\s*-->")
_VALID_MODES = frozenset({"supersede", "merge", "promote", "reject", "mark_stale"})


def _slug(text: str, limit: int = 80) -> str:
    return _SLUG_RE.sub("_", str(text)).strip("_")[:limit].rstrip("_")


def _parse_blocks(body: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a W2 map body into ``(preamble, [(paper_id, block_text), ...])``.

    A block runs from its ``<!-- w2:paper=id -->`` marker to the next marker (or EOF). Text before
    the first marker is the preamble — free / human-authored sections, preserved verbatim on merge.
    A body with no markers is all preamble (nothing to key on).
    """
    matches = list(_PAPER_KEY_RE.finditer(body))
    if not matches:
        return body, []
    preamble = body[: matches[0].start()]
    blocks: list[tuple[str, str]] = []
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        blocks.append((m.group("id"), body[m.start() : end]))
    return preamble, blocks


def _merge_bodies(existing: str, incoming: str) -> tuple[str, int, int]:
    """Union two W2 map bodies by paper key. EXISTING WINS — its blocks (with any human
    annotations) are kept verbatim; incoming blocks for NEW keys are appended. Returns
    ``(merged_body, added_count, skipped_count)`` — ``skipped`` counts incoming blocks whose
    key already existed and were therefore DISCARDED (L.B.6 F6: a silently dropped recompute
    used to be invisible to the caller). Never clobbers an existing key, never duplicates one.
    """
    ex_pre, ex_blocks = _parse_blocks(existing)
    in_pre, in_blocks = _parse_blocks(incoming)
    seen = {pid for pid, _ in ex_blocks}
    merged = list(ex_blocks)
    added = 0
    skipped = 0
    for pid, block in in_blocks:
        if pid not in seen:
            merged.append((pid, block))
            seen.add(pid)
            added += 1
        else:
            skipped += 1
    preamble = ex_pre if ex_pre.strip() else in_pre
    parts: list[str] = []
    if preamble.strip():
        parts.append(preamble.strip())
    parts.extend(block.strip() for _, block in merged)
    return "\n\n".join(parts) + "\n", added, skipped


def _split_artifact(text: str) -> tuple[dict, str, str]:
    """Parse an existing artifact into ``(frontmatter, title, body)``.

    ``body`` is everything after the ``# {title}`` line. Robust to ``---`` inside the body: the
    frontmatter fence is split with ``maxsplit=2``, so any later ``---`` stays in the body.
    """
    _, fm_raw, rest = text.split("---", 2)
    fm = yaml.safe_load(fm_raw) or {}
    rest = rest.lstrip("\n")
    title = ""
    if rest.startswith("# "):
        line, _, rest = rest.partition("\n")
        title = line[2:].strip()
    return fm, title, rest.lstrip("\n")


class ResultService:
    """Write review-gated harness artifacts into the vault; mode governs the re-run semantics."""

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
        mode: str = "supersede",
    ) -> Path:
        """Write / merge / transition one harness artifact keyed by ``(kind, identity)``.

        ``mode`` selects the re-run semantics (see the module docstring). Returns the artifact
        path; call ``write_result_detailed`` when you also need the merge counts.
        """
        return self.write_result_detailed(
            kind=kind,
            identity=identity,
            title=title,
            body=body,
            metadata=metadata,
            mode=mode,
        ).path

    def write_result_detailed(
        self,
        *,
        kind: str,
        identity: str,
        title: str,
        body: str,
        metadata: dict | None = None,
        mode: str = "supersede",
    ) -> WriteOutcome:
        """As ``write_result``, but returns a ``WriteOutcome`` carrying the merge counts (F6)."""
        if mode not in _VALID_MODES:
            raise ValueError(f"write_result: unknown mode {mode!r} (expected one of {sorted(_VALID_MODES)})")
        ident = str(identity).strip()
        if not ident:
            raise ValueError("write_result requires a non-empty identity")
        path = self.results_dir / f"{_slug(kind)}__{_slug(ident)}.md"

        if mode in ("promote", "reject", "mark_stale"):
            new_status = {
                "promote": "PROMOTED",
                "reject": "REJECTED",
                "mark_stale": "STALE",
            }[mode]
            return self._transition(path, new_status)
        if mode == "merge" and path.exists():
            return self._merge(path, title=title, body=body, metadata=metadata)

        # supersede (W1) or a first-write merge (no prior artifact yet)
        return self._write(
            path,
            kind=kind,
            ident=ident,
            title=title,
            body=body,
            metadata=metadata,
            status="PENDING_REVIEW",
            superseded_prior=path.exists(),
        )

    def _write(
        self,
        path: Path,
        *,
        kind: str,
        ident: str,
        title: str,
        body: str,
        metadata: dict | None,
        status: str,
        superseded_prior: bool,
    ) -> WriteOutcome:
        fm: dict = {
            "type": kind,
            "status": status,
            "identity": ident,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "superseded_prior": superseded_prior,
        }
        if metadata:
            fm.update(metadata)
        content = (
            f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)}"
            f"---\n\n# {title}\n\n{body}\n"
        )
        path.write_text(content, encoding="utf-8")
        _, blocks = _parse_blocks(body)
        return WriteOutcome(path=path, total=len(blocks))

    def _merge(
        self, path: Path, *, title: str, body: str, metadata: dict | None
    ) -> WriteOutcome:
        fm, ex_title, existing_body = _split_artifact(path.read_text(encoding="utf-8"))
        merged_body, added, skipped = _merge_bodies(existing_body, body)
        fm["status"] = "MERGED" if added else fm.get("status", "PENDING_REVIEW")
        fm["merged_added"] = added
        fm["merged_skipped"] = skipped
        fm["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        if metadata:
            fm.update(metadata)
        final_title = title or ex_title or "W2 Breadth Map"
        content = (
            f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)}"
            f"---\n\n# {final_title}\n\n{merged_body}"
        )
        path.write_text(content, encoding="utf-8")
        _, merged_blocks = _parse_blocks(merged_body)
        return WriteOutcome(
            path=path,
            merged_added=added,
            merged_skipped=skipped,
            total=len(merged_blocks),
        )

    def _transition(self, path: Path, new_status: str) -> WriteOutcome:
        if not path.exists():
            raise FileNotFoundError(f"write_result {new_status}: no artifact at {path}")
        fm, title, body = _split_artifact(path.read_text(encoding="utf-8"))
        fm["status"] = new_status
        content = (
            f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)}"
            f"---\n\n# {title}\n\n{body}"
        )
        if not content.endswith("\n"):
            content += "\n"
        path.write_text(content, encoding="utf-8")
        _, blocks = _parse_blocks(body)
        return WriteOutcome(path=path, total=len(blocks))
