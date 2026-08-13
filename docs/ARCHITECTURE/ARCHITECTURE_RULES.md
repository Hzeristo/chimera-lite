# ARCHITECTURE_RULES — precedence and the pre-change checklist

**Status:** ✅ SUBORDINATE. This document is **no longer the invariant SOT.**
**Authored:** 2026-07 · **Demoted:** 2026-08-11 (invariant reconciliation, Pass 2).

The invariants are the Architect-authored canonical:

| What | Where |
|---|---|
| **What must be true** (I0.x absolute · I1.x architectural · I2.x mutable · non-invariants) | [`INVARIANTS.md`](INVARIANTS.md) |
| **The formal objects** (artifact graph, evidence tiers, tags, transitions, I1–I4) | [`FORMAL_MODEL.md`](FORMAL_MODEL.md) |
| **How well the code actually holds it** (mode vs compliance, every gap, anchored) | [`ENFORCEMENT_DEBT.md`](ENFORCEMENT_DEBT.md) |

**This file retains exactly two jobs** the canonical does not cover:

1. the **level hierarchy** — which rule wins when two disagree (below);
2. the **Violation Detector** — the mandatory pre-change checklist (below).

Everything else here is a cross-reference. **Do not restate an invariant in this file.** The R1–R6
register it once carried is retained below as a *pointer table only*, because five years of sprint
docs, skills, and commit messages cite those ids and the mapping must stay resolvable.

> **Enforcement status moved.** The STRUCTURAL / ADVISORY axis and every debt row now live in
> [`ENFORCEMENT_DEBT.md`](ENFORCEMENT_DEBT.md), which splits *mode demanded* from *compliance
> observed* and anchors every row. An invariant's enforcement status is never recorded here.

---

## Level Hierarchy — the meta-rule (M7)

```
ARCHITECTURE  (INVARIANTS.md + FORMAL_MODEL.md)  ← the canonical; holds across ALL phases
      >
SPRINT        (docs/phases/*.md)                 ← single-phase / process constraints
      >
STYLE         (.claude/skills/*)                 ← code-quality / minimal-diff / taste rules
```

*(This document sits beside the ARCHITECTURE level, not at it: it declares the precedence rule and
the checklist, but states no invariant of its own.)*

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

## R1–R6 → the canonical (pointer table only)

The six rules this file used to state are now stated in `INVARIANTS.md`. **Nothing below is a rule
statement** — it is a redirect, kept because the R-ids are cited throughout `docs/phases/`,
`.claude/skills/`, commit messages, and `ENFORCEMENT_DEBT.md`. Read the canonical for the rule; read
`ENFORCEMENT_DEBT.md` for whether the code holds it.

| old id | title | now stated at | compliance |
|---|---|---|---|
| **R1** | MCP Judgment Prohibition | [`INVARIANTS.md`](INVARIANTS.md) **I1.1** | *(no open debt)* |
| **R2** | Human-Time Supremacy | **I0.1** | `ENFORCEMENT_DEBT.md` R2 (PARTIAL — seal unverified) |
| **R3** | Staging Gate Universality | **I1.2** | `ENFORCEMENT_DEBT.md` R3 (PARTIAL — scout non-advancement) |
| **R4** | ~~Tier Integrity~~ — **superseded, see below** | **I1.5** (existence) + **I2.1** (values) | *(no open debt)* |
| **R5** | Provenance Load-Bearing | **I0.2** | `ENFORCEMENT_DEBT.md` R5a (discharged) / R5b (OPEN) |
| **R6** | Human Authorship of Judgment | **I0.5**, plus **I1.3** (I-node support) | `ENFORCEMENT_DEBT.md` R6 (PARTIAL) |

### Two notes the redirect cannot carry silently

**R4 is not migrated — it is dropped.** R4 asserted that the *tier values*
(`scout`/`deep_read`/`harness_candidate`/`synthesis`) are themselves invariant: "not metadata —
they determine which code paths are legal." The canonical **rejects that scope.** `I1.5` makes the
*existence* of a stratification architectural; `I2.1` makes the *values* a Tier-2 **mutable choice**
that may be added, merged, or renamed. R4 therefore protected more than the canonical does, and the
excess is deliberately released. What survives: a K node still must not be silently defaulted to a
tier — but that now follows from I1.5 (candidate and committed must remain mechanically
distinguishable), not from the values being sacred.

