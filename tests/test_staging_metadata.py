"""Q.1b: create_staging_node metadata passthrough (D4).

Structural only — verifies the metadata merge is additive and backward-compatible.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from staging_service import StagingService


def _read_frontmatter(path: Path) -> dict:
    _, fm_raw, _ = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(fm_raw)


def test_metadata_merges_into_frontmatter(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(
        type="knowledge",
        title="X",
        body="b",
        metadata={"provenance": "ai-suggested", "grounded": "no_prior_match"},
    )
    fm = _read_frontmatter(path)
    assert fm["provenance"] == "ai-suggested"
    assert fm["grounded"] == "no_prior_match"


def test_metadata_omitted_is_backward_compatible(tmp_path: Path) -> None:
    svc = StagingService(tmp_path / "staging", tmp_path / "vault")
    path = svc.create_staging_node(type="knowledge", title="X", body="b")
    fm = _read_frontmatter(path)
    assert set(fm) == {"type", "status", "title", "created_at", "tags", "graph_edges"}
