"""Q.3: grounding works across all three real vault K-node schemas + the
duplicate-migration case (docs/audits/Q.0-reaudit.md Q3.1, Scout-2).

`extract_paper`'s grounding + supersede match a K node by its STEM + `type: knowledge`
frontmatter — never by the rest of the frontmatter shape. This proves `resolve_citations`
(grounding.py) resolves correctly regardless of which schema generation (A/B/C) wrote
the node, and that a duplicate-migration pair (same paper id, two schema shapes) still
resolves to exactly one proposal.
"""

from __future__ import annotations

from pathlib import Path

from grounding import resolve_citations

# Schema A — "BB Channel" generation (~370 vault nodes): no `graph_edges`, no
# `arxiv_id`, `score` is a STRING ("9/10"), `year` is the literal string "Unknown".
_SCHEMA_A = """---
type: knowledge
source_type: "Paper"
title: "Titans"
tags: [knowledge, raw_data]
chimera_status: unverified_by_human
score: "9/10"
year: "Unknown"
---

# Titans
"""

# Schema B — "Anatomist" generation (18 vault nodes): has `arxiv_id` + a stale
# `source_md`, `processed` flag, no `graph_edges` block.
_SCHEMA_B = """---
type: knowledge
chimera_status: deep_read
arxiv_id: "2506.06326v1-MemoryOS"
title: "MemoryOS"
processed: true
source_md: "crucible_core/papers/md_papers/2506.06326v1-MemoryOS.md"
---

# MemoryOS
"""

# Schema C — template-conformant generation (13 vault nodes): full keys + a
# (possibly empty) `graph_edges` scaffold.
_SCHEMA_C = """---
type: knowledge
status: unverified
arxiv_id: "2305.16291"
title: "VOYAGER"
score: 7
verdict: "Skim"
graph_edges:
  derives_from: []
  contradicts: []
  supersedes: []
---

# VOYAGER
"""

# Duplicate-migration pair: the same paper (2409.07429, AWM) re-ingested under two
# schema generations — a Schema-C node ("AWM") and a later Schema-A re-ingest
# ("AWM v2"), per reaudit Q3.1 (the real `Memp` C-vs-A precedent).
_DUP_SCHEMA_C = """---
type: knowledge
status: unverified
arxiv_id: "2409.07429"
title: "AWM"
score: 7
verdict: "Skim"
graph_edges:
  derives_from: []
  contradicts: []
  supersedes: []
---

# AWM
"""

_DUP_SCHEMA_A = """---
type: knowledge
source_type: "Paper"
title: "AWM"
tags: [knowledge, raw_data]
chimera_status: unverified_by_human
score: "8/10"
year: "Unknown"
---

# AWM v2
"""


def _write(vault: Path, stem: str, content: str) -> None:
    (vault / f"{stem}.md").write_text(content, encoding="utf-8")


def _make_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    _write(vault, "2501.00663v1-Titans", _SCHEMA_A)
    _write(vault, "2506.06326v1-MemoryOS", _SCHEMA_B)
    _write(vault, "2305.16291-VOYAGER", _SCHEMA_C)
    _write(vault, "2409.07429-AWM", _DUP_SCHEMA_C)
    _write(vault, "2409.07429v1-AWM", _DUP_SCHEMA_A)
    return vault


def test_schema_a_resolves_despite_string_score_and_no_arxiv_id(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    proposals = resolve_citations(["2501.00663v1"], vault)
    assert len(proposals) == 1
    assert proposals[0].target_stem == "2501.00663v1-Titans"
    assert proposals[0].edge_type == "derives_from"


def test_schema_b_resolves(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    proposals = resolve_citations(["2506.06326v1"], vault)
    assert len(proposals) == 1
    assert proposals[0].target_stem == "2506.06326v1-MemoryOS"


def test_schema_c_resolves(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    proposals = resolve_citations(["2305.16291"], vault)
    assert len(proposals) == 1
    assert proposals[0].target_stem == "2305.16291-VOYAGER"


def test_duplicate_migration_pair_resolves_to_exactly_one_node(tmp_path: Path) -> None:
    vault = _make_vault(tmp_path)
    proposals = resolve_citations(["2409.07429"], vault)
    assert len(proposals) == 1
    assert "2409.07429" in proposals[0].target_stem
