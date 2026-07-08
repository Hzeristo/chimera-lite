"""Staging protocol: create / promote / reject candidate K/T/I/D nodes."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import yaml

# K/T/I/D typed-edge vocabulary — mirrors docs/ARCHITECTURE/NODE_ONTOLOGY.md (the authority).
_TYPE_DEST = {"knowledge": "Knowledge", "thought": "Thoughts", "insight": "Insight", "decision": "Decision"}
_TYPE_EDGES: dict[str, dict[str, list]] = {
    "knowledge": {"derives_from": [], "supersedes": [], "contradicts": []},
    "thought":   {"derives_from": [], "supersedes": [], "contradicts": [], "dead_ends": [], "drives_decision": []},
    "insight":   {"synthesizes": [], "evidence_base": [], "derives_from": [], "drives_decision": [], "supersedes": [], "contradicts": []},
    "decision":  {"derives_from": [], "drives_decision": [], "dead_ends": [], "supersedes": [], "contradicts": []},
}
_SLUG_RE = re.compile(r'[\\/:*?"<>|\s]+')


class StagingService:
    def __init__(self, staging_dir: Path, vault_root: Path) -> None:
        self.staging_dir = staging_dir
        self.vault_root = vault_root
        staging_dir.mkdir(parents=True, exist_ok=True)

    def create_staging_node(
        self,
        type: str,
        title: str,
        body: str,
        edges: dict | None = None,
    ) -> Path:
        node_type = type.lower()
        if node_type not in _TYPE_DEST:
            raise ValueError(f"Unknown node type: {type!r}")
        graph_edges = dict(_TYPE_EDGES[node_type])
        if edges:
            for k, v in edges.items():
                if k not in graph_edges:
                    raise ValueError(
                        f"Unknown edge {k!r} for node type {node_type!r}; "
                        f"valid: {sorted(graph_edges)}"
                    )
                graph_edges[k] = v
        fm = {
            "type": node_type,
            "status": "PENDING_REVIEW",
            "title": title,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "tags": [node_type],
            "graph_edges": graph_edges,
        }
        slug = _SLUG_RE.sub("_", title)[:60].rstrip("_")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.staging_dir / f"{stamp}-{slug}.md"
        content = f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False)}---\n\n# {title}\n\n{body}\n"
        path.write_text(content, encoding="utf-8")
        return path

    def promote_node(self, staging_path: Path) -> Path:
        text = staging_path.read_text(encoding="utf-8")
        _, fm_raw, body = text.split("---", 2)
        fm = yaml.safe_load(fm_raw)
        node_type = fm.get("type", "thought")
        dest_sub = _TYPE_DEST.get(node_type, "Thoughts")
        fm["status"] = "active"
        slug = _SLUG_RE.sub("_", fm.get("title", "untitled"))[:60].rstrip("_")
        dest_dir = self.vault_root / dest_sub
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"{slug}.md"
        dest_path.write_text(
            f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False)}---\n{body}",
            encoding="utf-8",
        )
        staging_path.unlink()
        return dest_path

    def reject_node(self, staging_path: Path) -> None:
        staging_path.unlink()

    def stage_link_patch(
        self,
        from_stem: str,
        from_path: Path,
        from_type: str,
        edge_type: str,
        to_stem: str,
        to_path: Path | None = None,
    ) -> Path:
        """Write a reviewable link patch to the staging area (no live vault write).

        Records: append ``to_stem`` to ``graph_edges.<edge_type>`` of the FROM node
        (``from_path``). ``edge_type`` is validated against the ratified
        NODE_ONTOLOGY.md vocabulary for ``from_type``. Apply after review with
        ``apply_link_patch`` (O.2b). Returns the patch path.
        """
        node_type = from_type.lower()
        if node_type not in _TYPE_EDGES:
            raise ValueError(f"Unknown node type: {from_type!r}")
        if edge_type not in _TYPE_EDGES[node_type]:
            raise ValueError(
                f"Invalid edge {edge_type!r} for node type {node_type!r}; "
                f"valid: {sorted(_TYPE_EDGES[node_type])}"
            )
        patch = {
            "patch_type": "link",
            "status": "PENDING_REVIEW",
            "from": from_stem,
            "from_path": str(from_path),
            "from_type": node_type,
            "edge_type": edge_type,
            "to": to_stem,
            "to_path": str(to_path) if to_path is not None else None,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
        }
        slug = _SLUG_RE.sub("_", f"{from_stem}__{edge_type}__{to_stem}")[:80].rstrip("_")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.staging_dir / f"{stamp}-linkpatch-{slug}.md"
        body = (
            f"# Link patch: [[{from_stem}]] --{edge_type}--> [[{to_stem}]]\n\n"
            f"Adds `{to_stem}` to `graph_edges.{edge_type}` of `{from_path}`.\n\n"
            f"Review, then apply with `apply_link_patch`.\n"
        )
        content = (
            f"---\n{yaml.dump(patch, allow_unicode=True, default_flow_style=False, sort_keys=False)}"
            f"---\n\n{body}"
        )
        path.write_text(content, encoding="utf-8")
        return path
