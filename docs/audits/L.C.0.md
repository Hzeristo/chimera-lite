# Phase Audit: Phase L.C — Colligo: Candidate Consumption Paths

**Scope:** Read-only audit prerequisite for batch_planning of Phase L.C (the C.0 sprint).
**Output location:** `docs/audits/L.C.0.md`
**Date:** 2026-08-11
**Mode:** Read-only w.r.t. source — no fix proposals, no code modifications.
**Predecessor:** Phase L.B (Integratio), functionally sealed 2026-08-12 (`docs/audits/phase-L.B-seal-review.md`).
**Method:** R1 scout-before-read — five `chimera-repo-scout` (Haiku) passes fanned out per
question group, then full reads of only the scout-selected union.

---

## Files read

| Path | Lines | Notes |
|---|---|---|
| `docs/phases/phase-L.C.md` | 155 | full read — the spec under audit |
| `docs/phases/phase-L.md` | 311 | full read — parent phase, W1/W2 red lines |
| `docs/phases/phase-K.md` | 208 | full read — successor boundary |
| `docs/ARCHITECTURE/INVARIANTS.md` | 183 | full read — canonical |
| `docs/ARCHITECTURE/NODE_ONTOLOGY.md` | 215 | full read — edge vocabulary authority |
| `docs/ARCHITECTURE/ENFORCEMENT_DEBT.md` | 81 | full read — D-1/D-3/D-4/D-5, R2/R3/R6 |
| `docs/audits/phase-L.B-seal-review.md` | 153 | full read — inherited claims |
| `docs/logs/friction-260811.md` | 68 | full read — the registration class |
| `docs/TECHNICAL_DEBT.md` | 78 | full read — DEBT-020/021/022/023 |
| `docs/ACCEPTED_PARTIALS.md` | 284 | full read |
| `docs/phases/CODENAMES.md` | 79 | full read — ledger state |
| `.claude/skills/chimera-w1-verify/SKILL.md` | 70 | full read |
| `.claude/skills/chimera-deep-extract/SKILL.md` | 84 | full read |
| `.claude/agents/chimera-verbatim-verifier.md` | 60 | scout hits (output contract) |
| `.claude/skills/chimera-w2-map/SKILL.md` | 77 | scout hits |
| `.claude/agents/chimera-breadth-reducer.md` | 43 | scout hits (block format) |
| `mcp-servers/chimera-papers/staging_service.py` | 302 | lines 200-302 full; 13-18 + 82-96 + 149-172 via scout |
| `mcp-servers/chimera-vault/server.py` | 355 | scout hits — 11 `@mcp.tool` names, `write_result` sig |
| `mcp-servers/chimera-papers/server.py` | 296 | scout hits — 11 `@mcp.tool` names |
| `mcp-servers/chimera-papers/result_service.py` | 259 | scout hits — merge/supersede, `Harness/` |
| `mcp-servers/chimera-papers/core/schemas.py` | 469 | scout hits — `ExtractedClaim`, `KNodeExtraction` |
| `mcp-servers/chimera-papers/task_service.py` | 402 | scout hits — backgrounding surface |
| `mcp-servers/chimera-papers/w2_breadth.py` | 57 | scout hits — `plan_expansion` bounds |
| `tests/test_mcp_tool_registration.py` | 47 | scout hits — every assertion |
| `tests/test_architecture_dataflow.py` | 316 | scout hits — the two `.claude/` globs |
| `tests/test_ascend_node.py` | 107 | scout hits — the three I0.5 regressions |
| `tests/test_link_tools.py` | 212 | scout hits — committed-node patch tests |
| `prompts/obsidian_tpl/Tpl_thought.md` | 28 | full read — hand-authoring scaffold |

---

## Findings

