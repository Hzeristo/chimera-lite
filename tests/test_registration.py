"""Every component this repo names must be REACHABLE at runtime — as an MCP ``@mcp.tool`` AND
as a Claude Code agent definition.

Incident 2026-08-03: ``filter_service.analyze_paper_data`` shipped in L.B.2 with unit tests
proving the *function* worked, but it was never exposed as a tool — so ``chimera-triage-paper``
step 1 called a primitive that did not exist in the live registry, and Path 1 of the L.B.6 e2e
could not run. The L.B.2 tests asserted the primitive, never its REACHABILITY.

Friction-260811-01: a component becomes usable in two steps — WRITTEN, then REGISTERED. Three
separate incidents shipped components unreachable at runtime with green unit tests, because
only the first step was covered. This module asserts BOTH registration surfaces in one place:
MCP tool registration (parsing ``server.py``, no import — the servers instantiate FastMCP and
pull a heavy chain at module load) and Claude Code agent-definition parseability + naming.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SERVERS = {
    "chimera-papers": _REPO_ROOT / "mcp-servers" / "chimera-papers" / "server.py",
    "chimera-vault": _REPO_ROOT / "mcp-servers" / "chimera-vault" / "server.py",
}
_SKILLS_DIR = _REPO_ROOT / ".claude" / "skills"
_AGENTS_DIR = _REPO_ROOT / ".claude" / "agents"
# Non-agent ``chimera-*`` naming domains that a SKILL.md body may legitimately reference
# without meaning "spawn this agent" — MCP server directory names (e.g. "the MCP server
# (`chimera-papers`) makes no LLM call").
_MCP_SERVER_DIRS = {"chimera-papers", "chimera-vault"}

# The MCP tool primitives each skill actually orchestrates, read from its SKILL.md — an
# explicit map, never inferred by regex from prose. ``[]`` is a valid value: a skill that
# calls no MCP tool (e.g. the lens skills apply a canonical prompt file, not a tool call).
# Completeness (every skill directory has an entry here) is enforced by
# ``test_every_skill_is_covered_by_the_map`` below — that is what makes this explicit map safe.
_SKILL_REQUIRED_TOOLS = {
    "chimera-academic-observe": ["obsidian_graph_query", "vault_query"],
    "chimera-bb-persona": [],
    "chimera-code-taste": [],
    "chimera-commit-style": [],
    "chimera-deep-extract": ["get_paper_markdown", "load_criteria", "stage_deep_read_node"],
    "chimera-dependency-veto": [],
    "chimera-lens-agentic-illusion": [],
    "chimera-lens-forensic-leakage": [],
    "chimera-lens-math-decoration": [],
    "chimera-lens-ontological-map": [],
    "chimera-lens-state-collision": [],
    "chimera-lens-thermodynamic-decay": [],
    "chimera-mcp-taste": [],
    "chimera-sprint-discipline": [],
    "chimera-triage-paper": ["analyze_paper_data", "load_criteria", "write_scout_card"],
    "chimera-w1-verify": [
        "fetch_paper",
        "convert_pdf_to_md",
        "load_criteria",
        "read_vault_file",
        "write_result",
    ],
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


def test_every_skill_is_covered_by_the_map() -> None:
    # The completeness check that makes the explicit _SKILL_REQUIRED_TOOLS map safe: every
    # skill directory must have an entry (``[]`` is valid — a skill that calls no MCP tool).
    skill_dirs = {p.parent.name for p in _SKILLS_DIR.glob("*/SKILL.md")}
    assert skill_dirs, f"no SKILL.md files found under {_SKILLS_DIR}"
    missing = sorted(skill_dirs - _SKILL_REQUIRED_TOOLS.keys())
    assert not missing, f"skill(s) missing from _SKILL_REQUIRED_TOOLS: {missing}"


def _parse_flat_frontmatter(raw_block: str) -> object:
    # Agent frontmatter is flat, one key per line ("name: ...", "description: ...", a prose
    # value that legitimately contains its own ":" — e.g. "reducer: reduces a paper to..."
    # is real content in every one of these files, not malformed input). A literal
    # ``yaml.safe_load`` on the whole block trips PyYAML's block-mapping-ambiguity check on
    # that embedded colon. Quote each value first (real JSON/YAML string quoting) so PyYAML
    # still does the actual parsing — this only defuses the per-line ambiguity, it does not
    # replace the parse.
    quoted_lines = []
    for line in raw_block.splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        quoted_lines.append(f"{key}: {json.dumps(value.strip())}" if sep else line)
    return yaml.safe_load("\n".join(quoted_lines))


def _assert_no_crlf(path: Path, raw: bytes) -> None:
    # Incident 2026-08-10 / friction-260811-01 instance 3: a CRLF-fenced frontmatter
    # (``---\r\n``) still satisfies ``raw.startswith(b"---")`` — the byte-0 fence check
    # guards a *prepended* byte (e.g. a UTF-8 BOM), not a CRLF fence — and left
    # chimera-deep-extractor and chimera-paper-triager unreachable for three weeks with a
    # fully green test suite. ``.gitattributes`` pins ``.claude/agents/*.md`` and
    # ``.claude/skills/**/*.md`` to LF, but that pin is a patch on one door (a fresh clone /
    # an editor override still reintroduces CRLF); THIS assertion is the check.
    assert b"\r\n" not in raw, (
        f"{path}: contains CRLF line endings (incident 2026-08-10, friction-260811-01) — "
        "re-save with LF endings; .gitattributes pins this path to LF but does not enforce it"
    )


def test_every_agent_definition_parses() -> None:
    agent_paths = sorted(_AGENTS_DIR.glob("*.md"))
    assert agent_paths, f"no agent definitions found under {_AGENTS_DIR}"
    for path in agent_paths:
        raw = path.read_bytes()
        _assert_no_crlf(path, raw)

        # (a) the frontmatter fence opens at byte 0 — guards a *prepended* byte (e.g. a
        # UTF-8 BOM) that would push the fence off byte 0. This does NOT guard CRLF (see
        # _assert_no_crlf above, which does).
        assert raw.startswith(b"---"), f"{path.name}: frontmatter fence does not open at byte 0"

        text = raw.decode("utf-8")
        _, _, rest = text.partition("---")
        frontmatter_raw, sep, _ = rest.partition("\n---")
        assert sep, f"{path.name}: frontmatter fence never closes"

        # (b) the YAML frontmatter parses.
        frontmatter = _parse_flat_frontmatter(frontmatter_raw)
        assert isinstance(frontmatter, dict), f"{path.name}: frontmatter did not parse to a dict"

        # (c) required keys are present.
        missing_keys = {"name", "description", "tools"} - frontmatter.keys()
        assert not missing_keys, f"{path.name}: frontmatter missing key(s): {missing_keys}"

        # (d) name equals the filename stem.
        assert frontmatter["name"] == path.stem, (
            f"{path.name}: frontmatter name {frontmatter['name']!r} != filename stem {path.stem!r}"
        )


def test_every_skill_definition_has_no_crlf() -> None:
    # friction-260811-01: "tools and agents are the same class" — one registry assertion,
    # not two. A CRLF SKILL.md frontmatter breaks skill loading the identical way a CRLF
    # agent frontmatter does; this reuses _assert_no_crlf rather than a second mechanism.
    skill_paths = sorted(_SKILLS_DIR.glob("*/SKILL.md"))
    assert skill_paths, f"no SKILL.md files found under {_SKILLS_DIR}"
    for path in skill_paths:
        _assert_no_crlf(path, path.read_bytes())


def test_agents_named_by_skills_exist() -> None:
    # Scan SKILL.md bodies for backtick-quoted `chimera-*` agent-type references and assert
    # each resolves to a real agent definition. Two non-agent `chimera-*` naming domains are
    # excluded, not guessed away: skill directory names (a skill referencing another skill, or
    # itself) and MCP server directory names (e.g. "the MCP server (`chimera-papers`)").
    agent_stems = {p.stem for p in _AGENTS_DIR.glob("*.md")}
    skill_dirs = {p.parent.name for p in _SKILLS_DIR.glob("*/SKILL.md")}
    excluded = skill_dirs | _MCP_SERVER_DIRS

    reference_re = re.compile(r"`(chimera-[a-z0-9-]+)`")
    unresolved: list[str] = []
    for skill_path in sorted(_SKILLS_DIR.glob("*/SKILL.md")):
        body = skill_path.read_text(encoding="utf-8")
        for name in set(reference_re.findall(body)):
            if name in excluded:
                continue
            if name not in agent_stems:
                unresolved.append(f"{skill_path.parent.name}/SKILL.md references `{name}`")

    assert not unresolved, "unresolved chimera-* agent references:\n" + "\n".join(
        sorted(unresolved)
    )
