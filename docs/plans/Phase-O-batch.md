# Batch Plan: Phase O — Exocortex Write Surface

**Output location:** `docs/plans/Phase-O-batch.md`
**Audit reference:** `docs/audits/O.0.md` (date: 2026-07-07; + Decision-2 addendum, same date)
**Phase doc:** `docs/phases/phase-O.md` (sparse manifest — distinct from this batch plan)
**Driving frictions:**
- `docs/audits/N.B.0.md` Q4 — vault typed-edge graph is empty (0 nodes with populated `graph_edges`);
  Phase N.B (deep_recall) deferred until a graph exists to traverse.
- No tools to create T/I/D nodes or fill typed edges; PaperMiner writes only K Nodes (`phase-O.md:5-8`).
- *These are phase-declared frictions with no `docs/logs/` file; treated as user-authorized anticipatory
  work per the phase spec + the pre-planning decisions below (same convention as Phase N.A).*

This document is a single unit. User approves the whole sequence or rejects the whole sequence.
After approval, hand off to `chimera-code-taste` batch_execution mode.

---

## Pre-planning decisions (confirmed with user, 2026-07-07)

| # | Decision | Effect on plan |
|---|---|---|
| 1 | **O.1 = wire the orphaned `StagingService` + extend, not greenfield.** Gaps: (a) add K-type support, (b) MCP tool registration, (c) open the closed edge merge. ~50 lines Python. | Resolves cross-finding #1. O.1 splits into **O.1a** (schema authority, doc) + **O.1b** (wire + K + open-merge, code). `create_staging_node` (`staging_service.py:26-54`) is ~75-80% of `create_node` already. |
| 2 | **Canonical typed-edge schema = newer-by-mod-time; fallback to manual review if within 1 week.** Probe run in O.0 addendum; reports sync direction. | Resolves cross-finding #2. **Probe result: INCONCLUSIVE** (both families last written 2026-06-15, within ~26 min → fallback) → **manual reconciliation** into one authored authority `docs/ARCHITECTURE/NODE_ONTOLOGY.md`. Scoped as **O.1a**. |
| 3 | **`link_nodes` = Option B, stage-a-patch.** `link_nodes` writes a staging patch → user reviews → `apply_link_patch` merges it into the live node. | Resolves cross-finding #3. O.2 splits into **O.2a** (`link_nodes` stages a patch, no live write) + **O.2b** (`apply_link_patch`, the reviewed in-place merge — the only live-vault write in the phase). Honors the staging red line. |
| 4 | **Obsidian MCP = Option C (self-build thin wrapper).** DR audit (`obsidian-mcp-necessity.md`, `d50cf81`): 12 candidates, 0/3 pass Layer 2 — all app-dependent or thick foreign runtimes; none speaks K/T/I/D. No new dependency. | Resolves cross-finding #4. **O.3 reduces to a dependency-veto no-op + the phase-seal seed** — the "minimal file-write tool" the phase spec anticipates already IS O.1b + O.2 (`StagingService` / `VaultNoteWriter`). `.mcp.json` stays 2 servers. |
| — | **Design borrow (non-adoption):** read `zettelkasten-mcp`'s `link_nodes` for the in-place frontmatter YAML-merge pattern. Reference only — do not adopt its code. | Informs **O.2b**'s merge. Its pattern also already exists in-repo via `promote_node` (`staging_service.py:56-72`, split→`safe_load`→`dump`). |

### Planner reconciliation (read before approving)

1. **Risk rubric vs blast radius.** The template's risk levels are code-change-sized. Two sprints
   here write to `docs/staging/` **only** (contained blast radius) yet cross the line-count threshold —
   I mark them by line count but annotate the true blast radius. The one sprint that mutates a **live
   vault node** in place (**O.2b**) is 🔴 on merit, not just line count. A 🔴 here means "gate approval
   before execution," a 🟡 means "review behavior at execution."

