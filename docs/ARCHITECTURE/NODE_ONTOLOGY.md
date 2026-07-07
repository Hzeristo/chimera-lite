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

| Edge | Meaning (this node → target) | Applies to |
|---|---|---|
| `derives_from` | Provenance / lineage — this node was built from the target(s). | K T I D |
| `supersedes` | Replacement — this node obsoletes the target (newer/better understanding). | K T I D |
| `contradicts` | Conflict — this node's content conflicts with the target. *(Feeds state-collision arbitration + `deep_recall`.)* | K T I D |
| `dead_ends` | Abandonment — this node records a path/approach that was tried and dropped. | T D |
| `drives_decision` | Forward pointer — this node drove the target **decision**. | T I D |
| `synthesizes` | This **insight** fuses the target source nodes into a new understanding. | I |
| `evidence_base` | The supporting evidence for this **insight**. *(canonical name; was code's `verified_with`)* | I |

### Canonical set per type

- **K (knowledge)** — `derives_from`, `supersedes`, `contradicts`
- **T (thought)** — `derives_from`, `supersedes`, `contradicts`, `dead_ends`, `drives_decision`
- **I (insight)** — `synthesizes`, `evidence_base`, `derives_from`, `drives_decision`, `supersedes`, `contradicts`
- **D (decision)** — `derives_from`, `drives_decision`, `dead_ends`, `supersedes`, `contradicts`

The three universal edges (`derives_from`, `supersedes`, `contradicts`) are present on **all four** types so
`deep_recall` has a type-agnostic backbone to traverse.

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

---

## 5. Recommended vault-template updates (USER work — I must not touch `templates/`)

The repo authority is this file; Obsidian renders whatever frontmatter a note carries, so these are for
**consistency between hand-created and tool-created nodes**, not correctness. Optional, user-applied:

- `templates/Tpl_thought.md` — add `dead_ends: []`
- `templates/Tpl_decision.md` — add `contradicts: []`

(K and I vault templates already match the canonical set — no change.)

---

## 6. Out of scope for O.1a

- Backfilling edges on the ~250 existing K Nodes (`phase-O.md:43` — user work after O.3).
- Wiring the richer `obsidian_tpl/*.j2` node bodies (lesson/actionable/rationale scaffolds) — O.1b ships
  minimal-dict frontmatter (batch-plan reconciliation #5); this doc governs only the `graph_edges` vocabulary.
- `STAGING_PROTOCOL.md` (never migrated) — author separately if the need surfaces (batch-plan Deferred/open).

---

*Sprint O.1a — RATIFIED 2026-07-07. O.1b mirrors §4 into `_TYPE_EDGES`.*
