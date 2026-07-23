# INVARIANT RULES AUDIT — Rules-level SOT reconnaissance

**Status:** 🔵 AUDIT ARTIFACT (read-only). Not an authority. Input for the author of a future
`docs/ARCHITECTURE/ARCHITECTURE_RULES.md`.
**Authored:** 2026-07 (post-L.B.2 correction).
**Scope:** ALL authoritative documents — every `SKILL.md` + `references/*.md` + `_shared/*.md`
under `.claude/skills/`, all `docs/ARCHITECTURE/*.md`, and `docs/phases/phase-{K,L,L.B}.md`.
This is a **rules** audit, not a code audit. No running code was touched or inspected for behavior;
only what the documents *assert as constraints*.

**Method.** Each authoritative document was read in full (fidelity-critical docs read directly;
peripheral skills via two parallel read-only extraction passes). Every statement that *functions
as a rule* — "X must always Y", "X must never Z", "all A go through B", "no code path may do C" —
was extracted with its `file:line`, then classified by **Level** and **Status**.

- **Level** — the altitude a rule operates at. Conflating these is the L.B.2 error's root cause.
  - `ARCHITECTURE` — a system-wide invariant that must hold across ALL phases regardless of what
    is currently implemented.
  - `SPRINT` — a single-phase / process constraint (true for a phase, a mode, a workflow).
  - `STYLE` — a code-quality / formatting constraint.
- **Status** — `LIVE` (still valid and in force) · `STALE` (superseded by a later phase) ·
  `CONTRADICTED` (another rule says the opposite) · `IMPLICIT` (inferred from several statements;
  never stated as a single rule) · `DRAFT` (proposed, pending ratification) ·
  `VISION-NOT-ENFORCED` (stated as a rule but the enforcing code does not yet exist).

---

## Section 0 — The five principle categories: verdicts first

This is the heart of the audit. For each category the question is: **is there an EXPLICIT
architecture-level rule, or does the principle live only as (a) ST/phase discussion, (b) implicit
in code / tool docstrings, or (c) nowhere?** The L.B.2 error happened because a genuine
architecture invariant ("judgment lives in Claude subagents") existed only as a *definition* and a
*phase discussion*, while a SPRINT-level habit ("extend, don't rebuild; minimal modification") was
the only thing stated as an operative rule at the executor's altitude — so the executor followed the
SPRINT rule and wired an Anthropic/LLM call into an MCP server.

| # | Principle | Explicit ARCH rule today? | Where it actually lives | Verdict |
|---|---|---|---|---|
| 1 | **Judgment substrate** — MCP servers must not call any LLM (any vendor) | **NO** | Path-scoped skill red-lines (`chimera-deep-extract:23-25,72-74`; `chimera-triage-paper:23-27,63-65`) + a *generated description* (`ARCHITECTURE.md:48`). `chimera-dependency-veto:42` even *permits* the `openai` SDK. | **(a)+(b), not a standing invariant.** The single highest-risk gap. See §4-M1. |
| 2 | **Human-time supremacy** (dual clock: machine-time = candidates, human-time = truth) | **NO** — it is a *Definition + Theorem*, not a rule | `THEORETICAL_FRAMEWORK.md §1` (Def 2, Theorem 1, Corollary) — which *self-defers* to operational authorities. Consequences scattered as phase-scoped rules. | **Definition only.** "A definition can be ignored; a rule cannot." See §4-M2. |
| 3 | **Staging gate** — all candidates reach a committed tier only through review | **PARTIAL** | `phase-L.B` red-line + HSC-3 (`ascend_node` sole path to `Knowledge/`, "impossible by code constraint"); `CLAUDE.md` "Never auto-promote `docs/staging/`". Tool docstrings advisory. | **(b) + one narrow CLAUDE.md hard rule, phase-scoped.** Not a cross-phase invariant. See §4-M3. |
| 4 | **Tier integrity** — `chimera_tier` distinguishes origin/depth and is orthogonal to `status` | **YES (post-L.B.1)** | `NODE_ONTOLOGY.md §7` — an architecture authority: "never folded into each other", "`knowledge` is never defaulted", `Knowledge/` requires `deep_read`. | **The one category properly elevated to an authority.** Pre-L.B.1 it was NOWHERE (the C-1 CRITICAL gap). Now LIVE. See §1. |
| 5 | **Provenance load-bearing** — `[V]/[P]/[U]` must be structural (pipeline enforces), not advisory (agent respects) | **STATED, NOT ENFORCED** | `phase-K.md` red-line (strongest); `THEORETICAL_FRAMEWORK.md §3`; `PHILOSOPHY.md §3` ("enforce or delete" — was `chimera-core-philosophy:26-30`, skill retired 2026-07-23). But Phase K is **Qued** and `write_result`'s `verdict` is still an unvalidated `str` (`TAG_SYSTEM.md §9`). | **VISION-NOT-ENFORCED.** Today the tag is still advisory in code. See §4-M5. |

