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


def test_promote_node_is_retired(tmp_path: Path) -> None:
    """`promote_node` promoted staged T/I/D into the vault — an affordance for machine-written
    judgment bodies (I0.5 forbids them) that nothing ever used: every T/I/D node in the vault
    was hand-written in Obsidian. Retired 2026-08-11; its absence is the guarantee."""
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    assert not hasattr(svc, "promote_node")


@pytest.mark.parametrize("node_type", ["thought", "insight", "decision"])
def test_staging_refuses_to_author_judgment_nodes(tmp_path: Path, node_type: str) -> None:
    """I0.5 (Tier 0): T/I/D bodies are Architect-authored.

    `body` is caller-supplied and the caller of the MCP surface is Claude, so any T/I/D node
    created here carries an AI-written judgment body — "illegal, even if promoted". The staging
    buffer exists for AI-authored content (I1.2), which a judgment node must never be.
    """
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")

    with pytest.raises(ValueError, match="knowledge-only"):
        svc.create_staging_node(type=node_type, title=f"A {node_type}", body="AI-written")

    assert not list((tmp_path / "staging").glob("*.md"))


@pytest.mark.parametrize("dest_sub", ["Thoughts", "Insight", "Decision"])
def test_no_code_path_writes_a_judgment_node(tmp_path: Path, dest_sub: str) -> None:
    """The committed writer refuses every destination but Knowledge/.

    Belt to the braces above: even handed a T/I/D frontmatter directly, the one writer left
    will not put it in the vault.
    """
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    node_type = {"Thoughts": "thought", "Insight": "insight", "Decision": "decision"}[dest_sub]
    staged = tmp_path / "staging" / "handmade.md"
    staged.parent.mkdir(parents=True, exist_ok=True)
    # deep_read so ascend_node's TIER check passes and the DESTINATION guard is what fires.
    staged.write_text(
        f"---\ntype: {node_type}\nchimera_tier: deep_read\ntitle: Smuggled\n---\n\nbody\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="committed K tier only"):
        svc.ascend_node(staged)

    assert not (vault / dest_sub).exists()


def test_ascend_node_uses_the_vault_arxiv_id_moniker_convention(tmp_path: Path) -> None:
    """Incident 2026-08-12 "the gate that overwrites": the committed stem is `{id}-{Moniker}`.

    This is the vault's existing convention (`core.naming.expected_stem`), which every paper
    asset and `derives_from` target already used; only this writer diverged, slugging
    `title[:60]` and cutting mid-word. The moniker is the title's pre-colon segment because
    `KNodeExtraction.title` specifies that shape (`core/schemas.py:363`).
    """
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    staged = svc.create_staging_node(
        type="knowledge",
        title="MEMDREAMER: Hierarchical Graph Memory and Agentic Tool Retrieval for Long Video",
        body="b",
        chimera_tier="deep_read",
        metadata={"arxiv_id": "2606.07512"},
    )

    dest = svc.ascend_node(staged)

    assert dest == vault / "Knowledge" / "2606.07512-MEMDREAMER.md"
    # the old behaviour truncated mid-word; nothing may reintroduce it
    assert "Retrie.md" not in dest.name
    assert len(dest.stem) < 60


def test_ascend_node_refuses_to_overwrite_a_committed_node(tmp_path: Path) -> None:
    """I0.4: committed nodes are never deleted. Two ascends of one paper must not silently
    destroy the first — the realistic trigger is a re-extract at a new arXiv version, whose
    title (and therefore stem) is identical."""
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    kwargs = dict(
        type="knowledge",
        title="FluxMem: Training-Free Hierarchical Token Compression",
        body="first",
        chimera_tier="deep_read",
        metadata={"arxiv_id": "2603.02096"},
    )
    first = svc.ascend_node(svc.create_staging_node(**kwargs))
    assert first.read_text(encoding="utf-8").endswith("first\n") or "first" in first.read_text(
        encoding="utf-8"
    )

    second = svc.create_staging_node(**{**kwargs, "body": "second"})
    with pytest.raises(ValueError, match="Refusing to overwrite"):
        svc.ascend_node(second)

    assert "first" in first.read_text(encoding="utf-8")  # the committed node survived
    assert second.exists()  # and the staging file was NOT consumed


def test_ascend_node_allows_deliberate_supersession(tmp_path: Path) -> None:
    """The escape hatch is explicit: name the prior in `supersedes` and the replace proceeds."""
    vault = tmp_path / "vault"
    svc = StagingService(tmp_path / "staging", vault)
    kwargs = dict(
        type="knowledge",
        title="FluxMem: Training-Free Hierarchical Token Compression",
        body="first",
        chimera_tier="deep_read",
        metadata={"arxiv_id": "2603.02096"},
    )
    svc.ascend_node(svc.create_staging_node(**kwargs))

    replacement = svc.create_staging_node(
        **{**kwargs, "body": "second"},
        edges={"supersedes": ["2603.02096-FluxMem"]},
    )
    dest = svc.ascend_node(replacement)

    assert "second" in dest.read_text(encoding="utf-8")
