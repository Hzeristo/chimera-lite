# Phase Audit: Phase O — Exocortex Write Surface

**Scope:** Read-only audit prerequisite for `batch_planning` of Phase O (tools to create T/I/D
nodes, fill typed edges, and integrate with Obsidian — the write surface that unblocks the deferred
Phase N.B by populating the vault's typed-edge graph).
**Output location:** `docs/audits/O.0.md` (named for the O.0 sprint that authors it).
**Date:** 2026-07-07
**Mode:** Read-only w.r.t. source — no fix proposals, no code changes. The one write is this report.
**Q-list:** approved by user (2026-07-07), with the note that **Q2 is load-bearing above all** —
whether O.1's `create_node` is already built. In-scope surface is small (staging service + node
writers + templates + `.mcp.json`); read in full, no scout fan-out needed.

---

## Files read

| Path | Lines | Notes |
|---|---|---|
| `docs/phases/phase-O.md` | 1–44 | full — mission, 4 sprints (O.0–O.3), 3 sealing conditions, design decisions |
| `mcp-servers/chimera-papers/staging_service.py` | 1–76 | full — **`create_staging_node` / `promote_node` / `reject_node`** (the Q2 crux) |
| `mcp-servers/chimera-papers/ports/vault/vault_note_writer.py` | 1–75 | full — `write_knowledge_node` / `write_deep_read_node` (K + Deep_Read only) |
| `mcp-servers/chimera-papers/server.py` | 1–94 | full — 3 tools (`arxiv_miner`, `daily_paper_pipeline`, `check_task_status`); StagingService not registered |
| `mcp-servers/chimera-vault/server.py` | 1–126 | full (N.B.0) — 5 read tools; puts chimera-papers on `sys.path` (:15-17) |
| `mcp-servers/chimera-papers/core/config.py` | :138 | grep — `staging_dir` default = `<repo>/docs/staging` |
| `prompts/obsidian_tpl/{thought,insight,decision}_node.j2` | full | T/I/D rich templates — **authored but wired to no writer** |
| `prompts/obsidian_tpl/{knowledge,deep_read}_node.j2` | ref | the only two the pipeline renders (`vault_note_writer.py:34,59`) |
| `<vault>/templates/Tpl_{knowledge,thought,insight,decision}.md` | grep (N.B.0) | user-synced edge vocabulary (diverges from code — see Q4) |
| `.mcp.json` | 1–18 | full — only chimera-vault + chimera-papers; **no Obsidian MCP** |
| `CLAUDE.md` | refs | chimera-vault "write access only for staging-area operations"; never auto-promote `docs/staging/` |
| `docs/FINAL_CONTRACT/V.A-final-contract.md` | 14, 30–42 | full (N.B.0) — StagingService (V.A.3), astrocyte staging consumers (V.A.4, retired), `NODE_ONTOLOGY.md` ref |
| Glob `docs/ARCHITECTURE/**` | — | **empty** — `NODE_ONTOLOGY.md` + `STAGING_PROTOCOL.md` never migrated |
| Grep `StagingService`/`create_staging_node` (repo `*.py`) | — | referenced only in `staging_service.py` + `config.py` → **orphaned** |

---

## Findings

