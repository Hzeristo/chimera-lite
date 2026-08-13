# Cost-Incident Report: Model-Routing Gaps

**Date:** 2026-07-20
**Scope:** Where does Chimera Lite spend Opus tokens on Sonnet- or Haiku-class work?
**Method:** Static read of the two execution skills, the two W1/W2 orchestration skills,
the three Phase-L worker agent definitions, the shared routing docs, `phase-L.md`, the
`Phase-L-batch.md` sprint plan, and `chimera-papers/server.py`.
**Disposition:** Audit only. Nothing fixed. Recommendations stated, not applied.

**Model taxonomy used** (from the incident brief):
- **Haiku** — mechanical, deterministic, `output = f(input)`.
- **Sonnet** — moderate comprehension, code execution, pattern matching.
- **Opus** — cross-cutting judgment, architectural, genuinely ambiguous.

---

## TL;DR — the leak is narrower than feared, and structural

The **judgment workers are already well-routed.** The three subagents that carry the
harness's actual reasoning — `chimera-paper-classifier`, `chimera-verbatim-verifier`,
`chimera-breadth-reducer` — **pin `model: sonnet` in their agent-definition frontmatter**
(`*.md:5`). Frontmatter model overrides the session model, so these do **not** inherit
Opus even when spawned from an Opus session. In W2 that is the big-volume path (up to
~48 worker spawns per run), and it is banked at Sonnet already. Good.

The over-spend is concentrated in **two unguarded orchestrators** and **one fragile
binding pattern**:

1. **`chimera-w1-verify` and `chimera-w2-map` have no `<expected_model>` block.** The
   orchestration *loop* (normalize → resolve → sequence primitives → assemble → report)
   therefore runs at the **session model = Opus by default**, even though every unit of
   judgment inside it has been delegated to a Sonnet worker. The loop is glue; it is
   paying Opus rates.

