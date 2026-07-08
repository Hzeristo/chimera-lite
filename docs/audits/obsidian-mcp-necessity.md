# Obsidian MCP Servers — Market Survey & Necessity Audit

**Date:** 2026-07-07
**Context:** Phase O (Exocortex Write Surface), sprint O.3 — "use an Obsidian MCP if a market one
exists; else a minimal file-write tool" (`docs/phases/phase-O.md:23,35`). The O.0 audit
(`docs/audits/O.0.md`, Q7) flagged that decision as a `chimera-dependency-veto` touchpoint and
recommended verifying the market before building. This is that verification.
**Method:** ultracode research workflow (`wf_12536053-d21`) — 20 agents, 5 parallel survey lanes
(GitHub / npm / PyPI / MCP registries / web) → 79 raw candidates → 12 confirmed & enriched → Layer-2
necessity audit of the top 3 by stars. Stars/LOC/app-dependency verified live against the GitHub API
and raw source on 2026-07-07. (One Layer-2 agent — mcpvault — hit the structured-output retry cap;
re-run directly via WebFetch.)
**Status:** ✅ DECIDED (2026-07-07) — user confirmed **Option C**. See the Decision section below.
(Research complete; O.3 records the dependency-veto — no market MCP adopted, no new dependency.)

---

## Layer 1 — Market Survey (12 confirmed candidates, ranked by stars)

