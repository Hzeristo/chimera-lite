"""Q.2a: citation-resolution grounding — edges come ONLY from resolved citations,
NEVER topic/keyword similarity (Decision D3).
"""

from __future__ import annotations

from pathlib import Path

from core.schemas import EdgeProposal
from grounding import resolve_citations

_KNOWLEDGE_FM = """---
type: knowledge
status: active
title: {title}
---

# {title}
"""

_THOUGHT_FM = """---
type: thought
status: active
title: {title}
---

# {title}
"""


def _make_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "2305.16291-VOYAGER.md").write_text(
        _KNOWLEDGE_FM.format(title="VOYAGER"), encoding="utf-8"
    )
    (vault / "2409.07429-AWM.md").write_text(
        _KNOWLEDGE_FM.format(title="AWM"), encoding="utf-8"
    )
    (vault / "2311.00001-SomeThought.md").write_text(
        _THOUGHT_FM.format(title="SomeThought"), encoding="utf-8"
    )
    backup_dir = vault / ".migration_backup"
    backup_dir.mkdir()
    (backup_dir / "2401.99999-Backup.md").write_text(
        _KNOWLEDGE_FM.format(title="Backup"), encoding="utf-8"
    )
    return vault


def test_resolves_arxiv_id_to_knowledge_node(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    proposals = resolve_citations(["2305.16291"], vault)
    assert len(proposals) == 1
    proposal = proposals[0]
    assert isinstance(proposal, EdgeProposal)
    assert proposal.target_stem == "2305.16291-VOYAGER"
    assert proposal.edge_type == "derives_from"
    assert proposal.source_citation == "2305.16291"


def test_id_not_in_vault_resolves_to_nothing(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    assert resolve_citations(["1234.56789"], vault) == []


def test_migration_backup_note_never_proposed(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    # The id exists ONLY inside .migration_backup — must resolve to nothing.
    assert resolve_citations(["2401.99999"], vault) == []


def test_thought_node_never_proposed(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    # The id exists ONLY on a type: thought note — must resolve to nothing.
    assert resolve_citations(["2311.00001"], vault) == []


def test_templates_dir_excluded(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    templates_dir = vault / "templates"
    templates_dir.mkdir()
    (templates_dir / "2501.11111-Template.md").write_text(
        _KNOWLEDGE_FM.format(title="Template"), encoding="utf-8"
    )
    assert resolve_citations(["2501.11111"], vault) == []


def test_title_fallback_when_no_arxiv_id_in_reference(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    (vault / "NoIdTitle.md").write_text(
        _KNOWLEDGE_FM.format(title="NoIdTitle"), encoding="utf-8"
    )
    proposals = resolve_citations(["NoIdTitle"], vault)
    assert len(proposals) == 1
    assert proposals[0].target_stem == "NoIdTitle"


def test_multiple_references_dedup_and_mix(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    proposals = resolve_citations(
        ["2305.16291", "2305.16291", "2409.07429", "9999.99999"], vault
    )
    keys = {(p.target_stem, p.source_citation) for p in proposals}
    assert keys == {
        ("2305.16291-VOYAGER", "2305.16291"),
        ("2409.07429-AWM", "2409.07429"),
    }
    assert len(proposals) == 2  # de-duplicated
