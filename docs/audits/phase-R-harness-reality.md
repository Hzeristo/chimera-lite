# Phase R — Harness-Reality Audit

> ⛔ **Phase R retired / absorbed into Phase L (2026-07-16) — see `docs/phases/phase-L.md`.** This audit
> stays valid as lineage: its **F4** finding (substring tools ≠ semantic search over a depth-1 graph) is
> the retrieval-precision risk Phase L inherits, and L's Out-of-Scope names the `semantic_vault_search`
> mock interface (DEBT-019) surfaced here. Read below as the harness-reality check that shaped L's
> subagent-judgment + vault-criteria design.

**Scope:** Audit `docs/phases/phase-R.md` against the *actual* Claude Code harness —
i.e. does the spec's model of what the harness can enforce match how Claude Code
really behaves? Not a general phase audit; a targeted check of every harness assumption.

**Method.** Harness behavior confirmed against official docs (skills, memory, hooks,
how-claude-code-works) via a `claude-code-guide` pass; tool surface + repo config read
directly (`chimera-vault/server.py`, `.claude/settings.local.json`).

**Verdict.** The spec is *harness-literate* — it correctly names hooks as the deterministic
layer and correctly defers them to Phase S. But its **mission verb and seal criterion assume
an agent behavior the harness cannot guarantee at either tier (skill OR hook)**, and one red
line (`description frozen`) forecloses the exact lever that fixes the most likely failure mode.
Four findings need reconciliation before R.5 is executed or sealed; the toolchain sprints
(R.1–R.4) are harness-clean.

---

## The one fact everything turns on

| Mechanism | Deterministic *injection*? | Deterministic *behavior*? |
|---|---|---|
| CLAUDE.md | Yes (every session) | **No** — context, not enforced |
| Skill (incl. "always-active") | **No** — body loads only when invoked | **No** — soft prompt |
| Hook (UserPromptSubmit / PreToolUse) | Yes (fires at lifecycle event) | **Yes**, but only *block / modify / inject* — never *force a proactive tool call* |

There is **no harness mechanism that makes the model call a specific tool before it answers.**
Not a skill, not CLAUDE.md, not even a hook. A hook can *block the alternative* (deny an answer
path) or *inject content* (run the query itself and paste the result), but it cannot positively
compel the agent to reach for `obsidian_graph_query` first. Hold this against the spec's language
and the findings fall out.

---

## Findings (most actionable first)

### F1 — "always-active" is not a harness state, and the `description`-freeze red line forecloses the fix  **[Major]**