**The through-line.** Four of the five load-bearing principles (1, 2, 3, 5) are **not** stated as
architecture-level invariant rules in any operational document. Only category 4 (tier integrity)
was correctly elevated — and only *after* the C-1 audit forced it. This is the structural pattern
that produces L.B.2-class errors: the project's deepest commitments live as *philosophy, theory, and
phase-scoped red-lines*, while its executors act on *style and sprint* rules. The levels are not
reconciled anywhere.

---

## Section 1 — Explicit Architecture Rules (currently in force as rules)

Rules that ARE stated, ARE architecture-level (or the strongest operational form of one), and are
LIVE. This is the existing — scattered — de-facto SOT.

| Source | Statement (abbrev.) | Level | Status |
|---|---|---|---|
| `NODE_ONTOLOGY.md:130-131` | "Two ORTHOGONAL frontmatter axes … never folded into each other (Phase L.B red line: tier is not carried by `status`)." | ARCHITECTURE | LIVE |
| `NODE_ONTOLOGY.md:146-148` | "Why `knowledge` is never defaulted … a `knowledge` node created with no tier stays untiered so its writer is FORCED to declare `scout` vs `deep_read`." | ARCHITECTURE | LIVE |
| `NODE_ONTOLOGY.md:37-61` | Canonical 7-edge typed-edge vocabulary + per-type sets; "this file is the single place the K/T/I/D typed-edge vocabulary is defined." | ARCHITECTURE | LIVE |
| `NODE_ONTOLOGY.md:159-166` | Scout card `unverified` is "terminal-until-human"; scout tier stays in `inbox/` and is NEVER auto-promoted; `unverified → active` fires only via `ascend_node`. | ARCHITECTURE | LIVE |
| `TAG_SYSTEM.md:13-18` | "single source of truth for what `[V]`, `[P]`, `[U]` MEAN … Every consumer … must **reference** this file, never restate the definition." | ARCHITECTURE | LIVE |
| `TAG_SYSTEM.md:107-109` | "a `[V]` quote must come from Tier 1 or Tier 2. A quote from Tier 3 supports **at most `[P]`**." | ARCHITECTURE | LIVE (def) |
| `TAG_SYSTEM.md:164-166` | "**Gate 1 operates ONLY on `[V]/[P]/[U]`.** A Phase-Q K-node claim status is **not** a valid Gate-1 dependency until explicitly re-expressed … never automatic." | ARCHITECTURE | LIVE |
| `THEORETICAL_FRAMEWORK.md:110-113` | Separation Principle: source-verification (harness) and taste-verification (Architect) are *structurally* separate; the harness never settles taste. | ARCHITECTURE | LIVE (as theory) |
| `THEORETICAL_FRAMEWORK.md:19-24` | Drift rule: where this doc and an operational authority disagree on a detail, the authority wins and this doc defers. | ARCHITECTURE | LIVE |
| `CLAUDE.md` Hard rules | "This repo has ONE user. Do not generalize." | ARCHITECTURE | LIVE |
| `CLAUDE.md` Hard rules | "Never auto-promote `docs/staging/` candidates to the vault — user-reviewed." | ARCHITECTURE | LIVE (narrow) |
| `CLAUDE.md` Hard rules | "Do not invent MCP tools without a friction signal." | ARCHITECTURE | LIVE |
| `CLAUDE.md` Hard rules | "Obsidian vault `templates/` are user-synced; edit repo sources, not vault copies." | ARCHITECTURE | LIVE |
| `PHILOSOPHY.md §3` / `CLAUDE.md §Product philosophy` | "Advisory rigor is negative value … does it enforce, or just perform? Enforce it or delete it." (was `chimera-core-philosophy:26-30`; skill retired 2026-07-23, principle elevated to static docs) | ARCHITECTURE | LIVE (principle) |
| ~~`chimera-core-philosophy:40-41`~~ | "Chimera is an agent. Never drift toward YAML-defined workflows." | ARCHITECTURE | RETIRED 2026-07-23 (rarely violated; source deleted) |
| ~~`chimera-core-philosophy:52-57`~~ | Single-user: skip multi-provider / sandboxing / plugin SDKs / distributed tracing — "SaaS thinking contamination." | ARCHITECTURE | RETIRED 2026-07-23 (rarely violated; source deleted) |
| ~~`chimera-core-philosophy:70`~~ | Four-layer model (Persona/Skill/Tool/Lens) — "Never conflate these layers." | ARCHITECTURE | RETIRED 2026-07-23 (arch-volatile; source deleted) |
| `chimera-dependency-veto:13-29` | Permanent dependency vetoes (agent frameworks, structured-gen libs, observability, queues, vector DBs, auth/sandbox libs). | ARCHITECTURE | LIVE |
| `chimera-dependency-veto:43` | "**Never** add native `anthropic` / `google-generativeai` / `cohere` SDKs." | ARCHITECTURE | LIVE (but see §3-C1) |
| `chimera-mcp-taste/mcp_rules.md:177-178` | "Business logic never lives in `server.py` … thin adapter (<200 lines) … the concurrency guard is the one sanctioned exception (Phase M red line)." | ARCHITECTURE | LIVE |
| `_shared/subagent_routing.md:9-13` | Delegate to a PINNED agent type — model in the agent def's frontmatter, "never a call-site `model:` param." | ARCHITECTURE | LIVE |
| `_shared/subagent_routing.md:32-36` | "A subagent's prose is evidence for the main session, never the verdict." | ARCHITECTURE | LIVE |
| `_shared/doc_folders.md:29-32` | "Neither skill writes `phases/`; it is user-authored intent." / "Source code and architecture docs are written only by code-taste, within sprint scope." | ARCHITECTURE | LIVE |
| `_shared/falsifiability.md:13,37-40` | A lens analysis is incomplete without Mechanism + Evidence + Falsifiability; an unfalsifiable claim must be reported as such, "do not launder it into a finding." | ARCHITECTURE | LIVE |
| `chimera-bb-persona:85-88, 172-175` | "Substance is invariant. BB changes tone, never facts, numbers, `file:line`, or the recommendation." / restyle final answer only, never reasoning or tool output (Phase M reasoning-transparency red line). | ARCHITECTURE | LIVE |
| `chimera-sprint-discipline:71-78` | "NEVER WRITE in any mode: CLAUDE.md; Skill files; Source code; Architecture docs; `docs/phases/*` … only humans write intent." | ARCHITECTURE | LIVE |
| `chimera-code-taste/SKILL.md:51-53` | "Model binding is PINNED in the agent definitions, never passed as a call-site `model:` param." | ARCHITECTURE | LIVE |
| `chimera-code-taste/SKILL.md:95-101` | Pass/fail decided from the exit code ALONE, "never from the subagent's prose"; missing/non-integer exit code = FAIL. | ARCHITECTURE | LIVE (evidence-authority) |

