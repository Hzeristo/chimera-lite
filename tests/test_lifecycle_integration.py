"""L.B.4 lifecycle integration (CODE half): vault_query rows carry chimera_tier.

Mirrors ``tests/test_vault_tools.py`` (import ``vault_query`` inside the test body, since
it lives in the ``chimera-vault`` pythonpath root) — here the vault root is monkeypatched
to an isolated ``tmp_path`` fixture rather than the live vault, so the tier value is
deterministic.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest


class _FakeSettings:
    def __init__(self, vault_root: Path) -> None:
        self._vault_root = vault_root

    def require_path(self, field_name: str) -> Path:
        assert field_name == "vault_root"
        return self._vault_root


def _write_note(vault: Path, name: str, frontmatter: str) -> None:
    # Explicit \n (no Windows CRLF translation) — rg's ^...$ anchors need bare LF.
    (vault / name).write_bytes(f"---\n{frontmatter}---\nbody\n".encode("utf-8"))


@pytest.mark.skipif(shutil.which("rg") is None, reason="ripgrep (rg) not on PATH")
async def test_vault_query_row_carries_chimera_tier(tmp_path: Path, monkeypatch) -> None:
    import vault_query as vq

    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(
        vault,
        "Deep_Read_Node.md",
        "type: knowledge\nstatus: active\nchimera_tier: deep_read\ntitle: Deep Read Node\n",
    )

    monkeypatch.setattr(vq, "get_config", lambda: _FakeSettings(vault))

    out = await vq.vault_query(type="knowledge")

    assert "match(es)" in out
    assert "tier=deep_read" in out


@pytest.mark.skipif(shutil.which("rg") is None, reason="ripgrep (rg) not on PATH")
async def test_vault_query_row_falls_back_to_unknown_tier(
    tmp_path: Path, monkeypatch
) -> None:
    import vault_query as vq

    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(
        vault,
        "Untiered_Node.md",
        "type: knowledge\nstatus: unverified\ntitle: Untiered Node\n",
    )

    monkeypatch.setattr(vq, "get_config", lambda: _FakeSettings(vault))

    out = await vq.vault_query(type="knowledge")

    assert "tier=?" in out