2. **`chimera-code-taste` / `chimera-sprint-discipline` bind Sonnet/Haiku via prose
   params on generic `general-purpose` spawns, not via pinned agent defs.** If the
   `model:` param is dropped at the call site, the subagent silently inherits the
   session's Opus. This is a latent 3–5× overrun on the bulk of build + scan work
   (code-taste's own estimate, `SKILL.md:50`).

MCP tool calls (`load_criteria`, `fetch_paper`, `convert_pdf_to_md`, `write_result`,
`read_vault_file`, `arxiv_miner`, …) are **not** a model-spend site: they execute
deterministic Python and consume zero model tokens. The model cost *adjacent* to them is
the orchestrator that decides to call them and reads their output — i.e. finding #1.
Counting MCP tools themselves as "implicit Opus" would be a miscount.

---

## Q1 — Skill tasks that explicitly spawn subagents, and the model each should use

| Skill | Spawn task | Correct model (taxonomy) | Bound how / where |
|---|---|---|---|
| `chimera-sprint-discipline` | Repo-wide pattern scans (`SKILL.md:94-98`) | **Haiku** — grep/parse, `output=f(input)` | Prose only: "subagents (Haiku)" + `_shared/subagent_routing.md:8-9` "model: Haiku". **Unpinned.** |
| `chimera-sprint-discipline` | Migration-drift detection (broken imports/files) | **Haiku** — deterministic scan | Prose only. **Unpinned.** |
| `chimera-sprint-discipline` | Test/lint output parsing | **Haiku** — text reduction | Prose only. **Unpinned.** |
| `chimera-code-taste` | Run `check_taste.ps1` + parse tail (`SKILL.md:52-53,60-62,88-94`) | **Haiku** — verdict is the exit code, not prose | Prose: "Haiku via Agent `{model:"haiku"}`". **Unpinned param.** |
| `chimera-code-taste` | Run pytest + summarize failures | **Haiku** — output parsing | Prose param. **Unpinned.** |
| `chimera-code-taste` | Cross-file rule-violation scan | **Haiku** — pattern scan | Prose param. **Unpinned.** |
| `chimera-code-taste` | **Batch-execution delegation** — one worker per 🟢/🟡 sprint (`SKILL.md:71-83`) | **Sonnet** — pre-approved scope + red lines; edit + ruff + pytest | Prose: `Agent(model:"sonnet", general-purpose)`. **Unpinned param.** |
| `chimera-code-taste` | 🔴 sprint execution (`SKILL.md:84-86`) | **Opus** — high blast radius + human gate | Kept in main session OR "explicit-Opus subagent". Correct. |
| `chimera-w1-verify` | `chimera-paper-classifier` (`SKILL.md:30`) | **Sonnet** — 4-class + KG-anchored field | ✅ **Pinned** `model: sonnet` in agent def. |
| `chimera-w1-verify` | `chimera-verbatim-verifier` (`SKILL.md:35`) | **Sonnet** (fidelity-critical — see reverse finding) | ✅ **Pinned** `model: sonnet`. |
| `chimera-w2-map` | `chimera-paper-classifier` (`SKILL.md:28`) | **Sonnet** | ✅ **Pinned**. |
| `chimera-w2-map` | `chimera-breadth-reducer` (`SKILL.md:31`) | **Sonnet** — recon reduction | ✅ **Pinned**. |

**Two binding regimes exist.** The Phase-L workers use **regime (a): pinned frontmatter
`model:`** — robust, cannot be forgotten. The code-taste / sprint-discipline spawns use
**regime (b): a `model:` param passed at the call on a generic `general-purpose` type** —
fragile, silently falls back to session-Opus if omitted. Every gap below is either an
unguarded orchestrator or a regime-(b) site.

---

## Q2 — Call sites with NO effective model spec (implicit session-model = Opus)

| Call site | Runs at | Should run at | Why it's a spend |
|---|---|---|---|
| **`chimera-w1-verify` orchestration loop** (whole skill) | **Session (Opus)** — no `<expected_model>` | **Sonnet** | Claim-normalize, paper-resolve, sequence `load_criteria`/`fetch`/`convert`/`write_result`, assemble, report. All glue; judgment is in the pinned-Sonnet verifier. Runs every W1. |
| **`chimera-w2-map` orchestration loop** (whole skill) | **Session (Opus)** — no `<expected_model>` | **Sonnet** | Bounded-BFS scheduling, wave batching, block assembly, merge, report — resident across ~24 papers × 2 spawns. Longest-lived Opus context in the harness. |
| **code-taste batch-delegation worker** | Sonnet *iff* param passed; else **Opus** | **Sonnet** | Regime (b): unpinned. Bulk of 🟢/🟡 build work. |
| **code-taste verification subagents** | Haiku *iff* param passed; else **Opus** | **Haiku** | Regime (b): unpinned. Every sprint runs these. |
| **sprint-discipline scan/drift subagents** | Haiku *iff* param passed; else **Opus** | **Haiku** | Regime (b): unpinned. Every audit runs these. |
| Phase-L worker agents (classifier/verifier/reducer) | **Sonnet (pinned)** | Sonnet | ✅ Not a gap — regime (a). Banked save. |
| MCP tools in `server.py` (`arxiv_miner`, `ingest_paper`, `fetch_paper`, `convert_pdf_to_md`, `extract_paper`, `check_task_status`, + vault `load_criteria`/`write_result`) | **No model** (deterministic Python) | N/A | Not a model-spend site. Correctly carry no `model:`. Adjacent cost is the caller (rows 1–2). |
| `chimera-bb-persona` final-paragraph restyle (always-active) | Session (Opus) | Sonnet-class | Minor: rides the main turn; not a separate spawn, so not cleanly downgradable without splitting the turn. Noted, not ranked. |

---

## Q3 — Per sprint (L.1a → L.3b): cognitive demand vs model vs whether a skill says so

Build-time execution is routed by `chimera-code-taste`'s `<expected_model>` table
(`SKILL.md:42-54`): read/edit → Sonnet, subagent verify → Haiku, 🔴 → Opus + gate.
Risk levels are from `Phase-L-batch.md`.

| Sprint | Actual cognitive demand | Required model | Current (explicit/default) | `model:` field says so? | Gap |
|---|---|---|---|---|---|
| **L.1a** criteria matrix + `load_criteria` (🟡) | Thin MCP primitive + ordered compose + seed stubs | **Sonnet** | Sonnet (code-taste 🟡→Sonnet, *if param*) | Yes — code-taste table; regime (b) | None (latent unpin) |
| **L.1b** dual-classification subagent (🟡) | Author classifier prompt + field-anchoring convention | **Sonnet** | Sonnet build; product pinned Sonnet | Yes (table) + ✅ agent def pins worker | None |
| **L.2a** `fetch_paper` + `convert_pdf_to_md` (🟡) | Split existing fn; wrap live converter | **Sonnet** (Haiku-leaning; near-mechanical) | Sonnet (*if param*) | Yes (table); regime (b) | Minor (over-provisioned vs Haiku; touches GPU path — leave) |
| **L.2b** `write_result` write+supersede (🔴) | New lifecycle logic, C1 dependency schema, reuse Phase-Q supersede | **Opus** + gate | Opus (main / explicit-Opus + gate) | Yes — code-taste 🔴 rule | None (legit Opus) |
| **L.2c** W1 orchestration (🔴) | **Build:** cross-cutting orchestration design, disposition-before-role, C2 discipline | **Opus** (build) + gate | Opus + gate | Yes (build) | None for build |
| ↳ L.2c **run-time** | Drive the loop: normalize/resolve/sequence/assemble/report | **Sonnet** (run) | **Opus (default)** | **No — `chimera-w1-verify` has no `<expected_model>`** | **GAP (run-time)** |
| **L.3a** `write_result` merge + mark_stale (🟡) | ~30 lines; byte-preserving merge; reuse Phase-Q stale | **Sonnet** | Sonnet (*if param*) | Yes (table); regime (b) | None (latent unpin) |
| **L.3b** W2 orchestration (🔴) | **Build:** parallel-subagent scale design, bounded BFS, wave batching | **Opus** (build) + gate | Opus + gate | Yes (build) | None for build |
| ↳ L.3b **run-time** | Schedule BFS, batch waves, merge, report (workers are Sonnet-pinned) | **Sonnet** (run) | **Opus (default)** | **No — `chimera-w2-map` has no `<expected_model>`** | **GAP (run-time)** |

**The build/run distinction is the crux for the 🔴 sprints.** Designing W1/W2 (L.2c,
L.3b) is genuinely Opus-class one-time work and is correctly gated. *Running* the built
harness is recurring glue and should be Sonnet — but nothing in the W1/W2 skills says so,
so it defaults to Opus on every invocation.

---

## The five highest-spend gaps (Opus → Sonnet/Haiku, zero quality loss)

Ranked by frequency × per-run token volume × how cleanly the downgrade preserves quality.

### 1. W2 orchestration loop runs at Opus — `chimera-w2-map` has no `<expected_model>`
**Now:** session-Opus. **Should be:** Sonnet.
The W2 driver is resident across a bounded-BFS over up to 24 papers, coordinating ~48
worker spawns, merging keyed blocks, and writing — the **longest-lived Opus context in
the entire harness**. Every unit of judgment is already delegated to Sonnet-pinned workers
(`chimera-paper-classifier`, `chimera-breadth-reducer`), so the loop itself is pure
scheduling/assembly. Downgrading the loop to Sonnet loses no judgment quality.
**Fix (not applied):** add an `<expected_model>` block to `chimera-w2-map` recommending
Sonnet for the orchestration loop.

### 2. W1 orchestration loop runs at Opus — `chimera-w1-verify` has no `<expected_model>`
**Now:** session-Opus. **Should be:** Sonnet.
W1 is the ROI-core the Architect runs most often ("N times at 20–30 min each"). The loop —
claim-normalize, paper-resolve, sequence the primitives, assemble the verdict, report —
is glue; the verdict itself is produced by the Sonnet-pinned `chimera-verbatim-verifier`.
Highest *frequency* spend. **Fix (not applied):** add an `<expected_model>` block to
`chimera-w1-verify` recommending Sonnet for the loop (workers stay Sonnet-pinned).

### 3. Batch-execution delegation defaults to Opus when the `model:"sonnet"` param is dropped
**Now:** Sonnet iff remembered, else session-Opus. **Should be:** Sonnet (pinned).
`chimera-code-taste` delegates each 🟢/🟡 sprint to a generic `general-purpose` worker with
a *prose-instructed* `model:"sonnet"` (`SKILL.md:71-83`) — regime (b), unpinned. 🟢/🟡
sprints are the bulk of build work; a dropped param is code-taste's own "~3–5× overrun"
(`SKILL.md:50`). Sprints are pre-approved with red lines + file scope, so Sonnet is the
designed tier — Opus buys nothing. **Fix (not applied):** define a dedicated
Sonnet-pinned executor agent type (regime (a)) instead of a prose param on
`general-purpose`.

### 4. code-taste verification subagents default to Opus when `model:"haiku"` is dropped
**Now:** Haiku iff remembered, else session-Opus. **Should be:** Haiku (pinned).
`check_taste.ps1` tail parsing, pytest/ruff summarizing, cross-file scans — the contract
already says the **verdict is the exit code, not the subagent's prose** (`SKILL.md:88-93`),
so the reasoning is deterministic and Haiku-class. Running these at Opus is pure waste on
every sprint. **Fix (not applied):** pin Haiku on a dedicated verification agent type.

### 5. sprint-discipline scan/drift subagents default to Opus when `model:"haiku"` is dropped
**Now:** Haiku iff remembered, else session-Opus. **Should be:** Haiku (pinned).
Repo-wide pattern scans, migration-drift detection, test/lint parsing (`SKILL.md:94-98`;
`_shared/subagent_routing.md:8-9`) are grep/parse — `output=f(input)`. Every phase audit
runs these, and a phase audit is itself typically an Opus session, so the fallback lands
squarely on Opus. **Fix (not applied):** pin Haiku on a dedicated scan agent type.

**Shared root cause for #3–#5:** the project has a robust binding mechanism (regime (a):
pinned agent-def frontmatter, as used by the three Phase-L workers) and a fragile one
(regime (b): a `model:` param on a generic `general-purpose` spawn). #3–#5 are all regime
(b). Converting them to regime (a) removes the "operator forgot the param" failure mode
entirely. #1–#2 are a different miss: the orchestrator skills lack the `<expected_model>`
guardrail that code-taste and sprint-discipline already have.

