"""O.2a: link_nodes stages a reviewable patch (no live vault write).

Unit-level covers StagingService.stage_link_patch (validation + patch + no vault write).
A skippable live test exercises VaultReadAdapter.resolve_note_path against the real vault.
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


def test_stage_link_patch_writes_reviewable_patch(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    patch = svc.stage_link_patch(
        from_stem="Alpha Thought",
        from_path=tmp_path / "vault" / "Thoughts" / "Alpha Thought.md",
        from_type="thought",
        edge_type="derives_from",
        to_stem="Beta Paper",
        to_path=tmp_path / "vault" / "Knowledge" / "Beta Paper.md",
    )
    assert patch.parent == tmp_path / "staging"
    fm = _read_frontmatter(patch)
    assert fm["patch_type"] == "link"
    assert fm["status"] == "PENDING_REVIEW"
    assert fm["from_type"] == "thought"
    assert fm["edge_type"] == "derives_from"
    assert fm["to"] == "Beta Paper"
    # Staging-only — nothing lands in the vault.
    assert not list((tmp_path / "vault").rglob("*.md"))


def test_stage_link_patch_rejects_edge_wrong_for_type(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    # `synthesizes` is insight-only — invalid for a thought.
    with pytest.raises(ValueError, match="Invalid edge"):
        svc.stage_link_patch(
            from_stem="a", from_path=tmp_path / "a.md", from_type="thought",
            edge_type="synthesizes", to_stem="b",
        )


def test_stage_link_patch_rejects_unknown_type(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    with pytest.raises(ValueError, match="Unknown node type"):
        svc.stage_link_patch(
            from_stem="a", from_path=tmp_path / "a.md", from_type="paper",
            edge_type="derives_from", to_stem="b",
        )


def _vault_available() -> bool:
    try:
        from core.config import get_config

        return get_config().system.vault_root is not None
    except Exception:
        return False


@pytest.mark.skipif(not _vault_available(), reason="vault_root not configured")
def test_resolve_note_path_live() -> None:
    from core.config import get_config
    from ports.vault.vault_read_adapter import VaultReadAdapter

    cfg = get_config()
    adapter = VaultReadAdapter(cfg)
    vault_root = cfg.vault_root
    if vault_root is None or not vault_root.is_dir():
        pytest.skip("vault root not a directory")

    known = next(
        (p for p in vault_root.rglob("*.md")
         if ".obsidian" not in p.relative_to(vault_root).parts),
        None,
    )
    if known is None:
        pytest.skip("no notes in vault")

    resolved = adapter.resolve_note_path(known.stem)
    assert resolved is not None and resolved.stem == known.stem
    assert adapter.resolve_note_path("definitely-not-a-real-node-xyz123") is None


# --- O.2b: apply_link_patch (the one live-vault write) -----------------------------

# A node whose frontmatter deliberately uses quoting + inline lists a naive YAML
# round-trip would mangle, and a body containing a `---` horizontal rule.
_TARGET_NODE = '''---
type: thought
status: active
title: "My Title"
tags: [thought]
graph_edges:
  derives_from: []
  supersedes: []
lesson: "keep this exactly"
---

# My Title

Body line one.

---

After a horizontal rule.
'''


def _make_target(tmp_path: Path) -> Path:
    target = tmp_path / "vault" / "Thoughts" / "My Title.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_TARGET_NODE, encoding="utf-8")
    return target


def test_apply_link_patch_merges_edge(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    target = _make_target(tmp_path)
    patch = svc.stage_link_patch(
        from_stem="My Title", from_path=target, from_type="thought",
        edge_type="derives_from", to_stem="Some Source", to_path=None,
    )
    result = svc.apply_link_patch(patch)

    assert result == target
    assert not patch.exists()  # consumed
    fm = _read_frontmatter(target)
    assert fm["graph_edges"]["derives_from"] == ["Some Source"]
    assert fm["graph_edges"]["supersedes"] == []  # sibling edge untouched


def test_apply_preserves_body_and_nonedge_frontmatter_verbatim(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    target = _make_target(tmp_path)
    body_before = _TARGET_NODE.split("---", 2)[2]

    patch = svc.stage_link_patch(
        from_stem="My Title", from_path=target, from_type="thought",
        edge_type="derives_from", to_stem="Some Source",
    )
    svc.apply_link_patch(patch)
    new_text = target.read_text(encoding="utf-8")

    # Non-edge frontmatter kept byte-for-byte (a YAML round-trip would drop quotes / reflow).
    assert 'title: "My Title"' in new_text
    assert "tags: [thought]" in new_text
    assert 'lesson: "keep this exactly"' in new_text
    # Body (including the `---` rule) preserved exactly.
    assert new_text.split("---", 2)[2] == body_before


def test_apply_link_patch_is_idempotent(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    target = _make_target(tmp_path)
    for _ in range(2):
        patch = svc.stage_link_patch(
            from_stem="My Title", from_path=target, from_type="thought",
            edge_type="derives_from", to_stem="Some Source",
        )
        svc.apply_link_patch(patch)
        assert not patch.exists()
    fm = _read_frontmatter(target)
    assert fm["graph_edges"]["derives_from"] == ["Some Source"]  # no duplicate


def test_apply_rejects_non_link_patch(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    bogus = tmp_path / "staging" / "bogus.md"
    bogus.parent.mkdir(parents=True, exist_ok=True)
    bogus.write_text("---\npatch_type: something_else\n---\n\nnope\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Not a link patch"):
        svc.apply_link_patch(bogus)


def test_apply_on_knowledge_node_keeps_closing_fence(tmp_path: Path) -> None:
    """K nodes put graph_edges LAST in frontmatter — the splice must not eat the fence."""
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    target = tmp_path / "vault" / "Knowledge" / "Paper.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        '---\ntype: knowledge\nstatus: unverified\ntitle: "Paper"\n'
        "graph_edges:\n  derives_from: []\n  supersedes: []\n  contradicts: []\n"
        "---\n\n# Paper\n\nbody\n",
        encoding="utf-8",
    )
    patch = svc.stage_link_patch(
        from_stem="Paper", from_path=target, from_type="knowledge",
        edge_type="contradicts", to_stem="Rival",
    )
    svc.apply_link_patch(patch)
    new_text = target.read_text(encoding="utf-8")
    assert "\n---\n\n# Paper" in new_text          # closing fence intact on its own line
    fm = _read_frontmatter(target)
    assert fm["graph_edges"]["contradicts"] == ["Rival"]