2. **Decision-2 probe is inconclusive by design.** Mod-time cannot arbitrate the schema (same-day edits,
   O.0 addendum). This is not a blocker — it *promotes* O.1a from "pick the newer file" to "author one
   reconciled authority." The canonical vocabulary must be **user-ratified** (it is what the user's
   Obsidian vault renders) before O.1b hardcodes it. Re-plan trigger: if the user rejects the O.1a vocab.

3. **Host = chimera-vault; logic stays in chimera-papers.** All three tools register on
   `chimera-vault/server.py` (CLAUDE.md grants it "write access only for staging-area operations"; it
   already `sys.path`-imports the chimera-papers domain, `server.py:15-17`). The domain logic extends
   `chimera-papers/staging_service.py` (its home). Server-side tool bodies are **thin dispatchers**
   (lazy-import → call → return) so `server.py` stays under the <200-line thin-adapter red line
   (currently 126 lines; +~36 of dispatch ≈ 162).

4. **Total new code ≈ 110 lines** across O.1b + O.2a + O.2b — inside the user's "<150 likely" bound.
   O.1a and O.3 are doc/verify-only.

5. **Node-template choice (cross-finding #5): minimal-dict, not rich-`.j2`.** O.1b reuses
   `StagingService`'s Python-dict frontmatter (already works, already returns a staging path). Rendering
   the richer unwired `obsidian_tpl/*.j2` (lesson/actionable/rationale scaffolds) is deferred — it is not
   required for HSC 1 and would widen the thin scope. Flagged, not adopted.

---

## Sprint Sequence

```
O.0 (audit ✓, + Decision-2 addendum ✓)
   │
   ▼
O.1a  NODE_ONTOLOGY.md — reconcile + author the single K/T/I/D edge authority   (doc; user-ratified)
   │
   ▼
O.1b  create_node  — wire StagingService + add K + open edge merge  (code, staging-only write)
   │
   ▼
O.2a  link_nodes  — resolve endpoints, write a staging patch  (code, staging-only write)
   │
   ▼
O.2b  apply_link_patch  — reviewed in-place frontmatter merge  (code, THE live-vault write)
   │
   ▼
O.3   Obsidian-MCP veto confirmation + HSC-3 seal seed  (doc + verify)
   │
   ▼
seal (chimera-sprint-discipline phase_review)  →  unblocks Phase N.B
```

- **Strictly sequential.** O.1a defines the vocabulary O.1b emits; O.1b's `create_node` produces the
  nodes O.2 links; O.2b applies what O.2a stages; O.3 seals using all of the above. No parallel-eligible
  pair (unlike N.A) — each sprint consumes its predecessor's output.
- **Split analysis (process step 3):** O.1 → O.1a (doc authority) + O.1b (code) — different work modes,
  and O.1b cannot emit correct edges until O.1a picks the vocab. O.2 → O.2a (stage, safe) + O.2b
  (apply-to-live-vault, risky) — isolates the single live-write into its own gated sprint, mirroring
  Decision 3's stage-a-patch separation. Each sprint touches ≤3 files / ≤~50 lines.

---

## Sprint O.1a: NODE_ONTOLOGY.md — the single K/T/I/D typed-edge authority

**Anticipatory justification:** Two typed-edge vocabularies disagree (code family vs user-synced vault
`Tpl_*.md`) and the V.A authority doc `NODE_ONTOLOGY.md` never migrated (`docs/ARCHITECTURE/` is empty).
The Decision-2 mod-time probe was inconclusive (same-day edits). O.1b must not hardcode `_TYPE_EDGES`
until one canonical set is authored and user-ratified, else `create_node` emits edges the user's
Obsidian templates don't render.

**Predecessor assumptions:**
- None — first sprint. **Produces** `docs/ARCHITECTURE/NODE_ONTOLOGY.md`, the authority O.1b, O.2a,
  and O.2b all validate edges against. Re-plan trigger: if the user rejects the reconciled vocabulary.

**Risk level:** 🟡 MED (doc-only, but **decision-bearing**) — the canonical vocab defines what the
user's vault renders; it needs user sign-off before any code emits it. No code risk.

### 目标
Reconcile the two divergent K/T/I/D typed-edge vocabularies into one authored authority doc
`docs/ARCHITECTURE/NODE_ONTOLOGY.md`, resolving every per-key divergence with a stated rule.

### 设计要点(audit-derived)
- **Reconcile two families, do not silently pick one.** Code family (`staging_service.py:12-16` +
  `obsidian_tpl/*.j2`, internally consistent) vs user-synced vault `Tpl_*.md`. Known divergences
  (audit Q4): decision → code `depends_on` vs Tpl `derives_from`+`drives_decision`; thought → code
  lacks `promoted_to_insight`; insight → code `verified_with` vs Tpl `evidence_base`. Each resolved
  with an explicit rule (adopt / rename / union / drop) + reason. Audit ref: `O.0.md` Q4, cross-finding #2.
- **Add K's typed edges — the N.B.0 root cause.** `StagingService` rejects `type="knowledge"`
  (`staging_service.py:33-35`) and `knowledge_node.j2` emits **no** typed edges — this is *why* the
  live graph is empty (N.B.0 Q4). The ontology must define K's canonical edge keys so O.1b can populate
  them. Audit ref: `O.0.md` Q2; `N.B.0.md` Q4.
- **Re-home the authority doc.** Author into `docs/ARCHITECTURE/NODE_ONTOLOGY.md` (empty dir; the V.A
  `NODE_ONTOLOGY.md` never migrated). This becomes the single source O.1b's `_TYPE_EDGES` mirrors.
  Audit ref: `O.0.md` files-read (`docs/ARCHITECTURE/**` empty), Q8; `V.A-final-contract.md:14`.

### 任务范围
1. `docs/ARCHITECTURE/NODE_ONTOLOGY.md` (~new doc) — the 4 node types (K/T/I/D), each with its single
   canonical `graph_edges` key set + a resolution note per divergent key. Audit ref: Q2, Q4.

### 验收
- Doc defines all **4** types (K/T/I/D) with an explicit, single canonical `graph_edges` key set each.
- Every edge key is cross-checked against **both** `staging_service.py:12-16` **and** the vault
  `Tpl_*.md`; each divergence carries a stated resolution rule + reason.
- K has ≥1 canonical typed-edge key defined (closing the N.B.0 root cause).
- User ratifies the vocabulary before O.1b executes (recorded in the sprint summary).

### 红线
- ❌ Do NOT edit the vault `templates/` — user-synced; the authority lives repo-side only (phase-wide).
- ❌ Do NOT silently adopt one family — every divergence is explicitly resolved with a reason.
- ❌ No `.py` / no MCP changes in this sprint — doc-only.
- ❌ 不进行机会主义重构。

### 输出位置
- 文档: `docs/ARCHITECTURE/NODE_ONTOLOGY.md`
- CLAUDE.md / ROADMAP sprint status: 推迟至 seal 统一更新。

---

## Sprint O.1b: create_node — wire StagingService + add K + open edge merge

**Friction reference:** N.B.0 Q4 (empty graph) + `phase-O.md:5-8` (no T/I/D creation tool).

**Predecessor assumptions:**
- O.1a done — `NODE_ONTOLOGY.md` exists and its vocabulary is user-ratified. `_TYPE_EDGES` mirrors it.
  Re-plan trigger: if the ratified vocab differs materially from the code family (changes the K/T/I/D
  edge keys O.1b hardcodes).

**Risk level:** 🔴 HIGH by rubric (~40 new lines across 2 files) — **but contained blast radius:**
writes only to `docs/staging/`, never the live vault. Requires per-sprint approval; the risk is
correctness of the schema, not vault safety.

### 目标
Expose `StagingService.create_staging_node` as MCP tool `create_node(type, title, body, edges)` on
chimera-vault, add K-type support, and open the edge merge to the O.1a canonical vocabulary.

### 设计要点(audit-derived)
- **Wire, don't rebuild.** `create_staging_node(type, title, body, edges=None) -> Path` is already
  O.1's signature: typed-edge frontmatter → `docs/staging/`, returns a staging path. Audit ref:
  `O.0.md` Q2 (`staging_service.py:26-54`), cross-finding #1.
- **Add K.** Extend `_TYPE_DEST` + `_TYPE_EDGES` with `knowledge` (dest + K's O.1a edge keys); remove
  the K-reject at `staging_service.py:33-35`. Audit ref: `O.0.md` Q2.
- **Open the merge.** The current merge silently drops unknown keys (`if k in graph_edges`,
  `staging_service.py:36-40`). Align the accepted key set to O.1a so no valid edge is dropped, and
  reject truly-invalid keys loudly. Audit ref: `O.0.md` Q2.
- **Host on chimera-vault; thin dispatcher.** Register `@mcp.tool create_node` on
  `chimera-vault/server.py` (sanctioned staging-write host; already imports the chimera-papers domain,
  `server.py:15-17`). The tool body lazy-imports `StagingService`, calls it, returns the staging path —
  no domain logic in `server.py`. Audit ref: `O.0.md` Q8.
- **Returns staging path; never auto-promote.** `docs/staging/` target (`config.py:138`); promotion
  stays a separate explicit `promote_node` call. Matches the design decision + CLAUDE.md red line.
- **Minimal-dict frontmatter** (reconciliation #5) — reuse `StagingService`'s existing Python-dict
  frontmatter; do not wire the rich `.j2` templates (deferred).

### 任务范围
1. `mcp-servers/chimera-papers/staging_service.py` (~15 lines) — add `knowledge` to `_TYPE_DEST` +
   `_TYPE_EDGES`; open the edge merge to the O.1a key set. Audit ref: Q2.
2. `mcp-servers/chimera-vault/server.py` (~12 lines) — register `create_node` thin dispatcher →
   `StagingService.create_staging_node`, returns staging path. Audit ref: Q8.
3. `tests/` (~15 lines) — `create_node` writes K/T/I/D to `docs/staging/` with typed edges, returns
   the path, promotes nothing.

### 验收
- `create_node(type=knowledge|thought|insight|decision, …)` writes a staging file with typed
  `graph_edges` for **all 4** types — verify by reading a created staging file.
- A valid edge key from O.1a is preserved (not silently dropped); an invalid key is rejected loudly.
- Returns the `docs/staging/` path; nothing lands in the vault — verify the vault is unchanged.
- `create_node` is visible as a chimera-vault MCP tool.

### 红线
- ❌ **Never auto-promote** — `create_node` writes ONLY to `docs/staging/` (phase-wide).
- ❌ `server.py` stays a **thin adapter** (<200 lines; the tool body is a dispatcher, logic in the domain module).
- ❌ Do NOT touch the poll-model `TaskService` or the miner/daily-pipeline (out of scope).
- ❌ Emit only O.1a `NODE_ONTOLOGY.md` edge keys — no ad-hoc vocabulary.
- ❌ 不进行机会主义重构。

### 输出位置
- 代码: `mcp-servers/chimera-papers/staging_service.py`, `mcp-servers/chimera-vault/server.py`
- 测试: `tests/`
- 文档: 推迟至 O.3 / seal 统一更新。

---

## Sprint O.2a: link_nodes — resolve endpoints, stage a patch

**Friction reference:** `phase-O.md:22` (fill `derives_from` / `synthesizes` on existing nodes) — the
edges N.B's deep_recall would traverse.

**Predecessor assumptions:**
- O.1a done — edge-type validation uses `NODE_ONTOLOGY.md`. O.1b done — `create_node` produces the
  nodes being linked (and establishes the chimera-vault tool-dispatch pattern O.2a reuses).

**Risk level:** 🟡 MED (~30 lines, tests) — writes only a patch to `docs/staging/`; the target vault
node is untouched in this sprint.

### 目标
Add MCP tool `link_nodes(from, to, edge_type)` that resolves both endpoints, validates the edge type,
and writes a **staging patch file** describing the edge addition — no live vault write (Decision 3, stage half).

### 设计要点(audit-derived)
- **Reuse the endpoint resolvers.** `vault_read_adapter.py` `stem_to_paths` / `first_path_for_stem`
  (`:472-479`) + `find_authenticated_paper` (by arxiv_id, `:338-395`) resolve `from` / `to` by note
  stem or arxiv_id. Do not reimplement resolution. Audit ref: `O.0.md` Q6.
- **Validate `edge_type` against O.1a.** The edge must be a canonical key for the *from*-node's type
  (per `NODE_ONTOLOGY.md`); reject otherwise. Audit ref: `O.0.md` Q4; O.1a.
- **Stage a patch, don't write the node.** Write a small patch descriptor (target node path + edge_type
  + resolved target) to `docs/staging/`. Honors the "all vault writes go through review" red line.
  Audit ref: `O.0.md` Q5, cross-finding #3; Decision 3.

### 任务范围
1. `mcp-servers/chimera-papers/staging_service.py` (~18 lines) — `link_nodes` logic: resolve endpoints,
   validate edge_type, write patch to `docs/staging/`. Reuses `VaultReadAdapter` resolvers. Audit ref: Q5, Q6.
2. `mcp-servers/chimera-vault/server.py` (~12 lines) — register `link_nodes` thin dispatcher.
3. `tests/` (~12 lines) — `link_nodes` writes a patch (target node UNCHANGED); rejects unknown
   `edge_type` and unresolvable endpoints.

### 验收
- `link_nodes(from, to, edge_type)` produces a patch file in `docs/staging/`; the target vault node is
  **byte-for-byte unchanged** — verify by re-reading the node.
- `edge_type` is validated against the from-node type's canonical edges (O.1a); an invalid edge is rejected.
- Endpoints resolve by note stem and by arxiv_id.

### 红线
- ❌ **No live vault write in this sprint** — patch to `docs/staging/` only (phase-wide staging red line).
- ❌ Reuse `vault_read_adapter` resolvers — do not reimplement endpoint resolution.
- ❌ `edge_type` restricted to the O.1a vocabulary.
- ❌ 不进行机会主义重构。

### 输出位置
- 代码: `mcp-servers/chimera-papers/staging_service.py`, `mcp-servers/chimera-vault/server.py`
- 测试: `tests/`
- 文档: 推迟至 O.3 / seal。

---

## Sprint O.2b: apply_link_patch — the reviewed in-place frontmatter merge

**Friction reference:** `phase-O.md:22` (edges land on existing nodes) — completes the stage-a-patch loop.

**Predecessor assumptions:**
- O.2a done — a reviewed patch descriptor exists in `docs/staging/`. `apply_link_patch` consumes it.
  Re-plan trigger: if O.2a's patch format changes.

**Risk level:** 🔴 HIGH — **the only sprint that mutates a live vault node in place.** Requires
explicit per-sprint approval before execution. Blast radius = one content node's frontmatter.

### 目标
Add MCP tool `apply_link_patch(patch_path)` that, after user review of the O.2a patch, performs the
in-place frontmatter YAML merge appending the edge into the target vault node (Decision 3, apply half).

### 设计要点(audit-derived)
- **Reuse the `promote_node` parse/dump pattern.** `split("---", 2)` → `yaml.safe_load` → mutate →
  `yaml.dump`, exactly as promotion rewrites frontmatter (`staging_service.py:56-72`). The in-place
  merge is the one genuinely net-new capability (audit Q5) — no existing method edits a live node in place.
- **Design borrow (reference only):** `zettelkasten-mcp`'s `link_nodes` frontmatter-merge for the
  append pattern. Do not adopt its code. (Its shape already matches the in-repo `promote_node` pattern.)
- **Idempotent + non-destructive.** Appending an edge already present is a no-op (no dup); all non-edge
  frontmatter keys and the note body are preserved verbatim (parse/dump must not reformat content).
- **Review-gated.** Applies ONLY a patch that already exists in `docs/staging/` — never a direct
  arbitrary vault edit. This is the "promote"-analog for edges (the reviewed terminal staging op).

### 任务范围
1. `mcp-servers/chimera-papers/staging_service.py` (~30 lines) — `apply_link_patch`: read patch, load
   target node frontmatter, append edge idempotently, write back. Reuses promote parse/dump (`:56-72`). Audit ref: Q5.
2. `mcp-servers/chimera-vault/server.py` (~10 lines) — register `apply_link_patch` thin dispatcher.
3. `tests/` (~15 lines) — merge appends the edge to the target's `graph_edges`; re-apply is a no-op;
   body + other frontmatter untouched.

### 验收
- After `apply_link_patch`, the target node's `graph_edges` contains the new edge — verify by re-reading the node.
- Re-applying the same patch is a **no-op** (idempotent, no duplicate edge).
- Note body and all non-edge frontmatter keys are **unchanged** — verify by diff.

### 红线
- ❌ **Content nodes only** — NEVER edit vault `templates/` (user-synced) (phase-wide).
- ❌ Applies only a patch present in `docs/staging/` — no direct/arbitrary vault edits (review-gated).
- ❌ Preserve all non-edge frontmatter + body verbatim — no reformatting.
- ❌ 不进行机会主义重构。

### 输出位置
- 代码: `mcp-servers/chimera-papers/staging_service.py`, `mcp-servers/chimera-vault/server.py`
- 测试: `tests/`
- 文档: 推迟至 O.3 / seal。

---

## Sprint O.3: Obsidian-MCP veto confirmation + HSC-3 seal seed

**Friction reference:** `phase-O.md:23` (Obsidian MCP integration) — resolved to a no-op by the DR audit.

**Predecessor assumptions:**
- O.1b + O.2a + O.2b done — `create_node`, `link_nodes`, `apply_link_patch` all live. These ARE the
  "minimal file-write tool" the phase spec anticipates; O.3 adds no new tool.

**Risk level:** 🟢 LOW (doc + verify; no new code). The seal probe is verification.

### 目标
Record the Obsidian-MCP dependency-veto (Option C — no market MCP adopted; the thin wrapper is O.1b+O.2),
then run the HSC-3 seal seed and vault probe.

### 设计要点(audit-derived)
- **Confirm the veto — no new dependency.** DR audit `obsidian-mcp-necessity.md` (`d50cf81`): 12
  candidates, 0/3 pass Layer 2 (app-dependent or thick foreign runtime; none writes K/T/I/D).
  `.mcp.json` stays 2 servers. Audit ref: `O.0.md` Q7, cross-finding #4; Decision 4.
- **The file-write path already exists** — O.1b + O.2 over `StagingService` / `VaultNoteWriter`. O.3
  wires nothing new; it records the decision and seals.
- **✅ HSC-3 metric — PARTICIPATION, not origins (resolved 2026-07-07).** The probe counts nodes that
  participate in the typed-edge graph: a node counts if it is a **source** (own `graph_edges` non-empty)
  OR a **target** (its stem appears as `[[target]]` in another node's `graph_edges`, and it is a real
  node). This matches N.B `deep_recall`, which traverses **bidirectionally** (outgoing frontmatter edges
  + incoming grep). So each Thought that `derives_from` N real papers contributes 1 source + up to N
  targets. Live baseline is **12** (3 thoughts + the ~9 papers they point at); **5 real new thoughts +
  their targets reach ≥ 20 with ZERO fabricated K→K edges.** Real paper→paper edges are a bonus only.

### 任务范围
1. `docs/audits/obsidian-mcp-necessity.md` + `docs/phases/phase-O.md` O.3 note — record Option C / veto
   (no new dependency). (doc)
2. Seal seed — via `create_node` (+ optional real `link_nodes`/`apply_link_patch`), create 5 real
   Thought nodes each `derives_from` real papers, so thoughts + their targets reach ≥ 20 participants. (verify)
3. Run the participation probe (`scripts/seed_hsc3.py probe`) → confirm ≥ 20 participating nodes.

### 验收
- Veto recorded: `.mcp.json` unchanged (still 2 servers); no `obsidian` dependency added — verify by grep.
- Participation probe reports **≥ 20 participating nodes** (source ∪ target; HSC 3 / N.B unblock threshold).
- The 5 seed T Nodes + their edges are user-reviewed staging → promoted (never auto-promoted).

### 红线
- ❌ **No new dependency, no new MCP server** — `.mcp.json` stays 2 servers (phase-wide; Decision 4).
- ❌ Seed nodes go through `docs/staging/` → user review before promotion — no auto-promote.
- ❌ Do NOT fabricate K→K edges to inflate the count — only real relationships; NOT the out-of-scope 250-node backfill.
- ❌ 不进行机会主义重构。

### 输出位置
- 文档: `docs/audits/obsidian-mcp-necessity.md`, `docs/phases/phase-O.md`, ROADMAP sprint status.
- 验证: vault typed-edge probe output recorded in the phase_review.

---

## Phase-wide Red Lines

Apply across ALL sprints. Violation in any sprint halts the batch:

- ❌ **All vault writes go through `docs/staging/` → user review.** `create_node` and `link_nodes` write
  to staging; `apply_link_patch` applies only a reviewed patch; nothing auto-promotes (CLAUDE.md).
- ❌ **Zero new dependencies, zero new MCP servers** — no market Obsidian MCP, no Node runtime; `.mcp.json`
  stays 2 servers (Decision 4).
- ❌ **Thin adapters** — `chimera-vault/server.py` stays < 200 lines; tool bodies are dispatchers, domain
  logic lives in `chimera-papers/staging_service.py`. Total new code < 150 lines.
- ❌ **Never edit the vault `templates/`** (user-synced) — the schema authority is repo-side (`NODE_ONTOLOGY.md`).
- ❌ **Emit only `NODE_ONTOLOGY.md` (O.1a) edge keys** — no ad-hoc typed-edge vocabulary anywhere.
- ❌ **Do not touch** the poll-model `TaskService`, the miner/daily-pipeline, or any retired oligo/astrocyte surface.
- ❌ 不进行机会主义重构 across the batch.

---

## Hard Sealing Conditions (carried from `docs/phases/phase-O.md`)

MUST pass at `phase_review`:

1. **create_node writes all 4 types** — `create_node` produces K/T/I/D staging nodes with typed edges
   in frontmatter — verified by reading one staging file per type (O.1b acceptance).
2. **link_nodes adds edges to existing nodes** — `link_nodes` → review → `apply_link_patch` appends
   `derives_from` / `synthesizes` (etc.) to a live node — verified by re-reading the target node (O.2b acceptance).
3. **≥ 20 participating nodes** — after the O.3 seed (5 real Thoughts each `derives_from` real papers),
   the participation probe (`scripts/seed_hsc3.py probe`; a node counts as **source OR target**) reports
   ≥ 20 participating nodes — the **N.B unblock threshold**. Verified by the probe output. (Baseline 12.)

---

## Deferred / open (do not block O.1a–O.3)

- ~~**HSC-3 origin-count mechanism**~~ — **RESOLVED 2026-07-07**: the metric is **participation**
  (source ∪ target), not origins, matching N.B's bidirectional `deep_recall`. Baseline 12; 5 real
  thoughts reach ≥ 20 with no fabricated K→K edges. See `scripts/seed_hsc3.py`.
- **Rich `.j2` node templates** (cross-finding #5) — minimal-dict frontmatter ships in O.1b; wiring the
  richer `obsidian_tpl/*.j2` (lesson/actionable/rationale scaffolds) is a deferred follow-up.
- **Bulk backfill of ~250 existing K Nodes** — explicitly out of scope (`phase-O.md:43`); user work after O.3.
- **`STAGING_PROTOCOL.md`** — never migrated (audit Q8); the protocol lives in the V.A contract + code.
  Consider authoring alongside `NODE_ONTOLOGY.md` if O.1a surfaces the need (not a blocker).

---

## Approval

User approves the whole sequence or rejects the whole sequence.

Upon approval, hand off to `chimera-code-taste`:
> "Execute batch for Phase O per `docs/plans/Phase-O-batch.md`."

---

*Generated by chimera-sprint-discipline batch_planning mode.*
