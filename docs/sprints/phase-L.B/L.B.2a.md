# Modification Summary: L.B.2a

**Phase:** L.B — Consolidation
**Sprint:** L.B.2a — Model config slots + Anthropic client path 🟡
**Batch position:** 2 of 7 (parallel-eligible with L.B.3 after L.B.1)
**Date:** 2026-07-21
**Executed by:** Sonnet subagent (`chimera-sprint-executor`); design authored + reviewed + committed by main session (Opus).

## Objective
Add distinct Haiku and Sonnet judgment slots + a role-parameterized client builder, so L.B.2b
can route `filter_service` → Haiku and `single_paper_extract` → Sonnet instead of sharing the
one `llm.working` slot. Substrate only; no call-site behavior change.

## Files touched
| Path | Change |
|---|---|
| `core/config.py` | `_default_haiku_slot()` / `_default_sonnet_slot()` factories (current ids `claude-haiku-4-5` / `claude-sonnet-5`, provider `anthropic`, base_url `https://api.anthropic.com/v1`); two optional `LLMConfig` fields `haiku`/`sonnet` with those defaults |
| `bootstrap.py` | `_ROLE_SLOTS` + `build_client(role, settings=None)` — a thin role→slot selector reusing `build_openai_client_from_model_config` |
| `tests/test_model_slots.py` | new — slot defaults + `build_client` dispatch + unknown-role raise (hermetic) |

## Key design facts
- **No new dependency (dependency-veto).** `pyproject.toml` ships only `openai>=1.40`; the `anthropic` SDK is NOT installed. The Anthropic endpoint is reached through the existing `OpenAICompatibleClient` pointed at `https://api.anthropic.com/v1` — the `anthropic` provider was already wired in `_resolve_slot_api_key` / `_fallback_api_key_from_base_url`. `build_client` reuses `build_openai_client_from_model_config` verbatim.
- **Current model ids per the `claude-api` skill** — `claude-haiku-4-5`, `claude-sonnet-5`, no date suffixes. The stale `anthropic` PROVIDER slot (`claude-3-5-sonnet-20241022`) was left untouched (out of scope; L.B.2a adds dedicated judgment slots rather than repurposing the legacy provider slot).
- **Optional fields with `default_factory`** so an existing `~/.chimera/config.toml` without `[llm.haiku]`/`[llm.sonnet]` still validates under `extra="forbid"`.
- **Executor correction (accepted):** the factories were placed BEFORE `class LLMConfig` (not "near `_default_llm_config`" as the spec's prose said) — a `default_factory=` reference is evaluated at class-body execution, so a later definition would `NameError` at import. Same content, correct order.

## Verification
| Check | Status | Output |
|---|---|---|
| ruff | clean | exit 0 — "All checks passed!" (`uvx ruff`, ephemeral — not a project dep) |
| pytest (env-artifact deselected) | 121 passed | exit 0 |

## Known risk carried to L.B.6 (not a defect here)
Claude Sonnet 5 / current models reject `temperature` on the **native** Messages API. This path goes through Anthropic's **OpenAI-compatible** endpoint (which accepts OpenAI-style params), and `OpenAICompatibleClient` always sends `temperature`. The slots use low temps (haiku 0.0, sonnet 0.2). Whether the compat endpoint accepts/ignores `temperature` for these models is a **live-call** question — L.B.2a makes no network call (tests inspect the constructed client only). Verify on the first real call in L.B.6; if rejected, the fix is scoped to the client/endpoint config, not these slots.

## Red Line Status
| Red Line | Status |
|---|---|
| No new dependency; reuse existing client stack | ✓ (no `anthropic` import; OpenAICompatibleClient reused) |
| Models config-resolved — no hardcoded model in judgment code | ✓ (ids live in config.py factories) |
| Thin — slot logic in config/bootstrap, not tool bodies | ✓ |
| No call-site behavior change (that is L.B.2b) | ✓ (filter_service / single_paper_extract untouched) |
| No opportunistic refactoring | ✓ (stale provider slot left as-is) |

## Acceptance
- ✅ `llm.haiku`/`llm.sonnet` resolve to the current ids; `build_client("haiku"|"sonnet")` builds a client for each.
- ✅ No behavior change at call sites — L.B.2b wires them.
