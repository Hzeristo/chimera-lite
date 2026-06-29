# Sprint M.1 — Vault MCP wiring

**Status:** ✅ Complete (1 HSC element deferred to M.5 — see below)
**Commit:** {filled at commit}
**Risk:** 🔴 HIGH — executed under per-sprint approval ("Proceed to M.1", 2026-06-28).
**Plan ref:** `docs/plans/Phase-M-batch.md` → Sprint M.1
**Audit ref:** `docs/audits/M.0.md` Q1/Q2 + cross-finding #2

## Objective
Connect the five `chimera-vault` MCP tools to the real `VaultReadAdapter` + ripgrep
logic; delete their NOT-WIRED sentinels.

## What was done
- Authored `mcp-servers/chimera-vault/vault_tools.py` — `search_vault`,
  `search_vault_attribute`, `read_vault_file`, `obsidian_graph_query`. Adapter accessed
  via a structural `Protocol` (no domain import); returns plain `str` (MCP has no
  ToolOutput/artifact channel — artifacts dropped per plan).
- Authored `mcp-servers/chimera-vault/vault_query.py` — ported from oligo, flat import
  (`from core.config import get_config`), ripgrep subprocess.
- Rewrote `chimera-vault/server.py` — adds the sibling `chimera-papers` domain dir to
  `sys.path`, lazily constructs+binds `VaultReadAdapter(get_config())`, and delegates the
  five `@mcp.tool` bodies to the ported functions. All `_NOT_WIRED` removed.
- `ports/vault/vault_read_adapter.py`: imports `src.crucible.core.*` → `core.*` (flat).

## Verification (real exit codes)
- ruff: **0** — All checks passed.
- pytest (`tests/`): **0** — 6 passed, 1 skipped.
- Live (manual): `VaultReadAdapter(get_config()).query_graph("knowledge")` → **200 nodes**,
  real titles (`2402.07630v3-GRetriever_Deep_Read`).
- `grep NOT_WIRED mcp-servers/chimera-vault/*.py` → **0**.
- independence: `grep src.oligo` in M.1 files → 0.

## HSC status (sealing condition 1)
- Adapter-backed tools (`search_vault` / `search_vault_attribute` / `read_vault_file` /
  `obsidian_graph_query`): ✅ verified live against the real vault.
- `vault_query(type="knowledge")` **< 2s live**: ⏸ **deferred to M.5**. The code is wired
  and correct (loads config → resolves `vault_root` → attempts rg → graceful error), but
  `rg` is not on this dev shell's PATH (Claude's bundled ripgrep isn't exposed as a
  standalone `rg`). The timing test skips when `shutil.which("rg") is None`. **Prereq:
  install ripgrep on PATH for the M.5 live smoke** (already documented in CLAUDE.md).

## Accepted deviations / adjustments (declared at execution)
1. **`config.py` `extra="forbid"` → `extra="ignore"`** (top-level only; nested models keep
   `forbid`). Necessary so the shared `~/.chimera/config.toml` — which still carries the
   retired `[oligo]` section — loads after M.0.5 removed the `oligo` field. Surfaced when
   constructing the adapter via `get_config()`.
2. **`ports/vault/__init__.py` eager re-exports neutralized.** It imported
   `vault_note_writer` (an M.2 file) via `src.crucible`, which broke the vault-read import
   chain. All real consumers import the submodules directly, so the package re-export was
   unused; reading the vault no longer pulls the write/ingest chain.
3. **Tools return `str`** (ToolOutput/artifacts dropped) — per plan; MCP has no artifact
   channel. The astrocyte chip UI that consumed artifacts is retired.

## Predecessor handoff to M.2 / M.4
- `core.config` now tolerates unknown config sections; `ports.vault.vault_read_adapter`
  imports flat. `vault_note_writer.py` still imports `src.crucible.*` — M.2 rewrites it.
- M.5 prereq: ripgrep on PATH for the `vault_query` live timing check.
