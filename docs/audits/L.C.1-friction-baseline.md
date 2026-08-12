# L.C.1 — Friction Baseline

**Sprint:** C.1 (Phase L.C — Colligo) · **Risk:** 🟢 · **Date:** 2026-08-12
**Plan:** `docs/plans/Phase-L.C-batch.md` · **Spec:** `docs/phases/phase-L.C.md` (D1, D2)
**Purpose:** I1.4 ("three consumption routes, equal friction") is one of eight canonical
invariants with no mechanical verifier (`ENFORCEMENT_DEBT` D-5). This document is the observable.
Every friction-changing sprint in this phase (C.3a/b/c, C.4, C.5) is gated on it existing first.

**Status:** ✅ **COMPLETE (2026-08-12).** Routes 1 and 2 terminate in Obsidian, which no tool here
can observe, so their registers were supplied by the Architect (§5) rather than measured from the
repo. Route 3 and the composition census are measured directly. Nothing is estimated.

---

## 1. The metric

Unit: **Architect actions required to move one piece of candidate material into one committed
artifact.** Counted in three registers, per route:

| Register | Definition | Counting rule |
|---|---|---|
| **Invocations** | Skill or tool calls the Architect must initiate | One per invocation. A skill that internally spawns 3 subagents counts as **1** — the Architect initiated once |
| **Context switches** | Crossings of the Claude Code ↔ Obsidian boundary | One per crossing, each direction |
| **Manual transcription** | Characters the Architect retypes **that a machine already held** | Authoring one's own prose is **not** transcription — that is the work. Retyping a claim, a stem, or a YAML key the machine already produced **is** |

The third register's exclusion is the load-bearing one: without it, route 1 (pure observation)
would score as maximally "high friction" simply because thinking involves typing, and the metric
would recommend automating the one thing this system exists to protect.

**Deliberately crude.** A crude observable defeats an eloquent impression. Today there is none.

---

## 2. Reproduction

Re-run these at seal; they are the whole method.

```powershell
# Judgment-node population (route 1 / route 2 output)
$v = "D:\MAS\project_chimera_vault"
foreach ($d in @("Thoughts","Insight","Decision")) {
  "$d : " + (Get-ChildItem "$v\$d" -Recurse -Filter *.md -File | Measure-Object).Count
}

# Machine-side population (route 3 input + K tiers)
foreach ($d in @("inbox","01_Deep_Reads","Knowledge","Harness")) {
  "$d : " + (Get-ChildItem "$v\$d" -Recurse -Filter *.md -File | Measure-Object).Count
}

# Harness lifecycle states (route 3 terminal evidence)
Get-ChildItem "$v\Harness" -Filter *.md -File | ForEach-Object {
  $h = Get-Content $_.FullName -TotalCount 14
  "{0} | {1} | {2}" -f $_.Name, ($h|Select-String '^status:').Line, ($h|Select-String '^verdict:').Line
}
```

Typed counts via MCP: `vault_query(type="thought"|"insight"|"decision")`. **Note:** `vault_query`
matches the `templates/Tpl_*.md` files too — subtract them. It filters `type` / `status` /
`linked_to` only; `chimera_tier` is returned in each row's excerpt but is not a filter
(`vault_query.py:70-79`), so tier splits are counted from returned rows or via
`search_vault_attribute`.

---

## 3. Composition baseline (D2)

**Window start: 2026-08-12** (repo inception → this date; the vault predates chimera-lite, so
this is a cumulative census, not a rate. Seal-time and later readings are deltas against it.)

### Hand-authored judgment nodes — routes 1 and 2 output

| Folder | Files | Declaring the right `type:` | Notes |
|---|---|---|---|
| `Thoughts/` | 6 | 6 | All `type: thought`. 2 of 6 carry no `status:` |
| `Insight/` | 8 | **1** | 1 stray `....md`; 6 are legacy free-form notes in `Anti-patterns/`, `cognitive_science/`, `Meta-theory/` with no or partial frontmatter |
| `Decision/` | 1 | **0** | The single file is the stray `....md`. **There are zero decision nodes.** |

**Hand-authored total: 7 real judgment nodes** (6 T + 1 I + 0 D).

### Machine-produced material — route 3 input

| Folder | Files | Meaning |
|---|---|---|
| `inbox/` | **378** | scout-tier cards from `daily_paper_pipeline` / `ingest_paper` |
| `01_Deep_Reads/` | 18 | deep-read nodes (pre-`ascend_node` era) |
| `Knowledge/` | 3 | **committed** K tier — 1 is the stray `....md`, so **2 real** |
| `Harness/` | 6 | 4 `w1_verdict`, 2 `w2_breadth_map` |

