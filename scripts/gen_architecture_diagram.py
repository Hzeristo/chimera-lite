"""Generate the living dataflow map (docs/ARCHITECTURE/ARCHITECTURE.md).

Everything rendered here is DERIVED from source. Nothing about the flow is asserted by hand:

  - the ``@mcp.tool()`` inventory of both MCP servers (parsed from server.py source);
  - the pinned worker model of every ``.claude/agents/*.md`` subagent (YAML frontmatter);
  - and, for each declared WRITE SURFACE, the set of MCP tools that actually REACH it,
    computed by walking a reference graph over both server packages.

Why the reference graph rather than a hand-drawn flow (the L.B.5 defect, 2026-08-03): the
previous generator carried the four ingestion paths as a hardcoded literal. When L.B.2 moved
scout-card writing out of ``daily_paper_pipeline`` / ``ingest_paper`` and into the
``chimera-triage-paper`` skill's ``write_scout_card``, the literal kept asserting the old flow.
It reproduced byte-for-byte on every run while being false — determinism is not accuracy. A
write surface with no reachable tool is now reported as ORPHANED rather than silently drawn.

A declared write surface whose writer symbol no longer exists is a hard failure (SystemExit),
not a silently stale diagram.

Deterministic: no timestamps, no randomness; all collections sorted. Re-running against
unchanged source reproduces this file byte-for-byte.

Regenerate at every phase seal:
    .venv\\Scripts\\python.exe scripts/gen_architecture_diagram.py
"""

from __future__ import annotations

import ast
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SERVERS = {
    "chimera-papers": REPO_ROOT / "mcp-servers" / "chimera-papers" / "server.py",
    "chimera-vault": REPO_ROOT / "mcp-servers" / "chimera-vault" / "server.py",
}
SERVER_PKGS = [
    REPO_ROOT / "mcp-servers" / "chimera-papers",
    REPO_ROOT / "mcp-servers" / "chimera-vault",
]

TOOL_RE = re.compile(r"@mcp\.tool\(\)\s*\n\s*(?:async\s+)?def (\w+)\(")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(\S+)", re.MULTILINE)
MODEL_RE = re.compile(r"^model:\s*(\S+)", re.MULTILINE)


@dataclass(frozen=True)
class WriteSurface:
    """A terminal write destination, anchored to the ONE function that performs the write.

    ``writer_symbol`` must exist in ``module``; which tools reach it is derived, never declared.
    """

    surface_id: str
    destination: str
    module: str  # repo-relative
    writer_symbol: str
    note: str = ""


# The declared write surfaces. Only the ANCHOR (where the write happens) is stated here — it is
# verified against source on every run. Every edge into these surfaces is derived.
WRITE_SURFACES = [
    WriteSurface(
        surface_id="inbox",
        destination="inbox/<verdict>/  [chimera_tier=scout]",
        module="mcp-servers/chimera-papers/ports/vault/vault_note_writer.py",
        writer_symbol="write_knowledge_node",
        note="Scout tier. Never auto-promoted; ascension is a separate operator action.",
    ),
    WriteSurface(
        surface_id="staging",
        destination="docs/staging/  [chimera_tier=deep_read | synthesis]",
        module="mcp-servers/chimera-papers/staging_service.py",
        writer_symbol="create_staging_node",
        note="Review gate. Nothing here is live vault content until promoted or ascended.",
    ),
    WriteSurface(
        surface_id="committed",
        destination="<vault>/Knowledge|Thoughts|Insights|Decisions/",
        module="mcp-servers/chimera-papers/staging_service.py",
        writer_symbol="_promote_write",
        note=(
            "Shared write mechanics for promote_node + ascend_node. promote_node REFUSES "
            "chimera_tier=deep_read, which is what makes ascend_node the sole writer of "
            "Knowledge/ (structural, not conventional)."
        ),
    ),
    WriteSurface(
        surface_id="harness",
        destination="<vault>/Harness/",
        module="mcp-servers/chimera-papers/result_service.py",
        writer_symbol="write_result",
        note="W1 verdicts + W2 breadth maps. Review area, not the committed tier.",
    ),
    WriteSurface(
        surface_id="deep_reads_legacy",
        destination="<vault>/01_Deep_Reads/",
        module="mcp-servers/chimera-papers/ports/vault/vault_note_writer.py",
        writer_symbol="write_deep_read_node",
        note="Oligo-era surface; its only caller is the retired OpticsService.irradiate path.",
    ),
]