**Path-scoped judgment-substrate rules (the closest thing to a category-1 rule that exists).**
These are LIVE and correct, but SPRINT-level and *per-path*, not a system invariant:

| Source | Statement | Level | Status |
|---|---|---|---|
| `chimera-deep-extract:23-25` | "The MCP server (`chimera-papers`) makes NO LLM call anywhere in this path (L.B.2) … the server is never the judge." | SPRINT | LIVE (path-scoped) |
| `chimera-deep-extract:72-74` | "NEVER via deepseek or an Anthropic client inside the MCP server (`chimera-papers/server.py` makes NO LLM call, period)." | SPRINT | LIVE (path-scoped) |
| `chimera-triage-paper:63-65` | identical "NO LLM call … the server is never the judge." | SPRINT | LIVE (path-scoped) |
| `phase-L.md:166-169` | "W1/W2 are Claude Code orchestration, not MCP tools … Judgment never lives in an MCP tool." | SPRINT | LIVE (W1/W2-scoped) |
| `ARCHITECTURE.md:48` | "the MCP servers make NO LLM call." | — (generated *description*, not a rule) | LIVE description; see §3-C2 |

---

## Section 2 — Stale Rules (once valid, superseded by later phase changes)

| Source | Original statement | What changed | Why stale |
|---|---|---|---|
| `NODE_ONTOLOGY.md:9-11` | "This is the authority the deferred **Phase N.B** `deep_recall` will traverse. The vault graph is empty today (N.B.0 Q4)…" | Phase N.B (deep recall) was **CANCELLED** (2026-07-09) and Phase N sealed/truncated; retrieval retired until the vault-in-loop defect is fixed. | The rule's stated *purpose* (feed a future `deep_recall`) no longer holds. The edge vocabulary itself is LIVE; only the N.B justification is stale. |
| `NODE_ONTOLOGY.md:89-104 (§4)` | "What O.1b changes in code (do NOT execute here — O.1a is doc-only) … On ratification, `_TYPE_EDGES` becomes…" | O.1a ratified 2026-07-07; O.1b mirrored the set into `staging_service.py`. | Forward-looking sprint instruction, now completed. Reads as pending work; is done. Content LIVE, framing stale. |
| `TAG_SYSTEM.md:3-9` (status 🟡 DRAFT) + `§4/§5/§7` marked **⚖ RATIFY** | Tier taxonomy, "robust" P/U resolution, and the crosswalk are "proposed design decisions … pending the Architect's sign-off." | Still unratified at audit time. | Not stale — **DRAFT**. Flagged here so a canonical SOT does not cite §4/§5/§7 as settled law. |
| `TAG_SYSTEM.md:213-221 (§9)` | Consumer convergence table: `write_result` "`verdict: str` unvalidated → `Literal["V","P","U"]`"; verifier agent "no Tier clause". | These are *targets*, not yet all done. | The rules they point to (schema-reject verdict) are **VISION-NOT-ENFORCED** — see §4-M5. Listed as stale-if-read-as-done. |
| `chimera-mcp-taste` (whole skill) | Ten seam rules, all sourced from "real Phase M / M.5 incidents." | Still LIVE — but note the skill was **not updated after L.B.2**: it gained no "no LLM in server" principle even though L.B.2 was exactly an MCP-layer taste failure. | Not stale in content; stale in *coverage*. The one skill that should own category-1 does not. (Cross-ref §4-M1.) |

