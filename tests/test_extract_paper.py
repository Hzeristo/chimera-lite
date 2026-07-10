"""Q.2b: extract_paper orchestration (staging-only) + promote-time supersede.

All deps injected (stub LLM client, tmp staging + vault) — no real LLM / MinerU / config.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.schemas import ClaimFlag, ExtractedClaim, KClaimExtraction, Paper
from single_paper_extract import (
    _cited_arxiv_ids,
    _render_claims_body,
    extract_single_paper,
)
from staging_service import StagingService


def _extraction(n: int = 1) -> KClaimExtraction:
    claim = ExtractedClaim(
        statement="Residual routing decouples optimization difficulty from network depth.",
        falsification="A depth scan where residual and plain nets degrade identically.",
        sources=["3.57% ← Results «3.57% top-5 error»"],
        status="supported",
        tags=["residual"],
        flags=[ClaimFlag.NO_ABLATION],
    )
    return KClaimExtraction(claims=[claim for _ in range(n)], proposed_edges=[])


class _StubClient:
    def __init__(self, extraction: KClaimExtraction) -> None:
        self._extraction = extraction

    def generate_structured_data(
        self, *, system_prompt: str, user_prompt: str, response_model: object
    ) -> KClaimExtraction:
        return self._extraction


def _k_node(path: Path, node_type: str = "knowledge") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\ntype: {node_type}\ntitle: "{path.stem}"\n---\n\n# {path.stem}\n',
        encoding="utf-8",
    )


def _make_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    _k_node(vault / "inbox" / "Skim" / "2409.07429-AWM.md")
    _k_node(vault / ".migration_backup" / "2508.06433-Memp.md")  # must be excluded
    _k_node(vault / "inbox" / "Skim" / "some-thought.md", node_type="thought")
    return vault


def _paper(pid: str, cites: str = "") -> Paper:
    return Paper(id=pid, title=pid, content_path=Path("x.md"), raw_text=f"Body of {pid}. {cites}")


def _read_staged(path: Path) -> tuple[dict, str]:
    _, fm_raw, body = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(fm_raw), body


def test_cited_arxiv_ids_excludes_self() -> None:
    assert _cited_arxiv_ids(
        "we build on 2409.07429 and cite 2305.16291", exclude="2305.16291"
    ) == ["2409.07429"]


def test_render_body_has_claims() -> None:
    body = _render_claims_body(_extraction())
    assert "## Claims" in body and "Statement" in body


def test_extract_grounded_edge(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = extract_single_paper(
        paper_id="2305.16291",
        paper=_paper("2305.16291", cites="builds on 2409.07429"),
        llm_client=_StubClient(_extraction()),
        staging_service=staging,
    )
    fm, body = _read_staged(path)
    assert fm["type"] == "knowledge"
    assert fm["graph_edges"]["derives_from"] == ["[[2409.07429-AWM]]"]
    assert fm["provenance"] == "ai-suggested"
    assert fm["grounded"] == "citation_resolved"
    assert "Statement" in body
    # exactly ONE staged file (the K node) — no Insight/Thought/Decision file
    assert len(list((tmp_path / "staging").glob("*.md"))) == 1


def test_extract_no_prior_match(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = extract_single_paper(
        paper_id="2305.16291",
        paper=_paper("2305.16291", cites="no citations here"),
        llm_client=_StubClient(_extraction()),
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["grounded"] == "no_prior_match"
    assert fm["graph_edges"]["derives_from"] == []


def test_extract_excludes_migration_backup(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = extract_single_paper(
        paper_id="2305.16291",
        paper=_paper("2305.16291", cites="cite 2508.06433"),  # present only in .migration_backup
        llm_client=_StubClient(_extraction()),
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["grounded"] == "no_prior_match"  # backup node is never resolvable


def test_supersede_edge_when_existing_node(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    _k_node(vault / "inbox" / "Skim" / "2305.16291-VOYAGER.md")
    staging = StagingService(tmp_path / "staging", vault)
    path = extract_single_paper(
        paper_id="2305.16291",
        paper=_paper("2305.16291"),
        llm_client=_StubClient(_extraction()),
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["graph_edges"]["supersedes"] == ["[[2305.16291-VOYAGER]]"]


def test_promote_unlinks_superseded(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    old = vault / "inbox" / "Skim" / "2305.16291-VOYAGER.md"
    _k_node(old)
    staging = StagingService(tmp_path / "staging", vault)
    staged = staging.create_staging_node(
        type="knowledge",
        title="2305.16291",
        body="b",
        edges={"supersedes": ["2305.16291-VOYAGER"]},
    )
    assert old.exists()
    staging.promote_node(staged)
    assert not old.exists()  # the superseded node is unlinked on promotion
