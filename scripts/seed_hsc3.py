#!/usr/bin/env python
"""HSC-3 seal seed for Phase O — grow the vault typed-edge graph to >= 20 origin nodes.

Phase O's Hard Sealing Condition 3 (docs/phases/phase-O.md) requires that, after seeding
Thought nodes + typed edges, the vault shows >= 20 nodes whose ``graph_edges`` is non-empty
(the N.B ``deep_recall`` unblock threshold; N.B.0 Q4 measured 0). This script drives the
O.1b/O.2 write surface (StagingService + VaultReadAdapter) to seed that graph.

ARITHMETIC (see docs/plans/Phase-O-batch.md, O.3 note). The probe counts EDGE-ORIGIN nodes —
a node whose OWN frontmatter has a populated edge list (excluding .migration_backup/ and
templates/). An edge added by ``link_nodes`` lands on its FROM node, so only FROM nodes count.
Run `probe` first for the live baseline B; you then need (20 - B) more origin nodes:
    5 Thought nodes (each with derives_from populated at creation) = 5 origins
  + ~(15 - B) edges each originating from a DISTINCT existing Knowledge node
  ----------------------------------------------------------------------------------
  = >= 20 origin nodes.  (Live baseline is ~1, so ~14 K-origin edges + 5 thoughts.)
So the seed necessarily touches ~15 existing K nodes (targeted, NOT the out-of-scope
250-node bulk backfill). Fill KNOWLEDGE_EDGES below with REAL relationships between your
papers — this is genuine graph-building, not metric-gaming.

USAGE (run from the repo root with the project venv):
    .venv/Scripts/python.exe scripts/seed_hsc3.py probe     # count origin nodes (baseline / after)
    .venv/Scripts/python.exe scripts/seed_hsc3.py create    # write the Thought nodes to docs/staging/
    #   --> REVIEW docs/staging/ by hand <--
    .venv/Scripts/python.exe scripts/seed_hsc3.py promote   # move the reviewed Thoughts into the vault
    .venv/Scripts/python.exe scripts/seed_hsc3.py link      # stage + apply the typed edges
    .venv/Scripts/python.exe scripts/seed_hsc3.py probe     # confirm >= 20

`create` and `promote` are separate ON PURPOSE — nothing reaches the live vault until you run
`promote`/`link` explicitly (the never-auto-promote red line). The equivalent MCP-tool sequence
(after reloading chimera-vault) is: create_node -> [review] -> (promote) -> link_nodes ->
apply_link_patch; this script is that sequence's reference implementation via the domain layer.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

_DOMAIN = Path(__file__).resolve().parents[1] / "mcp-servers" / "chimera-papers"
if str(_DOMAIN) not in sys.path:
    sys.path.insert(0, str(_DOMAIN))

# ================================ EDIT ME ========================================
# 1) The 5 Thought nodes to seed. Each `derives_from` REAL Knowledge nodes already in
#    your vault, referenced by note stem (filename without .md) or arxiv_id.
THOUGHTS: list[dict] = [
    {
        "title": "PLACEHOLDER Thought 1 — replace me",
        "body": "Working note body. Replace with a real thought.",
        "derives_from": ["<REAL_K_STEM_OR_ARXIV_1>", "<REAL_K_STEM_OR_ARXIV_2>"],
    },
    {"title": "PLACEHOLDER Thought 2", "body": "...", "derives_from": ["<REAL_K_2>"]},
    {"title": "PLACEHOLDER Thought 3", "body": "...", "derives_from": ["<REAL_K_3>"]},
    {"title": "PLACEHOLDER Thought 4", "body": "...", "derives_from": ["<REAL_K_4>"]},
    {"title": "PLACEHOLDER Thought 5", "body": "...", "derives_from": ["<REAL_K_5>"]},
]

# 2) Typed edges that make EXISTING Knowledge nodes into edge-origins (to clear >= 20).
#    Each tuple: (from_node, edge_type, to_node). The from_node's frontmatter gains the edge.
#    Valid K edges: derives_from | supersedes | contradicts (see NODE_ONTOLOGY.md).
#    Add ~15 REAL relationships between your papers.  Run `python scripts/seed_hsc3.py suggest`
#    to list Knowledge nodes that currently have NO typed edges (good link candidates).
KNOWLEDGE_EDGES: list[tuple[str, str, str]] = [
    # ("<K paper A stem or arxiv>", "contradicts", "<K paper B>"),
    # ("<K paper C>", "supersedes", "<K paper D>"),
    # ... ~15 real ones ...
]
# =================================================================================


def _services():
    from core.config import get_config
    from ports.vault.vault_read_adapter import VaultReadAdapter
    from staging_service import StagingService

    cfg = get_config()
    svc = StagingService(cfg.system.staging_dir, cfg.require_path("vault_root"))
    adapter = VaultReadAdapter(cfg)
    return cfg, svc, adapter


def _vault_root(cfg) -> Path:
    root = cfg.vault_root
    if root is None or not root.is_dir():
        raise SystemExit("vault_root is not configured / not a directory.")
    return root


def _frontmatter(text: str) -> dict:
    if not text.lstrip().startswith("---"):
        return {}
    try:
        return yaml.safe_load(text.split("---", 2)[1]) or {}
    except Exception:
        return {}


# Non-live dirs excluded from the graph count: Obsidian internals, backups, sync templates.
_NONVAULT_DIRS = {".obsidian", ".migration_backup", "templates"}


def _iter_notes(vault_root: Path):
    for p in sorted(vault_root.rglob("*.md")):
        if _NONVAULT_DIRS & set(p.relative_to(vault_root).parts):
            continue
        yield p


def _has_typed_edges(fm: dict) -> bool:
    ge = fm.get("graph_edges")
    return isinstance(ge, dict) and any(
        isinstance(v, list) and len(v) > 0 for v in ge.values()
    )


def cmd_probe(cfg, svc, adapter) -> None:
    vault_root = _vault_root(cfg)
    total = 0
    per_type: dict[str, int] = defaultdict(int)
    for p in _iter_notes(vault_root):
        fm = _frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        if _has_typed_edges(fm):
            total += 1
            per_type[str(fm.get("type", "?"))] += 1
    print(f"Nodes with non-empty typed graph_edges: {total}")
    for t, n in sorted(per_type.items()):
        print(f"    {t}: {n}")
    print(f"HSC 3 (>= 20 origin nodes): {'PASS' if total >= 20 else 'NOT YET'}")


def cmd_suggest(cfg, svc, adapter) -> None:
    """List Knowledge nodes that currently have NO typed edges — link candidates."""
    vault_root = _vault_root(cfg)
    candidates = []
    for p in _iter_notes(vault_root):
        fm = _frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        if str(fm.get("type")) == "knowledge" and not _has_typed_edges(fm):
            candidates.append(p.stem)
    print(f"{len(candidates)} Knowledge node(s) with no typed edges (link candidates):")
    for stem in candidates[:40]:
        print(f"    {stem}")
    if len(candidates) > 40:
        print(f"    ... and {len(candidates) - 40} more")


def cmd_create(cfg, svc, adapter) -> None:
    for t in THOUGHTS:
        derives = [d for d in t.get("derives_from", []) if not d.startswith("<")]
        edges = {"derives_from": derives} if derives else None
        path = svc.create_staging_node(
            type="thought", title=t["title"], body=t["body"], edges=edges
        )
        print(f"    staged: {path.name}  (derives_from={derives or '[]'})")
    print("\nReview docs/staging/, then run:  scripts/seed_hsc3.py promote")


def cmd_promote(cfg, svc, adapter) -> None:
    titles = {t["title"] for t in THOUGHTS}
    promoted = 0
    for p in sorted(svc.staging_dir.glob("*.md")):
        fm = _frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        if (
            fm.get("type") == "thought"
            and fm.get("title") in titles
            and fm.get("status") == "PENDING_REVIEW"
        ):
            dest = svc.promote_node(p)
            print(f"    promoted: {dest}")
            promoted += 1
    print(f"\nPromoted {promoted} thought node(s). Next:  scripts/seed_hsc3.py link")


def cmd_link(cfg, svc, adapter) -> None:
    applied = 0
    for from_node, edge_type, to_node in KNOWLEDGE_EDGES:
        from_path = adapter.resolve_note_path(from_node)
        if from_path is None:
            print(f"    SKIP (from unresolved): {from_node!r}")
            continue
        to_path = adapter.resolve_note_path(to_node)
        if to_path is None:
            print(f"    SKIP (to unresolved): {to_node!r}")
            continue
        fm = _frontmatter(from_path.read_text(encoding="utf-8", errors="ignore"))
        from_type = str(fm.get("type", "")).strip()
        try:
            patch = svc.stage_link_patch(
                from_stem=from_path.stem, from_path=from_path, from_type=from_type,
                edge_type=edge_type, to_stem=to_path.stem, to_path=to_path,
            )
            svc.apply_link_patch(patch)
            print(f"    linked: {from_path.stem} --{edge_type}--> {to_path.stem}")
            applied += 1
        except (ValueError, FileNotFoundError) as e:
            print(f"    ERROR: {e}")
    print(f"\nApplied {applied} edge(s). Confirm with:  scripts/seed_hsc3.py probe")


_COMMANDS = {
    "probe": cmd_probe,
    "suggest": cmd_suggest,
    "create": cmd_create,
    "promote": cmd_promote,
    "link": cmd_link,
}


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if cmd not in _COMMANDS:
        raise SystemExit(f"Usage: seed_hsc3.py [{' | '.join(_COMMANDS)}]")
    cfg, svc, adapter = _services()
    _COMMANDS[cmd](cfg, svc, adapter)


if __name__ == "__main__":
    main()
