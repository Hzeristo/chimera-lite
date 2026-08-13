"""``vault_query`` must find notes regardless of line endings.

Incident 2026-08-12: the vault is edited on Windows and by Obsidian, so notes carry mixed line
endings. ``vault_query`` shells out to ripgrep with anchored patterns (``^status: X$``), and
without ``--crlf`` the ``$`` cannot match past a trailing ``\\r``. Every CRLF note was therefore
absent from the result — with no error, no warning, and a plausible-looking shorter list.

Observed live: ``vault_query(status="PENDING_REVIEW")`` returned 2 of the 6 pending Harness
artifacts. A workflow built on it would have silently hidden four verdicts from the Architect.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DOMAIN = Path(__file__).resolve().parents[1] / "mcp-servers" / "chimera-vault"
if str(_DOMAIN) not in sys.path:
    sys.path.insert(0, str(_DOMAIN))

import vault_query as vq

_NOTE = "---\ntype: knowledge\nstatus: PENDING_REVIEW\ntitle: {title}\n---\n\nbody\n"


class _StubSettings:
    def __init__(self, root: Path) -> None:
        self._root = root

    def require_path(self, _key: str) -> Path:
        return self._root


@pytest.fixture()
def vault(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "vault"
    root.mkdir()
    # Written as bytes so the line endings are exactly what this test is about — never let the
    # platform's newline translation decide the fixture.
    (root / "lf.md").write_bytes(_NOTE.format(title="LF note").encode("utf-8"))
    (root / "crlf.md").write_bytes(
        _NOTE.format(title="CRLF note").replace("\n", "\r\n").encode("utf-8")
    )
    monkeypatch.setattr(vq, "get_config", lambda: _StubSettings(root))
    return root


async def test_status_query_finds_crlf_notes(vault: Path) -> None:
    result = await vq.vault_query(status="PENDING_REVIEW")
    assert "lf.md" in result
    assert "crlf.md" in result, (
        "CRLF note missing — ripgrep needs --crlf or `$` cannot match past the trailing \\r, "
        "and the query returns a silently partial list"
    )
    assert "2 match(es)" in result


async def test_type_query_finds_crlf_notes(vault: Path) -> None:
    # The same anchored-pattern path is used for `type`, so it carries the same defect.
    result = await vq.vault_query(type="knowledge")
    assert "crlf.md" in result
    assert "2 match(es)" in result
