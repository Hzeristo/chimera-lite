# Audit — chimera-lens-* vs vault/criteria/* conflict & reconciliation options

**Type:** read-only audit → three options, **no recommendation** (the Architect chooses).
**Date:** 2026-07-18 · **Surfaces:** `.claude/skills/chimera-lens-*/SKILL.md` + `prompts/lenses/*.md`
(canonical) vs `<vault>/criteria/{type,field,disposition}/*.md`.
**Related:** `docs/audits/tag-system-consistency.md`, `docs/ARCHITECTURE/TAG_SYSTEM.md`.

---

## Q1 — Same axis or orthogonal? Do concrete statements DIRECTLY contradict?

**Orthogonal by intent, contradictory on the surface.** The two are different *kinds* of object:

- **Lens = analytical stance** — "how should this paper be critiqued?" Produces a **free-text**
  `verdict` (`schemas.py:340` `LensCritique.verdict: str`) built from a mechanism+evidence+falsifiability
  triple. It never emits `[V]/[P]/[U]` (grep: no lens prompt uses the tag vocabulary).
- **Criteria = epistemic standard** — "what evidence is required for `[V]`?" Produces a per-claim
  `[V]/[P]/[U]` verdict.

They do not contradict *as logic* — but two concrete statement-pairs give the **same object opposite
treatment**, which reads as contradiction to any consumer that doesn't hold the axis distinction:

**Sharpest conflict — an accuracy number: "decoration" vs "`[V]` grounding".**
- Lens: *"Reject endpoint-only metrics. Pure QA accuracy / win-rate / final-answer scores hide the
  process. Demand white-box, process-oriented evidence."* — `_shared/falsifiability.md:26-28`; echoed
  `prompts/lenses/forensic-leakage.md:29-31` ("endpoint-only metrics … demand process-level evidence").
- Criteria: *"[V] requires quoting the table row … absolute scores"* — `criteria/type/benchmark.md:73-78`.
- → The **same results-table accuracy number** is *decoration to reject* (lens) and *the `[V]` grounding*
  (criteria). Dissolves only under the axis split — **lens judges VALIDITY** (does the number mean the
  gain is real), **criteria judge VERIFICATION** (was the number actually reported). A subagent handed
  both sees `[V]` and "reject" on one number.

**Stance conflict — mandated doubt vs restrained doubt.**
- Lens is unconditionally adversarial: *"a forensic audit, not a summary of gains … hunt for leakage"*
  (`forensic-leakage.md:12-13`); *"report it as decoration, not as a validated result"* (`:44`).
- The disposition axis's **designed** purpose is to *restrain* that: *"target = paper → counter
  denigration"* (`phase-L.md`, disposition geometry). But the **authored** `disposition/paper-critic.md`
  instead counters author-*deference* (more scrutiny), which *aligns* with the lens. → The disposition
  axis has an **unresolved identity** (counter-denigrate per phase-L vs counter-deference as written) that
  flips whether it conflicts with or reinforces the lens.

## Q2 — Same pipeline point or different?

**Different points, different granularity — no same-point collision today.**

| | Lens | Criteria |
|---|---|---|
| Fires | (a) server-side in `extract_paper` synthesis (Phase Q, **sealed**) via the lens catalog in `extract_node.j2`; (b) interactively when a `chimera-lens-*` skill activates during deep-reading | Composed into the W1/W2 verbatim-verifier subagent (Phase L) via `load_criteria` |
| Granularity | **Whole paper** → one `LensCritique` (free-text) on the central claim | **One claim** → one `[V]/[P]/[U]` |
| Output | analytical critique | verification tag |

They do **not** receive the same claim at the same time (W1 loads criteria, **not** lenses;
`forensic-leakage SKILL.md:8-9` names its `prompts/lenses/*.md` the single source for the lens, read by
`extract_paper` — a different phase). **Agreement is needed only at the consumer:** a K-node carries a
lens verdict; a later W1 node carries a `[V]/[P]/[U]` on a claim citing that same paper. The Architect
(and Phase K Gate 1) may read both and hold two signals about one paper. If a future W-flow ever loads a
lens, this becomes a same-point collision — it is not one now.

## Q3 — Is disposition/ already doing what lens does? The three-way. Who owns "human ceiling"?

**Partly yes — the authored disposition file smuggled analytical CONTENT into a POSTURE axis.**
- In principle: **lens = WHAT to look for** (probes); **disposition = HOW to carry judgment** (anti-bias
  posture); **type/field = domain/verification standards**. Distinct roles.
- In fact: `disposition/paper-critic.md` contains *probes*, not just posture — "the defining equation is
  quoted" (`:47`), "the H/HD column has been read" (`:51`), "counter cost claims excluding 97%". These are
  lens-shaped analytical checks living in the disposition axis → a genuine **four-way** (lens body,
  `criteria/type`, `criteria/field`, `criteria/disposition`) for "what to check on an eval paper".

**"always check human ceiling" — the ownership test:**
| Surface | Contains it? |
|---|---|
| `prompts/lenses/forensic-leakage.md` | **No** (absent — grep-confirmed; nearest is "price the baseline") |
| `criteria/type/benchmark.md` | **Yes** — the `[U]` human-ceiling rule (`:26-30`) |
| `criteria/disposition/paper-critic.md` | **Yes** — the `[V]` procedure "read the H/HD column" (`:51`) |

→ The statement is **duplicated across two criteria files and absent from the lens** — no single owner
even *within* criteria today.

## Q4 — Independent drift across two edit surfaces

- **Lens:** `.claude/skills/` + `prompts/lenses/` — git-tracked, Claude-Code-edited (commit-level friction).
- **Criteria:** `<vault>/criteria/` — Obsidian-native, Architect-edited **zero-git** (daily cadence).