| Q# | Driving sprint | Question | Answer | Evidence | Risk |
|---|---|---|---|---|---|
| **Q1** | C.1 | Claim shape + what the L.B.4 "W1 offer" does | `ExtractedClaim` carries title / statement / falsification / status / `sources[ClaimSource]` / tags / flags; `KNodeExtraction.claims` is bounded 1-5. The "offer" already exists and is **prose in a skill**: step 7 surfaces 1-3 candidates as report text the Architect retypes into a separate W1 invocation. There is no queue, no handle, no machine-readable payload. | `core/schemas.py:304`, `:358`; `chimera-deep-extract/SKILL.md:62-68`; `docs/sprints/phase-L.B/L.B.4.md:24,31` | Low |
| **Q2** | C.1, C.5 | Can W1 take N claims per invocation? Where is the loop boundary? | **Strictly one claim per run.** The skill's "The loop" normalizes *the* claim (singular), spawns one classifier + one verifier, writes one result. The verifier agent's contract is one verdict. The N-boundary does not exist anywhere — not in code, not in prose; batching is the Architect re-invoking the skill. | `chimera-w1-verify/SKILL.md:26-58`; `chimera-verbatim-verifier.md:8,19` | Low |
| **Q3** | C.2 | What does W2 emit, and what is the thinnest extract-side entry? | W2 emits ONE merged markdown artifact at `<vault>/Harness/w2_breadth_map__<topic>.md`, body = keyed blocks `<!-- w2:paper=<id> -->` each carrying gap / number+quote / **`promote-candidate: yes\|no` + ≤12-word reason**. Merge preserves Architect annotations. Thinnest extract entry: `ingest_paper(arxiv_id)` → markdown path (no node, no LLM). The promote-candidate flag is **already the recommendation primitive C.2 needs** — it is plain text in a block, not a persistent-map structure, so a C.2 interface reading it survives W2's reshaping. | `result_service.py:1,10,54,63,81`; `chimera-w2-map/SKILL.md:44,58`; `chimera-breadth-reducer.md:18`; `single_paper_ingest.py:66`; `chimera-papers/server.py:111` | Low |
| **Q4** | C.3 | Is `depends_on` in the edge vocabulary? Where do W1 verdicts land? | **`depends_on` is not an edge and has not been one since Phase O.** It was ratified-renamed to `derives_from` (`NODE_ONTOLOGY.md:88,98`) and retired again by canonical r2; it survives **only** as the parameter name on `write_result`, deliberately unrenamed because Phase K reads that field (`ENFORCEMENT_DEBT` D-4). Verdicts land in `<vault>/Harness/` at `status: PENDING_REVIEW`, identity-superseded on re-run. The value is written into the artifact's own frontmatter — it is **not** an edge on any K/T/I/D node. | `NODE_ONTOLOGY.md:88,98`; `ENFORCEMENT_DEBT.md:47` (D-4); `chimera-vault/server.py:296,303`; `result_service.py:10,156,179-189` | **High** |
| **Q5** | C.3 | Does any path add an edge to an already-committed node? | **Yes — `apply_link_patch`, and it is the only vault-mutating edge writer.** It reads `from_path` from the patch, checks only `is_file()`, and splices `graph_edges` in place. No tier check, no status check, no staging check. Two tests assert this against committed `Knowledge/` nodes as intended behavior. Edge *legality* IS validated (against the target's own declared `type`); tier is not. | `staging_service.py:258-302` (esp. `:270,273-274,299-300`); `tests/test_link_tools.py:133-147,192-211` | **High** |
| **Q6** | C.4 | What authors a T/I/D node? What does `informed_by` attach to? | **Nothing. By design, at two enforced layers.** `create_node` is `Literal["knowledge"]`; `create_staging_node` raises on any other type; `promote_node` is removed; `_ascend_write` refuses every destination but `Knowledge/`. Three regressions lock it. T/I/D are hand-written in Obsidian from `prompts/obsidian_tpl/Tpl_{thought,insight,decision}.md`. `informed_by` is canonical (I0.5 mandates it) but absent from `_TYPE_EDGES` (D-3). ~~And adding it there would be inert, because the dicts govern writers that refuse T/I/D anyway.~~ **CORRECTED 2026-08-12 — that clause was false:** `_TYPE_EDGES` also gates `stage_link_patch` / `apply_link_patch` (`staging_service.py:225-230`, `:279-284`), which edit **existing** hand-written T/I/D nodes. Adding `informed_by` there is precisely the missing mechanism. See cross-finding 3. | `chimera-vault/server.py:171,182-186`; `staging_service.py:82-96,149-153,168-172`; `tests/test_ascend_node.py:62-67,70-81`; `NODE_ONTOLOGY.md:163-191`; `Tpl_thought.md:8-12`; `ENFORCEMENT_DEBT.md:46` (D-3) | **High** |
| **Q7** | C.5 | What backgrounding can a *skill* use? | `TaskService` is MCP-server-internal and reachable only as `arxiv_miner` / `daily_paper_pipeline` → `task_id` → poll `check_task_status`. A skill cannot enqueue arbitrary work into it, and a server-side queue **structurally cannot run W1** — MCP cannot spawn subagents (phase-L red line), and W1's judgment must happen in one. **The usable substrate is the harness's own background Task mechanism, not `TaskService`** — verified empirically this session: five background scouts ran detached and returned by completion notification. | `task_service.py:63,262,353,390`; `miner_tools.py:20`; `chimera-papers/server.py:1,286`; `phase-L.md:166-169`; live session evidence | Med |
| **Q8** | I1.4 gate | Step-count the three routes today | **Route 1 (zero AI):** open Obsidian, apply `Tpl_thought`, type. ~1 step, no repo surface. **Route 2 (AI-assisted):** run deep-extract (or read a W2 map), read output, switch to Obsidian, hand-copy `informed_by` — ~4 steps, the only one requiring manual YAML. **Route 3 (batch promote):** re-invoke `chimera-w1-verify` once per claim, then curate `Harness/` by hand — N invocations. Route 1 is the *lightest today*, so L.C's real I1.4 risk is not "AI routes are privileged" but the inverse: C.1/C.3/C.5 all smooth route 3, and nothing in the sprint list touches route 1 or 2 except C.4. | `Tpl_thought.md`; `chimera-deep-extract/SKILL.md:62`; `chimera-w1-verify/SKILL.md:26`; `NODE_ONTOLOGY.md:188-191` | Med |
| **Q9** | C.0.5 (adopted) | What covers registration surfaces? | `test_mcp_tool_registration.py` is 47 lines: it parses both `server.py` for `@mcp.tool()` names and asserts the tools **4 hardcoded skills** name are registered, plus two `analyze_paper_data` regressions. 17 skills exist; 13 are uncovered. **No test validates `.claude/agents/*.md` frontmatter at all** — `test_architecture_dataflow.py` globs the directory (`:136`) for diagram rendering, which reads the files but asserts nothing about parseability, required keys, or model pins. 8 agents, zero validation. This is exactly the gap instance 3 fell through. | `tests/test_mcp_tool_registration.py:28,42,47-51,54-63`; `tests/test_architecture_dataflow.py:136,313`; `friction-260811.md:40-45` | **High** |

---

## Cross-references discovered

- **`apply_link_patch` is C.3's mechanism and it already exists, already human-gated.** The
  stage → review → apply split means a W1-driven edge can be *staged* automatically without
  violating I0.1: the Architect's `apply_link_patch` call is the human-time commit. C.3 shrinks
  from "build an auto-edge writer" to "make verdict promotion stage the patch."
  Evidence: `staging_service.py:208-256` (stage), `:258-302` (apply).
- **Harness artifacts are not K/T/I/D nodes and carry no `_TYPE_EDGES` entry.** `apply_link_patch`
  raises `unknown type` for any node whose frontmatter `type` is outside the four. A W1 verdict
  artifact therefore cannot be a patch *target*. Evidence: `staging_service.py:278-280`;
  `NODE_ONTOLOGY.md:156` (harness_candidate is "not a K/T/I/D node").
- **W2's `promote-candidate` flag is the only W2 output C.2 needs.** It is per-block plain text,
  independent of whether the map persists. Evidence: `chimera-breadth-reducer.md:18`.
- **`_TYPE_EDGES` legal set for K is `derives_from` / `supersedes` / `contradicts`.** `evidence_base`
  — the semantically correct edge for "verified support" — is **I-node-only** in both code and
  canonical. Evidence: `staging_service.py:13-18`; `NODE_ONTOLOGY.md:50,61-64`.
- **DEBT-020/021 bound C.2 from the W2 side.** The reference parser does not exist and the BFS caps
  are enforced by skill prose, not by the tested `plan_expansion`. C.2 must not assume a crawl.
  Evidence: `TECHNICAL_DEBT.md` DEBT-020, DEBT-021; `w2_breadth.py:17,25`.

---

## Notable cross-findings (no fix proposals — flagging for planning)

1. **C.3's central noun names a concept retired two phases ago.** The spec's HSC 3 reads
   "Promoting a W1 verdict writes the `depends_on` edge in the target's frontmatter." `depends_on`
   is not an edge in the canonical vocabulary (I2.2 lists nine; it is not among them), was
   explicitly renamed away in Phase O, and exists today only as an MCP parameter name that
   `ENFORCEMENT_DEBT` D-4 records as misdescribing its own field. Worse, no *legal* K-node edge
   expresses "this claim is supported by this verdict": `evidence_base` is the right meaning and is
   I-only. So C.3 cannot be planned as written — the sprint needs a vocabulary decision before it
   has a target. Evidence: `phase-L.C.md:92`; `INVARIANTS.md:135-139`; `NODE_ONTOLOGY.md:50,61,88,98`;
   `ENFORCEMENT_DEBT.md:47`; `staging_service.py:13-18`.

2. **[RESOLVED 2026-08-12 — not a violation; no tier guard owed.]** The Architect settled this on
   ontological grounds: an edge here is frontmatter metadata (a list of wikilink stems), not a
   first-class relation object with its own identity and provenance as in a KG, so appending one
   does not modify the committed node's **content** — which is what I1.2's writer clause governs.
   `ascend_node` remains sole writer of *new committed nodes*. Recorded as `ENFORCEMENT_DEBT`
   **D-7**, with the definitional basis in `NODE_ONTOLOGY.md §2` and a scope annotation on the L.B
   seal row. The finding as originally written follows, unedited, as the record of what was found.

   **I1.2's "sole writer" claim is true of creation and false of mutation, and the L.B seal asserted
   it flatly.** `ascend_node` is the only path that *creates* a committed node; `apply_link_patch`
   *mutates* committed nodes' frontmatter with no tier or status guard, and is a registered MCP tool.
   This is not recorded in `ENFORCEMENT_DEBT` under R2, R3, or anywhere else — R3's residual gap is
   described as scout-card non-advancement only. Whether this is a violation or simply outside I1.2's
   intended scope is a **canonical scope question of the same shape as D-6** (which settled K-vs-T/I/D
   and left create-vs-mutate untouched). It is load-bearing for C.3, which would drive this path.
   Evidence: `INVARIANTS.md:76-81`; `ENFORCEMENT_DEBT.md:52-53` (R2/R3); `staging_service.py:270,273-274,299-300`;
   `tests/test_link_tools.py:192-211`; `phase-L.B-seal-review.md:38`.

3. **[CORRECTED 2026-08-12 — the second half of this finding was wrong.]** The first half stands:
   no tool authors a T/I/D **body**, and C.4's "auto-fill on authoring" premise was removed by
   `2b72978`. The second half — that fixing `ENFORCEMENT_DEBT` D-3 would be *inert* because
   `_TYPE_EDGES` "governs writers that reject T/I/D" — is **false**. `_TYPE_EDGES` has three
   consumers (`staging_service.py:104`, `:225-230`, `:279-284`), and only the first is
   `create_staging_node`; the other two are `stage_link_patch` and `apply_link_patch`, which
   operate on **existing** vault nodes of any K/T/I/D type — routinely hand-written Thoughts.
   `tests/test_staging_tools.py:51` states this explicitly and the audit misread its implication.

   The Architect's framing (2026-08-12) resolves it: **I0.5 reserves the *body*, and D-7 settled
   that an edge is metadata, not content** — so a tool writing an `informed_by` edge onto a
   hand-authored T-node authors no judgment and violates nothing. Closing D-3 is therefore not a
   red herring; it *is* the missing mechanism for I0.5's provenance mandate. C.4 is re-scoped
   accordingly. **Consequence beyond L.C:** edges are format work, the Architect does not do
   format work by hand (route-1 datum: "no links"), and no tool was permitted to do it on the
   judgment side — a candidate root cause for the long-empty typed graph (`friction-260708-01`,
   the N.B cancellation).

   **Original finding, retained as the record of what was found:**

   **C.4 as specified cannot be built, because its premise was removed the day before the seal.**
   The spec says "authoring a T/I node while viewing AI material auto-fills `informed_by`." Commit
   `2b72978` (2026-08-11) made *every* T/I/D authoring path refuse, at two layers, with three
   regressions. There is nothing to auto-fill *into* from the tool side. `informed_by`'s absence from
   `_TYPE_EDGES` (D-3) is therefore a red herring for C.4: fixing D-3 would add the key to dicts used
   only by writers that reject T/I/D. Any real C.4 must act on the **hand-authoring** surface —
   the Obsidian template and what the AI-side report hands the Architect to paste — not on a writer.
   Evidence: `phase-L.C.md:53,94-95`; `staging_service.py:82-96`; `chimera-vault/server.py:171,182-186`;
   `tests/test_ascend_node.py:70-81`; `ENFORCEMENT_DEBT.md:46`; `NODE_ONTOLOGY.md:188-191`.

4. **I1.4 — the invariant this entire phase exists to satisfy — has no mechanical verifier, and the
   phase's own gate for it is Architect-vibes.** `ENFORCEMENT_DEBT` D-5 records I1.4 among eight
   canonical invariants rendering UNCHECKABLE in the generated map. L.C's HSC 6 is "Architect-assessed:
   three sessions run with equal friction." Under the repo's own north star — *advisory rigor is
   negative value* — an equal-friction principle with no measurement is precisely the thing that
   launders a preference into a guarantee. The audit flags this without proposing the fix: L.C is the
   phase that would either give I1.4 an observable or knowingly ship it as convention.
   Evidence: `ENFORCEMENT_DEBT.md:48` (D-5); `phase-L.C.md:100-103`; `INVARIANTS.md:101-109`; `CLAUDE.md` north star.

5. **The sprint that smooths route 3 is the one already easiest to automate, and route 1 has no
   surface at all.** Q8's step count shows route 1 (pure observation) lives entirely in Obsidian and
   touches no repo code — meaning L.C *cannot* add ceremony to it, but also cannot help it, and any
   measurement of "equal friction" that counts tool steps will score it as free. Three of five sprints
   (C.1, C.3, C.5) target route 3. This is not yet a violation — I1.4 forbids smoothing one route while
   *taxing* another — but it is the asymmetry the VISION gate must actually look at.
   Evidence: `phase-L.C.md:18-23,47-55`; `Tpl_thought.md`; `INVARIANTS.md:101-109`.

6. **C.5's blocker is structural, not sizing.** The spec treats stream-mode as a weight problem
   ("2-3 sprints if full"). The real constraint: W1 judgment must run in a subagent, MCP cannot spawn
   subagents, so `TaskService` — the repo's only queue — can never host a backgrounded W1. The
   substrate that *can* is the harness's native background Task mechanism, which is outside the repo
   and untested by anything here. C.5a is therefore not "half of C.5"; it is a different build on a
   different substrate, and its risk is dependency-on-harness-behavior, not size.
   Evidence: `phase-L.md:166-169`; `task_service.py:353,390`; `chimera-papers/server.py:1`; `phase-L.C.md:151`.

7. **`friction-260811-01` names a class L.C is about to feed.** Every C-sprint ships a registered
   thing: new skill steps, possibly a new agent type, new edge writes. Coverage today is 4 of 17
   skills for MCP tools and **zero** for the 8 agent definitions. The friction's own prescription is
   one registry assertion covering both surfaces, not two.
   Evidence: `friction-260811.md:48-62`; `tests/test_mcp_tool_registration.py:28,47-51`;
   `tests/test_architecture_dataflow.py:136`.

8. **Phase L itself was never sealed.** `docs/sprints/phase-L/` holds L.1a–L.3 with no
   `phase-review.md`; `phase-L.md` and the CODENAMES ledger both still read **Active**; L.4 (HTML
   panel, optional) is unbuilt. L.B sealed as a sub-phase inside an unsealed parent, and L.C would be
   the second. Phase L's own HSC 5 — the VISION gate, "real survey material the Architect would feed
   into a semi-proposal" — has never been assessed. That gate, not L.C's, is the one measuring whether
   the harness works at all. Evidence: `docs/sprints/phase-L/` (6 files, no review);
   `phase-L.md:3,99,202-207`; `CODENAMES.md:44`.

9. **Two indices are stale, in opposite directions.** `CLAUDE.md` lists 5 `chimera-vault` tools; there
   are 11 (`create_node`, `ascend_node`, `link_nodes`, `apply_link_patch`, `write_result`, `load_criteria`
   are all absent from it) — user-confirmed stale this session, and this skill may never write that file.
   `CODENAMES.md`'s ledger carries single letters only, so the sub-phase codenames in active use
   (Integratio, Colligo) appear nowhere in the file the ROADMAP calls canonical for them; its own
   "ROADMAP sync" open slot is still open. Evidence: `CLAUDE.md` MCP servers section;
   `chimera-vault/server.py` (11 `@mcp.tool`); `CODENAMES.md:41-50,77-79`; `ROADMAP.md:428-429`.

---

## Audit complete

- 9 questions answered
- 61 file:line references
- 5 cross-references
- 9 notable cross-findings
- 4 questions at **High** risk (Q4, Q5, Q6, Q9)

**Blocking for batch_planning:** C.3 and C.4 have no buildable target as specified (cross-findings
1 and 3). Both require a spec amendment against the canonical vocabulary before sprint tasks can be
written. The Architect has authorized that amendment (2026-08-11, this session).

**Suggested next:** amend `docs/phases/phase-L.C.md`, then `batch_planning` for Phase L.C.

---

*Generated by chimera-sprint-discipline phase_audit mode.*