| Q# | Driving sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| **Q2** | O.1 | **⚠️ Is O.1's `create_node` already built?** | **~75–80% YES — and orphaned.** `StagingService.create_staging_node(type, title, body, edges=None) -> Path` is O.1's exact signature: it writes typed-edge frontmatter to `docs/staging/` and returns a staging path (matching the design's "returns staging path" decision). **Gaps:** (a) it rejects `type="knowledge"` — `_TYPE_DEST` is T/I/D only; (b) it is **not MCP-exposed** (a plain class, wired to nothing); (c) the edge merge is closed-vocabulary (`if k in graph_edges` silently drops unknown edge keys). So O.1 collapses from "build" to **wire + add K + reconcile edges**. | `staging_service.py:11, 26-54` (K-reject `:33-35`, merge `:36-40`, returns path `:51-54`); Grep → orphaned | **High** (scope-defining) |
| Q1 | O.0 | What write ops exist; any MCP-exposed? | Three writers exist, **none exposed as a create/link tool.** `VaultNoteWriter.write_knowledge_node`/`write_deep_read_node` (K + Deep_Read, called *inside* the long-running pipeline); `StagingService.create/promote/reject` (T/I/D staging, **unwired**). chimera-papers exposes only miner/pipeline/status; chimera-vault only 5 read tools. | `vault_note_writer.py:31-74`; `staging_service.py:26-75`; `chimera-papers/server.py:42-89`; `chimera-vault/server.py:51-121` | Low |
| Q3 | O.1 | T/I/D frontmatter renderers? | **Two divergent representations.** (1) `StagingService` builds a *minimal* frontmatter dict in Python (`type/status/title/created_at/tags/graph_edges` + body). (2) `obsidian_tpl/{thought,insight,decision}_node.j2` are *richer* (thought→`lesson`+Observation/Log; insight→`actionable`+`status: cross_verified`; decision→`rationale`+Abandoned) — but **wired to no writer** (`VaultNoteWriter` renders only `knowledge`/`deep_read`). Their edge vocab **agrees** with `StagingService._TYPE_EDGES`. O.1 must choose minimal-dict vs richer-`.j2`. | `staging_service.py:41-52`; `thought_node.j2:7-11`; `insight_node.j2:7-12`; `decision_node.j2:7-11`; `vault_note_writer.py:34,59` | Med |
| Q4 | O.1 | Single typed-edge schema authority per K/T/I/D? | **No — two families disagree and the authority doc is missing.** The **code family** (`StagingService._TYPE_EDGES` + `obsidian_tpl/*.j2`) is internally consistent but **diverges from the user-synced vault `Tpl_*.md`**: e.g. decision → code `depends_on` vs Tpl `derives_from`+`drives_decision`; thought → code lacks `promoted_to_insight`; insight → code `verified_with` vs Tpl `evidence_base`. `NODE_ONTOLOGY.md` (V.A's authority) **never migrated**. Must reconcile before O.1 hardcodes `_TYPE_EDGES`, else `create_node` emits edges the user's Obsidian templates don't recognize. | `staging_service.py:12-16`; `*_node.j2:7-*`; `Tpl_*.md` (N.B.0 Q3); Glob `NODE_ONTOLOGY*`→none; `V.A-final-contract.md:14` | **High** |
| **Q5** | O.2 | **⚠️ `link_nodes` in-place frontmatter edit — primitive or net-new?** | **Net-new, and it writes into live vault nodes.** No method edits an existing node's frontmatter in place; `promote_node` reads→rewrites→moves *staging→vault* (a promotion, not an edit). Its read/parse/dump pattern (`split("---",2)` → `yaml.safe_load` → `yaml.dump`) is reusable, but `link_nodes` is genuinely new. It targets **user-territory files** (CLAUDE.md cautions vault `templates/` are user-synced) → design must decide: edit-in-place vs stage-a-patch-for-review. | `staging_service.py:56-72` (promote pattern); no in-place editor; `CLAUDE.md` vault-write rules | **High** |
| Q6 | O.2 | How are link endpoints resolved? | Reusable resolvers exist: `VaultReadAdapter` stem→path map (`stem_to_paths`/`first_path_for_stem`) and `find_authenticated_paper` (by arxiv_id in filename). `link_nodes` can resolve `from`/`to` by note stem or arxiv_id via these. | `vault_read_adapter.py:472-479, 338-395` | Low |
| **Q7** | O.3 | **⚠️ Obsidian MCP — adapt or build?** | **Build (trivially) — the market-MCP branch is empty.** `.mcp.json` registers only chimera-vault + chimera-papers; no `obsidian` dependency anywhere (`*.toml/json` grep → none). O.3's "minimal file-write" fallback **already exists** — `StagingService`/`VaultNoteWriter` write markdown directly. Adopting a market Obsidian MCP would be a **new external dependency** (a `chimera-dependency-veto` decision), and the thin file-write path already satisfies the spec. O.3 is likely a near-no-op / veto confirmation. | `.mcp.json:2-17`; Grep `obsidian` (toml/json)→none; `staging_service.py:51-53` | Med |
| Q8 | all | Which server hosts the tools; staging-review compliance; `STAGING_PROTOCOL.md`? | **chimera-vault is the sanctioned home** — CLAUDE.md grants it "write access only for staging-area operations," and it already imports the chimera-papers domain package (`sys.path`), so it can host `create_node`/`link_nodes` over `StagingService`. The flow honors the red line: `create` → `docs/staging/` (`config.py:138`) → user review → `promote_node` (never auto-promote). **`STAGING_PROTOCOL.md` (+ `NODE_ONTOLOGY.md`) never migrated** — the protocol lives only in the V.A contract + the code. | `CLAUDE.md`; `chimera-vault/server.py:15-17`; `config.py:138`; `staging_service.py:56-75`; Glob `docs/ARCHITECTURE/`→empty | Med |

---

## Cross-references discovered

- **`StagingService._TYPE_EDGES` was derived from the `obsidian_tpl/*.j2` frontmatter** — the two
  agree edge-for-edge (thought/insight/decision). Evidence: `staging_service.py:12-16` vs
  `{thought,insight,decision}_node.j2:7-*`.
- **The staging flow already satisfies "never auto-promote"** — `create` targets `docs/staging/`
  (`config.py:138`), promotion is a separate explicit call (`staging_service.py:56`). Matches
  CLAUDE.md ("Never auto-promote `docs/staging/` candidates").
- **Phase O's HSC 3 restates the N.B.0 gate threshold** (≥ 20 nodes with typed edges), closing the
  loop: O exists to satisfy the exact metric that deferred N.B. Evidence: `phase-O.md:29-30`;
  `docs/audits/N.B.0.md` Q4.

---

## Notable cross-findings (no fix proposals — flagging for planning)

1. **O.1 is ~75–80% pre-built but orphaned.** `StagingService.create_staging_node` is `create_node`
   minus K-type, minus MCP exposure, minus edge-vocab reconciliation. Its V.A.4 consumers (astrocyte
   HTTP `staging_routes` + Tauri + Svelte) were **retired in Phase M**, leaving live-but-unreachable
   code. O.1 should be scoped as **wire + extend**, not greenfield. Evidence: `staging_service.py:26-54`;
   `V.A-final-contract.md:38-42`; Grep (orphaned).

2. **Two typed-edge schema families disagree, and the authority doc is gone** (highest-value decision).
   The code/`.j2` family is internally consistent but diverges from the user's vault `Tpl_*.md`, and
   `NODE_ONTOLOGY.md` never migrated. If O.1 hardcodes the code family, `create_node` will emit edges
   the user's Obsidian templates don't render (and vice-versa). **Batch planning must pick one canonical
   K/T/I/D edge set** (and probably re-author `NODE_ONTOLOGY.md` in-repo) before O.1. Evidence:
   `staging_service.py:12-16` vs `Tpl_*.md`; Glob `NODE_ONTOLOGY*`→none.

3. **`link_nodes` (O.2) is the only genuinely net-new capability, and it writes into live vault nodes.**
   Editing an existing note's frontmatter in place touches user-synced territory. Design must choose
   **edit-in-place vs stage-a-patch-for-review** — the safer, red-line-consistent option is to route
   edits through staging like node creation. Evidence: `staging_service.py:56-72`; `CLAUDE.md` vault rules.

4. **O.3's market-MCP branch is empty; the file-write path already exists.** No Obsidian MCP is
   registered or depended on; `StagingService`/`VaultNoteWriter` already *are* the "minimal file-write
   tool." Pursuing a market Obsidian MCP is a **dependency-veto** call against an existing thin path —
   O.3 may reduce to "confirm veto; no new dependency." Evidence: `.mcp.json:2-17`; Grep `obsidian`→none.

5. **Rich T/I/D `.j2` templates exist but are unwired** (`lesson`/`actionable`/`rationale` + section
   scaffolds). O.1's minimal-vs-rich choice (cross-finding, ties Q3): `StagingService`'s Python-dict
   frontmatter vs rendering the `.j2` for better-structured nodes (which would also unify the K path,
   already `.j2`-rendered). Evidence: `{thought,insight,decision}_node.j2`; `vault_note_writer.py:34,59`.

---

## Audit complete

- 8 questions answered (Q2 = the load-bearing crux, per user)
- ~35 `file:line` references
- 3 cross-references
- 5 notable cross-findings

**Suggested next — `batch_planning` IS unblocked** (unlike N.B.0, no gate fails; the write surface
largely exists). Planning must resolve four decisions the audit surfaced: **(1)** scope O.1 as
*wire + add-K + edge-reconcile* over the orphaned `StagingService`, not greenfield (cross-finding 1);
**(2)** pick the canonical K/T/I/D edge schema and re-home `NODE_ONTOLOGY.md` (cross-finding 2);
**(3)** decide `link_nodes` edit-in-place vs stage-a-patch (cross-finding 3); **(4)** confirm O.3 as
a dependency-veto no-op vs a real Obsidian-MCP integration (cross-finding 4). Plus the minimal-vs-rich
node template choice (cross-finding 5).

---

## Addendum (2026-07-07): Decision-2 mod-time probe

Per the user's Phase-O pre-planning **Decision 2** (canonical typed-edge schema = newer-by-mod-time
wins; fallback to manual review if the two families are within 1 week), the probe was run at
batch-planning time:

| Family | File | LastWriteTime |
|---|---|---|
| Code (`.j2`) | `prompts/obsidian_tpl/thought_node.j2` | 2026-06-15 02:20:23 |
| Code (`.j2`) | `prompts/obsidian_tpl/insight_node.j2` | 2026-06-15 02:20:27 |
| Code (`.j2`) | `prompts/obsidian_tpl/decision_node.j2` | 2026-06-15 02:20:28 |
| Code (`.j2`) | `prompts/obsidian_tpl/knowledge_node.j2` | 2026-06-15 08:28:40 |
| Vault (`Tpl`) | `<vault>/templates/Tpl_thought.md` | 2026-06-15 01:54:00 |
| Vault (`Tpl`) | `<vault>/templates/Tpl_insight.md` | 2026-06-15 01:54:06 |
| Vault (`Tpl`) | `<vault>/templates/Tpl_decision.md` | 2026-06-15 01:54:12 |
| Vault (`Tpl`) | `<vault>/templates/Tpl_knowledge.md` | 2026-06-15 01:52:50 |

**Result: INCONCLUSIVE → manual review (the fallback triggers).** Both families were last written
on the **same day (2026-06-15)**, T/I/D within ~26 minutes of each other. That delta is far inside
Decision 2's "within 1 week → manual review" window, so mod-time cannot arbitrate. The `.j2` code
family is marginally newer, but not decisively so.

**Sync direction: none.** The `.j2` (Jinja render templates) and the vault `Tpl_*.md` (Obsidian
note templates) are not a source→copy pair — they are two independent representations of the same
schema that happen to disagree (Q4). There is no repo-side source of `Tpl_*.md`, so the comparison
reports no stable sync direction. Reconciliation must therefore be **manual, into one authored
authority** — scoped as sprint **O.1a** in `docs/plans/Phase-O-batch.md`.

---

*Generated by chimera-sprint-discipline phase_audit mode.*
