"""Phase L.B sprint 1: `chimera_tier` — the orthogonal origin/depth axis (scout /
deep_read / harness_candidate / synthesis), added alongside (never folded into) `status`.

Mirrors the fixture conventions of ``tests/test_staging_tools.py`` (StagingService against
tmp dirs) and ``tests/test_prompts.py`` (PromptManager rendering real templates).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.schemas import DeepReadAtlas, Paper, PaperAnalysisResult, VerdictDecision
from ports.prompts.jinja_prompt_manager import PromptManager
from staging_service import StagingService


def _read_frontmatter(path: Path) -> dict:
    _, fm_raw, _ = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(fm_raw)


def _paper() -> Paper:
    return Paper(
        id="2305.16291",
        title="A Test Paper",
        content_path=Path("2305.16291.md"),
        raw_text="body text",
    )


def _analysis() -> PaperAnalysisResult:
    return PaperAnalysisResult(
        verdict=VerdictDecision.SKIM,
        short_moniker="TestSys",
        score=5,
        novelty_delta="Some delta.",
        mechanism_summary="Some mechanism.",
    )


# --- create_staging_node: chimera_tier resolution (StagingService) --------------------


def test_explicit_chimera_tier_is_honored(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(
        type="knowledge", title="K node", body="b", chimera_tier="deep_read"
    )
    fm = _read_frontmatter(path)
    assert fm["chimera_tier"] == "deep_read"


def test_tid_defaults_to_synthesis(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(type="thought", title="T node", body="b")
    fm = _read_frontmatter(path)
    assert fm["chimera_tier"] == "synthesis"


def test_knowledge_is_never_defaulted(tmp_path: Path) -> None:
    """C-1 acceptance: an untiered K node stays untiered — its writer MUST declare
    scout vs deep_read rather than being silently mis-tiered."""
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(type="knowledge", title="K node", body="b")
    fm = _read_frontmatter(path)
    assert "chimera_tier" not in fm


def test_scout_and_deep_read_tiers_are_distinct(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    scout_path = svc.create_staging_node(
        type="knowledge", title="Scout K", body="b", chimera_tier="scout"
    )
    deep_path = svc.create_staging_node(
        type="knowledge", title="Deep K", body="b", chimera_tier="deep_read"
    )
    scout_fm = _read_frontmatter(scout_path)
    deep_fm = _read_frontmatter(deep_path)
    assert scout_fm["chimera_tier"] == "scout"
    assert deep_fm["chimera_tier"] == "deep_read"
    assert scout_fm["chimera_tier"] != deep_fm["chimera_tier"]


# --- Template rendering: scout vs deep_read carry the tier in frontmatter -------------


def test_knowledge_node_template_renders_scout_tier() -> None:
    pm = PromptManager()
    rendered = pm.render(
        "obsidian_tpl/knowledge_node.j2",
        paper=_paper(),
        analysis=_analysis(),
        note_asset_basename="2305.16291-TestSys",
        current_date="2026-07-21",
    )
    fm_raw = rendered.split("---", 2)[1]
    assert "chimera_tier: scout" in fm_raw
    assert "status: unverified" in fm_raw


def test_deep_read_node_template_renders_deep_read_tier() -> None:
    pm = PromptManager()
    atlas = DeepReadAtlas(arxiv_id="2305.16291", short_moniker="TestSys")
    rendered = pm.render(
        "obsidian_tpl/deep_read_node.j2",
        paper=_paper(),
        atlas=atlas,
        note_asset_basename="2305.16291-TestSys",
        current_date="2026-07-21",
    )
    fm_raw = rendered.split("---", 2)[1]
    assert "chimera_tier: deep_read" in fm_raw
    assert "status: unverified" in fm_raw