**What breaks on divergence:** the two describe the *same* eval-integrity concerns at *different cadences*.
Criteria drift **faster** (zero-git, daily) than the lens (git). So: tighten `benchmark.md`'s `[V]` bar in
Obsidian and `extract_paper` K-nodes are still analyzed under the lens's **old** bar while W1 verifies
under the **new** one — same paper, two standards, no shared source, growing gap. And now that
`TAG_SYSTEM.md` is the canonical `[V]` authority, **criteria reference it but the lens sits entirely
outside it** (free-text verdict, no `V/P/U`) — so the lens can never be checked against the tag definition
at all.

---

## The three reconciliation options

*(Plain comparison table; per-option prose below. No recommendation — the Architect chooses.)*

| | **A — Hard separation** | **B — Criteria subsumes lens triggers** | **C — Lens=patterns, Criteria=standards** |
|---|---|---|---|
| **Claim** | Orthogonal axes; must NOT merge | Criteria are the single source; lens = a downstream action criteria fire | Composable halves; lens="what to look for", criteria="what counts as found" |
| **What changes** | Draw a bright line: strip analytical probes OUT of `criteria/disposition` (H-column, equation-read → back to lens); rule: criteria carry no probes, lenses carry no `[V]/[P]/[U]` | Trigger moves into criteria ("no H-row → fire forensic-leakage"); lens keeps its METHOD but loses its own trigger; `extract_paper` must call `load_criteria` for lens selection | Add a bidirectional LINK: each criterion cites its lens probe; each lens probe cites its `TAG_SYSTEM` threshold. Nothing deleted |
| **What stays** | Both systems intact in their own pipelines; no wiring change; lens outside `TAG_SYSTEM` | Lens method bodies; the `V/P/U` verdict as the funnel output | Both bodies intact (lens free-text + criteria tags); both pipelines; only the link is new |
| **Failure mode** | Shared checks (human ceiling) authored TWICE, two cadences → drift is **blessed as intentional** (Q4, now by design) | Vault edit changes sealed Phase-Q behavior; a criteria typo silently disables a lens; couples fluid vault → sealed extraction; inverts "lens is its own source of truth" (`forensic-leakage SKILL.md:8`) | The LINK is a THIRD drift surface crossing git↔Obsidian; a rename on either side breaks the cross-reference silently; nothing validates it |
| **Single-source for "human ceiling"** | **None** — lives in whichever axis needs it; duplication accepted | **`criteria/type/benchmark.md`** — owns the check AND the "fire lens" trigger | **Split**: lens owns the PATTERN ("scan the H row"), criteria own the STANDARD ("undiscussed anomaly → [U]"), joined by the link |
| **Who wins: lens "doubt" vs criteria "[P] sufficient"** | **Neither** — different questions; both stand; the Architect hand-reconciles | **Criteria** — the lens only fired because a criterion summoned it; its finding is an input to the `[P]`, not a rival verdict | **Neither** — they're halves: the lens's doubt IS the reason the criterion says `[P]` not `[V]`; no conflict by construction |
| **TAG_SYSTEM interaction** | Lens explicitly OUTSIDE the tag authority — clean boundary, but a lens "decoration" verdict never becomes a `[U]` Gate 1 can consume | Everything funnels through criteria → `TAG_SYSTEM` governs all, but forces the lens's rich critique into the `V/P/U` straitjacket | `TAG_SYSTEM` becomes the shared vocabulary BOTH halves reference — the anchor; but the lens must gain `V/P/U`-awareness, eroding its free-text richness |

### Option A — Hard separation (prose)
Owns exclusively: **lens** = whole-paper analytical critique (free-text `verdict`); **criteria** =
per-claim verification standard (`[V]/[P]/[U]`). The rule that prevents future overlap: *criteria files
never contain analytical probes; lens files never contain `[V]/[P]/[U]` thresholds* — which requires
removing the probes that already leaked into `disposition/paper-critic.md`. Failure mode if separation is
violated: the same check (human ceiling) needed by both the analytical read and the verification must be
written twice with no shared source — exactly the Q4 drift, now sanctioned. `[P]`-note: "sufficient" here
means only monotonicity-admissible (flows capped, not blocked); the lens's stronger "decoration" verdict
has no channel to override it — the Architect must.

### Option B — Criteria subsumes lens triggers (prose)
Lens skill files: bodies stay as METHODS; their function-based trigger (`forensic-leakage.md:3-9`) is
removed and re-homed in criteria. Criteria files: gain a `→ fire lens X` action clause per signal,
becoming the orchestration layer. Pipeline: `extract_paper` (which today loads **lenses, not criteria**)
must now `load_criteria` to pick lenses — a **new coupling of sealed Phase Q to the fluid vault**, and a
reopening of the Q seal. Failure mode: a zero-git vault edit silently changes server-side extraction; the
lens is no longer authoritative for when it looks.

### Option C — Lens patterns + criteria standards (prose)
Linking mechanism: an explicit cross-reference in each direction (criterion → lens-probe id; lens-probe →
`TAG_SYSTEM` threshold id). Drift prevention would need a checker that both files resolve their
references — but that checker must span git and Obsidian, which nothing currently does (the core failure
mode). Payoff: "lens says doubt / criteria says `[P]`" stops being a conflict — the doubt is *why* the
verdict is `[P]` and not `[V]`; the lens supplies the reason, the criterion supplies the tag.

---

**No recommendation is offered.** Each option resolves a different sub-question (A: keep them apart and
accept duplication; B: one source, at the cost of coupling the sealed extractor to the vault; C: compose
them, at the cost of a cross-surface link). The choice is the Architect's.
