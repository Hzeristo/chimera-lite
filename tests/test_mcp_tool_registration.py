"""Every MCP primitive a Claude Code skill calls must actually be REGISTERED as an ``@mcp.tool``.

Incident 2026-08-03: ``filter_service.analyze_paper_data`` shipped in L.B.2 with unit tests
proving the *function* worked, but it was never exposed as a tool — so ``chimera-triage-paper``
step 1 called a primitive that did not exist in the live registry, and Path 1 of the L.B.6 e2e
could not run. The L.B.2 tests asserted the primitive, never its REACHABILITY.

These tests close that gap by parsing the two ``server.py`` files (no import — the servers
instantiate FastMCP and pull a heavy chain at module load) and asserting the skill-required
primitives are present.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SERVERS = {
    "chimera-papers": _REPO_ROOT / "mcp-servers" / "chimera-papers" / "server.py",
    "chimera-vault": _REPO_ROOT / "mcp-servers" / "chimera-vault" / "server.py",
}

# The primitives the Phase-L / L.B skills orchestrate. Keyed by the skill that calls them, so a
# failure names the broken skill rather than just a missing string.
_SKILL_REQUIRED_TOOLS = {
    "chimera-triage-paper": ["analyze_paper_data", "load_criteria", "write_scout_card"],
    "chimera-deep-extract": ["get_paper_markdown", "load_criteria", "stage_deep_read_node"],
    "chimera-w1-verify": ["fetch_paper", "convert_pdf_to_md", "load_criteria", "write_result"],
    "chimera-w2-map": ["load_criteria", "write_result"],
}

# ``@mcp.tool()`` followed by the (possibly async) def it decorates.
_TOOL_RE = re.compile(r"@mcp\.tool\(\)\s*\n\s*(?:async\s+)?def\s+(\w+)", re.MULTILINE)


def _registered_tools() -> set[str]:
    names: set[str] = set()
    for server_name, path in _SERVERS.items():
        assert path.is_file(), f"{server_name} server.py missing at {path}"
        names |= set(_TOOL_RE.findall(path.read_text(encoding="utf-8")))
    return names


@pytest.mark.parametrize(("skill", "tools"), sorted(_SKILL_REQUIRED_TOOLS.items()))
def test_skill_required_tools_are_registered(skill: str, tools: list[str]) -> None:
    registered = _registered_tools()
    missing = [t for t in tools if t not in registered]
    assert not missing, f"{skill} calls unregistered MCP tool(s): {missing}"


def test_analyze_paper_data_is_registered() -> None:
    # The specific regression: the domain function existed and passed its unit tests, but the
    # @mcp.tool registration was absent, so no live client could reach it.
    assert "analyze_paper_data" in _registered_tools()


def test_analyze_paper_data_tool_delegates_to_miner_tools() -> None:
    # Thin-adapter rule: the tool body dispatches, it does not carry logic.
    source = _SERVERS["chimera-papers"].read_text(encoding="utf-8")
    assert "return await miner_tools.analyze_paper_data(paper_id)" in source