| # | Project | ★ | Updated | Lang | ~LOC | Obsidian **app** required? | What it exposes |
|---|---|--:|---|---|--:|:--|---|
| 1 | [MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) | 4039 | 2026-05 | Python | ~1270 | **YES** — app + Local REST API plugin | 15 tools: list/read/batch-read, simple+JsonLogic search, patch/append/put, tags, frontmatter, periodic notes, recent changes |
| 2 | [coddingtonbear/obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api) | 2602 | 2026-06 | TS | ~3400 | **YES** — *is* an in-app plugin | REST + built-in `/mcp/`: CRUD, surgical patch, search, active-file, periodic notes, command palette, tags, open-in-UI |
| 3 | [bitbonsai/mcpvault](https://github.com/bitbonsai/mcpvault) | 1507 | 2026-07 | TS | ~2300 | **no** — file-on-disk | 14 tools: read/write/patch/move/delete, batch read, BM25 search, get/update frontmatter, tags, vault stats |
| 4 | [jacksteamdev/obsidian-mcp-tools](https://github.com/jacksteamdev/obsidian-mcp-tools) | 832 | 2026-05 | TS | ~450+ | **YES** — app + REST plugin | search (simple/Dataview/**smart-semantic**), CRUD, active-file, `execute_template` (Templater). **Archived / read-only** |
| 5 | [StevenStavrakis/obsidian-mcp](https://github.com/StevenStavrakis/obsidian-mcp) | 717 | 2025-06 | TS | ~4500 | **no** — file-on-disk | read/create/edit/delete/move, create-dir, full-text search, tag add/remove/rename, multi-vault |
| 6 | [cyanheads/obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server) | 618 | 2026-06 | TS | ~3–5k | **YES** — app + REST plugin | 14 tools, surgical patch, frontmatter merge, BM25/Omnisearch, command dispatch; Hono transport, JWT/OAuth |
| 7 | [aaronsb/obsidian-mcp-plugin](https://github.com/aaronsb/obsidian-mcp-plugin) | 430 | 2026-07 | TS | ~5–8k | **YES** — in-app plugin (own server) | vault/edit/view, **graph traversal + path-finding**, Dataview, Bases, run commands, web fetch |
| 8 | [iansinnott/obsidian-claude-code-mcp](https://github.com/iansinnott/obsidian-claude-code-mcp) | 313 | 2025-06 | TS | ~2–3k | **YES** — in-app plugin | file view/replace/create/insert, workspace context, `obsidian_api`; WS + HTTP/SSE. No search/tags/dataview |
| 9 | [newtype-01/obsidian-mcp](https://github.com/newtype-01/obsidian-mcp) (`@huangyihe/obsidian-mcp`) | 308 | 2025-08 | TS | ~2400 | **YES** — app + REST plugin (fs fallback) | CRUD, search, move, folder mgmt, heading/block patch, auto-backlink, AI `notes_insight` |
| 10 | [skridlevsky/graphthulhu](https://github.com/skridlevsky/graphthulhu) | 169 | 2026-04 | Go | ~10k | **no** (Obsidian path); Logseq path needs API | ~38 tools: navigate/traverse, full-text + property queries, **graph analysis** (orphans, clusters, connections), write, **decision tracking**, journal |
| 11 | [entanglr/zettelkasten-mcp](https://github.com/entanglr/zettelkasten-mcp) | 159 | 2025-04 | **Python** | ~2900 | **no** — file-on-disk + SQLite index | ~14 tools: CRUD, **7 typed link types + inverses**, search, linked/similar/central/orphan discovery, rebuild-index |
| 12 | [devwhodevs/engraph](https://github.com/devwhodevs/engraph) | 150 | 2026-05 | Rust | ~25–30k | **no** — standalone binary | 25 tools: 5-lane hybrid (semantic+FTS+wikilink-graph+rerank+temporal), write, frontmatter/tags, health, PARA migration, local LLM |

**Market shape.** Two disjoint camps. **App-dependent** (needs the Obsidian *desktop GUI* running
+ the Local REST API plugin, or is itself an in-app plugin): #1, #2, #4, #6, #7, #8, #9 — the
majority, including the two most popular. **File-based** (reads/writes `.md` on disk, no app): #3,
#5, #10, #11, #12 — but every one is thick (2.3k–30k LOC) and, except zettelkasten-mcp, a foreign
runtime (TS/Go/Rust). **No candidate is a thin (<200-line) adapter, and none writes the chimera
K/T/I/D typed-edge schema** — they are generic vault/frontmatter servers.

---

## Layer 2 — Necessity Audit (top 3 by stars)

Baseline for the feature-delta comparison (what Chimera already has / would self-build):
`create_staging_node` (write markdown + YAML frontmatter), `promote_node` (move file), `link_nodes`
(edit frontmatter in place) — plus the existing read surface `search_vault` / `search_vault_attribute`
/ `obsidian_graph_query` / `vault_query` (ripgrep, headless, no app).

### #1 — mcp-obsidian (MarkusPfundstein) · 4039★ · Python · FAIL

- **Q1 Thickness — FAIL.** ~1,250 impl lines (`tools.py` 736 + `obsidian.py` 419 + `server.py` 95),
  15 tool-handler classes. The 95-line server is boilerplate; the real logic is 6× over the
  200-line thin-adapter ceiling. *(verified via raw main-branch line counts)*
- **Q2 App dependency — HARD.** Does **not** touch disk. Every op is an HTTPS call to the Local REST
  API plugin at `127.0.0.1:27124` (`OBSIDIAN_API_KEY`, `verify_ssl=False`). If the desktop app +
  plugin aren't running, the server is dead — it cannot operate headless.
- **Q3 Feature delta over file-write.** simple + JsonLogic search, Dataview DQL, tag search,
  parsed-frontmatter view, heading/block-relative patch, periodic notes, recent-changes.
  *No graph/backlink traversal, no semantic search.* Most of this Chimera already has on-disk.
- **Q4 Cost vs value.** Python deps are lean (`mcp`, `requests`, `dotenv`), MIT, healthy (last push
  2026-05, 473 forks) — but the true price is the **mandatory always-on Obsidian GUI + plugin + API
  key + self-signed TLS**. For a headless GPU paper-mining OS that reads a sibling folder via
  ripgrep, this re-buys search Chimera already has at the cost of a desktop-app runtime. **Not
  justified.**

### #2 — obsidian-local-rest-api (coddingtonbear) · 2602★ · TS · FAIL

- **Q1 Thickness — FAIL (worst).** ~3,400 non-test LOC across 10 files; `src/requestHandler.ts`
  **alone is 1,087 lines** (>5× the ceiling), `main.ts` ~850, `mcpHandler.ts` ~780. A full
  TypeScript Obsidian plugin, not an adapter.
- **Q2 App dependency — HARD (in-process).** It **is** the Local REST API plugin — it imports the
  `obsidian` API and runs *inside* the Obsidian process (HTTPS on `:27124`, now a built-in `/mcp/`).
  Endpoints like `/active/` (open note) and `/commands/` are meaningless without the live app.
- **Q3 Feature delta.** The richest set: surgical section/block/frontmatter patch, JsonLogic +
  Dataview queries, active-file access, periodic notes, command execution, tag listing, binary CRUD,
  open-in-UI. *No semantic search, no LLM edits.*
- **Q4 Cost vs value.** Actively maintained (4.1.3, 2026-06) — but a **Node/TS artifact + ~16 npm
  deps** bolted onto a Python project, functioning **only inside a desktop GUI process**. Not
  embeddable, not vendorable — all-or-nothing behind the app boundary. Most query value duplicates
  chimera-vault. **Not justified.**

### #3 — mcpvault (bitbonsai) · 1507★ · TS · FAIL *(the closest call)*

- **Q1 Thickness — FAIL.** ~2,300 LOC across 7 TS files (`filesystem.ts` ~1,064, `createServer.ts`
  ~440, + frontmatter/search/pathfilter/uri/types). Well over 200 lines.
- **Q2 App dependency — NONE ✅.** The one top-3 candidate that is purely file-on-disk:
  `npx @bitbonsai/mcpvault /path/to/vault`, no Obsidian app, no plugin. This is its real strength.
- **Q3 Feature delta.** BM25-reranked `search_notes`, `get_vault_stats` / `get_notes_info`,
  `manage_tags`, `update_frontmatter`, targeted `patch_note`, YAML-corruption guards,
  path-traversal/symlink security. **But it is a *generic* markdown-vault server** — no
  wikilink/backlink graph, no Dataview, and critically **no awareness of the chimera K/T/I/D
  `graph_edges` schema**. Its delta over Chimera's existing tools is mostly BM25 search (ripgrep
  already suffices for one user).
- **Q4 Cost vs value.** MIT, popular (1.5k★), active (2026-07) — **but** it drags a **Node 18+
  runtime into an all-Python (.venv 3.13) stack**, ships **no versioned releases** (`npx @latest`
  tracks `main` — an unpinnable moving target), and is ~2,300 lines of TypeScript that cannot be
  cheaply vendored across the language boundary. And it does not solve Phase O's actual need (writing
  *typed edges to the chimera schema*). **Not justified.**

**Layer-2 result: 0 / 3 pass.** All three fail thickness; two fail on a hard Obsidian-app
dependency; the file-based one fails on foreign-runtime + unversioned + schema-mismatch.

---

## Recommendation → **Option C — self-build a minimal MCP wrapper over `StagingService`**

Per the decision rules: candidates exist but are all **too thick and/or app-dependent** (and, for
the file-based ones, foreign-runtime and not K/T/I/D-aware) → **Option C**, not B, not A.

**Why not B (adopt a market MCP):**
- The two most popular (mcp-obsidian, obsidian-local-rest-api, 4039★ / 2602★) require the **Obsidian
  desktop GUI running** — a non-starter for a headless GPU pipeline. So do #4, #6, #7, #8, #9.
- The file-based alternatives are all **thick foreign runtimes** — mcpvault/StevenStavrakis (TS
  2.3k–4.5k), graphthulhu (Go ~10k), engraph (Rust ~25k) — violating the thin-adapter red line and
  importing a second language toolchain into a Python project.
- **None writes the chimera K/T/I/D typed-edge schema** — the one thing Phase O actually needs. Every
  candidate is a generic frontmatter/vault editor; the schema-specific logic (typed edges, staging→
  review→promote) would still be ours to build *on top of* whatever we adopt.
- This is textbook `chimera-dependency-veto`: heavy operational/runtime coupling for features Chimera
  largely already has (ripgrep search + graph query, headless, no app).

**Why not A (no MCP at all):** Phase O's purpose is to expose `create_node`/`link_nodes` so the vault
graph can be populated (the N.B unblocker). A "no write surface" outcome would abandon Phase O. The
O.0 audit already found `StagingService.create_staging_node` is ~75% of `create_node`, sitting
**orphaned** (its retired astrocyte consumers were removed in Phase M). Wiring it is small.

**What Option C is (already scoped by O.0):** a thin (~<200-line) Python `@mcp.tool` layer in
`chimera-vault` (whose CLAUDE.md mandate already grants "write access only for staging-area
operations") delegating to the existing `StagingService` — add K-type support, reconcile the typed-
edge vocabulary to one canonical schema, expose `create_node` + `link_nodes`. No new dependency, no
foreign runtime, no desktop-app requirement, writes the chimera schema natively.

**Prior art worth borrowing (not adopting):** [zettelkasten-mcp](https://github.com/entanglr/zettelkasten-mcp)
(#11) is the only Python, file-based, *typed-link-aware* server (7 semantic link types + inverses,
graph discovery). It is ~2,900 LOC on its own schema/SQLite index — too much to adopt — but its
typed-link API and orphan/hub discovery are a useful design reference for O.2 `link_nodes` and the
eventual N.B `deep_recall`.

---

## Decision (2026-07-07) — Phase O.3

**Option C confirmed by the user.** No market Obsidian MCP is adopted; no new dependency; `.mcp.json`
stays two servers (chimera-vault + chimera-papers). The "minimal file-write tool" the phase spec
anticipated already exists as the O.1b + O.2 write surface over `StagingService`:

- **O.1b** `create_node` — K/T/I/D staging nodes with typed edges (shipped; HSC 1).
- **O.2a/O.2b** `link_nodes` + `apply_link_patch` — reviewed typed-edge links onto existing nodes
  (shipped; HSC 2).

`chimera-dependency-veto` recorded: adopting any surveyed candidate would import a desktop-app
dependency or a thick foreign runtime (TS/Go/Rust, 2.3k–30k LOC) to buy generic frontmatter editing
Chimera already has via ripgrep + the K/T/I/D-native tools above — and none of them speaks the chimera
schema. The veto stands.

**Design reference borrowed (not adopted):** `zettelkasten-mcp`'s typed-link API informed O.2's edge
model; its code was not used.

**O.3 residual:** the phase seal (HSC 3 — ≥20 nodes with typed edges) via `scripts/seed_hsc3.py`. This
audit's research obligation is closed.

---

## Appendix — provenance

- Workflow run `wf_12536053-d21`; 79 raw candidates surveyed, 12 confirmed, 3 deep-audited.
- Star counts, LOC, and app-dependency verified against the GitHub API / raw source on 2026-07-07.
- One deep-dive (mcpvault) re-run directly after its workflow agent hit the structured-output cap;
  file-based/no-app and ~2,300 LOC confirmed via the repo page + install docs.
- This document is research input for the O.3 decision. No code changed.
