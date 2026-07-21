"""Phase Q (rebuilt) + L.B.2 externalized: ``get_paper_markdown`` (read primitive) and
``stage_deep_read_node`` (the deterministic staging back-half) + promote-time supersede.

L.B.2 stripped the LLM call out of this module — judgment now happens in the
``chimera-deep-extract`` skill's Sonnet subagent, which hands ``stage_deep_read_node`` an
already-produced ``KNodeExtraction``. All deps injected (a stub settings object, tmp staging +
vault) — no real LLM / MinerU / config.
"""

from __future__ import annotations

from pathlib import Path

import pytest
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
    get_paper_markdown,
    stage_deep_read_node,
)
from staging_service import StagingService


class _StubPaperMiner:
    def __init__(self, md_papers_dir: Path) -> None:
        self.md_papers_dir = md_papers_dir


class _StubSettings:
    """Minimal duck-typed stand-in for ``ChimeraConfig`` — only the attributes
    ``_resolve_markdown`` actually reads (``paper_miner_or_default.md_papers_dir`` +
    ``project_root``, the latter unused here since the tmp dir is already absolute)."""

    def __init__(self, md_papers_dir: Path) -> None:
        self.project_root = md_papers_dir
        self._pm = _StubPaperMiner(md_papers_dir)

    @property
    def paper_miner_or_default(self) -> _StubPaperMiner:
        return self._pm


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
    assert "**Mechanism:**" in body
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


def test_get_paper_markdown_returns_existing_path(tmp_path: Path) -> None:
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    (md_dir / "2305.16291.md").write_text("# VOYAGER\n", encoding="utf-8")
    path = get_paper_markdown("2305.16291", settings=_StubSettings(md_dir))
    assert path == md_dir / "2305.16291.md"


def test_get_paper_markdown_missing_raises(tmp_path: Path) -> None:
    md_dir = tmp_path / "md_papers"
    md_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        get_paper_markdown("2305.16291", settings=_StubSettings(md_dir))


async def test_stage_deep_read_node_grounded_edge(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = await stage_deep_read_node(
        paper_id="2305.16291",
        extraction=_extraction(),
        paper=_paper("2305.16291", cites="builds on 2409.07429"),
        staging_service=staging,
    )
    fm, body = _read_staged(path)
    assert fm["type"] == "knowledge"
    assert fm["chimera_tier"] == "deep_read"
    assert fm["graph_edges"]["derives_from"] == ["[[2409.07429-AWM]]"]
    assert fm["provenance"] == "ai-suggested"
    assert fm["grounded"] == "citation_resolved"
    assert fm["arxiv_id"] == "2305.16291"  # identity preserved even though title is the paper name
    assert fm["title"] == "ResNet: Residual Learning for Deep Networks"
    assert "## Synthesis" in body
    # exactly ONE staged file (the K node) — no Insight/Thought/Decision file
    assert len(list((tmp_path / "staging").glob("*.md"))) == 1


async def test_stage_deep_read_node_accepts_dict_extraction(tmp_path: Path) -> None:
    # The subagent's structured output arrives as JSON -> a plain dict through the MCP tool
    # boundary; stage_deep_read_node must validate it into a KNodeExtraction itself.
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = await stage_deep_read_node(
        paper_id="2305.16291",
        extraction=_extraction().model_dump(mode="json"),
        paper=_paper("2305.16291"),
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["chimera_tier"] == "deep_read"
    assert fm["title"] == "ResNet: Residual Learning for Deep Networks"


async def test_stage_deep_read_node_no_prior_match(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = await stage_deep_read_node(
        paper_id="2305.16291",
        extraction=_extraction(),
        paper=_paper("2305.16291", cites="no citations here"),
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["grounded"] == "no_prior_match"
    assert fm["graph_edges"]["derives_from"] == []


async def test_stage_deep_read_node_excludes_migration_backup(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    path = await stage_deep_read_node(
        paper_id="2305.16291",
        extraction=_extraction(),
        paper=_paper("2305.16291", cites="cite 2508.06433"),  # present only in .migration_backup
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["grounded"] == "no_prior_match"  # backup node is never resolvable


async def test_supersede_edge_when_existing_node(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    _k_node(vault / "inbox" / "Skim" / "2305.16291-VOYAGER.md")
    staging = StagingService(tmp_path / "staging", vault)
    path = await stage_deep_read_node(
        paper_id="2305.16291",
        extraction=_extraction(),
        paper=_paper("2305.16291"),
        staging_service=staging,
    )
    fm, _ = _read_staged(path)
    assert fm["graph_edges"]["supersedes"] == ["[[2305.16291-VOYAGER]]"]


async def test_stage_deep_read_node_reports_progress(tmp_path: Path) -> None:
    # Incident 2026-07-13: silent blocking tool. The domain function emits stage progress at the
    # documented boundaries; the other tests exercise the progress=None (no-ctx) path.
    vault = _make_vault(tmp_path)
    staging = StagingService(tmp_path / "staging", vault)
    seen: list[tuple[float, str]] = []

    async def _progress(frac: float, msg: str) -> None:
        seen.append((frac, msg))

    await stage_deep_read_node(
        paper_id="2305.16291",
        extraction=_extraction(),
        paper=_paper("2305.16291"),
        staging_service=staging,
        progress=_progress,
    )
    assert [f for f, _ in seen] == [0.0, 0.4, 0.85, 1.0]
    assert any("Grounding" in m for _, m in seen)


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
