"""O.1b: create_node (StagingService) writes K/T/I/D staging nodes with typed edges.

Unit-level — exercises StagingService directly against tmp dirs (no config/env), so it
verifies the ratified NODE_ONTOLOGY.md vocabulary, the open-but-validated edge merge, and
the never-auto-promote contract without a live vault.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_DOMAIN = Path(__file__).resolve().parents[1] / "mcp-servers" / "chimera-papers"
if str(_DOMAIN) not in sys.path:
    sys.path.insert(0, str(_DOMAIN))

from staging_service import StagingService, _TYPE_DEST, _TYPE_EDGES  # noqa: E402

# The canonical sets from docs/ARCHITECTURE/NODE_ONTOLOGY.md §2 (post-ratification).
CANONICAL = {
    "knowledge": {"derives_from", "supersedes", "contradicts"},
    "thought": {"derives_from", "supersedes", "contradicts", "dead_ends", "drives_decision"},
    "insight": {"synthesizes", "evidence_base", "derives_from", "drives_decision", "supersedes", "contradicts"},
    "decision": {"derives_from", "drives_decision", "dead_ends", "supersedes", "contradicts"},
}


def _read_frontmatter(path: Path) -> dict:
    _, fm_raw, _ = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(fm_raw)


def test_ontology_mirrors_node_ontology_doc() -> None:
    """_TYPE_EDGES / _TYPE_DEST match the ratified authority (renames applied, K added)."""
    assert set(_TYPE_DEST) == {"knowledge", "thought", "insight", "decision"}
    assert _TYPE_DEST["knowledge"] == "Knowledge"
    for node_type, keys in CANONICAL.items():
        assert set(_TYPE_EDGES[node_type]) == keys, node_type
    # Ratified renames: old code-only keys are gone.
    assert "verified_with" not in _TYPE_EDGES["insight"]
    assert "depends_on" not in _TYPE_EDGES["decision"]


@pytest.mark.parametrize("node_type", ["knowledge", "thought", "insight", "decision"])
def test_create_node_writes_typed_edges(tmp_path: Path, node_type: str) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(type=node_type, title=f"Test {node_type}", body="body text")

    assert path.exists()
    assert path.parent == tmp_path / "staging"          # staged, not vaulted
    fm = _read_frontmatter(path)
    assert fm["type"] == node_type
    assert fm["status"] == "PENDING_REVIEW"
    assert set(fm["graph_edges"]) == CANONICAL[node_type]


def test_edges_merge_populates_valid_key(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(
        type="thought", title="linked thought", body="b",
        edges={"derives_from": ["Some Note"]},
    )
    fm = _read_frontmatter(path)
    assert fm["graph_edges"]["derives_from"] == ["[[Some Note]]"]  # normalized to wikilink form
    # untouched keys stay empty
    assert fm["graph_edges"]["dead_ends"] == []


def test_edges_prewrapped_not_double_wrapped(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(
        type="thought", title="pw", body="b",
        edges={"derives_from": ["[[Already Linked]]"]},
    )
    fm = _read_frontmatter(path)
    assert fm["graph_edges"]["derives_from"] == ["[[Already Linked]]"]  # no double [[ ]]


def test_unknown_edge_key_is_rejected_loudly(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    with pytest.raises(ValueError, match="Unknown edge"):
        svc.create_staging_node(
            type="thought", title="bad", body="b",
            edges={"bogus_edge": ["x"]},
        )


def test_unknown_type_is_rejected(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    with pytest.raises(ValueError, match="Unknown node type"):
        svc.create_staging_node(type="paper", title="x", body="b")


def test_create_never_promotes_into_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    svc.create_staging_node(type="knowledge", title="k node", body="b")
    # Nothing lands under the vault root — creation is staging-only.
    assert not list(vault.rglob("*.md"))
