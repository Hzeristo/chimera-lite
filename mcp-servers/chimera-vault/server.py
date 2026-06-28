"""chimera-vault MCP server — read and query the Obsidian research vault.

This module is the AUTHORITATIVE tool contract for the vault surface migrated from
oligo's ``vault_tools.py`` and ``vault_query.py``. Each ``@mcp.tool`` declares the
name, arguments, and docstring Claude Code sees.

Migration status (see CLAUDE.md): the underlying domain code is not yet wired. Each
tool lazy-imports its implementation from a sibling module that migration sprint 1
will create (``vault_tools.py`` with flat imports + a ``VaultReadAdapter`` bound to
``CHIMERA_VAULT_ROOT``). Until then, calls return ``_NOT_WIRED`` rather than crashing,
so the server still starts and the contract is introspectable.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("chimera-vault")

_NOT_WIRED = (
    "[chimera-vault] Tool contract is live, but the domain implementation is not "
    "wired yet (migration sprint 1). Pending: port vault_tools/vault_query to flat "
    "imports and bind VaultReadAdapter to CHIMERA_VAULT_ROOT."
)


def _vault_root() -> str:
    """Vault path from the env var set in .mcp.json (empty string if unset)."""
    return os.environ.get("CHIMERA_VAULT_ROOT", "")


def _as_text(out: object) -> str:
    """Normalize a domain return (str or ToolOutput-like) to a string."""
    return getattr(out, "text", None) or str(out)


@mcp.tool()
async def search_vault(query: str, top_k: int = 3) -> str:
    """Search the Obsidian vault for notes whose bodies match the query (keyword-style).

    Args:
        query: Keywords to match in note bodies (non-empty).
        top_k: Maximum snippets to return (default 3).
    """
    try:
        from vault_tools import search_vault as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(query, top_k=top_k))


@mcp.tool()
async def search_vault_attribute(key: str, value: str, top_k: int = 5) -> str:
    """Search the vault by YAML frontmatter (key must exist; value matched as substring).

    Args:
        key: Frontmatter field name (e.g. ``type``, ``tags``).
        value: Substring to find within that field's value.
        top_k: Maximum hits (default 5).
    """
    try:
        from vault_tools import search_vault_attribute as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(key, value, top_k=top_k))


@mcp.tool()
async def read_vault_file(path: str) -> str:
    """Read the full content of a vault note by its path.

    Args:
        path: Note path relative to the vault root (or absolute under the vault root).
    """
    try:
        from vault_tools import read_vault_file as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(path))


@mcp.tool()
async def obsidian_graph_query(
    node_type: str | None = None,
    link_pattern: str | None = None,
    max_depth: int = 2,
) -> str:
    """Query the Obsidian graph for nodes and links (frontmatter type, wikilinks, edges).

    Args:
        node_type: Filter by YAML ``type`` (knowledge / thought / insight / decision).
        link_pattern: Substring that must appear in the note body.
        max_depth: Graph BFS depth from seed nodes (clamped 1–8; default 2).
    """
    try:
        from vault_tools import obsidian_graph_query as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(node_type, link_pattern, max_depth=max_depth))


@mcp.tool()
async def vault_query(
    type: str | None = None,
    status: str | None = None,
    linked_to: str | None = None,
) -> str:
    """Ripgrep vault frontmatter for notes matching type, status, or edge target.

    Returns title + path + excerpt per match. Requires ripgrep (``rg``) on PATH.

    Args:
        type: Node type to match (knowledge, thought, insight, decision).
        status: Status value to match (e.g. unverified, active, dead_end).
        linked_to: arxiv_id or title substring that must appear in a graph_edges list.
    """
    try:
        from vault_query import vault_query as _impl  # type: ignore  # sprint 1
    except ImportError:
        return _NOT_WIRED
    return _as_text(await _impl(type=type, status=status, linked_to=linked_to))


if __name__ == "__main__":
    mcp.run()
