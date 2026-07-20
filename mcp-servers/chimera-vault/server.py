"""chimera-vault MCP server — read/query the vault + stage K/T/I/D nodes for review.

Thin adapter: the @mcp.tool functions declare the contract and delegate to the ported
tool bodies (``vault_tools`` / ``vault_query`` for reads; ``StagingService`` for
``create_node``). The real domain logic lives in ``VaultReadAdapter`` + ``StagingService``
(under the sibling chimera-papers domain package) + ripgrep. Writes are staging-only
(``docs/staging/`` → user review); this server never auto-promotes into the vault.
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
async def load_criteria(type: str, role: str, field: str | None = None) -> str:
    """Compose the runtime criteria matrix for a research-harness subagent (W1/W2 etc).

    Reads up to four vault files under ``criteria/`` and concatenates them, IN THIS EXACT
    ORDER — capability axes always load before disposition axes:

        1. ``criteria/type/{type}.md``           (capability — verification shape)
        2. ``criteria/field/{field}.md``         (capability — domain taste; only if field given)
        3. ``criteria/disposition/{role}.md``    (disposition — anti-bias posture)
        4. ``criteria/disposition/_general.md``  (disposition — anti-early-stop / graded-confidence)

    This order is load-bearing: capability criteria establish what "verified" even means for
    this paper type/field before the disposition axes bias how the subagent should carry
    itself while verifying. Because criteria live in the vault (not in code), editing a file
    in Obsidian changes subagent behavior on the very next run — no commit required. A missing
    file is never fabricated; it is replaced with an explicit
    ``[no criteria file: criteria/<...>.md]`` marker in its place.

    Args:
        type: Paper type — the closed 4-class set {benchmark, method, theory, survey}
            (not hard-validated here).
        role: Disposition role, e.g. ``paper-critic`` or ``proposal-evaluator``.
        field: Optional domain/field (e.g. ``nlp``, ``robotics``); an open axis, frequently
            absent — omit to skip that section entirely.
    """
    _ensure_adapter()
    return await vault_tools.load_criteria(type, role, field=field)


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


@mcp.tool()
async def create_node(
    type: str,
    title: str,
    body: str,
    edges: dict | None = None,
) -> str:
    """Create a K/T/I/D node in the staging area for user review (never auto-promoted).

    Writes a markdown node with typed ``graph_edges`` frontmatter to ``docs/staging/``
    and returns the staging path. Promotion into the vault is a separate, explicit step —
    this tool never writes into the live vault.

    Args:
        type: Node type — ``knowledge``, ``thought``, ``insight``, or ``decision``.
        title: Node title (also used to derive the staging filename).
        body: Markdown body of the node.
        edges: Optional typed edges, e.g. ``{"derives_from": ["Some Note"]}``. Keys must be
            valid for the node type per ``docs/ARCHITECTURE/NODE_ONTOLOGY.md``; unknown keys
            are rejected. Values are lists of target wikilink stems.
    """
    from core.config import get_config
    from staging_service import StagingService

    config = get_config()
    service = StagingService(config.system.staging_dir, config.require_path("vault_root"))
    path = service.create_staging_node(type=type, title=title, body=body, edges=edges)
    return str(path)


@mcp.tool()
async def link_nodes(from_node: str, to_node: str, edge_type: str) -> str:
    """Stage a typed-edge link between two vault nodes for review (no live write).

    Resolves both endpoints, validates ``edge_type`` for the FROM node's type against
    ``docs/ARCHITECTURE/NODE_ONTOLOGY.md``, and writes a reviewable patch to
    ``docs/staging/``. Apply it after review with ``apply_link_patch``. This tool never
    edits the vault.

    Args:
        from_node: Source node — note stem/title or arxiv_id. Gains ``edge_type: [to_node]``.
        to_node: Target node — note stem/title or arxiv_id (the link destination).
        edge_type: Typed edge (e.g. derives_from, synthesizes); must be valid for the
            FROM node's type per NODE_ONTOLOGY.md.
    """
    import yaml

    from core.config import get_config
    from ports.vault.vault_read_adapter import VaultReadAdapter
    from staging_service import StagingService

    config = get_config()
    adapter = VaultReadAdapter(config)
    from_path = adapter.resolve_note_path(from_node)
    if from_path is None:
        raise ValueError(f"Could not resolve 'from' node: {from_node!r}")
    to_path = adapter.resolve_note_path(to_node)
    if to_path is None:
        raise ValueError(f"Could not resolve 'to' node: {to_node!r}")

    try:
        from_type = str((yaml.safe_load(from_path.read_text(encoding="utf-8").split("---", 2)[1]) or {}).get("type", "")).strip()
    except (IndexError, ValueError, yaml.YAMLError):
        from_type = ""

    service = StagingService(config.system.staging_dir, config.require_path("vault_root"))
    patch = service.stage_link_patch(
        from_stem=from_path.stem,
        from_path=from_path,
        from_type=from_type,
        edge_type=edge_type,
        to_stem=to_path.stem,
        to_path=to_path,
    )
    return str(patch)


@mcp.tool()
async def apply_link_patch(patch_path: str) -> str:
    """Apply a reviewed link patch — merge its edge into the target vault node in place.

    Reads the patch from ``docs/staging/`` (produced by ``link_nodes``), appends the edge
    to the target node's ``graph_edges`` (idempotent — a duplicate is a no-op), and consumes
    the patch. Preserves the note body and every non-edge frontmatter line verbatim. This is
    the ONLY vault-mutating tool — run it only after reviewing the patch.

    Args:
        patch_path: Path to the link patch in docs/staging/ (as returned by link_nodes).
    """
    from core.config import get_config
    from staging_service import StagingService

    config = get_config()
    service = StagingService(config.system.staging_dir, config.require_path("vault_root"))
    target = service.apply_link_patch(Path(patch_path))
    return str(target)


@mcp.tool()
async def write_result(
    kind: str,
    identity: str,
    title: str,
    body: str,
    verdict: str | None = None,
    depends_on: list[str] | None = None,
    mode: str = "supersede",
) -> str:
    """Write a research-harness result artifact into the vault for the Architect's review.

    WHEN: a Phase L W1/W2 workflow has produced a result to persist — a W1 claim verdict
    ([V]/[P]/[U] + verbatim grounding quotes), or a W2 breadth map. Writes into ``<vault>/Harness/``
    with a review ``status`` so the Architect curates it in Obsidian (the harness + Obsidian "two
    curation paths"). This is NOT a K/T/I/D node and is never auto-promoted.
    WHAT: writes one markdown artifact keyed by ``(kind, identity)``. ``mode`` sets the re-run
    semantics:
    - ``supersede`` (default — W1): a re-run REPLACES the artifact; pass ``verdict`` + ``depends_on``
      so the dependency structure lands in frontmatter (Phase K Gate 1 reads it — never stored bare).
    - ``merge`` (W2 breadth map): a re-run UNIONS the map by paper key — ADDS new papers, PRESERVES
      the Architect's in-Obsidian annotations verbatim. W2 renders each paper as a keyed block
      ``<!-- w2:paper=<id> -->`` so the merge can key on it. Merge never clobbers.
    - ``reject`` / ``mark_stale``: status transition on an EXISTING artifact (body untouched).

    Args:
        kind: Artifact kind, e.g. ``w1_verdict`` / ``w2_breadth_map``.
        identity: Stable identity — a claim_hash / arxiv_id (W1) or a topic / seed-set slug (W2).
        title: Human-readable artifact title.
        body: Markdown body — verdict + quotes (W1), or keyed paper blocks (W2).
        verdict: For ``w1_verdict`` — the tag ``V`` / ``P`` / ``U``.
        depends_on: The claim / quote ids the verdict rests on (C1 — recorded, not just the verdict).
        mode: ``supersede`` | ``merge`` | ``reject`` | ``mark_stale``.
    """
    from core.config import get_config
    from result_service import ResultService

    config = get_config()
    metadata: dict = {}
    if verdict is not None:
        metadata["verdict"] = verdict
    if depends_on is not None:
        metadata["depends_on"] = depends_on
    service = ResultService(config.require_path("vault_root") / "Harness")
    path = service.write_result(
        kind=kind, identity=identity, title=title, body=body, metadata=metadata or None, mode=mode
    )
    return str(path)


if __name__ == "__main__":
    mcp.run()