def parse_tools(server_path: Path) -> list[str]:
    return sorted(TOOL_RE.findall(server_path.read_text(encoding="utf-8")))


def parse_agent_model(agent_path: Path) -> tuple[str, str] | None:
    match = FRONTMATTER_RE.match(agent_path.read_text(encoding="utf-8"))
    if not match:
        return None
    frontmatter = match.group(1)
    name_match = NAME_RE.search(frontmatter)
    model_match = MODEL_RE.search(frontmatter)
    if not name_match or not model_match:
        return None
    return name_match.group(1), model_match.group(1)


def _alias_map(tree: ast.Module) -> dict[str, str]:
    """``from x import y as _y`` → {"_y": "y"}. The servers lazy-import under aliases, so an
    unresolved alias would break every reachability chain that crosses a module boundary."""
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for entry in node.names:
                if entry.asname:
                    aliases[entry.asname] = entry.name.rsplit(".", maxsplit=1)[-1]
    return aliases


def build_reference_graph() -> dict[str, set[str]]:
    """Map every function name to every symbol its body references.

    References, not just call-expression targets: this codebase routes blocking work through
    ``asyncio.to_thread(some.writer, ...)``, where the writer is an ARGUMENT rather than the
    callee. A call-only graph would miss `create_staging_node` entirely.

    Names are merged across modules (a bare function name is one node). That is deliberate — it
    resolves both the thin-adapter chain, where a tool and its delegate share a name, and method
    calls on instances, without needing full type inference.
    """
    graph: dict[str, set[str]] = {}
    for pkg in SERVER_PKGS:
        for py_path in sorted(pkg.rglob("*.py")):
            try:
                tree = ast.parse(py_path.read_text(encoding="utf-8"))
            except SyntaxError:  # not our source to police; skip rather than fail the map
                continue
            aliases = _alias_map(tree)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                bucket = graph.setdefault(node.name, set())
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        raw = child.id
                    elif isinstance(child, ast.Attribute):
                        raw = child.attr
                    else:
                        continue
                    bucket.add(raw)
                    if raw in aliases:
                        bucket.add(aliases[raw])
    return graph


def find_chain(start: str, target: str, graph: dict[str, set[str]]) -> list[str] | None:
    """Shortest reference chain start → target, or None when the target is unreachable."""
    if start == target:
        return [start]
    seen = {start}
    queue: deque[list[str]] = deque([[start]])
    while queue:
        chain = queue.popleft()
        for ref in sorted(graph.get(chain[-1], set())):
            if ref == target:
                return [*chain, ref]
            if ref not in seen and ref in graph:
                seen.add(ref)
                queue.append([*chain, ref])
    return None


def verify_writer_symbol(surface: WriteSurface) -> int:
    """Return the writer's def line, or fail loudly. A declared surface whose writer vanished
    means the map is describing code that no longer exists — the exact rot this replaces."""
    module_path = REPO_ROOT / surface.module
    if not module_path.is_file():
        raise SystemExit(f"[dataflow] write surface {surface.surface_id!r}: missing {surface.module}")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == surface.writer_symbol:
            return node.lineno
    raise SystemExit(
        f"[dataflow] write surface {surface.surface_id!r}: writer {surface.writer_symbol!r} "
        f"not found in {surface.module}. The map cannot describe code that does not exist."
    )


def derive_flows(
    tools_by_server: dict[str, list[str]], graph: dict[str, set[str]]
) -> list[tuple[WriteSurface, int, list[tuple[str, str, list[str]]]]]:
    """For each write surface: its verified anchor line and every (server, tool, chain) reaching it."""
    all_tools = sorted(
        (server, tool) for server, tools in tools_by_server.items() for tool in tools
    )
    derived = []
    for surface in WRITE_SURFACES:
        line = verify_writer_symbol(surface)
        edges = []
        for server, tool in all_tools:
            chain = find_chain(tool, surface.writer_symbol, graph)
            if chain is not None:
                edges.append((server, tool, chain))
        derived.append((surface, line, edges))
    return derived