### The ratio

**378 machine-ingested cards : 7 hand-authored judgment nodes**, and **2** committed K nodes in
the entire history of the vault.

This is the number D2 exists to track. It is not yet evidence of a nudge — the vault's scout
volume is a pipeline artifact, and most of those 378 were never meant to be read deeply. But it
is the honest starting point, and if the hand-authored column does not move while the others do,
that is the drift, visible without argument.

---

## 4. Route baselines

### Route 3 — batch promote (AI-driven, human-curated) — **MEASURED**

Walked against the live vault, 2026-08-12.

| Register | Count | Evidence |
|---|---|---|
| Invocations | **N** (one `chimera-w1-verify` run per claim) | The skill's loop normalizes *the* claim, singular; no N-claim entry exists (`chimera-w1-verify/SKILL.md:26-58`) |
| Context switches | **≥1**, then the route **dead-ends** | Verdicts land in `Harness/` at `PENDING_REVIEW` for Obsidian curation (`result_service.py:187`) |
| Manual transcription | **All of it** — every support edge hand-written as YAML | No automated edge staging exists |

**The route cannot be completed.** `_VALID_MODES = frozenset({"supersede", "merge", "reject",
"mark_stale"})` (`result_service.py:56`) — there is no `promote`. `phase-L.md:139-142` declares
`PENDING_REVIEW → PROMOTED`; no code implements it.

**Confirmed empirically: all 6 Harness artifacts are `PENDING_REVIEW`. Not one has ever been
promoted, rejected, or marked stale.** The route has never been walked to its end by anyone,
which is why the missing terminal operation survived two phase specs unnoticed.

Verdict distribution across the 4 W1 artifacts: 1 `V`, 2 `P`, 1 `U`. The single `[V]`
(`Harness/w1_verdict__2606.16353.md`) is C.3c's acceptance fixture.

#### Route 3 re-measured after C.3a + C.3c (2026-08-12)

Live run of `chimera-w1-review` against the same vault, 4 pending verdicts.

| Register | Before | After |
|---|---|---|
| Invocations | **N** (one `chimera-w1-verify` per claim) + the promote that did not exist | **1** |
| Context switches | ≥1, then the route dead-ended | **0** |
| Manual transcription | every support edge hand-written as YAML | **0** |
| Completes? | **No** — no `promote` mode existed | **Yes** |