**R1's scope widened on the way across.** R1 banned "calling an LLM." `I1.1` bans judgment **by any
route** — client construction, host sampling (`ctx.session.create_message` / `ctx.sample`), or any
other delegation — because the prohibition is on judgment *location*, not on client construction.
A tool that constructs no client and still returns a verdict violates I1.1 and would have passed R1.

## Violation Detector — mandatory pre-change checklist

Before ANY proposed change (code, tool, skill, workflow), ask each question. A "yes" is a **stop**:
the change violates an invariant and must be redesigned, regardless of how small or sprint-scoped it
looks.

| Ask | If yes → violates |
|---|---|
| Does this route **judgment** into an MCP server process by any means — client, host sampling (`ctx.session.create_message` / `ctx.sample`), or other delegation? | **I1.1** |
| Does this advance a node's committed status without an Architect-initiated action? | **I0.1** |
| Does this treat a mid-tool `ctx.elicit` confirm as that action? (it is not — see below) | **I0.1** |
| Does this let AI-authored content reach a committed tier without passing the single ascension gate? | **I1.2** |
| Does this make candidate material and committed truth mechanically indistinguishable? | **I1.5** |
| Does this assign a `[V]` without a recorded verbatim Tier-1/2 quote? | **I0.2** |
| Does this let a node's status exceed the minimum over its **support-bearing** edges? | **I0.2** |
| Does this treat one verification type (truth / novelty / significance) as a proxy for another? | **I0.3** |
| Does this delete or rewrite committed history instead of superseding it? | **I0.4** |
| Does this auto-generate a T/I/D node **body**, or record AI influence as anything but `informed_by`? | **I0.5** |
| Does this smooth one of the three consumption routes while adding ceremony to another? | **I1.4** |

**And the meta-check (M7):** *Does this change honor a SPRINT or STYLE rule (minimal diff, extend
not rebuild) at the cost of any canonical invariant?* If yes → the invariant wins. Rebuild.

**Elicit clarification (retained — the canonical states the rule, this states the trap).**
`ctx.elicit` inside an agent tool call may collect *parameters* (machine-time information gathering).
It does **not** constitute the human-time action I0.1 requires. Truth advance requires an
Architect-initiated action — an Obsidian promote, an explicit `ascend_node` invocation — not a
mid-pipeline confirm-click. A confirm-click launders machine-time into committed status while
appearing to satisfy I0.1: the human is answering a prompt *inside* an agent turn the agent itself
scheduled, which is not the same as the human deciding to advance a belief. It is the more dangerous
failure, because the provenance chain would show a human event and still be false.

---

## Appendix A — Level index (which subordinate rules defer to which invariant)

| Invariant | Subordinate SPRINT/STYLE rules it outranks |
|---|---|
| I1.1 | `chimera-code-taste` minimal-diff / "extend not rebuild"; `chimera-dependency-veto:42` (openai SDK); `phase-L.B.md:60-61` (deepseek-for-extraction — retired) |
| I0.1, I1.2 | `CLAUDE.md` "never auto-promote"; tool docstrings ("never writes into the live vault") |
| I1.5, I2.1 | `NODE_ONTOLOGY.md §7` (tier/status axes — subordinate authority, referenced not restated) |
| I0.2 | `TAG_SYSTEM.md §3–§6` (tag semantics authority); `phase-K.md` red lines |
| I0.5, I1.3 | `THEORETICAL_FRAMEWORK.md §2` Separation Principle; node-creation convention |
| I2.2 | `NODE_ONTOLOGY.md §2` (edge vocabulary + per-type sets) |

## Appendix B — Enforcement-debt register → **moved**

The enforcement-debt register now lives in its own document:
[`docs/ARCHITECTURE/ENFORCEMENT_DEBT.md`](ENFORCEMENT_DEBT.md).

It was extracted (2026-08-11) because the canonical cites it directly — `INVARIANTS.md:28`, `:47`,
`:155` and `FORMAL_MODEL.md:99` — so the compliance record needed a stable address of its own rather
than an appendix position inside this file. The extraction carried every row forward unchanged and
added the two debts the canonical names (provenance decay, `stale` status) plus one defect in the
R5b checker itself.

**Do not restate a debt row here.** One register, one address; a second copy is how a discharged
gap gets quietly re-asserted, or a live one silently dropped.
