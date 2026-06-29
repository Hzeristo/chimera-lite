"""M.1 vault-wiring smoke against the live vault (skips if not configured).

Verifies sealing condition 1: vault_query(type="knowledge") returns real notes in <2s,
plus adapter-backed search/graph/read and the no-sentinel / independence guards.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

_VAULT_DIR = Path(__file__).resolve().parents[1] / "mcp-servers" / "chimera-vault"


def _vault_available() -> bool:
    try:
        from core.config import get_config

        return get_config().system.vault_root is not None
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _vault_available(), reason="vault_root not configured (~/.chimera/config.toml)"
)


@pytest.mark.skipif(shutil.which("rg") is None, reason="ripgrep (rg) not on PATH")
async def test_vault_query_knowledge_under_2s() -> None:
    import vault_query as vq

    t = time.perf_counter()
    out = await vq.vault_query(type="knowledge")
    dt = time.perf_counter() - t
    assert out.startswith("[vault_query]"), out[:80]
    assert "match(es)" in out, "expected at least one knowledge note"
    assert dt < 2.0, f"vault_query took {dt:.2f}s (HSC requires <2s)"


async def test_adapter_backed_search_and_graph() -> None:
    import vault_tools
    from core.config import get_config
    from ports.vault.vault_read_adapter import VaultReadAdapter

    vault_tools.set_vault_adapter(VaultReadAdapter(get_config()))

    graph = await vault_tools.obsidian_graph_query(node_type="knowledge", max_depth=1)
    assert "[Graph Query]" in graph

    search = await vault_tools.search_vault("memory", top_k=2)
    assert isinstance(search, str) and search.strip()


def test_no_sentinels_and_independent() -> None:
    for py in _VAULT_DIR.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "NOT_WIRED" not in text, py.name
        assert "src.oligo" not in text, py.name