Observed: 4 verdicts rendered with their grounding quotes, 1 selected, 1 promoted
(`PENDING_REVIEW → PROMOTED`), 3 left untouched, both W2 maps correctly out of scope, body
byte-intact, no patch staged (the `[V]`'s paper has no committed K node).

**This was the first promotion in the vault's history.** Before it, all 6 harness artifacts had
sat at `PENDING_REVIEW` since they were written, because the transition did not exist.

The register that matters is the last row. Route 3's friction was never really "N invocations" —
it was infinite, because the route had no end.

### Route 2 — AI-assisted authoring — **PARTIAL**

| Register | Count | Status |
|---|---|---|
| Invocations | **1** (`chimera-deep-extract`), +1 if W1 is run on a surfaced claim | Measured — skill-side is observable |
| Context switches | **1+** (Claude Code → Obsidian to author) | Measured as a lower bound; the return crossings are not observable from here |
| Manual transcription | **`informed_by` key *and* value, both typed by hand** | Measured. `Tpl_thought.md:8-12` has four `graph_edges` keys and no `informed_by`, so the Architect types the key too. This is exactly C.4's target |

Blocked half: the authoring session's own action count. Architect input required.

### Route 1 — pure observation — **ARCHITECT-BLOCKED**

| Register | Count | Status |
|---|---|---|
| Invocations | 0 (structurally — the route never enters Claude Code) | Known by construction |
| Context switches | 0 | Known by construction |
| Manual transcription | **0 by definition** — the note is the work, not retyped machine output | Known by construction |

Route 1 has **no repo surface at all** (audit cross-finding 5). Its friction is entirely inside
Obsidian and can only be reported by the Architect. **This is the finding, not a gap in the
measurement:** the phase cannot smooth route 1, cannot measure it from here, and any step-count
comparison will score it as free while it may not feel free at all. That asymmetry is what the
VISION gate must judge, and it is why C.4 (the boundary bridge) is the sprint that matters most
for I1.4.

---

## 5. Architect-supplied registers (2026-08-12) — **RECEIVED**

Reported by the Architect as a description of normal practice, not a staged walk-through. Recorded
as such: these are habits, not a timed trial.

### Route 1 — pure observation

> *"Create a T node via keyboard shortcut, fill the contents, and no links."*

| Register | Count | Reading |
|---|---|---|
| Invocations | **1** (an Obsidian keyboard shortcut) | Never enters Claude Code |
| Context switches | **0** | Never leaves the editor |
| Manual transcription | **0** | The contents are the work, not retyped machine output |
| **Edges filled** | **0** | The decisive datum — see below |

### Route 2 — AI-assisted

> `informed_by` is **skipped entirely.**

### What these two answers actually establish

Route 1 is not merely low-friction; it is **1 action and zero edges at authoring time**.

**Correction (2026-08-12, during C.4b).** An earlier revision of this section claimed all six
T-nodes carry empty `graph_edges`. That is **false**, and the truth is more useful. Measured on
disk:

| Node | `derives_from` | `informed_by` |
|---|---|---|
| Thought-implicit restriction and deep personalization | 0 | key absent |
| Thought-memory bench-implementation pitfalls | **4** | key absent |
| Thought-memory bench-mix arch | **2** | key absent |
| Thought-trajectory-pattern grounding (DR6) | **6** | key absent |
| Thought-visual memory cellings | **1** | key absent |
| Thought-visual memory substrates | **2** | key absent |

**Five of six carry edges — 15 `derives_from` links in total**, every one pointing at a deep-read
node. The Architect demonstrably *does* fill edges by hand; "no links" describes the authoring
*moment*, not the node's final state. Edges arrive in a later pass.

**What is never filled is `informed_by` — the one key absent from the template.** That is a far
stronger causal story than "the Architect does not do format work": the edge type present in
`Tpl_thought.md` gets populated 15 times, and the edge type missing from it gets populated zero
times. **Template presence predicts edge population**, which makes C.4a's one-line template change
the intervention most likely to move the number, and makes the vault-template sync
(`NODE_ONTOLOGY.md` §5) the Architect's highest-leverage action rather than housekeeping.

`informed_by` is not typed, not pasted — **not recorded at all**. So I0.5's mandated provenance
record is not merely mechanism-less (`ENFORCEMENT_DEBT` D-3); it is **unused**. That moves C.4
from an ergonomics problem to an adoption one, exactly as anticipated.

And the Architect's framing names the cause: **edges are format work — they are not "machine/AI
free."** Filling `informed_by` correctly requires the exact key, the exact wikilink stem, and the
exact list syntax. That is machine work, not judgment, and it is not the work being done at the
moment a thought is written. The metric's third register was built to protect the Architect's
prose from being counted as friction; this datum shows the converse also holds — **structured edge
entry is friction that a human should never have been paying.**

**Consequence beyond this sprint.** I0.5 reserves the *body*; D-7 settled that an edge is
metadata, not content. So a tool may write judgment-node edges, and `stage_link_patch` /
`apply_link_patch` have been able to do so since Phase O — the vocabulary simply excluded
`informed_by`. This is a candidate root cause for the typed graph being empty for months
(`friction-260708-01`, the Phase N.B cancellation), and a better one than "the write path was
missing": the write path existed and its vocabulary did not reach the judgment side.

Constraint the Architect attached, carried into C.4's red lines: **propose, never auto-apply.**
Claude proposes the edge on an unlinked node; the Architect explicitly orders the apply.

---

## 6. Findings carried out of C.1

1. **Route 3 has never been completed.** All 6 Harness artifacts sit at `PENDING_REVIEW`; the
   terminal transition does not exist in code. Owned by C.3a.
2. **There are zero Decision nodes and one Insight node** with correct frontmatter. The K/T/I/D
   ontology is, in practice, a K/T ontology. Not an L.C deliverable — recorded because D2's
   drift measure is nearly degenerate on the I and D axes.
3. **`Insight/` holds 6 legacy free-form notes** outside the schema (no or partial frontmatter,
   in three subfolders). They are invisible to `vault_query` and to any typed traversal. Not in
   scope (no opportunistic refactoring); relevant to any future graph work.
4. **A stray `....md` exists in `Insight/`, `Decision/`, and `Knowledge/`.** Counted and excluded
   above. Not investigated — out of scope.
5. **`chimera_tier` is absent from every hand-authored T/I/D node** (`tier=?` on all rows). This
   is consistent with `NODE_ONTOLOGY.md §7.1`, which assigns `synthesis` to hand-written nodes and
   records that no code path sets it. Tier-based counting therefore does not work on the judgment
   side; count by `type` and folder.

---

*Sprint C.1 — partial. Registers for routes 1 and 2 await Architect input (§5); everything
measurable from the repo and vault is recorded above.*
