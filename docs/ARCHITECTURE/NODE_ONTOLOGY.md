# NODE_ONTOLOGY — Chimera Lite K/T/I/D typed-edge authority

**Status:** ✅ RATIFIED (2026-07-07) — both renames approved by the user (Phase O, sprint O.1a).
**Authored:** 2026-07-07 · **Sprint:** O.1a (`docs/plans/Phase-O-batch.md`) · **Audit:** `docs/audits/O.0.md` Q4 / cross-finding #2.
**Supersedes:** the three scattered, disagreeing definitions below are now unified here.
`StagingService._TYPE_EDGES` (`mcp-servers/chimera-papers/staging_service.py:12-16`) mirrors this file (done in O.1b), and
this file is the single place the K/T/I/D typed-edge vocabulary is defined.

> This is the authority the deferred **Phase N.B** `deep_recall` will traverse. The vault graph is empty
> today (N.B.0 Q4) precisely because the write path emits an inconsistent / incomplete edge set. O.1a fixes
> the *definition*; O.1b emits it; O.2 links with it; O.3 seeds it.

---

## 1. Why this doc exists

Three representations of the "same" typed-edge schema disagree, and the V.A authority doc `NODE_ONTOLOGY.md`
never migrated into this repo (`docs/ARCHITECTURE/` was empty). The **Decision-2 mod-time probe was
inconclusive** (both families last written 2026-06-15, within ~26 min → the "within 1 week → manual review"
fallback; see `docs/audits/O.0.md` addendum). So mod-time cannot pick a winner — the schema is reconciled
here **by hand**, with an explicit rule per divergent edge.

### The three sources (read directly, 2026-07-07)

| Type | Code family — `_TYPE_EDGES` + `obsidian_tpl/*.j2` | User-synced vault — `templates/Tpl_*.md` |
|---|---|---|
| **K** | *(absent from `_TYPE_EDGES` — `create_staging_node` rejects `knowledge`)*; `.j2`: `derives_from, supersedes, contradicts` | `derives_from, supersedes, contradicts` |
| **T** | `derives_from, supersedes, contradicts, dead_ends` | `derives_from, drives_decision, supersedes, contradicts` |
| **I** | `synthesizes, verified_with, derives_from, supersedes, contradicts` | `synthesizes, evidence_base, derives_from, drives_decision, supersedes, contradicts` |
| **D** | `depends_on, dead_ends, supersedes, contradicts` | `derives_from, dead_ends, drives_decision, supersedes` |

Evidence: `staging_service.py:12-16`; `{thought,insight,decision,knowledge,deep_read}_node.j2:7-17`;
`<vault>/templates/Tpl_{knowledge,thought,insight,decision}.md` (grep, 2026-07-07).

---

## 2. Canonical edge vocabulary (proposed)

All edges are **directional**, stored in a node's frontmatter as a list of target wikilink stems, pointing
**from this node → the target(s)**. An empty list (`[]`) means "no such edge yet."

> **An edge is metadata, not an object** (Architect ruling, 2026-08-12). Unlike a KG proper, an edge
> here has no independent identity, no provenance of its own, and no existence apart from the
> frontmatter list it sits in. The consequence is scope, not convenience: appending an edge to a
> committed node does **not** modify that node's committed **content**, so it does not engage
> `INVARIANTS.md` I1.2's writer clause. `ascend_node` is the sole writer of *new committed nodes*;
> `apply_link_patch` mutating an existing node's `graph_edges` is a distinct, human-invoked path and
> needs no tier guard. Recorded as `ENFORCEMENT_DEBT.md` **D-7**.

