# ARCHITECTURE_RULES — Chimera Lite invariant rules (the SOT)

**Status:** ✅ AUTHORITY. This document has ONE job: state the invariant rules as **hard
constraints** that hold across ALL phases and **override any sprint- or style-level instruction**.
**Authored:** 2026-07 · **Source:** `docs/ARCHITECTURE/INVARIANT_RULES_AUDIT.md` §4 (M1–M7), §5.
**Consumers reference this file; they never restate or override it** (the drift rule —
`TAG_SYSTEM.md §9`, `THEORETICAL_FRAMEWORK.md §0`).

Each rule carries an **enforcement status**:

- **STRUCTURAL** — a schema / gate / code path makes it load-bearing; violating it is impossible or
  is caught by an automated check. The rule is real.
- **ADVISORY** — the invariant is committed, but the enforcing code does not yet exist. By this
  project's own north star (*advisory rigor is negative value* — `PHILOSOPHY.md §3`),
  an advisory rule is **acknowledged technical debt, not a shipped guarantee.** Every advisory gap
  below names the phase that lands it. See the enforcement-debt register (Appendix B).

---

## Level Hierarchy — the meta-rule (M7)

```
ARCHITECTURE  (this document)      ← invariants, hold across ALL phases
      >
SPRINT        (docs/phases/*.md)   ← single-phase / process constraints
      >
STYLE         (.claude/skills/*)   ← code-quality / minimal-diff / taste rules
```

**When two rules conflict, the higher level wins — always.** An architecture invariant is never
traded away for a smaller diff, a faster sprint, or "extend, don't rebuild." **If honoring an
invariant requires rebuilding rather than extending, rebuild.**

