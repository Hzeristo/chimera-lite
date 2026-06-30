"""chimera-vault MCP server — read and query the Obsidian research vault.

Thin adapter: the @mcp.tool functions declare the contract and delegate to the
ported tool bodies (``vault_tools`` / ``vault_query``). The real domain logic lives
in ``VaultReadAdapter`` (under the sibling chimera-papers domain package) + ripgrep.
"""

from __future__ import annotations

import sys
from pathlib import Path

# The shared domain package (core/, ports/) lives under the sibling papers server.
# Put it on sys.path so this server can import core.config + the VaultReadAdapter.
_DOMAIN = Path(__file__).resolve().parent.parent / "chimera-papers"
if str(_DOMAIN) not in sys.path:
    sys.path.insert(0, str(_DOMAIN))

import logging  # noqa: E402

from mcp.server.fastmcp import FastMCP  # noqa: E402

import vault_query as vault_query_mod  # noqa: E402
import vault_tools  # noqa: E402

# Logs to stderr only — stdout is the MCP JSON-RPC channel (see chimera-papers/server.py).
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

mcp = FastMCP("chimera-vault")

_adapter_ready = False


def _ensure_adapter() -> None:
    """Construct + bind the process-wide VaultReadAdapter on first use (lazy so the
    server starts even before config is reachable)."""
    global _adapter_ready
    if _adapter_ready:
        return
    from core.config import get_config
    from ports.vault.vault_read_adapter import VaultReadAdapter

    vault_tools.set_vault_adapter(VaultReadAdapter(get_config()))
    _adapter_ready = True


@mcp.tool()
async def search_vault(query: str, top_k: int = 3) -> str:
    """Search the Obsidian vault for notes whose bodies match the query (keyword-style).

    Args:
        query: Keywords to match in note bodies (non-empty).
        top_k: Maximum snippets to return (default 3).
    """
    _ensure_adapter()
    return await vault_tools.search_vault(query, top_k=top_k)


@mcp.tool()
async def search_vault_attribute(key: str, value: str, top_k: int = 5) -> str:
    """Search the vault by YAML frontmatter (key must exist; value matched as substring).

    Args:
        key: Frontmatter field name (e.g. ``type``, ``tags``).
        value: Substring to find within that field's value.
        top_k: Maximum hits (default 5).
    """
    _ensure_adapter()
    return await vault_tools.search_vault_attribute(key, value, top_k=top_k)


@mcp.tool()
async def read_vault_file(path: str) -> str:
    """Read the full content of a vault note by its path.

    Args:
        path: Note path relative to the vault root (or absolute under the vault root).
    """
    _ensure_adapter()
    return await vault_tools.read_vault_file(path)


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
    _ensure_adapter()
    return await vault_tools.obsidian_graph_query(
        node_type, link_pattern, max_depth=max_depth
    )


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
    return await vault_query_mod.vault_query(type=type, status=status, linked_to=linked_to)


if __name__ == "__main__":
    mcp.run()
