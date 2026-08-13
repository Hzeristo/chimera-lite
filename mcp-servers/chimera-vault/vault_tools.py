"""Vault search/read tool bodies for the chimera-vault MCP server.

Thin wrappers over a ``VaultReadAdapter`` injected by the server at startup
(``set_vault_adapter``). They return plain strings — the MCP layer has no
structured ToolOutput/artifact channel, so the adapter's formatted text is the
contract. Adapter access is via a structural Protocol, so this module imports no
domain package directly.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class _VaultToolPort(Protocol):
    """Structural type for the vault backend (``VaultReadAdapter`` or a test double)."""

    async def search_notes(self, query: str, top_k: int = 3) -> str: ...

    async def search_by_attribute(self, key: str, value: str, top_k: int = 5) -> str: ...

    async def query_graph(
        self,
        node_type: str | None = None,
        link_pattern: str | None = None,
        max_depth: int = 2,
    ) -> list[dict[str, Any]]: ...

    def read_file(self, path: str) -> str: ...


_vault_adapter: _VaultToolPort | None = None


def set_vault_adapter(adapter: _VaultToolPort) -> None:
    """Bind the process-wide vault adapter (called once by the server at startup)."""
    global _vault_adapter
    _vault_adapter = adapter


def _adapter() -> _VaultToolPort:
    if _vault_adapter is None:
        raise RuntimeError("Vault adapter not initialized")
    return _vault_adapter


async def search_vault(query: str, top_k: int = 3) -> str:
    q = (query or "").strip()
    if not q:
        return "[Tool Error]: search_vault requires a non-empty query string."
    return await _adapter().search_notes(q, top_k)


async def search_vault_attribute(key: str, value: str, top_k: int = 5) -> str:
    k = (key or "").strip()
    v = (value or "").strip()
    if not k or not v:
        return "[Tool Error]: search_vault_attribute requires non-empty key and value."
    return await _adapter().search_by_attribute(k, v, top_k)


async def read_vault_file(path: str) -> str:
    p = (path or "").strip()
    if not p:
        return "[Tool Error]: read_vault_file requires a non-empty path string."
    try:
        content = _adapter().read_file(p)
    except FileNotFoundError:
        return f"[Tool Error]: read_vault_file file not found: {p}"
    except ValueError as e:
        return f"[Tool Error]: read_vault_file invalid path: {e}"
    return f"[File: {p}]\n\n{content}"


def compose_criteria(
    read_file: Callable[[str], str],
    *,
    type: str,
    role: str,
    field: str | None = None,
) -> str:
    """Compose a three-axis criteria matrix (capability, then disposition) from the vault.

    Pure function over an injected ``read_file`` callable so it is trivially unit-testable
    without a live vault or a full ``ChimeraConfig``. Reads, IN THIS EXACT ORDER (capability
    axes before disposition axes — order is load-bearing, not cosmetic):

    1. ``criteria/type/{type}.md``           — capability: verification shape for the paper type.
    2. ``criteria/field/{field}.md``         — capability: domain taste (only if ``field`` given).
    3. ``criteria/disposition/{role}.md``    — disposition: anti-bias posture for the role.
    4. ``criteria/disposition/_general.md``  — disposition: anti-early-stop / graded-confidence.

    Any missing file is never fabricated and never raises — it is replaced by an explicit
    ``[no criteria file: criteria/<...>.md]`` marker so the caller can see what's unauthored.
    ``field`` is an open, unvalidated axis (frequently absent by design); ``type`` is not
    validated here either — validation, if any, belongs to the caller.

    Args:
        read_file: Callable taking a vault-root-relative path, returning its text content,
            and raising ``FileNotFoundError`` when the path does not exist.
        type: Paper type (e.g. benchmark, method, theory, survey).
        role: Disposition role (e.g. paper-critic, proposal-evaluator).
        field: Optional domain/field name; omitted entirely from composition if ``None``.
    """

    def _section(header: str, rel_path: str) -> str:
        try:
            content = read_file(rel_path)
        except FileNotFoundError:
            content = f"[no criteria file: {rel_path}]"
        return f"{header}\n\n{content}"

    sections = [_section(f"## [type: {type}]", f"criteria/type/{type}.md")]
    if field is not None:
        sections.append(_section(f"## [field: {field}]", f"criteria/field/{field}.md"))
    sections.append(_section(f"## [disposition: {role}]", f"criteria/disposition/{role}.md"))
    sections.append(
        _section("## [disposition: _general]", "criteria/disposition/_general.md")
    )
    return "\n\n".join(sections)


async def load_criteria(type: str, role: str, field: str | None = None) -> str:
    return compose_criteria(_adapter().read_file, type=type, role=role, field=field)


def _format_graph_rows(
    node_type: str | None,
    link_pattern: str | None,
    rows: list[dict[str, Any]],
) -> str:
    if not rows:
        bits: list[str] = []
        if node_type:
            bits.append(f"type={node_type!r}")
        if link_pattern:
            bits.append(f"pattern={link_pattern!r}")
        tail = ", ".join(bits) if bits else "no matching notes in vault"
        return f"[Graph Query] No nodes found ({tail})"
    out = f"[Graph Query] Found {len(rows)} nodes:\n\n"
    for node in rows[:10]:
        title = node.get("title", "?")
        ntype = node.get("type", "")
        links = node.get("links") or []
        line = f"- {title}"
        if ntype:
            line += f" ({ntype})"
        out += line + "\n"
        if links:
            out += f"  Links: {', '.join(str(x) for x in links[:5])}\n"
    if len(rows) > 10:
        out += f"\n… and {len(rows) - 10} more (showing first 10).\n"
    return out


async def obsidian_graph_query(
    node_type: str | None = None,
    link_pattern: str | None = None,
    max_depth: int = 2,
) -> str:
    nt = None if node_type is None else (str(node_type).strip() or None)
    lp = None if link_pattern is None else (str(link_pattern).strip() or None)
    md = max(1, min(int(max_depth), 8))
    rows = await _adapter().query_graph(nt, lp, md)
    return _format_graph_rows(nt, lp, rows)
