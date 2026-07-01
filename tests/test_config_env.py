"""I-1 regression: flat CHIMERA_<paper_miner key> env vars must reach paper_miner.*.

Bug (incident 2026-06-30 I-1): pydantic-settings' env source only surfaces env vars that
match a *defined* field, so a flat CHIMERA_PAPERS_ROOT (nested field) was silently dropped by
extra="ignore". The config now folds these env names into paper_miner explicitly.
"""

from __future__ import annotations

from core.config import ChimeraConfig


def test_flat_papers_root_env_maps_to_nested(monkeypatch) -> None:
    monkeypatch.setenv("CHIMERA_PAPERS_ROOT", r"D:\I1_TEST\papers")
    cfg = ChimeraConfig()
    # non-default path — proves the override actually moves it (not default==intended)
    assert "I1_TEST" in str(cfg.paper_miner_or_default.papers_root)


def test_flat_arxiv_query_env_maps(monkeypatch) -> None:
    monkeypatch.setenv("CHIMERA_ARXIV_QUERY", "cat:cs.LG AND all:probe")
    cfg = ChimeraConfig()
    assert cfg.paper_miner_or_default.arxiv_query == "cat:cs.LG AND all:probe"


def test_no_env_uses_default(monkeypatch) -> None:
    monkeypatch.delenv("CHIMERA_PAPERS_ROOT", raising=False)
    cfg = ChimeraConfig()
    assert cfg.paper_miner_or_default.papers_root.name == "papers"