---

## Secondary findings (not over-spend; recorded for completeness)

- **Reverse gap — `chimera-verbatim-verifier` may be *under*-provisioned at Sonnet.**
  This is the fidelity-critical operation of the whole instrument: graded [V]/[P]/[U] with
  disposition-correction (counter over-denigrate/over-defer, non-binary) applied over
  vault criteria. That is closer to cross-cutting judgment than to pattern-matching. The
  project's own north star — "fidelity is the scarce good; advisory rigor is negative
  value" (CLAUDE.md) — argues *against* cheapening the verifier. Not a cost gap (it is the
  opposite); flagged as a quality watch. If verdict quality is ever doubted, the verifier
  is the first place to try Opus, and the high-stakes adversarial pair (phase-L.md load
  sequence step 4 / Notes L.3) is the sanctioned place for it.
- **`chimera-paper-classifier` bundles a Haiku-class sub-decision into a Sonnet worker.**
  The closed-4-class `type` (benchmark/method/theory/survey) from title+abstract is
  near-deterministic (Haiku); the KG-anchored `field` genuinely needs Sonnet. As a single
  worker the correct floor is Sonnet, and splitting it would add spawn overhead + latency
  ×24 in W2. **Leave as Sonnet** — this is a Sonnet-tier micro-optimization, not an
  Opus→cheaper win, so it is out of the top-5 by construction.
- **L.2a primitives (`fetch_paper`/`convert_pdf_to_md`) are Haiku-leaning but routed
  Sonnet.** Near-mechanical lifts of existing code, but they touch the GPU/MinerU path;
  Sonnet is the defensible-conservative choice. Marginal.

---

## Recommended remediation (stated, NOT applied)

1. Add an `<expected_model>` block (Sonnet for the loop) to **`chimera-w1-verify`** and
   **`chimera-w2-map`** — closes gaps #1–#2, the recurring run-time spend.
2. Replace regime-(b) prose params with **pinned agent-def types** for the three
   recurring build/scan roles — closes gaps #3–#5, the latent fallback-to-Opus:
   - a Sonnet-pinned **sprint-executor** type (batch delegation),
   - a Haiku-pinned **verification** type (check_taste/pytest/ruff parsing),
   - a Haiku-pinned **scan** type (pattern/drift scans).
3. Keep the Phase-L worker pins (Sonnet) and the 🔴-sprint Opus + human gate exactly as
   they are — they are correct.

*Generated as a static routing audit. No skills, agents, or code were modified.*