*Note:* Phase-K's `Status: Qued` (`phase-K.md:2`) is not "stale" — it is a not-yet-executed phase.
Its rules are VISION-NOT-ENFORCED, tracked under §4-M5, not here.

---

## Section 3 — Contradicted Rules (two documents say opposite things)

| # | Rule A | Rule B | Nature | Which should win |
|---|---|---|---|---|
| C1 | `chimera-dependency-veto:42` — "Only `openai` Python SDK. Other providers via OpenAI-compatible base URL." (an LLM SDK is *permitted*, with no restriction on *where* it is called) | `chimera-deep-extract:72-74` / `chimera-triage-paper:63-65` — "server … makes NO LLM call, period." | **Latent, level-crossing.** Dependency-veto sanctions the very SDK by which an in-server LLM call is made (this is how deepseek judgment lived in-MCP pre-L.B). The skill red-lines forbid the call only *on their own paths*. Nothing forbids it generally. | Neither is wrong at its altitude; the **missing** rule (§4-M1) must reconcile them: "the `openai` SDK is permitted for the Architect's cross-model *primitives*, never for judgment, and never inside an MCP server process." |
| C2 | `ARCHITECTURE.md:48` (generated SOT) — "the MCP servers make NO LLM call." | `phase-L.B.md:61-62` — "deepseek is retired as a JUDGMENT model. It **may remain for cheap data extraction** (citation parsing, etc.)." | **Direct.** "May remain for extraction" = an in-server LLM call is permitted; the generated diagram asserts none exist. | Resolve explicitly. Either (a) the L.B carve-out is dead and the invariant is "zero LLM calls in-server" (then `phase-L.B:61-62` must be retired), or (b) the carve-out lives and `ARCHITECTURE.md:48` must read "no LLM *judgment* call." The audit recommends (a) — the carve-out is the exact seam L.B.2 slipped through. |
| C3 | `THEORETICAL_FRAMEWORK.md` (ARCHITECTURE invariant) — "judgment lives in Claude subagents / the harness never settles." | `chimera-code-taste` minimalism cluster — `batch_execution_process.md:43` "Never reconstruct via Write"; `rules_and_antipatterns.md:6` "≤3 files / ≤50 new lines"; `taste_rules.md:119` "mixes no refactor into feature work." (the "minimal modification / EXTEND not rebuild" ethos) | **Level conflation — the archetypal L.B.2 fault.** No content contradiction, but when a task says "migrate `single_paper_extract` to Sonnet", the SPRINT minimalism rule ("extend in place, small diff") points *toward* wiring an LLM client into the existing server, while the ARCHITECTURE invariant demands *restructuring* to a subagent. The invariant is not stated at the executor's altitude, so the SPRINT rule won. | The ARCHITECTURE invariant must **always** win over SPRINT minimalism, and must be *stated as such*. Minimal-diff is subordinate to substrate correctness. This is the single most important structural lesson. |
| C4 | `THEORETICAL_FRAMEWORK.md §1:51-52` — 4-edge subset `{derives_from, synthesizes, contradicts, dead_ends}`. | `NODE_ONTOLOGY.md §2` — canonical **7**-edge vocabulary. | **Resolved, annotated.** TF explicitly labels its set "illustrative" and defers (`§1:55-57`, `§9:291`). | `NODE_ONTOLOGY.md` (already the authority). No action — documented here only to confirm the drift rule is working as intended. |
| C5 | `CLAUDE.md` — "Never auto-promote `docs/staging/` candidates … user-reviewed." (implies *all* candidates are review-gated) | Scout path (`chimera-triage-paper:66-68`, `NODE_ONTOLOGY.md §7.2`) — scout cards auto-write to `inbox/` at `status: unverified`, *not* to `docs/staging/`. | **Apparent, not real.** `inbox/` ≠ `docs/staging/`; the scout card is human-gated by tier (`ascend_node`), so nothing is *promoted*. But the CLAUDE.md rule's wording undersells a second review surface. | Keep the CLAUDE.md rule; a canonical SOT should generalize it to "no candidate (any tier, any location) advances to a committed tier without a human event" — see §4-M3. |

