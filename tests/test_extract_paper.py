"""Phase Q (rebuilt): extract_paper orchestration (staging-only) + promote-time supersede.

All deps injected (stub LLM client, tmp staging + vault) — no real LLM / MinerU / config. The stub
returns a full ``KNodeExtraction`` (synthesis + lens + attack + claims); the extraction prompt is
still rendered (it reads the canonical lens catalog), so this also proves the prompt loads.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.schemas import (
    AttackVectors,
    ClaimFlag,
    ClaimSource,
    ExtractedClaim,
    KNodeExtraction,
    LensCritique,
    LensFinding,
    Paper,
    PaperSynthesis,
)
from single_paper_extract import (
    _cited_arxiv_ids,
    _render_node_body,
    extract_single_paper,
)
from staging_service import StagingService


def _extraction(n: int = 1) -> KNodeExtraction:
    claim = ExtractedClaim(
        title="Identity shortcuts decouple optimization from depth",
        statement="Residual routing decouples optimization difficulty from network depth.",
        falsification="A depth scan where residual and plain nets degrade identically.",
        status="supported",
        sources=[ClaimSource(quote="3.57% top-5 error", location="Results")],
        tags=["residual"],
        flags=[ClaimFlag.NO_ABLATION],
    )
    return KNodeExtraction(
        title="ResNet: Residual Learning for Deep Networks",
        synthesis=PaperSynthesis(
            motivation='Deep plain nets degrade in training. "deeper nets, higher training error" ← Intro',
            bb_analysis="Depth without the vanishing-gradient tax.",
            mechanism="Identity shortcuts let gradients skip layers.",
            algorithm_steps=["Add identity shortcut", "Train deeper"],
            results='3.57% top-5 on ImageNet. "3.57% top-5 error" ← Results',
        ),
        lenses=[LensCritique(
            lens_name="Math Decoration Verdict",
            triggered_by="Reformulates plain nets and asks the reader to accept the residual as load-bearing.",
            findings=[LensFinding(heading="Residual as identity", body="The residual is a plain identity add.")],
            verdict="Load-bearing: removing the shortcut breaks deep training.",
        )],
        attack=AttackVectors(
            vectors=["Shortcut helps optimization, not representation."],
            beat_baseline="Normalized init + a careful LR schedule.",
            exploit_flaw="Probe whether the gains persist with better init alone.",
        ),
        claims=[claim for _ in range(n)],
    )


class _StubClient:
    def __init__(self, extraction: KNodeExtraction) -> None:
        self._extraction = extraction

    def generate_structured_data(
        self, *, system_prompt: str, user_prompt: str, response_model: object
    ) -> KNodeExtraction:
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


def test_render_body_has_all_four_sections() -> None:
    body = _render_node_body(_extraction())
    assert "## Synthesis" in body
    assert "**Motivation (the gap):**" in body  # arc opens with the gap
    assert "**Results (did it work):**" in body  # arc closes with the payoff
    assert "## Lens Critique" in body
    assert "Attack Vectors" in body
    assert "## Mechanism Claims" in body and "**Statement:**" in body
    # grounding-by-quote renders as "quote" <- location
    assert '"3.57% top-5 error" ← Results' in body
    # human-fill review hook is injected
    assert "[My Critique]" in body


def test_render_strips_double_markers() -> None:
    # Live smoke (STALE, 2605.06527) exposed the LLM prefixing steps with numbers and vectors with
    # 💥, which the renderer then doubled ("1. 1.", "> 💥 💥"). The renderer strips defensively.
    node = _extraction()
    node.synthesis.algorithm_steps = ["1. first", "2) second"]
    node.attack.vectors = ["💥 💥 boom", "\U0001f4a5️ vs", "plain"]
    body = _render_node_body(node)
    assert "1. 1." not in body and "2. 2)" not in body
    assert "> 💥 💥" not in body
    assert "1. first" in body and "2. second" in body
    assert "> 💥 boom" in body and "> 💥 vs" in body and "> 💥 plain" in body


def test_render_two_lenses_both_appear() -> None:
    # Hybrid policy: a benchmark-about-a-mechanism (STALE) carries two lenses; both render.
    node = _extraction()
    node.lenses.append(
        LensCritique(
            lens_name="State Collision Stress Test",
            triggered_by="The paper's subject is conflict arbitration under contradiction.",
            findings=[LensFinding(heading="Arbitration", body="Superposition vs. true resolution?")],
            verdict="Superposition, not true arbitration.",
        )
    )
    body = _render_node_body(node)
    assert "## Lens Critique — Math Decoration Verdict" in body
    assert "## Lens Critique — State Collision Stress Test" in body


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
    assert fm["arxiv_id"] == "2305.16291"  # identity preserved even though title is the paper name
    assert fm["title"] == "ResNet: Residual Learning for Deep Networks"
    assert "## Synthesis" in body
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
