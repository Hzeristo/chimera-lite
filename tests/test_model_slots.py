"""Phase L.B.2a: dedicated Haiku/Sonnet judgment slots (config) + role-parameterized client
builder (bootstrap.build_client).

Hermetic — builds an explicit ``ChimeraConfig``/``LLMConfig`` rather than relying on a real
``~/.chimera/config.toml``. Reuses the existing ``anthropic`` provider slot + OpenAI-compatible
client machinery; no ``anthropic`` SDK import anywhere.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bootstrap import build_client
from core.config import ChimeraConfig, LLMConfig, LLMModelConfig, SystemConfig
from ports.llm.openai_compatible_client import OpenAICompatibleClient


def _working_slot() -> LLMModelConfig:
    return LLMModelConfig(
        provider="openai",
        model="gpt-4o-mini",
        api_key="x",
        base_url="https://api.openai.com/v1",
    )


def _wash_slot() -> LLMModelConfig:
    return LLMModelConfig(
        provider="deepseek",
        model="deepseek-chat",
        api_key="x",
        base_url="https://api.deepseek.com",
    )


def _make_settings(tmp_path: Path) -> ChimeraConfig:
    """Explicit, hermetic settings — haiku/sonnet slots carry a non-empty api_key so
    ``build_openai_client_from_model_config`` resolves without touching real env/TOML."""
    return ChimeraConfig(
        system=SystemConfig(vault_root=tmp_path),
        llm=LLMConfig(
            working=_working_slot(),
            wash=_wash_slot(),
            haiku=LLMModelConfig(
                provider="anthropic",
                model="claude-haiku-4-5",
                api_key="test-key",
                base_url="https://api.anthropic.com/v1",
            ),
            sonnet=LLMModelConfig(
                provider="anthropic",
                model="claude-sonnet-5",
                api_key="test-key",
                base_url="https://api.anthropic.com/v1",
            ),
        ),
    )


def test_haiku_slot_defaults_to_claude_haiku_4_5() -> None:
    cfg = LLMConfig(working=_working_slot(), wash=_wash_slot())
    assert cfg.haiku.model == "claude-haiku-4-5"


def test_sonnet_slot_defaults_to_claude_sonnet_5() -> None:
    cfg = LLMConfig(working=_working_slot(), wash=_wash_slot())
    assert cfg.sonnet.model == "claude-sonnet-5"


def test_build_client_haiku_returns_expected_model(tmp_path: Path) -> None:
    settings = _make_settings(tmp_path)
    client = build_client("haiku", settings)
    assert isinstance(client, OpenAICompatibleClient)
    assert client.model == "claude-haiku-4-5"


def test_build_client_sonnet_returns_expected_model(tmp_path: Path) -> None:
    settings = _make_settings(tmp_path)
    client = build_client("sonnet", settings)
    assert isinstance(client, OpenAICompatibleClient)
    assert client.model == "claude-sonnet-5"


def test_build_client_unknown_role_raises(tmp_path: Path) -> None:
    settings = _make_settings(tmp_path)
    with pytest.raises(ValueError, match="Unknown client role"):
        build_client("nonsense", settings)