---

## Section 4 — Missing Rules (architecture principles with no explicit rule statement)

**Priority-ranked by likelihood of causing an L.B.2-class error** (a genuine invariant, invisible at
the executor's altitude, silently violated by a locally-reasonable edit). Each entry names the
principle, where it appears *implicitly*, and a proposed canonical statement.

### M1 — 🔴 HIGHEST: "No MCP server process may call any LLM (any vendor, any purpose)."
- **This is the L.B.2 rule.** It is the one whose absence directly caused the error under audit.
- **Appears implicitly in:** `THEORETICAL_FRAMEWORK.md` Separation Principle (judgment vs harness);
  `phase-L.md:166-169` (W1/W2-scoped); `chimera-deep-extract:72-74` & `chimera-triage-paper:63-65`
  (path-scoped, post-hoc); `ARCHITECTURE.md:48` (a *generated description*, self-erasing at each
  regen); `chimera-mcp-taste/mcp_rules.md:177-178` (thin adapter — but this only pushes logic to the
  *service layer*, where an LLM client would still sit *inside the server process* and pass the rule).
- **Actively undercut by:** `chimera-dependency-veto:42` (permits `openai` SDK) and
  `phase-L.B.md:61-62` (permits in-server deepseek for extraction). See §3-C1, §3-C2.
- **Why nothing caught it:** `chimera-mcp-taste`, the skill that owns MCP-layer taste, has *no such
  principle* — its ten rules are about PATH/console/stdio/deps/adapter-thinness. `thin_adapter`
  explicitly *allows* business logic in the service layer. An executor following "extend, minimal
  diff" (§3-C3) plus "openai SDK is fine" (dependency-veto) violates **no stated rule**.
- **Proposed canonical statement:** *"An MCP server process (server.py and every module it imports at
  runtime) MUST NOT call any LLM — not deepseek, not the `openai` SDK against any base URL, not the
  `anthropic` SDK, not any hosted model. All LLM judgment lives in Claude Code Task subagents. MCP
  provides only non-LLM primitives (fetch, convert, read, query, deterministic transform, write).
  This holds regardless of vendor, purpose (judgment OR 'cheap extraction'), or how small the diff.
  Retire the `phase-L.B:61-62` deepseek-for-extraction carve-out."*

