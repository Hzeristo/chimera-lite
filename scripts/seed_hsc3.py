#!/usr/bin/env python
"""HSC-3 seal seed for Phase O — grow the vault typed-edge graph to >= 20 PARTICIPATING nodes.

Phase O's Hard Sealing Condition 3 (docs/phases/phase-O.md) requires >= 20 vault nodes that
PARTICIPATE in the typed-edge graph (the N.B ``deep_recall`` unblock threshold; N.B.0 Q4
measured 0). This script drives the O.1b/O.2 write surface (StagingService + VaultReadAdapter).

METRIC — participation, NOT origins. N.B ``deep_recall`` traverses BIDIRECTIONALLY: outgoing
edges from a node's ``graph_edges`` frontmatter, AND incoming edges found by grepping other
nodes' ``graph_edges`` for ``[[this-node]]``. A node is traversable — "participates" — if it is:
  (a) a SOURCE — its own ``graph_edges`` has a non-empty list, OR
  (b) a TARGET — its stem appears as ``[[target]]`` in some other node's ``graph_edges``
                 (and it is a real vault node).
Directed edges live only on the source, so a target-only node (a K paper a thought points at)
is still fully traversable and MUST count. The old origin-only count under-reported and tempted
fabricating K->K edges to hit the number — that is gaming, not graph-building.

ARITHMETIC. A Thought that ``derives_from`` N real papers contributes 1 source + up to N new
targets = up to N+1 participants. So:
    3 existing thoughts + the ~9 distinct papers they point at   ~= 12 participating (today)
  + 5 real new thoughts + their (mostly new) target papers        -> >= 20
with ZERO fabricated K->K edges. Real paper->paper edges (A extends/contradicts B) are a BONUS,
not a requirement — add them via KNOWLEDGE_EDGES only if genuinely true.

USAGE (run from the repo root with the project venv):
    .venv/Scripts/python.exe scripts/seed_hsc3.py probe     # participation count (baseline / after)
    .venv/Scripts/python.exe scripts/seed_hsc3.py create    # write the Thought nodes to docs/staging/
    #   --> REVIEW docs/staging/ by hand <--
    .venv/Scripts/python.exe scripts/seed_hsc3.py promote   # move the reviewed Thoughts into the vault
    .venv/Scripts/python.exe scripts/seed_hsc3.py link      # (optional) apply REAL paper->paper edges
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

# 2) OPTIONAL — REAL paper->paper relationships only (A extends / contradicts / supersedes B).
#    Each tuple: (from_node, edge_type, to_node); the from_node's frontmatter gains the edge.
#    Valid K edges: derives_from | supersedes | contradicts (see NODE_ONTOLOGY.md).
#    NOT required to reach >= 20 — thoughts + their targets already do that under the
#    participation metric. Add entries here ONLY if the relationship is genuinely true; do NOT
#    fabricate K->K edges to inflate the count. `suggest` lists nodes not yet in the graph.
KNOWLEDGE_EDGES: list[tuple[str, str, str]] = [
    # ("<K paper A stem or arxiv>", "contradicts", "<K paper B>"),  # only if REAL
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


def _edge_target_stem(value) -> str:
    """Normalize a graph_edges target ('[[stem|alias]]' / '[[stem#h]]' / 'stem') to its stem."""
    s = str(value).strip()
    if s.startswith("[[") and s.endswith("]]"):
        s = s[2:-2]
    return s.split("|", 1)[0].split("#", 1)[0].strip()


def _scan_graph(vault_root: Path):
    """Walk live nodes once. Returns (node_type, sources, targets):
    node_type: {stem -> frontmatter type}; sources: stems with a non-empty own edge list;
    targets: normalized target stems referenced by any node's graph_edges."""
    node_type: dict[str, str] = {}
    sources: set[str] = set()
    targets: set[str] = set()
    for p in _iter_notes(vault_root):
        fm = _frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        node_type.setdefault(p.stem, str(fm.get("type", "?")))
        ge = fm.get("graph_edges")
        if not isinstance(ge, dict):
            continue
        has_edge = False
        for v in ge.values():
            if isinstance(v, list):
                for x in v:
                    if x:
                        has_edge = True
                        targets.add(_edge_target_stem(x))
        if has_edge:
            sources.add(p.stem)
    return node_type, sources, targets


def cmd_probe(cfg, svc, adapter) -> None:
    vault_root = _vault_root(cfg)
    node_type, sources, targets = _scan_graph(vault_root)
    all_stems = set(node_type)
    resolved_targets = targets & all_stems       # targets that are real vault nodes
    dangling = targets - all_stems
    participants = sources | resolved_targets

    per_type: dict[str, int] = defaultdict(int)
    for stem in participants:
        per_type[node_type.get(stem, "?")] += 1

    print(f"Graph PARTICIPATION (source OR target): {len(participants)}")
    print(f"    sources  (own non-empty edges) : {len(sources)}")
    print(f"    targets  (pointed at, resolved): {len(resolved_targets)}")
    if dangling:
        print(f"    dangling targets (no vault node): {len(dangling)}")
    for t, n in sorted(per_type.items()):
        print(f"    participating {t}: {n}")
    print(f"HSC 3 (>= 20 participating nodes): {'PASS' if len(participants) >= 20 else 'NOT YET'}")


def cmd_suggest(cfg, svc, adapter) -> None:
    """List Knowledge nodes NOT yet participating (neither source nor target) — the unconnected
    papers a new thought could point at to grow participation."""
    vault_root = _vault_root(cfg)
    node_type, sources, targets = _scan_graph(vault_root)
    participating = sources | (targets & set(node_type))
    candidates = [
        stem for stem, t in sorted(node_type.items())
        if t == "knowledge" and stem not in participating
    ]
    print(f"{len(candidates)} Knowledge node(s) not yet in the graph (link candidates):")
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