The spec treats academic-observe as *both* `ALWAYS-ACTIVE`
(`SKILL.md:3`, CLAUDE.md skill #7) *and* auto-selected by its description
(`phase-R.md:61-63`: "The description is what drives auto-selection"). These are not two
properties of one skill — they are two different claims, and only the second is real.

- **Harness reality:** no frontmatter flag forces a skill body into every turn. "Always-active"
  is achieved *only* by the model choosing to honor the description. The `description` is the
  **single** activation lever; if a skill under-triggers, the fix *is* the description.
- **Consequence for R.5:** the forced-lookup instruction is gated by **two** discretion points —
  (a) the model decides to load the skill (per description), then (b) obeys the in-body "MUST
  query." The spec assumes (a) is free ("always active"), so it books all the risk on (b).
  The riskier gate is (a): on a long-paper turn the model may never load academic-observe at all.
- **The trap:** red line `phase-R.md:61-63` freezes the description ("must not change... Only the
  skill body changes in R.5"). If R.5 fails because the skill *didn't load*, the only lever that
  fixes it is the one the red line forbids. The red line is aimed at protecting auto-selection but
  actually protects the wrong thing — it locks the activation lever while leaving mutable the body
  that was never the bottleneck.

**Recommendation:** (1) Correct the language: academic-observe is *high-propensity auto-load*, not
guaranteed-active. (2) Bring the `description` **into** R.5 scope as the activation lever; replace
the freeze with "preserve the auto-selection *intent* (still fires on research-analysis turns);
tune wording if activation-recall is the observed failure." Keep the body rewrite too — but stop
assuming activation is free.

---

### F2 — Hard Sealing Condition 1 spot-checks a *rate* with a single observation  **[Major]**

`phase-R.md:68-76` seals the phase on: "the agent queries the vault BEFORE answering... **Assessed
by the Architect on a real question, not a fixture.**"

- **Harness reality:** skill adherence to "MUST call X" is a **probability, not a guarantee**
  (confirmed: soft prompt, model discretion). One green question proves the skill *can* fire — not
  that it *reliably* fires, and especially not under the condition the spec itself fears most
  (long paper context, `phase-R.md:101-105`).
- A single-shot seal on a stochastic behavior is not durable: the same skill, unchanged, can miss
  the next turn. The seal would certify a coin that happened to land heads once.

**Recommendation:** Define the gate as **adherence over N sampled questions (N≥5)**, deliberately
including one long-context turn, and **record the observed rate** in the seal verdict. The phase's
own thesis is "test the skill ceiling" (`:105`) — a ceiling is a rate, so measure the rate. Sealing
should read e.g. "queried before answering on k/N, including the long-context case," not a binary ✅.

---

### F3 — Mission verb ("the agent consults / queries") is unreachable at *both* tiers; only *injection* is  **[Major, conceptual]**

The whole phase is framed as making **the agent** walk the graph: "makes the agent actually consult
it during reasoning" (`:8`), "the agent queries the vault BEFORE answering" (`:70`), north star
"ambient multi-source reasoning" (`:117`). Phase S is described as the deterministic version:
"Hook-based deterministic vault injection" (`:122`).

- **Harness reality:** the deterministic realization is a **UserPromptSubmit hook that itself runs
  the query and injects the result** into the prompt. In that design **the agent never consults the
  vault — the harness pre-consults and feeds it**. Hooks cannot force the agent to *call* a tool
  first; they can only inject or block. So the "agent walks the graph on its own initiative" ideal
  is reachable at *neither* tier: R.5 approximates it softly (ask nicely → probabilistic), Phase S
  replaces it with injection (hook queries → agent can't reason without the result already present).
- The spec's Phase S wording ("injection") is actually correct — but the Mission and sealing
  language ("the agent queries") describe the *unreachable* framing and contradict it. This matters
  because R.5's success criterion is written in the agency framing ("agent queries before answering")
  when what's testable is "did vault content appear in / shape the answer."

**Recommendation:** Reconcile the language to the reachable target: **"vault content is in front of
the agent before it reasons"** (agent-surfaced in R.5, hook-injected in Phase S). Recognize
explicitly that no phase makes the agent *volitionally* consult the vault deterministically — that
ideal is a UX outcome, not an enforceable behavior. This also clarifies the R.5→S escalation: S is
not "the same thing but forced," it's a *different mechanism* (injection) that sidesteps agent
discretion entirely.

---

### F4 — Even a fired lookup may not surface the right node: the tools are substring matchers, not semantic search  **[Major, partly out-of-harness]**

The seal *example* (`:75-76`, mirrored in Mission `:29-31`): ask about MemGPT eviction, confirm the
agent "retrieves and cites your T node on 'recency ≠ importance.'"

- **Tool reality** (`chimera-vault/server.py:89-123`): `obsidian_graph_query(node_type,
  link_pattern, max_depth)` matches a **body substring**; `vault_query(type, status, linked_to)`
  matches **frontmatter**. Neither does conceptual retrieval. "MemGPT eviction" → "recency ≠
  importance" is a *semantic* hop with near-zero literal token overlap; the tools will likely miss
  it. This is pre-existing **DEBT-003** (keyword-only, low precision on conceptual queries).
- **The silent second gate:** R.5 can *pass its mechanical criterion* (a query fired) while
  *failing its intent* (the relevant node never surfaces). "A query happened" and "the right node
  was found" are different assertions; the seal conflates them.
- **Compounding — the graph is thin.** Per project memory `[[vault-graph-edges-empty]]`: the vault's
  typed edges are wide-and-shallow (depth-1 stars), and retrieval was *retired* pending "the
  vault-in-loop agentic defect fixed + vault filled with ARA-styled nodes." R.5 is that re-attempt.
  `obsidian_graph_query` BFS at depth 1–2 has little to traverse — the mechanism may have nothing
  to walk even when it fires on the right seed.

**Recommendation:** Split the seal into (a) *did a lookup fire* (the harness/skill question, F1–F3)
and (b) *did the relevant node surface* (the retrieval-precision question, DEBT-003). Pick a seal
question whose vault node shares **literal tokens** with the query, or explicitly accept retrieval
precision as an independent, named risk — arguably the *real* Phase R risk, orthogonal to agent
willingness. Do not let a substring-tool miss read as "the agent refused to consult the vault."

---

## What the spec gets right (harness-affirmed)

- **Hook deferral is accurate and clean.** UserPromptSubmit / PreToolUse in `settings.json` *are*
  the deterministic layer (`:55-57`, `:122-123`), and the repo currently has **none**
  (`settings.local.json` holds only `enabledMcpjsonServers`). "No hook-based injection in Phase R"
  is a real, verifiable boundary, not a vibe.
- **R.4 URL return is harness-compatible.** An MCP tool returns text; a Cloudflare URL string is
  fine, and "no auto-open" is *trivially* true — the harness never auto-opens a tool-result URL.
  The "no embedded viewer" line correctly reflects the retired-frontend reality.
- **Thin-adapter red line** matches the existing server shape (`chimera-vault/server.py` delegates;
  logic lives in domain modules). R.1/R.2/R.3 as domain-module work with thin dispatchers is sound.
- **The R.5→Phase S escalation instinct is right** — skills are the cheap ceiling, hooks the
  deterministic floor — subject to the F3 reframing of *what* the hook actually does.

---

## Minor / out-of-scope-of-harness

- **R.4 dependency check (dependency-veto, not harness):** "Cloudflare-tunneled URL" (`:47`) implies
  a `cloudflared` process. Red line `:60` says "no new dependency." `cloudflared` is an external
  binary, not a Python dep — verify it's already provisioned (legacy astrocyte tunnel?) or R.4 and
  the red line conflict. Flag only.
- **academic-observe body vs. tool contract (minor drift):** the skill body (`SKILL.md:33-35`)
  describes `obsidian_graph_query` as "BFS over the wikilink graph," but the tool's `link_pattern`
  arg is a **body substring**, and `max_depth` seeds BFS — the skill's mental model of the tool is
  looser than the contract. Worth tightening in the R.5 body rewrite so the instruction tells the
  model to call the tool the way it actually works.

---

## Proposed adjustments to `phase-R.md` (PROPOSED — for the Architect to apply; phase intent is yours)

1. **Mission / Seal language (F3):** change "the agent queries the vault before answering" →
   "vault content reaches the agent before it reasons (agent-surfaced in R.5; hook-injected in
   Phase S)." Note that agent-volitional consultation is not deterministically enforceable at any tier.
2. **Hard Sealing Condition 1 (F2):** seal on adherence over N≥5 sampled questions incl. one
   long-context turn; record the rate, not a binary.
3. **Red line "description frozen" (F1):** replace with "preserve auto-selection *intent*; the
   description is the activation lever and is in-scope for R.5 tuning if activation-recall is the
   observed miss." Correct "always-active" → "high-propensity auto-load."
4. **Split the seal (F4):** separate "a lookup fired" from "the relevant node surfaced"; name
   retrieval precision (DEBT-003 + `[[vault-graph-edges-empty]]`) as an independent Phase R risk,
   or choose a literal-token-overlap seal question.
5. **R.4 (minor):** confirm `cloudflared` is already present or amend the "no new dependency" line.

---

## Bottom line

Phase R's engineering (R.1–R.4) is harness-clean. Its **gate (R.5) is built on the one thing the
harness will not give you — a guaranteed pre-answer tool call** — and the spec half-knows this
("test the skill ceiling") but its Mission and seal language still promise the guaranteed version.
Two cheap fixes make the phase honest: (1) seal on a measured *rate*, not a single pass; (2) stop
freezing the `description`, which is the actual activation lever. And go in eyes-open on F4: even a
perfectly obedient agent can't retrieve a semantic match from substring tools over a depth-1 graph —
that gap is Phase R's quiet second boss, and it's not a harness problem, it's a retrieval-quality one.