### M2 — 🔴 "Belief advances only on a human event; machine-time produces candidates only."
- The dual-clock is the deepest architectural commitment in the system and exists **only as a
  Definition + Theorem** (`THEORETICAL_FRAMEWORK.md §1:59-75`), which self-defers to operational
  authorities that never restate it as a rule.
- **Appears implicitly in:** `phase-L.B` `ascend_node`-is-the-only-gate red-line; `CLAUDE.md`
  never-auto-promote; every skill's "nominate vs promote" language (`chimera-w2-map:56,69`).
- **Why it is a risk:** a definition can be "honored in spirit" and quietly bypassed by any new write
  path that doesn't route through `ascend_node`. Nothing states, at the code-authoring altitude, that
  *no code path may transition a node to a committed/believed state except a human-invoked action.*
- **Proposed canonical statement:** *"No code path may advance a node's belief state (uncommitted →
  committed, `unverified`/`PENDING_REVIEW` → `active`). Only a human-invoked action (`ascend_node`,
  `promote_node`, manual Obsidian edit) does. Machine-time (pipelines, subagents, W1/W2) produces
  only `PENDING`/`unverified` candidate material. Any new write path MUST leave belief unchanged."*

### M3 — 🟡 "Every candidate reaches a committed tier only through a single human-gated ascension path."
- Category 3. Strong but **phase-scoped** (`phase-L.B` HSC-3) and split across `inbox/` (scout) vs
  `docs/staging/` (deep_read) with only a narrow `CLAUDE.md` line generalizing it.