| Edge | Meaning (this node → target) | Applies to |
|---|---|---|
| `derives_from` | Provenance / lineage — this node was built from the target(s). | K T I D |
| `supersedes` | Replacement — this node obsoletes the target (newer/better understanding). | K T I D |
| `contradicts` | Conflict — this node's content conflicts with the target. *(Feeds state-collision arbitration + `deep_recall`.)* | K T I D |
| `dead_ends` | Abandonment — this node records a path/approach that was tried and dropped. | T D |
| `drives_decision` | Forward pointer — this node drove the target **decision**. | T I D |
| `synthesizes` | This **insight** fuses the target source nodes into a new understanding. | I |
| `evidence_base` | The supporting evidence for this **insight** or **knowledge** node. *(canonical name; was code's `verified_with`)* | K I |
| `collides_with` | Two claims occupy the same evidence envelope without directly contradicting; each's success structurally blocks the other's novelty. *(Distinct from `contradicts`, which is a conflict of content.)* | K T I D |
| `informed_by` | Records that a T/I/D node was authored **while viewing** an AI output (W2 map, extract synthesis). Context, not derivation — it documents the tool used and never transfers authorship (`INVARIANTS.md` I0.5). | T I D |

> **`evidence_base` extended to K** (Architect ratification, 2026-08-12 — Phase L.C sprint C.3b).
> W1 verifies a claim that usually lives in a Knowledge node, and its verdict artifact is that
> claim's supporting evidence — with no legal K edge to express "supported by this verdict," the
> phase Mission (every committed node's support chain is traceable) was unreachable. I2.2 (Tier 2)
> states the edge vocabulary is mutable, so this is a documented evolution, not a canonical breach.
> `evidence_base` is support-bearing (below), so it must stay auto-written and traversable per
> **I0.2**, and closing this gap is what makes a K node's chain traceable to Tier-1 evidence per
> **I1.3** — Phase K's monotonicity gate will read this edge on Knowledge nodes.

**Support-bearing subset.** Monotonicity (`INVARIANTS.md` I0.2) propagates along
`evidence_base`, `synthesizes`, `derives_from` — and **only** those. `informed_by` is explicitly
**not** support-bearing: an AI output that informed a node is not a dependency of it. Authority for
the subset is `FORMAL_MODEL.md` (`support(v)`); this file does not restate it.

### Canonical set per type

- **K (knowledge)** — `derives_from`, `supersedes`, `contradicts`, `evidence_base`, `collides_with`
- **T (thought)** — `derives_from`, `supersedes`, `contradicts`, `dead_ends`, `drives_decision`, `collides_with`, `informed_by`
- **I (insight)** — `synthesizes`, `evidence_base`, `derives_from`, `drives_decision`, `supersedes`, `contradicts`, `collides_with`, `informed_by`
- **D (decision)** — `derives_from`, `drives_decision`, `dead_ends`, `supersedes`, `contradicts`, `collides_with`, `informed_by`

The three universal edges (`derives_from`, `supersedes`, `contradicts`) are present on **all four** types so
`deep_recall` has a type-agnostic backbone to traverse. `collides_with` joins them as a fourth
universal edge (any two claims can share an evidence envelope); `informed_by` is T/I/D-only, because
I0.5 scopes it to judgment-type nodes whose bodies are Architect-authored.

> **Code sync complete** (2026-08-12, Phase L.C sprint C.4a). `StagingService._TYPE_EDGES`
> (`staging_service.py:13-18`) now mirrors the sets above exactly — `collides_with` on all four
> types, `informed_by` on T/I/D only. `ENFORCEMENT_DEBT.md` **D-3 is discharged**. The mirror is
> guarded by `tests/test_staging_tools.py::test_ontology_mirrors_node_ontology_doc`, which asserts
> against this file's sets rather than against the code's own.

---

## 3. Per-divergence resolution (the rules)

Each divergent key, with the rule applied and why. **A = adopt · R = rename · +Add · −Drop.**

| Type | Key | Rule | Reason |
|---|---|---|---|
| K | *(whole `knowledge` entry)* | **+Add to `_TYPE_EDGES`** | Code rejects `knowledge` (`staging_service.py:33-35`) — the direct cause of the empty graph. `.j2` + vault already agree on the 3 keys; adopt them verbatim. |
| T | `dead_ends` | **A (keep)** | Code/`.j2` has it, vault lacks it. Thoughts can be abandoned; the edge is meaningful. → **user vault-template gains `dead_ends`** (recommended, §5). |
| T | `drives_decision` | **A (keep)** | Vault has it, code lacks it. A thought can drive a decision; keep the forward pointer. → **code gains `drives_decision`.** |
| I | `verified_with` → `evidence_base` | **R (rename)** ⚠️ | Same semantics (an insight's supporting evidence). Canonicalize on the **vault's** term `evidence_base` to match the user's live convention. Code renames. *No existing node uses `verified_with` (T/I graph is empty), so the rename is data-safe.* |
| I | `drives_decision` | **A (keep)** | Vault has it, code lacks it. Insight → decision forward pointer. → **code gains `drives_decision`.** |
| D | `depends_on` → `derives_from` | **R (rename)** ⚠️ | Code-only `depends_on` ≈ provenance; the vault + every other type use the universal `derives_from`. Unify on `derives_from` to keep one provenance edge. Code renames. *No existing decision node uses `depends_on`.* |
| D | `contradicts` | **A (keep)** | Code/all-other-vault-types have it; vault **D** is the lone omission — decisions certainly can conflict. Restore it. → **user vault-template gains `contradicts`** (recommended, §5). |
| D | `drives_decision` | **A (keep)** | Vault has it (a decision can drive a follow-on decision); code lacks it. → **code gains `drives_decision`.** |
| — | `promoted_to_insight` | **−Drop** | Appears in **neither** source on direct read (the O.0 audit's sampling guessed it; the live `Tpl_thought.md` has `drives_decision`, not this). Not adopted. |

### ✅ Two renames — RATIFIED by the user (2026-07-07)

Both near-synonym renames were approved as recommended:

1. **`verified_with` → `evidence_base`** (insight) — APPROVED. Adopt the vault's live term.
2. **`depends_on` → `derives_from`** (decision) — APPROVED. Unify on the universal provenance edge.

---

## 4. What O.1b changes in code (do NOT execute here — O.1a is doc-only)

On ratification, `StagingService._TYPE_EDGES` becomes exactly the §2 canonical set:

```python
_TYPE_DEST = {"knowledge": "Knowledge", "thought": "Thoughts", "insight": "Insight", "decision": "Decision"}
_TYPE_EDGES = {
    "knowledge": {"derives_from": [], "supersedes": [], "contradicts": []},
    "thought":   {"derives_from": [], "supersedes": [], "contradicts": [], "dead_ends": [], "drives_decision": []},
    "insight":   {"synthesizes": [], "evidence_base": [], "derives_from": [], "drives_decision": [], "supersedes": [], "contradicts": []},
    "decision":  {"derives_from": [], "drives_decision": [], "dead_ends": [], "supersedes": [], "contradicts": []},
}
```

*(K's destination subfolder `"Knowledge"` is a placeholder — confirm the actual vault K folder name in O.1b.)*

> **Superseded snapshot.** The block above is the **O.1b-era** target and is kept as the record of
> what that sprint changed. It no longer matches the code: `evidence_base` was extended to K
> (C.3b) and `collides_with` / `informed_by` were added (C.4a). **§2 is the authority** — read it,
> not this snippet, and `tests/test_staging_tools.py::test_ontology_mirrors_node_ontology_doc`
> asserts the code against §2.

---

## 5. Recommended vault-template updates (USER work — I must not touch `templates/`)

The repo authority is this file; Obsidian renders whatever frontmatter a note carries, so these are for
**consistency between hand-created and tool-created nodes**, not correctness. Optional, user-applied:

- `templates/Tpl_thought.md` — add `dead_ends: []`
- `templates/Tpl_decision.md` — add `contradicts: []`

**Added 2026-08-12 (C.4a), and this one matters more than the two above.** The repo sources
`prompts/obsidian_tpl/Tpl_{thought,insight,decision}.md` gained `informed_by: []`. Syncing it into
the vault's own templates is what makes the field present at the moment a judgment node is
authored — the point at which the Architect is demonstrably *not* filling edges by hand
(`docs/audits/L.C.1-friction-baseline.md` §5: *"no links"*, `informed_by` skipped entirely). A
tool can now propose the edge either way, but a node whose template lacks the key starts life
without a slot for its own provenance.

(K and I vault templates already match the canonical set — no change.)

---

## 6. Out of scope for O.1a

- Backfilling edges on the ~250 existing K Nodes (`phase-O.md:43` — user work after O.3).
- Wiring the richer `obsidian_tpl/*.j2` node bodies (lesson/actionable/rationale scaffolds) — O.1b ships
  minimal-dict frontmatter (batch-plan reconciliation #5); this doc governs only the `graph_edges` vocabulary.
- `STAGING_PROTOCOL.md` (never migrated) — author separately if the need surfaces (batch-plan Deferred/open).

---

## 7. `chimera_tier` + `status` — the two lifecycle axes (Phase L.B, 2026-07-21)

Two ORTHOGONAL frontmatter axes govern a node's place in the pipeline. They are never
folded into each other (Phase L.B red line: tier is not carried by `status`).

### 7.1 `chimera_tier` — origin/depth (which writer made this node, and how deep)

The C-1 defect (`docs/audits/workflow-drift-audit.md`): every K writer emitted
`type: knowledge`, so a shallow triage card and a full deep-read node were
indistinguishable. `chimera_tier` is the net-new field that separates them.

| tier | Meaning | Writer (active code path) |
|---|---|---|
| `scout` | Shallow LLM triage of a fetched paper — an inbox card, not yet read in depth. | `VaultNoteWriter.write_knowledge_node` (`knowledge_node.j2`) — `daily_pipeline` / `ingest_paper`. |
| `deep_read` | Full-paper extraction (synthesis + lens + attack + ARA claims, or the survey atlas). | `single_paper_extract` (via `create_staging_node`, staging) + `VaultNoteWriter.write_deep_read_node` (`deep_read{,_survey}_node.j2`, optics). |
| `harness_candidate` | A W1/W2 research-harness artifact awaiting Architect curation. | `ResultService.write_result` → `Harness/` (already `kind`-keyed with a review status; the tier is this documented mapping — harness artifacts are not K/T/I/D nodes). |
| `synthesis` | A user-authored T/I/D node — reasoning, not ingestion. | **No code path. The Architect writes these in Obsidian by hand** (see §7.1.1). |

**Why `knowledge` is never defaulted.** A `knowledge` node created with no tier stays
untiered so its writer is FORCED to declare `scout` vs `deep_read`. A silent K default would
re-open C-1.

#### 7.1.1 T/I/D are hand-written — above all

**No tool authors a Thought, Insight, or Decision.** I0.5 (Tier 0) reserves judgment-type
bodies for the Architect: *"A T/I/D node with an AI-written body violates I0.5 — illegal,
even if promoted."* A `body` passed to an MCP tool is written by the tool's caller, and the
caller of this system's MCP surface is Claude — so a machine path that accepts a T/I/D body
is a machine path for AI-authored judgment, whatever the intent behind it.

Accordingly, as of **2026-08-11**:

- `create_staging_node` / the `create_node` MCP tool are **knowledge-only**; T/I/D are
  refused with an error pointing at Obsidian.
- `promote_node` — which moved staged T/I/D into the vault — is **retired**. `ascend_node` is
  now the only path from staging into any committed tier, and `_ascend_write` refuses every
  destination but `Knowledge/`.
- This row previously named `create_staging_node` as the `synthesis` writer while defining
  the tier as "user-authored", a contradiction that stood until the drift was traced.

The evidence that this was always the real workflow: every T/I/D node in the vault carries
**spaces** in its filename (`Thought-visual memory substrates.md`), while the retired writer
slugged whitespace to underscores. In the seven weeks the machine path existed, not one node
used it.

**How AI output legitimately reaches a judgment node.** It informs the Architect, who writes
the body. Provenance is recorded with `informed_by` (§2), which documents the tool consulted
and is explicitly **not** support-bearing — it transfers no authorship (I0.5, I2.2). Note the
open gap: `informed_by` is defined in the canonical but not yet emittable in code
(`ENFORCEMENT_DEBT.md` D-3), so today it is typed by hand in frontmatter — which, for a
hand-authored node, is the correct place for it anyway.

### 7.2 `status` — lifecycle (committed vs uncommitted)

`status` is orthogonal to tier: it tracks whether a node is committed, independent of how
deep it is. The live vocabulary (EXTENDED, not rebuilt — Phase L.B fact F4):

| status | Stage | Set by |
|---|---|---|
| `unverified` | Inbox scout card — landed, not yet human-reviewed. | `knowledge_node.j2` |
| `PENDING_REVIEW` | Staged K/T/I/D candidate awaiting review. | `create_staging_node` |
| `active` | Committed into the vault. | `promote_node` (staging → vault); `ascend_node` (inbox\|staging → `Knowledge/`, Phase L.B.3) |
| `cross_verified` | Insight confirmed across sources (I nodes). | `insight_node.j2` |

**The "inert inbox status" gap (C-1) is resolved by the tier axis + `ascend_node`, not by
an auto-transition.** A scout card's `unverified` is intentionally terminal-until-human:
scout tier stays in `inbox/` and is NEVER auto-promoted (phase red line). The transition
`unverified → active` fires only when the Architect ascends the node via `ascend_node`
(Phase L.B.3). The status is human-gated, not dead.

*(Anomaly, NOT fixed here — no opportunistic refactoring: `deep_read_survey_node.j2` uses
`chimera_status: survey_deep_read` instead of `status:`. It carries `chimera_tier: deep_read`
like the other deep-read template; reconciling its status key is deferred.)*

*Sprint O.1a — RATIFIED 2026-07-07. O.1b mirrors §4 into `_TYPE_EDGES`.*