> This is the rule whose absence caused **L.B.2**. A SPRINT/STYLE minimalism habit ("extend in
> place, small diff" — `chimera-code-taste`) pointed toward wiring an LLM client into an existing
> MCP server, while the ARCHITECTURE invariant ("judgment lives in Claude subagents") demanded
> restructuring. The invariant was never stated at the executor's altitude, so the style rule won.
> This section exists so that can never be the correct reading again.

**Enforcement:** STRUCTURAL as a review protocol (the Violation Detector below is mandatory before
any change); the level of each *other* rule is declared in its heading.

---

## R1 — MCP Judgment Prohibition

> **No MCP server process may call any LLM — any vendor, any model, any wrapper, any purpose
> (including "cheap extraction").**

The prohibition binds `server.py` **and every module it imports at runtime** (the service and port
layers included — pushing an LLM client "down" into the service layer does not escape this rule).
All LLM judgment — triage, synthesis, classification, verification, *and* extraction — lives in
Claude Code Task subagents. MCP provides only **non-LLM primitives**: fetch, convert, read, query,
deterministic transform, write.

- **Violation class:** L.B.2 — adding an API client (deepseek, `openai` SDK, `anthropic` SDK, any
  hosted model) to an MCP server, at any layer, for any reason.
- **Exception policy: NONE.** If an LLM is needed, it goes through a **skill → subagent**, never
  through an MCP tool. This retires the `phase-L.B` "deepseek may remain for cheap data extraction"
  carve-out (`phase-L.B.md:60-61`) and bounds the `openai`-SDK permission
  (`chimera-dependency-veto:42`): that SDK is admissible only for the Architect's cross-model
  subagent primitives, **never inside an MCP server process.**
- **Enforcement:** STRUCTURAL — grep verification is a hard sealing condition (`phase-L.B` HSC-2;
  L.B.6 runs it end-to-end). Source of truth for actual state: the generated `ARCHITECTURE.md`
  ("the MCP servers make NO LLM call", line 48).
- **Update required elsewhere:** `chimera-mcp-taste` must reference R1 as an explicit principle —
  today its `thin_adapter` rule (`mcp_rules.md:177-178`) *permits* business logic in the service
  layer, where an LLM client would pass unremarked. That silence is the gap R1 closes.

---

## R2 — Human-Time Supremacy

> **No code path advances a node's committed status without a human action in its provenance chain.**

Machine-time (pipelines, subagents, W1/W2) produces only `unverified` / `PENDING_REVIEW` candidate
material. The `unverified → active` (or staged → committed) transition fires only on a human-invoked
action. This is Theorem 1 of the manifold (`THEORETICAL_FRAMEWORK.md §1`) expressed as an operational
constraint: *belief advances exclusively on human-time.*

- **Violation class:** auto-promotion of AI-generated content — any new write path that flips a node
  to a committed/believed state without a human event.
- **Enforcement:** STRUCTURAL — `ascend_node` is the sole gate into `Knowledge/` and requires human
  invocation (`phase-L.B` HSC-3; the tool is present in the generated inventory,
  `ARCHITECTURE.md:22, 60`).
- **Current gap:** the tool exists; the **seal** claim "a direct write to `Knowledge/` without
  `ascend_node` is impossible by code constraint" is verified at **L.B.3 / L.B.6**. Treat R2 as
  STRUCTURAL-pending-seal: if L.B.3 has not sealed in the working context, it is ADVISORY until the
  code-constraint check passes.

---

## R3 — Staging Gate Universality

> **All AI-authored candidate content enters `vault/Harness/` or `docs/staging/` (or the `inbox/`
> scout holding tier) before any committed tier. Direct writes to `Knowledge/` are prohibited by
> code constraint.**

`Knowledge/` (the committed K tier) has exactly one writer: `ascend_node`, which requires
`chimera_tier=deep_read` and a human invocation. Scout cards (`inbox/`) and staged K/T/I/D
candidates (`docs/staging/`) are human-gated holding tiers; **neither auto-advances.**

- **Violation class:** an `inbox/` bypass, or any code path writing a committed tier without
  `ascend_node`.
- **Enforcement:**
  - `Knowledge/` write path: **STRUCTURAL** after L.B.3 seals (same pending-seal caveat as R2).
  - `inbox/` scout tier: **ADVISORY** now — the "never auto-promote" guarantee is a phase red line
    (`phase-L.B.md:57-59`) + a `CLAUDE.md` hard rule; it is human-gated by tier (`ascend_node`), but
    the *non-advancement of a scout card* rests on convention plus the tier axis, not a dedicated
    structural refusal. Debt tracked to L.B.6 end-to-end verification.

---

## R4 — Tier Integrity

> **`chimera_tier` is the vault's type system. `scout` / `deep_read` / `harness_candidate` /
> `synthesis` are not metadata — they determine which code paths are legal.**

`chimera_tier` and `status` are two ORTHOGONAL axes and are never folded into each other (tier is not
carried by status). A `knowledge` node created with no tier stays untiered so its writer is **forced**
to declare `scout` vs `deep_read` — a silent K default would re-open the C-1 defect.

- **Source:** `NODE_ONTOLOGY.md §7` — the one principle from the audit that was properly elevated to
  an architecture authority (via the C-1 audit). This rule points there; it does not restate §7.
- **Violation class:** writing a K node without an explicit tier; using `status` to encode depth;
  treating `deep_read` as a label rather than the precondition `ascend_node` enforces.
- **Enforcement:** STRUCTURAL after L.B.1 (`create_staging_node` refuses to default `knowledge`;
  `ascend_node` gates on `chimera_tier=deep_read`). L.B.1 is the load-bearing sprint everything else
  in L.B depends on.

---

## R5 — Provenance Load-Bearing

> **`[V]` / `[P]` / `[U]` tags carry a structural guarantee. A `[V]` requires verbatim Tier-1/2
> evidence. Gate 1 (monotonicity) is pipeline-enforced, not agent-chosen.**

A synthesis inherits its weakest dependency's status: `status(n) ≤ min status of its recorded
`depends_on``. Gate 1 reads the **recorded** `depends_on`; it never re-infers dependencies with an
LLM. Tier-3 (authorial framing) can never ground `[V]` — at most `[P]`. Semantics live in
`TAG_SYSTEM.md`; this rule references them.

- **Violation class:** assigning a tag without verbatim evidence; reasoning with a `[U]`/`[P]` claim
  as if `[V]` (the confession failure — `THEORETICAL_FRAMEWORK.md §3`); a gate implemented as a
  prompt instruction the agent "may honor" rather than a schema that rejects.
- **Enforcement:** **ADVISORY** — `write_result.verdict` is still an unvalidated `str`
  (`TAG_SYSTEM.md §9`), and Phase K (which lands schema-reject + Gate-1 monotonicity) is **Queued**,
  not built. **This rule is aspirational until K.1 runs.** Debt: constrain `verdict` to
  `Literal["V","P","U"]`; make Gate 1 a schema-structural refusal.

---

## R6 — Human Authorship of Judgment

> **T / I / D node bodies are Architect-authored. No code path writes T/I/D body content without an
> explicit human action.**

Taste-verification (T and I nodes: reasoning, judgment, cross-person confirmation) cannot be
automated (`THEORETICAL_FRAMEWORK.md §2`, Definition 4). The harness produces source-verified
*candidate* material; the Architect settles taste. I nodes are never auto-generated — only on a user
call, from verified T-groups.

- **Violation class:** a pipeline or subagent emitting T/I/D **body** content; auto-generating an
  insight from unverified material.
- **Enforcement:** **CONVENTION** — no structural code gate exists yet. `create_node` writes only to
  staging and `synthesis` tier is human-authored by node type, but nothing structurally prevents a
  future path from populating a T/I/D body. Debt: no phase currently owns a structural gate here;
  flag for the next tier/authorship sprint.

---

## Violation Detector — mandatory pre-change checklist

Before ANY proposed change (code, tool, skill, workflow), ask each question. A "yes" is a **stop**:
the change violates an invariant and must be redesigned, regardless of how small or sprint-scoped it
looks.

| Ask | If yes → violates |
|---|---|
| Does this add or route an LLM call inside an MCP server process (any layer, any purpose)? | **R1** |
| Does this advance a node's truth/committed status without a human action in the chain? | **R2** |
| Does this write to a committed tier (`Knowledge/`) without going through `ascend_node`? | **R3** |
| Does this create/handle a K node with the `chimera_tier` field bypassed or defaulted? | **R4** |
| Does this assign a `[V]/[P]/[U]` tag without recorded verbatim Tier-1/2 evidence? | **R5** |
| Does this auto-generate a T/I/D node **body**? | **R6** |

**And the meta-check (M7):** *Does this change honor a SPRINT or STYLE rule (minimal diff, extend
not rebuild) at the cost of any R1–R6 invariant?* If yes → the invariant wins. Rebuild.

---

## Appendix A — Level index (which subordinate rules defer to which invariant)

| Invariant | Subordinate SPRINT/STYLE rules it outranks |
|---|---|
| R1 | `chimera-code-taste` minimal-diff / "extend not rebuild"; `chimera-dependency-veto:42` (openai SDK); `phase-L.B.md:60-61` (deepseek-for-extraction — retired by R1) |
| R2, R3 | `CLAUDE.md` "never auto-promote"; tool docstrings ("never writes into the live vault") |
| R4 | `NODE_ONTOLOGY.md §7` (source authority — R4 references, does not restate) |
| R5 | `TAG_SYSTEM.md §3–§6` (semantics authority); `phase-K.md` red lines |
| R6 | `THEORETICAL_FRAMEWORK.md §2` Separation Principle; node-creation convention |

## Appendix B — Enforcement-debt register (every ADVISORY gap + the phase that lands it)

| Rule | Gap | Lands at |
|---|---|---|
| R2 | `ascend_node` "impossible by code constraint" seal not yet verified in-context | L.B.3 seal / L.B.6 end-to-end |
| R3 | `inbox/` scout non-advancement rests on convention + tier axis, not a dedicated refusal | L.B.6 verification |
| R5 | `write_result.verdict` is unvalidated `str`; Gate-1 monotonicity not schema-enforced | Phase K (Queued) — K.1 |
| R6 | No structural gate prevents auto-writing a T/I/D body | Unhomed — next authorship sprint |

> An ADVISORY rule is a **promise with no teeth yet**. It is listed here so it cannot be mistaken for
> a shipped guarantee, and so the debt is discharged deliberately — not quietly dropped when its
> phase is built.