- **Appears implicitly in:** `phase-L.B:57-58,80-82`; `NODE_ONTOLOGY.md §7.2`; tool docstrings
  (`create_node` "never writes into the live vault", `ascend_node` "SOLE code path that writes
  `Knowledge/`") — but docstrings are advisory, not a stated invariant.
- **Proposed canonical statement:** *"`Knowledge/` (the committed K tier) has exactly one writer:
  `ascend_node`, which requires `chimera_tier=deep_read` and a human invocation. No other code path
  may write to a committed tier. Scout (`inbox/`) and staging (`docs/staging/`) are both
  human-gated holding tiers; neither auto-advances."*

### M4 — 🟡 "Provenance / edges are produced by deterministic resolution, never fabricated by a model."
- The "never fabricate edges/quotes" rule is stated per-path (`chimera-deep-extract:53-55,79-80`
  "edges minted ONLY by deterministic citation-resolution … never accept an `edges` field from the
  subagent"; `chimera-w1-verify:64` "no tag without a verbatim quote") but never generalized.
- **Why it matters:** it is the structural guarantee behind `[V]` and behind graph integrity. Stated
  once, system-wide, it prevents a future writer from letting a subagent propose edges "to save a
  step."
- **Proposed canonical statement:** *"Typed edges and `[V]` grounding quotes are produced only by
  deterministic resolution (citation matching, verbatim extraction with location). No LLM output is
  accepted as an edge set or as grounding without deterministic verification. A claim that cannot be
  deterministically grounded is `[U]` — never a fabricated `[V]`."*

### M5 — 🟡 "`[V]/[P]/[U]` propagation is structural (schema-enforced), never advisory."
- Category 5. Stated forcefully (`phase-K.md:90-93`, `THEORETICAL_FRAMEWORK.md §3:129-130`,
  `PHILOSOPHY.md §3`) but **VISION-NOT-ENFORCED**: Phase K is Qued and `write_result`'s
  `verdict` is still an unvalidated `str` (`TAG_SYSTEM.md §9:216`). Today the tag *is* advisory.
- **Status caveat:** this is not "missing" so much as "stated as a rule the code does not yet keep."
  A canonical SOT should list it as a **committed-but-pending** invariant, with the enforcement debt
  (schema `Literal["V","P","U"]`, Gate-1 monotonicity) named explicitly so it cannot be quietly
  dropped when Phase K is built.
- **Proposed canonical statement:** *"A verdict tag is only as real as its schema. `write_result`
  MUST reject any `verdict` not in `{V,P,U}`; Gate 1 MUST force a synthesis's status ≤ its weakest
  recorded dependency, computed from recorded `depends_on`, never re-inferred by an LLM. Until this
  is code, `[V]/[P]/[U]` is advisory and — by the project's own north star — negative value."*

### M6 — 🟢 "Every fidelity mechanism must enforce or be deleted (the anti-theater rule)."
- This *is* stated (`PHILOSOPHY.md §3`, `CLAUDE.md §Product philosophy`) — elevated to static docs; the STYLE-tier skill that originally held it was retired 2026-07-23. It is the meta-rule under M1/M4/M5.
- **Proposed canonical statement (elevate, don't invent):** *"No advisory rigor. Before any
  provenance flag, criteria file, tier field, or verifier ships, state its enforcement mechanism
  (what schema/gate/code path makes it load-bearing). If there is none, it is theater — delete it or
  do not build it. This is a seal condition, not a preference."*

### M7 — 🟢 "Levels are explicit; an ARCHITECTURE invariant outranks any SPRINT/STYLE rule."
- **The meta-missing-rule this entire audit exists to surface.** Nowhere does any document state that
  rules have altitudes, or that a system invariant beats a local minimalism rule when they pull in
  opposite directions (§3-C3). L.B.2 is precisely this collision resolved the wrong way.
- **Proposed canonical statement:** *"Every rule declares its level (ARCHITECTURE / SPRINT / STYLE).
  When two rules conflict, the higher altitude wins, always: an architecture invariant is never
  traded away for a smaller diff, a faster sprint, or 'extend not rebuild.' If honoring an invariant
  requires rebuilding rather than extending, rebuild."*

---

## Section 5 — Recommended canonical `ARCHITECTURE_RULES.md` structure

Not the document itself — the proposed headings and which rules belong under each, as input for the
author. The organizing principle: **one file, all invariants, each with (level, enforcement
mechanism, status).** Every entry must name *how* it is enforced, or be marked
`VISION-NOT-ENFORCED` — the anti-theater rule (M6) applied to the SOT itself.

```
# ARCHITECTURE_RULES.md — Chimera Lite invariant rules (the SOT)
  Preamble:
    - This file lists ONLY architecture-level invariants (hold across ALL phases).
    - Each rule: ID · Statement · Enforcement mechanism · Status (LIVE / VISION-NOT-ENFORCED).
    - Rule 0 (the meta-rule, M7): levels are explicit; ARCHITECTURE > SPRINT > STYLE on conflict.
    - Drift rule: phase docs and skills REFERENCE this file; they never restate or override it.

  §1  Judgment substrate            ← M1 (new), §3-C1/C2 reconciliation, path-scoped rules promoted
      - AR-1  No LLM call inside any MCP server process (any vendor, any purpose).
      - AR-2  All LLM judgment lives in pinned Claude Code Task subagents.
      - AR-3  MCP provides non-LLM primitives only.
      - AR-4  openai/anthropic SDK policy (reconcile dependency-veto:42-43 with AR-1).

  §2  The dual clock (belief authority)   ← M2, THEORETICAL_FRAMEWORK §1 elevated
      - AR-5  Belief advances only on a human event.
      - AR-6  Machine-time produces PENDING/unverified candidates only.

  §3  Ascension & tiers             ← M3, §4 tier-integrity rules (already LIVE in NODE_ONTOLOGY §7)
      - AR-7  Knowledge/ has one writer: ascend_node, human-invoked, requires deep_read.
      - AR-8  chimera_tier ⟂ status; K is never tier-defaulted. (ref NODE_ONTOLOGY §7)
      - AR-9  No candidate auto-advances from inbox/ or docs/staging/.

  §4  Provenance & the graph        ← M4, M5, TAG_SYSTEM + phase-K
      - AR-10 Edges/quotes are deterministic, never model-fabricated.
      - AR-11 [V]/[P]/[U] semantics: reference TAG_SYSTEM.md; Tier-1/2 required for [V].
      - AR-12 Gate 1 monotonicity is schema-structural, from recorded depends_on. [VISION-NOT-ENFORCED]
      - AR-13 write_result.verdict is schema-restricted to {V,P,U}. [VISION-NOT-ENFORCED]

  §5  Anti-theater (the north star as a gate)   ← M6, core-philosophy elevated
      - AR-14 Enforce or delete: no advisory rigor ships without a named enforcement mechanism.

  §6  Scope & shape (the project's identity)    ← existing CLAUDE.md + core-philosophy rules
      - AR-15 One user; do not generalize.
      - AR-16 Chimera is an agent; no YAML workflows; no framework drift.
      - AR-17 No new dependency without a friction signal; honor the veto list.
      - AR-18 Four-layer model (Persona/Skill/Tool/Lens) — never conflate.

  §7  Authorship & write authority   ← sprint-discipline / doc_folders / bb-persona
      - AR-19 Humans author intent: phases/, CLAUDE.md, skills, source (except in-sprint), arch docs.
      - AR-20 Subagent prose is evidence, never the verdict; pass/fail from exit code alone.
      - AR-21 Model pins live in agent defs, never call-site params.
      - AR-22 Reasoning transparency: persona restyles the verdict only, never reasoning/tool output.

  Appendix A — Level index: which existing SPRINT/STYLE rules are subordinate to which AR-invariant.
  Appendix B — Enforcement debt register: every VISION-NOT-ENFORCED rule + the phase that lands it.
```

**Authoring guidance for the SOT writer:**
1. **Promote, don't invent.** AR-4/AR-8/AR-11 and all of §6/§7 already exist as LIVE rules (Section 1)
   — the SOT's job is to *collect and level them*, plus add the four genuinely missing ones
   (AR-1, AR-5, AR-7-general, AR-10) and elevate two principles (AR-14, Rule 0).
2. **Every rule names its enforcement.** If a rule cannot name a schema/gate/code path that makes it
   load-bearing, mark it `VISION-NOT-ENFORCED` and add it to Appendix B — never let it read as LIVE.
   (This is M6 applied reflexively.)
3. **Reconcile §3-C1/C2 before publishing.** The `openai`-SDK permission and the deepseek-extraction
   carve-out must be explicitly retired or explicitly bounded; leaving both live re-opens M1.
4. **Update `chimera-mcp-taste`** to reference AR-1 as its 11th principle — the MCP-taste skill is
   where an executor doing MCP work will look, and today it is silent on the one rule that matters most.
5. Add a one-line pointer to this SOT from `CLAUDE.md` Hard rules and from `TAG_SYSTEM.md §9` /
   `THEORETICAL_FRAMEWORK.md §9` consumer tables, so the drift rule binds it to the existing authorities.

---

## Appendix — Coverage & confidence

- **Read directly (fidelity-critical):** `THEORETICAL_FRAMEWORK.md`, `ARCHITECTURE.md`,
  `TAG_SYSTEM.md`, `NODE_ONTOLOGY.md`, `phase-K.md`, `phase-L.md`, `phase-L.B.md`,
  `chimera-mcp-taste/{SKILL.md,references/mcp_rules.md}`.
- **Read via parallel read-only extraction:** the remaining 16 `SKILL.md`, 9 `references/*.md`,
  and 6 `_shared/*.md` (chimera-sprint-discipline + refs, chimera-code-taste + refs,
  chimera-dependency-veto, chimera-commit-style, chimera-academic-observe, chimera-bb-persona,
  chimera-w1-verify, chimera-w2-map, chimera-deep-extract, chimera-triage-paper, six lens skills,
  chimera-core-philosophy [deleted 2026-07-23]).
- **`CLAUDE.md`** rules cited from the always-loaded project context.
- **Not inspected:** running code (out of scope — rules audit only), `docs/audits/*`, `docs/plans/*`,
  `docs/incidents/*`, phase docs other than K/L/L.B. Where those are referenced by a rule they are
  named, not read.
- **Confidence:** HIGH on Sections 0, 3, 4 (the five-category verdicts and the L.B.2 root cause were
  cross-checked against the primary documents directly). MEDIUM on the exhaustiveness of Section 1's
  STYLE-level enumeration (STYLE rules were catalogued but not all reproduced — they are subordinate
  to the invariants and belong in Appendix A of the SOT, not its body).
```
