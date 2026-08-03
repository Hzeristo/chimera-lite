"""L.B.5 acceptance, redesigned from DETERMINISM to ACCURACY (2026-08-03).

The original acceptance was "re-running reproduces the artifact byte-for-byte." A hardcoded
literal reproduces perfectly forever while being false, and that is exactly what happened: the
flow section kept asserting `daily_paper_pipeline` / `ingest_paper` wrote scout cards to
`inbox/` long after L.B.2 moved that write behind `write_scout_card`. Reproducibility was
measured; correctness was assumed.

The acceptance is now: **every flow edge must map to a real write call site.** These tests
assert the derivation itself — each declared write surface's writer exists in source, each
rendered edge is backed by a reference chain that terminates at that writer, and the specific
falsehoods that rotted are absent. Determinism is retained as a secondary property, not as the
proof of correctness.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GEN_PATH = _REPO_ROOT / "scripts" / "gen_architecture_diagram.py"
_ARTIFACT = _REPO_ROOT / "docs" / "ARCHITECTURE" / "ARCHITECTURE.md"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_architecture_diagram", _GEN_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gen = _load_generator()


@pytest.fixture(scope="module")
def flows():
    tools_by_server = {name: gen.parse_tools(path) for name, path in gen.SERVERS.items()}
    graph = gen.build_reference_graph()
    return gen.derive_flows(tools_by_server, graph)


# --- accuracy: the anchors are real -------------------------------------------------------


@pytest.mark.parametrize("surface", gen.WRITE_SURFACES, ids=lambda s: s.surface_id)
def test_writer_symbol_exists_in_declared_module(surface) -> None:
    # verify_writer_symbol raises SystemExit if the writer is gone — a declared surface may
    # never describe code that does not exist.
    line = gen.verify_writer_symbol(surface)
    assert line > 0


# --- accuracy: every rendered edge maps to a real write call site --------------------------


def test_every_edge_has_a_chain_terminating_at_the_writer(flows) -> None:
    for surface, _line, edges in flows:
        for _server, tool, chain in edges:
            assert chain, f"{tool} -> {surface.surface_id} has an empty chain"
            assert chain[0] == tool, f"chain for {tool} does not start at the tool: {chain}"
            assert chain[-1] == surface.writer_symbol, (
                f"chain for {tool} -> {surface.surface_id} does not terminate at "
                f"{surface.writer_symbol!r}: {chain}"
            )


def test_every_mermaid_edge_is_a_derived_edge(flows) -> None:
    """Nothing may appear in the diagram that the derivation did not produce."""
    derived = {
        (tool, surface.surface_id) for surface, _line, edges in flows for _s, tool, _c in edges
    }
    text = _ARTIFACT.read_text(encoding="utf-8")
    mermaid = text.split("```mermaid", 1)[1].split("```", 1)[0]

    rendered: set[tuple[str, str]] = set()
    for line in mermaid.splitlines():
        if "-->" not in line:
            continue
        left, right = line.split("-->", 1)
        tool = left.strip().split("[", 1)[0].removeprefix("tool_")
        surface_id = right.strip().removesuffix("_dest")
        rendered.add((tool, surface_id))

    assert rendered == derived, (
        f"diagram edges diverge from derivation.\n"
        f"  only in diagram: {sorted(rendered - derived)}\n"
        f"  only in derivation: {sorted(derived - rendered)}"
    )


# --- the specific rot this replaces --------------------------------------------------------


def test_scout_writes_come_only_from_write_scout_card(flows) -> None:
    inbox = next(f for f in flows if f[0].surface_id == "inbox")
    reaching = {tool for _s, tool, _c in inbox[2]}
    assert reaching == {"write_scout_card"}, (
        f"inbox/ must be reachable ONLY via write_scout_card (L.B.2 sole scout writer); got {reaching}"
    )


@pytest.mark.parametrize("tool", ["daily_paper_pipeline", "ingest_paper"])
def test_fetch_convert_tools_no_longer_write_scout_cards(flows, tool: str) -> None:
    # The rotted literal claimed both wrote to inbox/<verdict>/ at chimera_tier=scout. L.B.2
    # made them fetch+convert primitives that write no node at all.
    inbox = next(f for f in flows if f[0].surface_id == "inbox")
    assert tool not in {t for _s, t, _c in inbox[2]}


def test_no_mcp_tool_to_subagent_edges() -> None:
    """MCP tools never spawn subagents — skills do. The old diagram drew phantom triager edges."""
    text = _ARTIFACT.read_text(encoding="utf-8")
    mermaid = text.split("```mermaid", 1)[1].split("```", 1)[0]
    for agent in ("chimera-paper-triager", "chimera-deep-extractor", "triager", "extractor"):
        assert agent not in mermaid, f"phantom subagent edge for {agent!r} is back in the diagram"


def test_orphaned_surface_is_reported_not_drawn(flows) -> None:
    legacy = next(f for f in flows if f[0].surface_id == "deep_reads_legacy")
    assert legacy[2] == [], "01_Deep_Reads/ has a live MCP writer now — the note is stale"
    assert "ORPHANED" in _ARTIFACT.read_text(encoding="utf-8")


# --- secondary: the artifact is current and reproducible ----------------------------------


def test_committed_artifact_matches_current_source(flows) -> None:
    tools_by_server = {name: gen.parse_tools(path) for name, path in gen.SERVERS.items()}
    agents = []
    for agent_path in sorted((_REPO_ROOT / ".claude" / "agents").glob("*.md")):
        parsed = gen.parse_agent_model(agent_path)
        if parsed is not None:
            agents.append(parsed)
    agents.sort(key=lambda pair: pair[0])

    expected = gen.render(tools_by_server, agents, flows)
    actual = _ARTIFACT.read_text(encoding="utf-8")
    assert actual.replace("\r\n", "\n") == expected, (
        "ARCHITECTURE.md is stale — regenerate with scripts/gen_architecture_diagram.py"
    )