def _md_cell(text: str) -> str:
    """Escape a value for a markdown table cell — destinations contain `|` (alternation)."""
    return text.replace("|", "\\|")


def _mermaid_label(text: str) -> str:
    """Mermaid labels choke on `|`, `<`, `>` and nested brackets; keep it legible but inert."""
    return (
        text.replace('"', "'")
        .replace("|", " / ")
        .replace("<", "")
        .replace(">", "")
        .replace("[", "(")
        .replace("]", ")")
    )


def render(
    tools_by_server: dict[str, list[str]],
    agents: list[tuple[str, str]],
    flows: list[tuple[WriteSurface, int, list[tuple[str, str, list[str]]]]],
) -> str:
    lines: list[str] = []
    lines.append("# Chimera Lite — Dataflow Map (generated)")
    lines.append("")
    lines.append(
        "Generated by `scripts/gen_architecture_diagram.py`. Do not hand-edit — regenerate "
        "at every phase seal. Every write edge below is DERIVED from a reference chain in "
        "source; none is asserted by hand. Describes actual code as it stands; never aspiration."
    )
    lines.append("")

    lines.append("## MCP tool inventory")
    lines.append("")
    for server_name in sorted(tools_by_server):
        lines.append(f"### {server_name}")
        lines.append("")
        for tool_name in tools_by_server[server_name]:
            lines.append(f"- `{tool_name}`")
        lines.append("")

    lines.append("## Subagent -> model pins")
    lines.append("")
    lines.append("| agent | model |")
    lines.append("|---|---|")
    for agent_name, model in agents:
        lines.append(f"| {agent_name} | {model} |")
    lines.append("")

    lines.append("## Write surfaces (derived)")
    lines.append("")
    lines.append(
        "Judgment is externalized out of the MCP layer entirely (Phase L.B): the MCP servers "
        "make NO LLM call. Subagents are spawned by Claude Code SKILLS, never by an MCP tool — "
        "so no tool-to-subagent edge is drawn here, because none exists in code."
    )
    lines.append("")
    lines.append("| destination | writer | anchor | reached by |")
    lines.append("|---|---|---|---|")
    for surface, line, edges in flows:
        anchor = f"`{surface.module}:{line}`"
        writer = f"`{surface.writer_symbol}`"
        reached = (
            ", ".join(f"`{tool}`" for _, tool, _ in edges)
            if edges
            else "**ORPHANED — no MCP tool reaches this**"
        )
        lines.append(f"| `{_md_cell(surface.destination)}` | {writer} | {anchor} | {reached} |")
    lines.append("")

    lines.append("### Derived reference chains")
    lines.append("")
    lines.append("Each edge above, with the chain that proves it:")
    lines.append("")
    for surface, _line, edges in flows:
        for _server, tool, chain in edges:
            lines.append(
                f"- `{tool}` -> `{surface.destination}` via `{' -> '.join(chain)}`"
            )
    lines.append("")

    for surface, _line, _edges in flows:
        if surface.note:
            lines.append(f"- `{surface.destination}` — {surface.note}")
    lines.append("")

    lines.append("```mermaid")
    lines.append("flowchart TD")
    for surface, _line, edges in flows:
        dest_node = f"{surface.surface_id}_dest"
        lines.append(f'    {dest_node}["{_mermaid_label(surface.destination)}"]')
        for _server, tool, _chain in edges:
            lines.append(f'    tool_{tool}["{tool}"] --> {dest_node}')
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    tools_by_server = {name: parse_tools(path) for name, path in SERVERS.items()}
    agents_dir = REPO_ROOT / ".claude" / "agents"
    agents: list[tuple[str, str]] = []
    for agent_path in sorted(agents_dir.glob("*.md")):
        parsed = parse_agent_model(agent_path)
        if parsed is not None:
            agents.append(parsed)
    agents.sort(key=lambda pair: pair[0])

    graph = build_reference_graph()
    flows = derive_flows(tools_by_server, graph)

    out_path = REPO_ROOT / "docs" / "ARCHITECTURE" / "ARCHITECTURE.md"
    out_path.write_text(render(tools_by_server, agents, flows), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
