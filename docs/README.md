# docs/ — who reads what, and what must never be loaded whole

**Read this before opening anything else under `docs/`.** It is a router, not a summary: its job is
to tell you what *not* to load. `docs/` is ~1.6 MB; a session that opens the wrong directory
wholesale has spent its context on history it did not need and will reason worse for it.

**The red line: progressive disclosure.** Load the smallest thing that answers the question. An
archive is **grepped, never read through** — `Grep` for the symptom, open the one file that matches,
stop. If you find yourself reading a third file from an archive directory, you are researching, not
answering, and should say so out loud.

Load policy follows decay class (`docs/phases/PHILOSOPHY.md` §5) almost exactly: **generative** docs
constrain behaviour so they must be known; **descriptive** docs are consulted when current state
matters; **historical** docs are evidence, retrieved on demand and never browsed.

| Path | Consumer | Kind | Load policy |
|---|---|---|---|
| `ARCHITECTURE/INVARIANTS.md` | every agent, before any change | generative | **Read before changing anything.** FROZEN — reference, never restate |
| `ARCHITECTURE/ENFORCEMENT_DEBT.md` | anyone relying on an invariant | descriptive | **Read before trusting an invariant.** An invariant is not a shipped guarantee |
| `ARCHITECTURE/FORMAL_MODEL.md`, `NODE_ONTOLOGY.md`, `TAG_SYSTEM.md` | agents touching nodes/edges/tags | generative | Reference on demand — look up the rule you need |
| `ARCHITECTURE/ARCHITECTURE_RULES.md` | before any change | generative | The Violation Detector checklist. Subordinate to INVARIANTS |
| `ARCHITECTURE/THEORETICAL_FRAMEWORK.md`, `AUTO_RESEARCH_REQ_REFS.md` | design discussions | reference | On demand. Defers to the canonical on any divergence |
| `ARCHITECTURE/ARCHITECTURE.md` | orientation | descriptive, **generated** | Do not hand-edit — `python scripts/gen_architecture_diagram.py` |
| `phases/PHILOSOPHY.md`, `CODENAMES.md` | naming a phase, arguing about scope | generative | On demand. Does not decay; no date needed |
| `phases/phase-*.md` | the phase in flight | mixed | **Only the active phase.** Sealed phases are archive |
| `ROADMAP.md` | orientation, phase history | descriptive | Skim for position. Self-admittedly lags the build |
| `plans/` | the batch in flight | historical once executed | **Archive.** Only the active batch plan is live |
| `sprints/` | writing a sprint record; seal review | historical | **Archive — grep, never browse.** Evidence for a seal |
| `audits/` | phase audit input; seal reviews | historical | **Archive — grep.** Largest directory here |
| `incidents/` | a defect that smells familiar | historical | **Archive — grep the symptom.** Never read through |
| `logs/friction-*.md` | phase audit; batch planning | historical | **Archive — grep.** Entries before 2026-07-08 use a retired Chinese schema; tolerate the variance, never rewrite them |
| `logs/DEFECTS.md` | "have we seen this shape before?" | mixed | **Read the rules and the Live status block; grep the ledgers.** The 38 entries are an index, not reading material |
| `staging/` | **not documentation** | — | Vault candidates awaiting `ascend_node`. Never auto-promote |
| `TECHNICAL_DEBT.md`, `ACCEPTED_PARTIALS.md` | seal reviews | descriptive | On demand |
| `MIGRATION_LINEAGE.md`, `plunder_list.md` | provenance questions about inherited code | historical | Archive |

## The three that are actually always-relevant

Everything above is on demand except these, and even these are pointers rather than payloads:

1. **`ARCHITECTURE/INVARIANTS.md`** — what must be true. Frozen.
2. **`ARCHITECTURE/ENFORCEMENT_DEBT.md`** — what the code actually holds. Check before relying on 1.
3. **`ARCHITECTURE/ARCHITECTURE_RULES.md`** — the checklist to run before changing anything.

`../CLAUDE.md` is the only always-loaded document and deliberately stays lean; `../TBD.md` carries
what is open and waiting on the Architect.

## Why this file is itself allowed to exist

It states **policy**, not contents — no file counts, no lists that grow. Adding a sprint record does
not falsify a line here, which is what keeps a router from becoming the next thing that quietly goes
stale. If a directory's *purpose* changes, this file is wrong and should be fixed; if a directory
merely gains files, it is not.
