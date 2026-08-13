# Workflow Drift Audit — the four-path ingestion model vs. reality

**Type:** Read-only three-way drift audit (ST vision ↔ code ↔ Claude Code's operating belief).
**Date:** 2026-07-20 · **Branch:** `phase-L-w1w2-ontology-docs` (worktree; reads code identical to `phase-L`).
**Scope:** the four-path knowledge-ingestion model asserted in `docs/ARCHITECTURE/THEORETICAL_FRAMEWORK.md`
and `CLAUDE.md § Knowledge Ingestion Paths`. **No fixes applied.** Every code claim carries `file:line`.
Q4 is an honest self-report of my behavior, not a code claim.

> **Bottom line up front.** The four paths all *exist*, but they are **not one system** — Paths 1–2 are
> MCP tools whose judgment runs on **deepseek**, Paths 3–4 are **skills** whose judgment runs in **Claude
> subagents**. The ST doc's premise "judgment lives in Claude subagents" is true for half the model and
> false for the other half, and nothing in the code marks the seam. See §Drift matrix and §Issues.

---

## Q1 — `daily_paper_pipeline`: where it writes, what it produces

| # | Finding | Evidence |
|---|---|---|
| Q1.1 | Per-paper triage is a **deepseek** call via `generate_structured_data`, unchanged. Not replaced by a subagent. | `filter_service.py:45` `self.llm_client.generate_structured_data(... response_model=PaperAnalysisResult)` (`:48`). Client = `build_openai_client` → `settings.default_llm_model` = `deepseek-chat` (`bootstrap.py:108-125`; `core/config.py:178-182`, `:222-232`). Daily wiring: `daily_chimera_service.py:259-265` spawns `filter_queue_worker`; `batch_filter_workflow.py:154,208,210` → `write_knowledge_node`. |
| Q1.2 | **Thin** K node. Verdict/score/moniker + one-line novelty + mechanism summary + flaws. **Empty `graph_edges`**, `status: unverified`. No synthesis / lens / attack / claims. | Schema `PaperAnalysisResult` (`core/schemas.py:69-139`: verdict, short_moniker, score, novelty_delta, mechanism_summary, critical_flaws, …). Rendered template `prompts/obsidian_tpl/knowledge_node.j2:1-18` (`status: unverified` `:3`; `graph_edges: derives_from/supersedes/contradicts: []` `:14-17`); body `:28-48` = Core Contribution / Mechanism / Critical Flaws only. |
| Q1.3 | Writes **directly into the vault** at `inbox_folder/<Verdict>/`. **Bypasses `docs/staging/`.** | `ports/vault/vault_note_writer.py:24` `inbox_folder`; `:40` `target_dir = vault_inbox_dir / analysis.verdict.value`; `:43` `output_path.write_text(...)`. No `StagingService` in this path. |

Q1.3 is real but **precise**: the target is `inbox/<verdict>/`, **not** `Knowledge/`. It is a scout landing
zone inside the vault, and the node carries `status: unverified`. So it does not assert committed truth —
but it does place AI-authored material inside the vault boundary with **no review-buffer and no
status-transition machinery** (see Q6 and Issue C‑2).

---

## Q2 — `extract_paper`: what it produces

| # | Finding | Evidence |
|---|---|---|
| Q2.1 | Response model is **`KNodeExtraction`** — the RICH shape (synthesis + 1–2 lenses + attack + 1–5 claims). Not `KClaimExtraction` (that pre-rebuild atomic shape no longer exists; the atomic unit is `ExtractedClaim`, a *sub-field*). | `single_paper_extract.py:189` `response_model=KNodeExtraction`. Model: `core/schemas.py:358-367` (`synthesis: PaperSynthesis`, `lenses: 1-2`, `attack: AttackVectors`, `claims: 1-5`). Renderer `single_paper_extract.py:73-158`. |
| Q2.2 | Output goes to **`docs/staging/`** via `StagingService.create_staging_node`; **never touches the live vault**; supersedes the paper's prior node **on promotion** (manual). | `single_paper_extract.py:285` `StagingService(cfg().system.staging_dir, vault_root)`; `:286-293` `create_staging_node(type="knowledge", …)`; docstring `:224-225` "never touches the live vault"; supersede edge `:270-272`. Promote path is manual (no code promotes). |
| Q2.3 | **No subagent.** Judgment is a direct **deepseek** `generate_structured_data` call. ST's "judgment moves to Claude subagents" is **not** implemented here. | `single_paper_extract.py:186-190` `llm_client.generate_structured_data(... response_model=KNodeExtraction)`; client resolved from `bootstrap.build_openai_client` (`:257-260`) = deepseek. No `Task` / subagent anywhere in the module. |

So Path 2's **output contract matches ST** (rich, staged, human-promoted) while its **judgment mechanism
contradicts ST** (deepseek, not a Claude subagent). Additional friction: `extract_paper` reuses
already-converted markdown and **runs no MinerU** (`server.py:182`; `single_paper_extract.py:196-209`
`_resolve_markdown` raises `FileNotFoundError` if the `<id>.md` is absent) — so it cannot deep-read a
paper that has not been ingested/converted first.

---

## Q3 — Are W1 and W2 exposed as MCP tools?

**Q3.1 — full `@mcp.tool()` inventory (both servers):**

- `chimera-papers` (`mcp-servers/chimera-papers/server.py`): `arxiv_miner` (`:60`), `daily_paper_pipeline`
  (`:76`), `ingest_paper` (`:103`), `fetch_paper` (`:133`), `convert_pdf_to_md` (`:153`), `extract_paper`
  (`:177`), `check_task_status` (`:197`).
- `chimera-vault` (`mcp-servers/chimera-vault/server.py`): `search_vault` (`:54`), `search_vault_attribute`
  (`:66`), `read_vault_file` (`:79`), `load_criteria` (`:90`), `obsidian_graph_query` (`:120`),
  `vault_query` (`:139`), `create_node` (`:157`), `link_nodes` (`:187`), `apply_link_patch` (`:234`),
  `write_result` (`:255`).

**There is NO `w1`/`w2` MCP tool.** W1 and W2 are **Claude Code skills** — `/chimera-w1-verify`
(`.claude/skills/chimera-w1-verify/SKILL.md`) and `/chimera-w2-map`
(`.claude/skills/chimera-w2-map/SKILL.md`) — that orchestrate the MCP *primitives* (`load_criteria`,
`write_result`, `fetch_paper`, `convert_pdf_to_md`) plus Task subagents. `ToolSearch` will **not** surface
"w1"/"w2"; it surfaces those primitives. **This matches ST by design** ("Claude Code *is* the agent loop;
MCP provides the primitives; judgment lives in Task subagents") — but anyone expecting an
`mcp__chimera-papers__w1_verify` tool will not find one (clarity risk, Issue M‑1).

**Q3.2 — does `/chimera-w1-verify` match `phase-L.md`'s W1?** Yes, on the two load-bearing points:
- Loads criteria from the vault dynamically: `chimera-w1-verify/SKILL.md:46` `load_criteria(type, field, role="paper-critic")` → the `load_criteria` tool (`chimera-vault/server.py:90`) composes `criteria/type/…`, `criteria/field/…`, `criteria/disposition/…`.
- Verbatim check runs in an **isolated subagent** (`chimera-verbatim-verifier`), never main context, never deepseek: `SKILL.md:22-24`, `:49-51`, red lines `:62-63`. Verdict + quotes → `write_result(kind="w1_verdict")` at `status: PENDING_REVIEW` (`:53-56`).

**Q3.3 — `extract_paper` present/callable?** Yes. MCP tool name **`mcp__chimera-papers__extract_paper`**
(`server.py:177`), delegating to `miner_tools.extract_paper` → `single_paper_extract.extract_single_paper`.

---

## Q4 — What Claude Code actually does today (honest self-report)

**Q4.1 — "deep read this paper: [arxiv_id]".** There is **no single tool** that deep-reads a fresh arXiv id,
and my behavior is genuinely ambiguous:
- If I reach for `extract_paper` first (the "rich" tool), it **fails** on a never-ingested id —
  `_resolve_markdown` raises `FileNotFoundError` because no `md_papers/<id>.md` exists
  (`single_paper_extract.py:196-209`). So a naive "deep read → `extract_paper`" errors out.
- If I reach for `ingest_paper`, I get a **thin triage card** in `inbox/`, *not* a deep read — and I might
  not notice the shortfall.
- The intended sequence (documented only in a module docstring, `single_paper_ingest.py:8-9`) is
  `ingest_paper` → `read_vault_file` → an N.A lens skill → `create_node`; the rich path is a **separate**
  `extract_paper` that needs the converted markdown to already exist. I do **not** reliably know to run this
  two-step dance without re-reading the code — which is itself evidence of belief-drift.

**Q4.2 — "what is the key contribution of StreamForest?".** Honestly: the disciplined answer is **(a)** — call
`search_vault` / `vault_query` / `search_vault_attribute` first, and the always-active
`chimera-academic-observe` skill is meant to push me there. The real failure mode is **(b)** — answering
from training weights. For a specific system name like "StreamForest," (b) is high hallucination risk and
produces **no error**. My own memory records this as a known "vault-in-loop agentic defect" (retrieval was
retired until it is fixed), i.e. I do **not** reliably pull from the vault mid-reasoning. I should hard-commit
to (a); I cannot claim I always do. I would **not** call `extract_paper` on the fly for a definitional
question (wrong tool, and it needs a pre-converted paper).

**Q4.3 — `extract_paper` timing.** It returns in **seconds–tens of seconds**, not minutes: one deepseek
`generate_structured_data` call (`single_paper_extract.py:186`) + a synchronous citation-grounding walk over
the vault (`resolve_citations`, `:264-266`). It runs **no MinerU** and **no subagent**. The minutes-long,
MinerU-bound path is `ingest_paper` / `daily_paper_pipeline` / `convert_pdf_to_md`. So my prior mental model
— "extract_paper = slow, subagent-driven deep read" — was **wrong on both counts** (it is fast and
deepseek-driven).

---

## Q5 — Three-way drift diagnosis

### Q5.1 — Code vs. `THEORETICAL_FRAMEWORK.md`'s four-path model

| Path | Verdict | Evidence |
|---|---|---|
| 1 — `daily_paper_pipeline` → thin K node (inbox/) | **MATCHES** | Thin `PaperAnalysisResult` node → `inbox/<verdict>/`, empty edges, `status: unverified` (`filter_service.py:45`; `knowledge_node.j2:1-18`; `vault_note_writer.py:40-43`). |
| 2 — `extract_paper` → rich K node (staging/ → Knowledge/) | **PARTIAL — output matches, mechanism CONTRADICTS** | Rich `KNodeExtraction`, staged, human-promoted (`single_paper_extract.py:189,285-293`) ✓; but judgment is **deepseek, not a Claude subagent** (`:186`), contradicting ST's core "judgment in subagents." Also needs pre-converted markdown (no MinerU, `:196-209`). |
| 3 — W1 claim verify → sub-K verdict (Harness/) | **MATCHES (as a skill, not a tool)** | `/chimera-w1-verify` loads criteria + isolated subagent + `write_result` PENDING_REVIEW (`SKILL.md:46,49-56`). No MCP tool exists — by ST design. |
| 4 — W2 breadth map → meta-K map (Harness/) | **MATCHES (as a skill, not a tool)** | `/chimera-w2-map` bounded-BFS + per-paper classify/reduce subagents + `write_result(mode="merge")` (`SKILL.md:26-56`). No MCP tool — by ST design. |

### Q5.2 — Where my pre-audit understanding was wrong

- **Believed `extract_paper` uses a Claude subagent** (ST framing "judgment moves to subagents"). **Wrong** —
  direct deepseek (`single_paper_extract.py:186`). Only W1/W2 use subagents.
- **Believed `ingest_paper` yields a rich Knowledge node.** **Wrong** — it yields the *same thin triage card*
  as the daily pipeline, in `inbox/` (`single_paper_ingest.py:104-111` → `write_knowledge_node`).
- **Believed the four paths were one uniform system** (I wrote the four-path section into `CLAUDE.md` /
  `NODE_ONTOLOGY.md` last task without flagging the deepseek-vs-subagent split). **Wrong** — the model is
  half-tool/deepseek, half-skill/subagent, and the docs I wrote do not say so.
- **Believed `extract_paper` was the slow deep-read.** **Wrong** — it is fast; MinerU lives in the *ingest*
  paths (Q4.3).

### Q5.3 — The single most dangerous silent drift

**`type: knowledge` is overloaded, and `status` never transitions — so the vault cannot tell a scout-tier
triage card from a deep-read node, and no machine marks the human-commit boundary.**
- `daily_paper_pipeline` and `ingest_paper` write `type: knowledge`, `status: unverified`, empty edges into
  `inbox/` (`knowledge_node.j2:2-17`). `extract_paper` writes `type: knowledge` too (`single_paper_extract.py:288`).
  Nothing in the frontmatter distinguishes "1 deepseek triage pass" from "rich extraction," and nothing ever
  moves `status: unverified` → verified (the documented `status=?` deferred issue in `CLAUDE.md`).
- This is the textbook silent failure: **no error, wrong behavior.** I call `ingest_paper` for a "deep read,"
  get a thin card labelled `knowledge`, then answer research questions from it (or from weights, Q4.2)
  believing I did a deep read. A graph consumer keying on `type: knowledge` conflates the tiers. The
  `status: unverified` field is present but inert — **advisory rigor** in the precise sense the core
  philosophy warns against ("a flag that only performs rigor launders opinion into knowledge").

---

## Q6 — Staging-bypass risk

**Q6.1 — Any K/T/I/D entering `vault/Knowledge/` or `vault/Thoughts/` *without* `docs/staging/`?**
Precisely: **no path writes to `Knowledge/` or `Thoughts/` directly.** The knowledge tier's review boundary
is intact — `create_node` (`chimera-vault/server.py:157-183`) and `extract_paper`
(`single_paper_extract.py:285-293`) both go through `docs/staging/`. **But two non-`docs/staging/` vault
writes exist:**
- `daily_paper_pipeline` + `ingest_paper` → **`inbox/<verdict>/` directly**, no review buffer
  (`vault_note_writer.py:40-43`). Mitigation: it is `inbox/` (scout), `status: unverified`, thin. It is
  **not** `Knowledge/`. Flagged **HIGH, not CRITICAL** (Issue C‑2) — it does not violate "human commits
  truth" for committed nodes, but it puts AI material in the vault with no gate and an inert status field.
- W1/W2 → **`vault/Harness/` directly** via `write_result`, but at `status: PENDING_REVIEW`
  (`result_service.py:136`) — a *review-gated* in-vault buffer by design ("the two curation paths,"
  `result_service.py:1-6`), never auto-promoted.

`apply_link_patch` (`chimera-vault/server.py:234-251`) is the **one tool that mutates a live vault node**
(appends an edge) — but only from a human-reviewed patch produced by `link_nodes` → `docs/staging/`. Human-
invoked, not auto. Not a bypass.

**Q6.2 — Does the W1/W2 harness auto-promote?** **No.** Everything stays `PENDING_REVIEW` until the Architect
acts: `write_result` writes `status: "PENDING_REVIEW"` (`result_service.py:136`), W2 moves to `MERGED` only
as a re-run union (`:171`), and `reject`/`mark_stale` are explicit transitions (`:123-124`). Skill red lines
enforce it: W1 "lands … PENDING_REVIEW for the Architect to curate" (`chimera-w1-verify/SKILL.md:55-56`); W2
"nominates; the Architect promotes … no auto-ingest, no auto-K-node" (`chimera-w2-map/SKILL.md:69`).
`extract_paper` "never auto-promotes into the vault" (`server.py:184-185`); `create_node` "never
auto-promoted" (`:163`).

---

## Drift matrix

| Aspect | Intended (ST / `THEORETICAL_FRAMEWORK.md`) | Code reality | My prior belief | Drift? |
|---|---|---|---|---|
| Path 1 daily → thin K node, inbox/ | scout/triage layer, high-volume | thin `PaperAnalysisResult` → `inbox/<verdict>/`, deepseek (`filter_service.py:45`, `vault_note_writer.py:40`) | thin, deepseek, inbox | **MATCH** |
| Path 2 extract → rich K node, staging | deep-read; "judgment in subagents" | rich `KNodeExtraction` → `docs/staging/` **but deepseek, no subagent, no MinerU** (`single_paper_extract.py:186,285`) | thought it used a subagent + was slow | **PARTIAL / mechanism CONTRADICTS** |
| Path 3 W1 → sub-K verdict, Harness | subagent verbatim check, criteria-loaded | `/chimera-w1-verify` skill: criteria + isolated subagent + `write_result` PENDING_REVIEW (`SKILL.md:46-56`) | matched | **MATCH (skill, not tool)** |
| Path 4 W2 → meta-K map, Harness | bounded recon, merge-not-clobber | `/chimera-w2-map` skill: bounded BFS + subagents + `write_result(merge)` (`SKILL.md:26-56`; `result_service.py:56-76`) | matched | **MATCH (skill, not tool)** |
| Judgment substrate | "judgment lives in Claude subagents" | **split**: Paths 1–2 deepseek; Paths 3–4 Claude subagents | assumed uniform subagents | **CONTRADICTS (half)** |
| W1/W2 as callable tools | primitives are MCP; loop is Claude Code | no `w1`/`w2` MCP tool; skills only | expected them as tools | **by design (clarity risk)** |
| `ingest_paper` output | "a vault Knowledge node" (docstring `server.py:106,111`) | thin triage card in `inbox/`, same as daily | expected rich | **CONTRADICTS (naming)** |
| Node-tier marking | human commits truth (Theorem 1) | all `type: knowledge`; `status: unverified` never transitions | assumed tiers were distinguishable | **CONTRADICTS (inert status)** |
| Auto-promotion | none; human-in-the-loop | none (staging + Harness PENDING_REVIEW) | matched | **MATCH** |

---

## Priority-ranked issues

### CRITICAL — silent wrong behavior
- **C‑1. Overloaded `type: knowledge` + inert `status`.** Thin triage cards (`daily`/`ingest`) and rich
  extractions (`extract_paper`) all carry `type: knowledge`; `status: unverified` is set once
  (`knowledge_node.j2:3`) and never advances. No machine boundary between candidate and committed, and no
  way to tell scout-tier from deep-tier. Produces wrong outputs with no error (Q5.3). This is the concrete
  form of the `CLAUDE.md` `status=?` deferred issue, and it is *advisory rigor* per the core philosophy.
- **C‑2. Behavioral: vault-bypass on definitional questions.** I can answer "what is X?" from training
  weights instead of `vault_query`/`search_vault` (Q4.2), with no error. Compounded by the two-step,
  under-documented deep-read dance (Q4.1) that nudges me toward the thin `ingest_paper` or a failing
  `extract_paper`. Known "vault-in-loop" defect; not code-fixable alone.

### HIGH — missing functionality blocking the vision
- **H‑1. ST's "judgment in Claude subagents" is unimplemented for Paths 1–2.** Triage (`filter_service.py:45`)
  and extraction (`single_paper_extract.py:186`) run on **deepseek**. Only the harness (W1/W2) honors the
  subagent premise. The docs I wrote last task assert the four-path model without disclosing this seam.
- **H‑2. No single "deep-read a fresh paper" path.** `extract_paper` needs pre-converted markdown and runs no
  MinerU (`single_paper_extract.py:196-209`); a cold arXiv id requires `ingest_paper`/`convert_pdf_to_md`
  first. The intended chain lives only in a module docstring (`single_paper_ingest.py:8-9`), not in any
  tool contract or skill.
- **H‑3. `ingest_paper` over-promises.** Docstring sells "a vault Knowledge node" / "into my Knowledge base"
  (`server.py:106-111`) but delivers the *thin* triage card (`single_paper_ingest.py:104-111`). Same tier as
  `daily`, not the rich Path 2.

### MEDIUM — inconsistency that degrades but doesn't break
- **M‑1. W1/W2 discoverability.** No `w1`/`w2` MCP tool; they are skills (`/chimera-w1-verify`,
  `/chimera-w2-map`). Correct by ST design, but invisible to `ToolSearch` and easy to mistake for missing
  functionality.
- **M‑2. Two review buffers, one principle.** K/T/I/D stage in `docs/staging/`; W1/W2 stage in
  `vault/Harness/`. Both are review-gated, but "staging" is now two places — the ST doc and `CLAUDE.md`
  describe the buffers separately and never state the union rule ("nothing AI-authored is committed truth
  until a human acts, in *either* buffer").

---

## Honest assessment — does the four-path model actually exist in code?

Yes — all four paths run — but "the four-path model" as a *single coherent ingestion system* is **more
documentation than code today.** What exists is two different machines wearing one label: a **deepseek batch/
extract machine** (Paths 1–2: `daily_paper_pipeline`, `extract_paper` — MCP tools, deepseek judgment, writing
thin cards to `inbox/` and rich nodes to `docs/staging/`) and a **Claude-subagent harness** (Paths 3–4: the
`/chimera-w1-verify` and `/chimera-w2-map` skills — subagent judgment, writing review-gated artifacts to
`vault/Harness/`). The ST doc's unifying premise — that judgment lives in Claude subagents — is true for the
harness half and false for the ingestion half, and neither the code nor the docs I wrote last task mark that
seam. The genuinely load-bearing gap is not any single missing path; it is that **the vault cannot
distinguish the tiers these paths produce** (`type: knowledge` is uniform, `status` is inert), so the model's
integrity currently rests on convention and on my remembering which tool does what — exactly the
convention-not-enforcement condition the project treats as negative value. The four-path model is a faithful
*map*; the code is a partially-different *territory*, and the difference is silent.
