"""M.0.5 import smoke: the ported `core` package loads flat, is oligo-free, and
computes the chimera-lite repo root (not project_chimera's depth)."""

from __future__ import annotations

from pathlib import Path

_CORE_DIR = (
    Path(__file__).resolve().parents[1]
    / "mcp-servers"
    / "chimera-papers"
    / "core"
)


def test_core_modules_import() -> None:
    import core.config  # noqa: F401
    import core.naming  # noqa: F401
    import core.platform  # noqa: F401
    import core.schemas  # noqa: F401


def test_artifact_and_tooloutput_present() -> None:
    from core.schemas import Artifact, ToolOutput

    out = ToolOutput(text="hi", artifacts=[Artifact(kind="vault_note", path="x.md")])
    assert out.artifacts is not None
    assert out.artifacts[0].kind == "vault_note"


def test_project_root_is_chimera_lite() -> None:
    from core.platform import get_project_root

    assert get_project_root().name == "chimera-lite"


def test_core_has_no_oligo_imports() -> None:
    for py in _CORE_DIR.glob("*.py"):
        assert "src.oligo" not in py.read_text(encoding="utf-8"), py.name
