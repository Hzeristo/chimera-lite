"""L.B.3: ascend_node is the SOLE writer of <vault>/Knowledge/.

Unit-level — exercises StagingService directly against tmp dirs (mirrors
tests/test_staging_tools.py). Covers: a deep_read K node ascends; a non-deep_read
(scout/synthesis/untiered) K node is refused by ascend_node; promote_node structurally
refuses deep_read nodes (the guard that makes ascend_node's sole-writer guarantee
code-enforced, not conventional); promote_node still works for T/I/D nodes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_DOMAIN = Path(__file__).resolve().parents[1] / "mcp-servers" / "chimera-papers"
if str(_DOMAIN) not in sys.path:
    sys.path.insert(0, str(_DOMAIN))

from staging_service import StagingService  # noqa: E402


def _read_frontmatter(path: Path) -> dict:
    _, fm_raw, _ = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(fm_raw)


def test_ascend_node_promotes_deep_read_k_node_to_knowledge(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    staged = svc.create_staging_node(
        type="knowledge", title="Deep Read Node", body="b", chimera_tier="deep_read"
    )

    dest = svc.ascend_node(staged)

    assert dest == vault / "Knowledge" / "Deep_Read_Node.md"
    assert dest.exists()
    fm = _read_frontmatter(dest)
    assert fm["status"] == "active"
    assert fm["chimera_tier"] == "deep_read"
    assert not staged.exists()  # staging file consumed


@pytest.mark.parametrize("tier", ["scout", "synthesis", None])
def test_ascend_node_refuses_non_deep_read_tier(tmp_path: Path, tier: str | None) -> None:
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    staged = svc.create_staging_node(
        type="knowledge", title="Not Deep Read", body="b", chimera_tier=tier
    )

    with pytest.raises(ValueError, match="deep_read"):
        svc.ascend_node(staged)

    assert not (vault / "Knowledge").exists() or not list((vault / "Knowledge").glob("*.md"))
    assert staged.exists()  # refused — staging file untouched


def test_promote_node_refuses_deep_read_node_structurally(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    staged = svc.create_staging_node(
        type="knowledge", title="Deep Read Via Promote", body="b", chimera_tier="deep_read"
    )

    with pytest.raises(ValueError, match="ascend_node"):
        svc.promote_node(staged)

    assert not (vault / "Knowledge").exists() or not list((vault / "Knowledge").glob("*.md"))
    assert staged.exists()  # refused — staging file untouched


@pytest.mark.parametrize(
    "node_type,dest_sub",
    [("thought", "Thoughts"), ("insight", "Insight"), ("decision", "Decision")],
)
def test_promote_node_still_works_for_tid_nodes(
    tmp_path: Path, node_type: str, dest_sub: str
) -> None:
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    staged = svc.create_staging_node(type=node_type, title=f"A {node_type}", body="b")

    dest = svc.promote_node(staged)

    assert dest == vault / dest_sub / f"A_{node_type}.md"
    assert dest.exists()
    fm = _read_frontmatter(dest)
    assert fm["status"] == "active"
    assert not staged.exists()
